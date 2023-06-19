from typing import Annotated
from schema import TodoRequest
from fastapi import Depends, HTTPException, Path, APIRouter
from sqlalchemy.orm import Session
from starlette import status

import models
from database import SessionLocal

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all_todos(db: db_dependency):
    return db.query(models.Todos).all()


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(models.Todos).get(todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found")


@router.post("/todo/create", status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo_request: TodoRequest):
    todo_model = models.Todos(**todo_request.dict())
    db.add(todo_model)
    db.commit()


@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency, todo_request: TodoRequest,
                      todo_id: int = Path(gt=0)):
    todo_model = db.query(models.Todos).get(todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo is not found")
    update_data = {
        field: value
        for field, value in todo_request.dict().items()
        if value is not None
    }
    for field, values in update_data.items():
        setattr(todo_model, field, values)
    db.commit()


@router.delete("/todo/delete/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(models.Todos).get(todo_id)
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo is not found")
    db.delete(todo_model)
    db.commit()
