from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import nlp
from routers import ocr

import uvicorn

app = FastAPI(openapi_url="/api/v1/mci-paddle/openapi.json", docs_url="/api/v1/mci-paddle/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(nlp.router, prefix="/api-nlp/v1/mci-paddle", tags=["NLP"])
app.include_router(ocr.router, prefix="/api-ocr/v1/mci-paddle", tags=["OCR"])


@app.get("/")
async def root():
    return {"message": "MCI Paddle API"}


if __name__ == "__main__":
    uvicorn.run("endpoints:app", host="0.0.0.0", port=13345)
