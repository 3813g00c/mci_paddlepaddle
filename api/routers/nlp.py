from fastapi import APIRouter, File, UploadFile, Form, HTTPException, status
from fastapi.responses import JSONResponse
from api.model import nlp_req

from paddlenlp import Taskflow

router = APIRouter()
d = [{'乙方': [{'end': 31, 'probability': 0.9064625720266939,
                'start': 19,
                'text': '叶县建昆市政工程有限公司'}],
      '总价': [{'end': 241,
                'probability': 0.38169450510338265,
                'start': 231,
                'text': '参拾玖万捌仟伍佰\n元'}],
      '甲方': [{'end': 15,
                'probability': 0.872258847048073,
                'start': 9,
                'text': '叶县境保护局'}]}]


@router.post("/nlp")
async def run_ocr(req: nlp_req.NLPReq):
    t_schema = req.t_schema
    if t_schema is None or len(t_schema) == 0 or len(req.content) == 0:
        return {"error": "Input is empty"}
    result = None
    try:
        ie = Taskflow('information_extraction', schema=req.t_schema)
        r_list = ie(req.content)
        if isinstance(r_list, list):
            result = r_list[0]
    except Exception:
        print("error")
    if result is None:
        raise HTTPException(status_code=400, detail=f"Failed to process the input.")

    return JSONResponse(status_code=status.HTTP_200_OK, content=result)
