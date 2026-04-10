import secrets
import os
from typing import Optional
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime
from dotenv import load_dotenv  

from database import get_db, init_db
from models_db import User, ChatMessage
from chat_engine import chat_engine
from crisis import detect_crisis, get_crisis_response


load_dotenv()

app = FastAPI(title="Mental Health Chatbot")

templates = Jinja2Templates(directory="templates")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

sessions = {}


@app.on_event("startup")
def startup_event():
    init_db()
    if chat_engine.use_gemini:
        pass
    else:
        print("Erorr")


def get_password_hash(password: str) -> str:
    
    if len(password.encode('utf-8')) > 72:
        password = password[:72]
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if len(plain_password.encode('utf-8')) > 72:
        plain_password = plain_password[:72]
    return pwd_context.verify(plain_password, hashed_password)


def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("session_token")
    if not token or token not in sessions:
        return None
    username = sessions[token]
    user = db.query(User).filter(User.username == username).first()
    return user


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@app.post("/signup_form_submit")
async def signup_submit(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")

        hashed_password = get_password_hash(password)
        new_user = User(username=username, hashed_password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return RedirectResponse(url="/login?registered=true", status_code=303)
    except HTTPException:
        raise
    except Exception as e:
        print(f"SIGNUP ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, registered: Optional[str] = None):
    return templates.TemplateResponse("login.html", {
        "request": request,
        "registered": registered
    })


@app.post("/login_form_submit")
async def login_submit(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, str(user.hashed_password)):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    session_token = secrets.token_urlsafe(32)
    sessions[session_token] = username

    response = RedirectResponse(url="/chat", status_code=303)
    response.set_cookie(key="session_token", value=session_token, httponly=True)
    return response


@app.get("/logout")
async def logout(request: Request):
    token = request.cookies.get("session_token")
    if token and token in sessions:
        del sessions[token]

    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("session_token")
    return response


@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    chat_history = db.query(ChatMessage).filter(
        ChatMessage.user_id == user.id
    ).order_by(ChatMessage.timestamp.desc()).limit(20).all()

    chat_history.reverse()

    return templates.TemplateResponse("chat.html", {
        "request": request,
        "username": user.username,
        "chat_history": chat_history
    })


@app.post("/chat/send")
async def send_message(
    request: Request,
    message: str = Form(...),
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if detect_crisis(message):
        response_text = get_crisis_response()
    else:
        response_text = chat_engine.get_response(message, str(user.username))

    chat_message = ChatMessage(
        user_id=user.id,
        message=message,
        response=response_text
    )
    db.add(chat_message)
    db.commit()

    return RedirectResponse(url="/chat", status_code=303)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)