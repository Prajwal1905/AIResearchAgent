from pydantic import BaseModel


class TopicRequest(BaseModel):
    topic: str
    custom_format: str=None