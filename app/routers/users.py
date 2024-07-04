from app import schemas, crud
from app.database import SessionLocal
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Form, Response
from typing import List
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request
from typing import Optional
from starlette.middleware.authentication import AuthenticationMiddleware


templates = Jinja2Templates(directory="templates")
app = FastAPI()

@app.middleware("http")
async def add_user_to_request(request: Request, call_next):
    token = request.cookies.get("access_token")
    request.state.user = None

    if token:
        username: Optional[str] = schemas.decode_access_token(token)
        if username:
            try:
                db: Session = next(get_db())
                user = schemas.get_user(db, username)
                if user:
                    request.state.user = user
            except Exception as e:
                print(f"Error fetching user: {e}")

    response = await call_next(request)
    return response
app.add_middleware(AuthenticationMiddleware, backend=add_user_to_request)


@app.get("/")
def home(request: Request):
    """Home page"""
    return templates.TemplateResponse("home.html", {"request": request})

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all users"""
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """Get a user by id"""
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.get("/register")
def register_user(request: Request):
    """Create a new user"""
    return templates.TemplateResponse("auth/register.html",{"request": request, "name": "FastAPI"})

@router.get("/login", response_model=schemas.User)
def login_user(request: Request):
    """Login a user"""
    return templates.TemplateResponse("auth/login.html",{"request": request, "name": "FastAPI"})

@router.post("/users/", response_model=schemas.User)
def create_user( username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)):
    """Create a new user"""
    db_user = crud.get_user_by_email(db, email=email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = schemas.get_password_hash(password)
    user_data = schemas.UserCreate(username=username, email=email, password_hash=hashed_password)
    return crud.create_user(db=db, user=user_data)

@router.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Update a user by id"""
    return crud.update_user(db=db, user_id=user_id, user=user)

@router.delete("/users/{user_id}", response_model=schemas.User)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a user by id"""
    return crud.delete_user(db=db, user_id=user_id)

@router.post("/logout")
def logout_user(response: Response):
    """Logout a user"""
    response.delete_cookie("access_token")
    return {"message": "Logout successful"}