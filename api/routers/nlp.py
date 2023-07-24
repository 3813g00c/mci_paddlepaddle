from fastapi import APIRouter
from api.model import nlp_req

from paddlenlp import Taskflow

router = APIRouter()


@router.post("/nlp")
async def run_ocr(req: nlp_req.NLPReq):
    req.t_schema
    ie = Taskflow('information_extraction', schema=req.t_schema)
    r = ie(req.content)
    pass
