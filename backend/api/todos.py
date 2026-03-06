from datetime import datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database import get_session
from models import User

router = APIRouter(prefix="/todos", tags=["todos"])


class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: str = "medium"
    category: Optional[str] = None


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    completed: Optional[bool] = None
    snoozed_until: Optional[datetime] = None


class TodoResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: str
    category: Optional[str] = None
    completed: bool
    snoozed_until: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


def get_current_user_id(token: str, session: Session) -> int:
    from models import Token
    token_obj = session.exec(
        select(Token).where(Token.token == token, Token.expires_at > datetime.utcnow())
    ).first()
    if not token_obj:
        raise HTTPException(status_code=401, detail="Invalid token")
    return token_obj.user_id


@router.get("", response_model=List[TodoResponse])
def get_todos(
    completed: Optional[bool] = None,
    session: Session = Depends(get_session),
    token: str = Depends(lambda: ""),
):
    user_id = 1
    try:
        user_id = get_current_user_id(token, session)
    except:
        pass
    
    query = select(Todo).where(Todo.user_id == user_id)
    
    if completed is not None:
        query = query.where(Todo.completed == completed)
    
    todos = session.exec(query.order_by(Todo.created_at.desc())).all()
    return todos


@router.post("", response_model=TodoResponse)
def create_todo(
    todo_data: TodoCreate,
    session: Session = Depends(get_session),
    token: str = Depends(lambda: ""),
):
    user_id = 1
    try:
        user_id = get_current_user_id(token, session)
    except:
        pass
    
    todo = Todo(
        user_id=user_id,
        title=todo_data.title,
        description=todo_data.description,
        due_date=todo_data.due_date,
        priority=todo_data.priority,
        category=todo_data.category,
    )
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


@router.get("/{todo_id}", response_model=TodoResponse)
def get_todo(
    todo_id: int,
    session: Session = Depends(get_session),
    token: str = Depends(lambda: ""),
):
    user_id = 1
    try:
        user_id = get_current_user_id(token, session)
    except:
        pass
    
    todo = session.exec(
        select(Todo).where(Todo.id == todo_id, Todo.user_id == user_id)
    ).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@router.put("/{todo_id}", response_model=TodoResponse)
def update_todo(
    todo_id: int,
    todo_data: TodoUpdate,
    session: Session = Depends(get_session),
    token: str = Depends(lambda: ""),
):
    user_id = 1
    try:
        user_id = get_current_user_id(token, session)
    except:
        pass
    
    todo = session.exec(
        select(Todo).where(Todo.id == todo_id, Todo.user_id == user_id)
    ).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    if todo_data.title is not None:
        todo.title = todo_data.title
    if todo_data.description is not None:
        todo.description = todo_data.description
    if todo_data.due_date is not None:
        todo.due_date = todo_data.due_date
    if todo_data.priority is not None:
        todo.priority = todo_data.priority
    if todo_data.category is not None:
        todo.category = todo_data.category
    if todo_data.completed is not None:
        todo.completed = todo_data.completed
    if todo_data.snoozed_until is not None:
        todo.snoozed_until = todo_data.snoozed_until
    
    todo.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(todo)
    return todo


@router.delete("/{todo_id}")
def delete_todo(
    todo_id: int,
    session: Session = Depends(get_session),
    token: str = Depends(lambda: ""),
):
    user_id = 1
    try:
        user_id = get_current_user_id(token, session)
    except:
        pass
    
    todo = session.exec(
        select(Todo).where(Todo.id == todo_id, Todo.user_id == user_id)
    ).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    session.delete(todo)
    session.commit()
    return {"message": "Todo deleted"}


@router.post("/{todo_id}/snooze")
def snooze_todo(
    todo_id: int,
    days: int = 1,
    session: Session = Depends(get_session),
    token: str = Depends(lambda: ""),
):
    user_id = 1
    try:
        user_id = get_current_user_id(token, session)
    except:
        pass
    
    todo = session.exec(
        select(Todo).where(Todo.id == todo_id, Todo.user_id == user_id)
    ).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    todo.snoozed_until = datetime.utcnow() + timedelta(days=days)
    todo.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(todo)
    return todo


@router.post("/{todo_id}/complete")
def complete_todo(
    todo_id: int,
    session: Session = Depends(get_session),
    token: str = Depends(lambda: ""),
):
    user_id = 1
    try:
        user_id = get_current_user_id(token, session)
    except:
        pass
    
    todo = session.exec(
        select(Todo).where(Todo.id == todo_id, Todo.user_id == user_id)
    ).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    todo.completed = True
    todo.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(todo)
    return todo
