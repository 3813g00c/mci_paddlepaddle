import base64

from fastapi import APIRouter, File, UploadFile, Form, HTTPException, status
from fastapi.responses import JSONResponse
from api.config import settings
from PIL import Image
import urllib.request
import requests
from io import BytesIO
import api.utils as u
import os
import time

import json

from typing import Optional

router = APIRouter()


def cv2_to_base64(doc):
    # 将图像数据编码为Base64字符串
    return base64.b64encode(doc).decode('utf-8')


def invoke_ocr(doc, c):
    worker_pid = os.getpid()
    print(f"Handling OCR request with worker PID: {worker_pid}")
    start_time = time.time()

    image = cv2_to_base64(doc)

    data = {"key": ["image"], "value": [image]}
    r = requests.post(url=settings.ocr_url, data=json.dumps(data))
    result = r.json()
    print("erro_no:{}, err_msg:{}".format(result["err_no"], result["err_msg"]))
    # check success
    values = []
    if result["err_no"] == 0:
        ocr_result = result["value"][0]
        try:
            for item in eval(ocr_result):
                # return transcription and points
                print("{}, {}".format(item[0], item[1]))
                values.append(item[0][0])
        except Exception as e:
            print(ocr_result)
            print("No results")

    else:
        print(
            "For details about error message, see PipelineServingLogs/pipeline.log"
        )

    # values = u.merge_data(values)

    end_time = time.time()
    processing_time = end_time - start_time
    print(f"OCR done, worker PID: {worker_pid}")

    return values, processing_time


@router.post("/ocr")
async def run_ocr(file: Optional[UploadFile] = File(None), image_url: Optional[str] = Form(None)):
    if file:
        if file.content_type in ["image/jpeg", "image/jpg", "image/png"]:
            doc = BytesIO(await file.read()).getvalue()
        else:
            return {"error": "Invalid file type. Only JPG/PNG images  are allowed."}

        result, processing_time = invoke_ocr(doc, file.content_type)

        u.log_stats(settings.ocr_stats_file, [processing_time, file.filename])
        print(f"Processing time OCR: {processing_time:.2f} seconds")
    elif image_url:
        # test image url: https://raw.githubusercontent.com/katanaml/sparrow/main/sparrow-data/docs/input/invoices/processed/images/invoice_10.jpg
        # test PDF: https://raw.githubusercontent.com/katanaml/sparrow/main/sparrow-data/docs/input/receipts/2021/us/bestbuy-20211211_006.pdf
        with urllib.request.urlopen(image_url) as response:
            content_type = response.info().get_content_type()

            if content_type in ["image/jpeg", "image/jpg", "image/png"]:
                doc = Image.open(BytesIO(response.read()))
            else:
                return {"error": "Invalid file type. Only JPG/PNG images are allowed."}
        result, processing_time = invoke_ocr(doc, content_type)

        # parse file name from url
        file_name = image_url.split("/")[-1]
        u.log_stats(settings.ocr_stats_file, [processing_time, file_name])
        print(f"Processing time OCR: {processing_time:.2f} seconds")
    else:
        result = {"info": "No input provided"}

    if result is None:
        raise HTTPException(status_code=400, detail=f"Failed to process the input.")

    return JSONResponse(status_code=status.HTTP_200_OK, content=result)


@router.get("/statistics")
async def get_statistics():
    file_path = settings.ocr_stats_file

    # Check if the file exists, and read its content
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            try:
                content = json.load(file)
            except json.JSONDecodeError:
                content = []
    else:
        content = []

    return content
