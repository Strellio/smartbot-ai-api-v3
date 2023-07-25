from dotenv import load_dotenv
from fastapi import FastAPI
from langcorn import create_service
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.conversation import conversation
from app.models import Input, Output


app = FastAPI()

load_dotenv()


@app.post("/conversation")
async def input(input: Input):
    result = Output(output=conversation(input))
    return [{"text": result.output, "recipient_id": input.sender}]

origins = [
    "<http://localhost>",
    "<http://localhost:5173>",
    "...Your Domains..."
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
