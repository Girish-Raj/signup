from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine, SessionLocal
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import models
import schemas


app = FastAPI()
#############################  Config  ################################### 


origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


Base.metadata.create_all(engine)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

################################################################ 


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        
        
@app.get("/users")
def get_users(db: Session = Depends(get_session)):
 return db.query(models.User).all()

@app.post("/signup",response_model=schemas.UserCreate)
def signup(user: schemas.UserCreate, db: Session = Depends(get_session)):
    
    hashed_pass = pwd_context.hash(user.password)
    userdb = models.User(name=user.name, email=user.email, password=hashed_pass)
    
    db.add(userdb)
    db.commit()
    db.refresh(userdb)
    
    return userdb

@app.post("/login",)
def login(body: schemas.UserLogin, db: Session = Depends(get_session)):
    email = body.email
    password = body.password
    
    # check if user is already in the database
    userInDb = db.query(models.User).filter_by(email=email).first()
    
    if not userInDb:
        return {"Error": "User not found"}
    
    
    # verify password
    valid_pass = pwd_context.verify(password , userInDb.password)
        
    if not valid_pass:
        return {"Error": "Invalid password"}
    
    return {"msg":"Successfully logged in"}