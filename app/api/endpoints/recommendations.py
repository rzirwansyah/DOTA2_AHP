from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from decimal import Decimal

from app.api import deps
from app.models import models
from app.schemas import recommendation as reco_schema
from app.core.ahp import AHPProcessor

router = APIRouter()

@router.post("/preferences", response_model=reco_schema.StatusResponse, summary="Mengirimkan preferensi kriteria")
def submit_preferences(
    *,
    db: Session = Depends(deps.get_db),
    prefs_in: reco_schema.PreferencesCreate,
    current_user: models.Users = Depends(deps.get_current_user)
):
    """
    Menerima preferensi user, menghitung bobot AHP, dan menyimpannya.
    """
    match_id = prefs_in.matchId
    match = db.query(models.Matches).filter(models.Matches.id == match_id, models.Matches.user_id == current_user.id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found or does not belong to user")

    # Ambil semua kriteria dari DB untuk mapping ID dan Code
    criterias_db = db.query(models.Criterias).all()
    criteria_map_id = {c.id: c for c in criterias_db}
    criteria_map_code = {c.code: c for c in criterias_db}
    
    # Hapus bobot lama jika ada
    db.query(models.Weights).filter(models.Weights.match_id == match_id).delete()
    db.query(models.Rankings).filter(models.Rankings.match_id == match_id).delete()

    # --- 1. Hitung bobot kriteria utama ---
    main_criteria_ranks = prefs_in.preferences.criteria
    goal_id = criteria_map_code['MG'].id # Asumsi 'MG' adalah kode untuk Tujuan Utama
    
    # Simpan ranking kriteria utama
    for i, crit_id in enumerate(main_criteria_ranks):
        db.add(models.Rankings(match_id=match_id, context_criterion_id=goal_id, criterion_id=crit_id, rank_order=i+1))

    ahp_main = AHPProcessor(main_criteria_ranks)
    if ahp_main.consistency_ratio > 0.1:
        raise HTTPException(status_code=400, detail=f"Main criteria preferences are inconsistent (CR: {ahp_main.consistency_ratio:.2f})")
    
    main_weights = ahp_main.weights
    for crit_id, weight in main_weights.items():
        db.add(models.Weights(match_id=match_id, criterion_id=crit_id, context_criterion_id=goal_id, weight=Decimal(weight)))

    # --- 2. Hitung bobot sub-kriteria dan bobot global ---
    sub_criteria_groups = prefs_in.preferences.subCriteria.dict()
    for group_name, rankings in sub_criteria_groups.items():
        if not rankings: continue
        
        # Dapatkan parent (context) dari sub-kriteria ini
        first_sub_crit_id = rankings[0]
        parent_code = criteria_map_id[first_sub_crit_id].parent
        parent_id = criteria_map_code[parent_code].id
        
        # Simpan ranking sub-kriteria
        for i, crit_id in enumerate(rankings):
             db.add(models.Rankings(match_id=match_id, context_criterion_id=parent_id, criterion_id=crit_id, rank_order=i+1))

        ahp_sub = AHPProcessor(rankings)
        if ahp_sub.consistency_ratio > 0.1:
            raise HTTPException(status_code=400, detail=f"Sub-criteria {parent_code} preferences are inconsistent (CR: {ahp_sub.consistency_ratio:.2f})")
        
        local_weights = ahp_sub.weights
        parent_global_weight = main_weights.get(parent_id, 0)
        
        for crit_id, local_weight in local_weights.items():
            global_weight = Decimal(local_weight) * Decimal(parent_global_weight)
            db.add(models.Weights(match_id=match_id, criterion_id=crit_id, context_criterion_id=parent_id, weight=global_weight))

    db.commit()
    return {"status": "success"}


@router.post("/alternatives", response_model=reco_schema.StatusResponse, summary="Mengirimkan penilaian hero alternatif")
def submit_alternatives(
    *,
    db: Session = Depends(deps.get_db),
    alts_in: reco_schema.AlternativesCreate,
    current_user: models.Users = Depends(deps.get_current_user)
):
    """
    Menerima penilaian user untuk 5 hero alternatif terhadap semua sub-kriteria.
    """
    match_id = alts_in.matchId
    match = db.query(models.Matches).filter(models.Matches.id == match_id, models.Matches.user_id == current_user.id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found or does not belong to user")
    
    # Hapus data alternatif lama jika ada
    db.query(models.Alternatives).filter(models.Alternatives.match_id == match_id).delete()

    criterias_db = db.query(models.Criterias).filter(models.Criterias.parent.isnot(None)).all()
    criteria_map_code = {c.code: c.id for c in criterias_db}

    for hero_alt in alts_in.heroes:
        hero_id = hero_alt.heroId
        scores = hero_alt.alternative.dict(by_alias=True) # by_alias=True untuk mendapatkan key 'PA-HC'
        
        for crit_code, score_val in scores.items():
            crit_id = criteria_map_code.get(crit_code.replace('_', '-'))
            if crit_id:
                db_alt = models.Alternatives(
                    match_id=match_id,
                    hero_id=hero_id,
                    criterion_id=crit_id,
                    score=Decimal(score_val)
                )
                db.add(db_alt)
    
    db.commit()
    return {"status": "success"}


@router.get("/{match_id}", response_model=reco_schema.RecommendationResponse, summary="Mendapatkan rekomendasi hero")
def get_recommendation(
    *,
    db: Session = Depends(deps.get_db),
    match_id: int,
    current_user: models.Users = Depends(deps.get_current_user)
):
    """
    Menghitung skor akhir dan memberikan urutan rekomendasi hero.
    """
    match = db.query(models.Matches).filter(models.Matches.id == match_id, models.Matches.user_id == current_user.id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found or does not belong to user")

    # 1. Ambil semua bobot global sub-kriteria
    goal_id = db.query(models.Criterias.id).filter(models.Criterias.parent.is_(None)).scalar()
    weights_db = db.query(models.Weights).filter(
        models.Weights.match_id == match_id,
        models.Weights.context_criterion_id != goal_id
    ).all()
    if not weights_db:
        raise HTTPException(status_code=400, detail="Preferences for this match must be submitted first.")
    
    weights_map = {w.criterion_id: w for w in weights_db}

    # 2. Ambil semua penilaian alternatif
    alternatives_db = db.query(models.Alternatives).filter(models.Alternatives.match_id == match_id).all()
    if not alternatives_db:
        raise HTTPException(status_code=400, detail="Alternatives for this match must be submitted first.")
    
    # --- AWAL PERBAIKAN ---
    # Hapus data lama dengan cara yang aman
    weight_ids_to_delete = [w.id for w in weights_db]
    if weight_ids_to_delete:
        db.query(models.Judgements).filter(models.Judgements.weight_id.in_(weight_ids_to_delete)).delete(synchronize_session=False)
    db.query(models.Scores).filter(models.Scores.match_id == match_id).delete(synchronize_session=False)
    # --- AKHIR PERBAIKAN ---
    
    # 3. Hitung judgement (score * weight)
    hero_scores = {} # {hero_id: total_score}
    
    for alt in alternatives_db:
        weight_obj = weights_map.get(alt.criterion_id)
        if weight_obj:
            weight_score = alt.score * weight_obj.weight
            
            # Simpan ke tabel judgements
            db.add(models.Judgements(weight_id=weight_obj.id, alternative_id=alt.id, weight_score=weight_score))
            
            # Akumulasi skor
            if alt.hero_id not in hero_scores:
                hero_scores[alt.hero_id] = Decimal(0)
            hero_scores[alt.hero_id] += weight_score

    # 4. Simpan skor akhir ke tabel scores
    for hero_id, final_score in hero_scores.items():
        db.add(models.Scores(match_id=match_id, hero_id=hero_id, final_score=final_score))
        
    db.commit()

    # 5. Ambil hasil dari tabel scores dan urutkan
    final_scores_db = db.query(models.Scores)\
        .options(joinedload(models.Scores.hero))\
        .filter(models.Scores.match_id == match_id)\
        .order_by(desc(models.Scores.final_score))\
        .all()
        
    recommendations = [
        reco_schema.RecommendationHero(
            heroId=s.hero_id,
            heroName=s.hero.name,
            finalScore=float(s.final_score)
        ) for s in final_scores_db
    ]

    return {"status": "success", "recommendations": recommendations}