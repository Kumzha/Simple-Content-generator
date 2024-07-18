import openai
from openai import OpenAI
import os
from sqlalchemy.orm import Session
from dotenv import load_dotenv

import crud, models
import threading
from concurrent.futures import ThreadPoolExecutor


load_dotenv()


client = openai.OpenAI(
    api_key = os.environ.get("OPENAI_API_KEY"),
)

semaphore = threading.Semaphore(5)

def generate_content(db: Session, content: str) -> str:
    with semaphore:
        search_term = crud.get_search_term(db, content)
        if not search_term:
            search_term = crud.create_search_term(db,content)
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Write a detailed article about {content}"},
            ],
            model="gpt-3.5-turbo",

        )    
        generated_text = response.choices[0].message.content
        crud.create_generated_content(db, generated_text, search_term.id)

        return generated_text
    
def analyze_content(db: Session, content: str):
    with semaphore:
        search_term = crud.get_search_term(db, content)
    if not search_term:
        search_term = crud.create_search_term(db, content)
    readability = get_readability_score(content)
    sentiment =  get_sentiment_analysis(content)
    crud.create_sentiment_analysis(db, readability, sentiment, search_term.id)

    return readability, sentiment

def get_readability_score(content: str) -> str:
    return "Readability score: Good"


def get_sentiment_analysis(content: str) -> str:
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Analyze, the sentiment of the following text: {content}"},
        ],
        model="gpt-3.5-turbo",
        max_tokens=10
    )    

    return response.choices[0].message.content