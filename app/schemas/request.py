from pydantic import BaseModel
from typing import Union

class TopicRequest(BaseModel):
    topic: str
    custom_format: Union[str, None] = None

class FollowUpRequest(BaseModel):
    question: str
    report: dict

class DownloadRequest(BaseModel):
    topic: str
    sections: dict

class ScriptRequest(BaseModel):
    topic: str
    style: str = "educational"
