from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, crud, auth, database,models
from app.services import ai_generator
from app.database import get_db
from app.models import User, Question, AnswerLog

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/login")
async def login(form_data: schemas.UserCreate, db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user or not user.is_admin:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/questions/generate-description")
async def generate_description(word: str, current_user: schemas.UserOut = Depends(auth.get_current_admin_user)):
    description = await ai_generator.generate_description(word)
    return {"word": word, "generated_description": description}

@router.post("/questions")
def add_question(question: schemas.QuestionCreate, db: Session = Depends(get_db), current_user=Depends(auth.get_current_admin_user)):
    existing_question = db.query(models.Question).filter(models.Question.word == question.word).first()
    if existing_question:
        raise HTTPException(status_code=400, detail="Question with this word already exists")
    return crud.create_question(db, question)

@router.get("/questions")
def list_questions(db: Session = Depends(get_db), current_user=Depends(auth.get_current_admin_user)):
    return crud.get_questions(db)


@router.delete("/questions/{question_id}")
def delete_question(question_id: int, db: Session = Depends(get_db), current_user=Depends(auth.get_current_admin_user)):
    success = crud.delete_question(db, question_id)
    if not success:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"detail": "Question deleted successfully"}




@router.get("/stats/questions-per-day")
def questions_per_day(db: Session = Depends(get_db), current_user=Depends(auth.get_current_admin_user)):
    return crud.get_question_counts_by_day(db)

@router.get("/stats/users-per-day")
def users_per_day(db: Session = Depends(get_db), current_user=Depends(auth.get_current_admin_user)):
    return crud.get_user_counts_by_day(db)


@router.get("/stats/answers-per-day", response_model=List[schemas.AnswerStatsByDate])
def answers_per_day(db: Session = Depends(get_db)):
    return crud.get_answer_stats_by_day(db)

@router.get("/stats/questions-by-success-rate")
def questions_by_success_rate(db: Session = Depends(get_db), current_user=Depends(auth.get_current_admin_user)):
    return crud.get_question_success_rate_stats(db)