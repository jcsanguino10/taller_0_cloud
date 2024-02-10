from sqlalchemy.orm import Session
import entities, schema
import imghdr
from fastapi import UploadFile

FOLDER_URL = "./images_users"
default_url_icon = "example.com"

# User

def save_image_user(user_id:str, file: UploadFile):
    try:
        url_img = f"{FOLDER_URL}/user_{user_id}.{file.filename.split('.')[-1]}"
        with open(url_img, "wb") as image_file:
            image_file.write(file.file.read())
        return url_img
    except:
        raise Exception("Error: Error saving the image")


def get_user(db: Session, user_id: int):
    return db.query(entities.User).filter(entities.User.id == user_id).first()

def get_user_by_name_and_pass(db: Session, name: str, password:str):
    return db.query(entities.User).filter(entities.User.name == name, entities.User.password == password).first()

def get_user_by_name(db: Session, name: str):
    return db.query(entities.User).filter(entities.User.name == name).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(entities.User).offset(skip).limit(limit).all()

def create_user(db: Session, name:str, password:str, image: UploadFile):
    db_user = entities.User(
        name = name,
        password = password,
        image = str(default_url_icon)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    try:
        if image is not None:
            db_user.image = save_image_user(db_user.id, image)
            db.commit()
            db.refresh(db_user)
    except:
        db.rollback()
        raise Exception("Error: no se pudo guardar la imagen")
    return db_user

# Category

def get_category(db: Session, category_id: int):
    return db.query(entities.Category).filter(entities.Category.id == category_id).first()

def get_category_by_name(db: Session, name: str):
    return db.query(entities.Category).filter(entities.Category.name == name).first()

def get_categories(db: Session, user_id):  
    user_categories = db.query(entities.Category).join(entities.Task).filter(entities.Task.user == user_id).distinct().all()
    return user_categories

def delete_category(db: Session, category_id: int):
    try:
        cat = db.query(entities.Category).get(category_id)
        db.delete(cat)
        db.commit()
        return True
    except:
        return False

def create_category(db: Session, category: schema.CreateCategory):
    db_category = entities.Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

#Task

def get_task(db: Session, task_id: int):
    return db.query(entities.Task).filter(entities.Task.id == task_id).first()

def get_tasks_by_user(db: Session, user_id: int):
    return db.query(entities.Task).filter(entities.Task.user == user_id).all()

def delete_task(db: Session, task_id: int):
    try:
        task = db.query(entities.Task).get(task_id)
        db.delete(task)
        db.commit()
        return True
    except:
        return False
    
def update_task(db: Session, task: schema.TaskData):
    try:
        task_db =  db.query(entities.Task).filter(entities.Task.id == task.id).first()
        for field in task.__dict__:
            if field != "id" and hasattr(task, field):
                setattr(task_db, field, getattr(task, field))
        db.commit
        return True
    except:
        return False


def create_task(db: Session, task: schema.CreateTask):
    db_task = entities.Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task