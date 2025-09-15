from fastapi import FastAPI
from app.database import engine, Base
from app.routes import admin_routes, user_routes
from app.database import SessionLocal
from app import crud, schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Language Learning Game")

app.include_router(admin_routes.router)
app.include_router(user_routes.router)

@app.get("/")
def root():
    return {"message": "API is working"}

def create_initial_admin():
    db = SessionLocal()
    admin_user = crud.get_user_by_username(db, "admin")
    if not admin_user:
        admin_data = schemas.UserCreate(username="admin", password="admin123")
        crud.create_user(db, admin_data, is_admin=True)
        print("Admin user created with username='admin' and password='admin123'")
    else:
        print("Admin user already exists.")
    db.close()

create_initial_admin()
