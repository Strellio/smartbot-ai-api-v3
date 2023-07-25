

from pydantic import BaseModel


class Input(BaseModel):
    sender: str
    message: str
    metadata: dict


class Output(BaseModel):
    output: str
