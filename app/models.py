

from pydantic import BaseModel


class InputMetadata(BaseModel):
    chat_platform_id: str
    business_id: str


class Input(BaseModel):
    sender: str
    message: str
    metadata: InputMetadata


class Output(BaseModel):
    output: str
