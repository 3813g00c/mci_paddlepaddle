from pydantic import BaseModel


class NLPReq(BaseModel):
    t_schema: list
    content: str
