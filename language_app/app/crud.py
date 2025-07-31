from sqlalchemy.orm import Session
from app import models, schemas
from app.auth import get_password_hash
from sqlalchemy import Integer, func, cast, Date
from datetime import datetime
from app.models import User


def create_user(db: Session, user: schemas.UserCreate, is_admin: bool = False):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password, is_admin=is_admin)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_question(db: Session, question: schemas.QuestionCreate):
    db_question = models.Question(word=question.word, description=question.description)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question

def get_questions(db: Session):
    return db.query(models.Question).all()

def get_question(db: Session, question_id: int):
    return db.query(models.Question).filter(models.Question.id == question_id).first()

def delete_question(db: Session, question_id: int):
    question = get_question(db, question_id)
    if question:
        db.delete(question)
        db.commit()
        return True
    return False


def log_answer_attempt(db: Session, user_id: int, question_id: int, is_correct: bool):
    log = models.AnswerLog(
        user_id=user_id,
        question_id=question_id,
        is_correct=is_correct
    )
    db.add(log)
    db.commit()
    return log


def get_answer_stats_by_day(db):
    results = db.query(
        func.date(models.AnswerLog.timestamp).label("date"),
        func.sum(cast(models.AnswerLog.is_correct, Integer)).label("correct"),
        func.count(models.AnswerLog.id).label("total")
    ).group_by(func.date(models.AnswerLog.timestamp)).order_by(func.date(models.AnswerLog.timestamp)).all()

    stats = []
    for row in results:
        stats.append({
            "date": str(row.date),  
            "correct": row.correct,
            "incorrect": row.total - row.correct
        })
    return stats


def get_question_counts_by_day(db: Session):
    results = (
        db.query(func.date(models.Question.created_at), func.count(models.Question.id))
        .group_by(func.date(models.Question.created_at)).order_by(func.date(models.Question.created_at))
        .all()
    )
    return [{"date": r[0], "count": r[1]} for r in results]


def get_user_counts_by_day(db: Session):
    results = (
        db.query(func.date(models.User.created_at), func.count(models.User.id))
        .group_by(func.date(models.User.created_at)).order_by(func.date(models.User.created_at))
        .all()
    )
    return [{"date": r[0], "count": r[1]} for r in results]
