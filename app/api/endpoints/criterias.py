from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.models import models
from app.schemas import criteria as criteria_schema

router = APIRouter()

@router.get("", response_model=criteria_schema.CriteriaResponse, summary="Mendapatkan referensi kriteria dan sub-kriteria")
def get_all_criterias(
    db: Session = Depends(deps.get_db),
    current_user: models.Users = Depends(deps.get_current_user)
):
    """
    Mengambil seluruh struktur model AHP, dari tujuan, kriteria, hingga sub-kriteria.
    """
    all_db_criterias = db.query(models.Criterias).all()
    
    # Buat mapping dari code ke object criteria
    criteria_map = {c.code: c for c in all_db_criterias}
    
    # Cari tujuan utama (parent is NULL)
    goal_db = next((c for c in all_db_criterias if c.parent is None), None)
    if not goal_db:
        raise HTTPException(status_code=404, detail="Goal (main objective) not found in database")

    # Buat struktur response
    response_model = criteria_schema.ModelSchema.from_orm(goal_db)
    
    main_criteria_db = [c for c in all_db_criterias if c.parent == goal_db.code]
    
    for mc_db in main_criteria_db:
        main_criteria_schema = criteria_schema.CriteriaSchema.from_orm(mc_db)
        
        sub_criteria_db = [c for c in all_db_criterias if c.parent == mc_db.code]
        for sc_db in sub_criteria_db:
            main_criteria_schema.sub_criterias.append(criteria_schema.SubCriteriaSchema.from_orm(sc_db))
        
        response_model.criterias.append(main_criteria_schema)

    return {"status": "success", "model": response_model}