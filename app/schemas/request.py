from pydantic import BaseModel
from typing import Union, List, Optional

class TopicRequest(BaseModel):
    topic: str
    custom_format: Union[str, None] = None

class FollowUpRequest(BaseModel):
    question: str
    report: dict

class DownloadRequest(BaseModel):
    topic: str
    sections: dict
    references: Optional[List[dict]] = []
    domain: Optional[str] = ""

class ScriptRequest(BaseModel):
    topic: str
    style: str = "educational"

class FileChatRequest(BaseModel):
    question: str
    content: str
    history: list = []
    images: list = []  
