from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, crud, auth, database
from datetime import datetime
from app import models 
from app.database import get_db
router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db, user)

@router.post("/login")
def login(form_data: schemas.UserCreate, db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/questions", response_model=list[schemas.QuestionOut])
def get_questions(db: Session = Depends(get_db), current_user=Depends(auth.get_current_user)):
    return crud.get_questions(db)

# @router.post("/questions/check-answer")
# def check_answer(answer_data: schemas.AnswerCheck, db: Session = Depends(get_db), current_user=Depends(auth.get_current_user)):
#     question = crud.get_question(db, answer_data.question_id)
#     if not question:
#         raise HTTPException(status_code=404, detail="Question not found")
#     is_correct = (answer_data.answer.strip().lower() == question.word.lower())
#     return {"correct": is_correct}

@router.post("/questions/check-answer")
def check_answer(answer_data: schemas.AnswerCheck, db: Session = Depends(get_db), current_user=Depends(auth.get_current_user)):
    question = crud.get_question(db, answer_data.question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    is_correct = (answer_data.answer.strip().lower() == question.word.lower())

    answer_log = models.AnswerLog(
        question_id=answer_data.question_id,
        is_correct=is_correct,
        timestamp=datetime.utcnow()
    )
    db.add(answer_log)
    db.commit()

    return {"correct": is_correct}


# @router.get("/stats/users-per-day")
# def users_per_day(db: Session = Depends(get_db), current_user=Depends(auth.get_current_admin_user)):
#     return crud.get_user_counts_by_day(db)
