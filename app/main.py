from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from starlette.concurrency import run_in_threadpool

import models, crud, database, utils, schemas

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/generate/")
async def generate_content(payLoad: schemas.GeneratePayload, db: Session = Depends(get_db)):
    generated_text = await run_in_threadpool(utils.generate_content, db, payLoad.topic)

    return{"generated_text": generated_text}

@app.post("/analyze/")
async def analyze_content(payLoad: schemas.AnalyzePayload, db: Session = Depends(get_db)):
    readability, sentiment = await run_in_threadpool(utils.analyze_content, db, payLoad.content)

    return{"readability": readability, "sentiment": sentiment}