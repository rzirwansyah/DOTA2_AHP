import enum
from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Numeric, Date,
    UniqueConstraint
)
from sqlalchemy.dialects.postgresql import JSONB, ENUM
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

# Definisi Enum sesuai dengan yang ada di PostgreSQL
class GameModeEnum(enum.Enum):
    all_pick = 'All Pick'
    turbo_mode = 'Turbo Mode'
    captain_mode = 'Captain Mode'
    single_draft = 'Single Draft'

class ResultBattleEnum(enum.Enum):
    win = 'Win'
    lose = 'Lose'
    draw = 'Draw'

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    matches = relationship("Matches", back_populates="user")

class Heroes(Base):
    __tablename__ = 'heroes'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    attribute = Column(String(100), nullable=False)
    attack_type = Column(String(50), nullable=False)
    difficulty = Column(String(20), nullable=False)
    role1 = Column(String(20), nullable=False)
    role2 = Column(String(20))
    role3 = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Criterias(Base):
    __tablename__ = 'criterias'
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, nullable=False)
    parent = Column(String(10))
    name = Column(String(255), nullable=False)
    description = Column(String(255))
    paraphrase = Column(String(255))
    narration = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Matches(Base):
    __tablename__ = 'matches'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    match_name = Column(String(255))
    match_date = Column(Date, nullable=False)
    match_mode = Column(ENUM(GameModeEnum, name='game_mode'), nullable=False)
    ally_team = Column(String(255))
    allies = Column(JSONB, nullable=False)
    enemy_team = Column(String(255))
    enemies = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("Users", back_populates="matches")
    rankings = relationship("Rankings", back_populates="match")
    alternatives = relationship("Alternatives", back_populates="match")
    weights = relationship("Weights", back_populates="match")
    scores = relationship("Scores", back_populates="match")
    history = relationship("Histories", back_populates="match", uselist=False)

class Rankings(Base):
    __tablename__ = 'rankings'
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey('matches.id'), nullable=False)
    context_criterion_id = Column(Integer, ForeignKey('criterias.id'), nullable=False)
    criterion_id = Column(Integer, ForeignKey('criterias.id'), nullable=False)
    rank_order = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (UniqueConstraint('match_id', 'context_criterion_id', 'rank_order', name='_match_context_rank_uc'),)

    match = relationship("Matches", back_populates="rankings")
    context_criterion = relationship("Criterias", foreign_keys=[context_criterion_id])
    criterion = relationship("Criterias", foreign_keys=[criterion_id])

class Alternatives(Base):
    __tablename__ = 'alternatives'
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey('matches.id'), nullable=False)
    hero_id = Column(Integer, ForeignKey('heroes.id'), nullable=False)
    criterion_id = Column(Integer, ForeignKey('criterias.id'), nullable=False)
    score = Column(Numeric, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (UniqueConstraint('match_id', 'hero_id', 'criterion_id', name='_match_hero_crit_uc'),)

    match = relationship("Matches", back_populates="alternatives")
    hero = relationship("Heroes")
    criterion = relationship("Criterias")

class Weights(Base):
    __tablename__ = 'weights'
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey('matches.id'), nullable=False)
    criterion_id = Column(Integer, ForeignKey('criterias.id'), nullable=False)
    context_criterion_id = Column(Integer, ForeignKey('criterias.id'), nullable=True)
    weight = Column(Numeric(10, 5), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (UniqueConstraint('match_id', 'criterion_id', name='_match_crit_uc'),)

    match = relationship("Matches", back_populates="weights")
    criterion = relationship("Criterias", foreign_keys=[criterion_id])
    context_criterion = relationship("Criterias", foreign_keys=[context_criterion_id])

class Judgements(Base):
    __tablename__ = 'judgements'
    id = Column(Integer, primary_key=True, index=True)
    weight_id = Column(Integer, ForeignKey('weights.id'), nullable=False)
    alternative_id = Column(Integer, ForeignKey('alternatives.id'), nullable=False)
    weight_score = Column(Numeric(10, 5), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (UniqueConstraint('weight_id', 'alternative_id', name='_weight_alt_uc'),)

    weight = relationship("Weights")
    alternative = relationship("Alternatives")

class Scores(Base):
    __tablename__ = 'scores'
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey('matches.id'), nullable=False)
    hero_id = Column(Integer, ForeignKey('heroes.id'), nullable=False)
    final_score = Column(Numeric(10, 5), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (UniqueConstraint('match_id', 'hero_id', name='_match_hero_score_uc'),)

    match = relationship("Matches", back_populates="scores")
    hero = relationship("Heroes")

class Histories(Base):
    __tablename__ = 'histories'
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey('matches.id'), nullable=False, unique=True)
    hero_id = Column(Integer, ForeignKey('heroes.id'), nullable=False)
    match_result = Column(ENUM(ResultBattleEnum, name='result_battle'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (UniqueConstraint('match_id', 'hero_id', name='_match_hero_history_uc'),)

    match = relationship("Matches", back_populates="history")
    hero = relationship("Heroes")