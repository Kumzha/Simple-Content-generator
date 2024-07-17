import openai
import os
from sqlalchemy.orm import Session
from dotenv import load_dotenv

import crud, models
import threading
from concurrent.futures import ThreadPoolExecutor


load_dotenv()

OPENAI_API_KEY = os.getenv("OPEN_API_KEY")
openai.api_key = OPENAI_API_KEY

semaphore = threading.Semaphore(5)

def generate_content(db: Session, topic: str) -> str:
    with semaphore:
        search_term = crud.get_search_term(db, topic)
        if not search_term:
            search_term = crud.create_search_term(db,topic)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Write a detailed article about {topic}"},
            ]
        )    
        generated_text = response.choices[0].message['content'].strip()