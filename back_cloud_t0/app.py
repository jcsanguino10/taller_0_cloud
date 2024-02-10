from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
import crud, entities, schema
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from database import SessionLocal, engine
from jose import JWTError, jwt

SECRET_KEY = "e495fd6722159e05be44f58d6ce255046dcd45725f9a858bb2f875905651dc78"
ALGORITHM = "HS256"
ACCESS_TOKEN_DATE_MINUTES = 120

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="userlogin")

entities.Base.metadata.drop_all(bind=engine)
entities.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost:3000",  # Update with your React app's origin
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = SessionLocal()

# Security

credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def create_access_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, key=SECRET_KEY)
        username= int(payload.get("sub"))
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials 1",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_data = schema.TokenData(id_user=username)
    except JWTError as err:
        print(err)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials 2",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = crud.get_user(db, token_data.id_user)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials 3",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def validate_user(user_id, user_id2):
    if user_id != user_id2:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This user can not do this operation",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Roots

@app.get("/")
def read_root():
    return {"Welcome" : "Welcome to task API"}

# User

@app.post("/userlogin")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> schema.Token:
    user = crud.get_user_by_name_and_pass(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": str(user.id)})
    return schema.Token(access_token=access_token, token_type="bearer")

@app.get("/user")
async def get_info_user(user: Annotated[schema.UserData, Depends(get_current_user)]):
    return user

@app.post("/user")
async def create_user(name: str = Form(...), password:str = Form(...), image: UploadFile = File(None)):
    db_user = crud.get_user_by_name(db, name)
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered")
    else:
        try:
            db_user = crud.create_user(db, name, password, image)
        except Exception as exp:
            raise HTTPException(status_code=400, detail=str(exp))
    return db_user


# Category

@app.post("/category")
async def create_category(category: schema.CreateCategory, _: Annotated[schema.UserData, Depends(get_current_user)]):
    db_category = crud.get_category_by_name(db, category.name)
    if db_category:
        raise HTTPException(status_code=400, detail="Category already registered")
    else:
        db_category = crud.create_category(db, category)
    return db_category

@app.get("/category_id/{category_id}")
async def get_category_id(category_id: int):
    db_category = crud.get_category(db, category_id)
    if not db_category:
        raise HTTPException(status_code=400, detail="Category not exists")
    return db_category

@app.get("/category_name/{category_name}")
async def get_category(category_name: str):
    db_category = crud.get_category_by_name(db, category_name)
    if not db_category:
        raise HTTPException(status_code=400, detail="Category not exists")
    return db_category

@app.get("/categories")
async def get_category( current_user: Annotated[schema.UserData, Depends(get_current_user)]):
    db_category = crud.get_categories(db, current_user.id)
    return db_category

@app.delete("/category/{category_id}")
async def del_category(category_id: int, _: Annotated[schema.UserData, Depends(get_current_user)]):
    answer = crud.delete_category(db, category_id)
    if not answer:
        raise HTTPException(status_code=400, detail="Category not exists")
    return "Category deleted!"

# Task

@app.post("/task")
async def create_task(task: schema.CreateTask, current_user: Annotated[schema.UserData, Depends(get_current_user)]):
    validate_user(task.user, current_user.id)
    db_user = current_user
    db_category = crud.get_category(db, task.category)
    if not db_user:
        raise HTTPException(status_code=400, detail="User not exists")
    elif not db_category:
        raise HTTPException(status_code=400, detail="Category not exists")
    db_task = crud.create_task(db, task)
    return db_task

@app.get("/task/{task_id}")
async def get_task_id(task_id: int, current_user: Annotated[schema.UserData, Depends(get_current_user)]):
    db_task = crud.get_task(db, task_id)
    validate_user(current_user.id, db_task.user)
    if not db_task:
        raise HTTPException(status_code=400, detail="Task not exists")
    return db_task

@app.put("/task/{task_id}")
async def update_task(task_id: str, task:schema.TaskData, current_user: Annotated[schema.UserData, Depends(get_current_user)]):
    validate_user(task.user, current_user.id)
    db_task = crud.get_task(db, task_id)
    if not db_task:
        raise HTTPException(status_code=400, detail="Task not exists")
    else:
        db_task = crud.update_task(db,task)
    return "Task updated!"

@app.get("/tasks/user/{user_id}")
def get_task_user(user_id:str ,user: Annotated[str, Depends(get_current_user)]):
    validate_user(user_id, str(user.id))
    db_tasks = crud.get_tasks_by_user(db,user.id)
    return db_tasks

@app.delete("/task/{task_id}")
async def del_task(task_id: int, current_user: Annotated[schema.UserData, Depends(get_current_user)]):
    task = crud.get_task(db,task_id)
    validate_user(task.user, current_user.id)
    answer = crud.delete_task(db, task_id)
    if not answer:
        raise HTTPException(status_code=400, detail="Category not exists")
    return "Category deleted!"