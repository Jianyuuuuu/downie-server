#!/usr/bin/env python

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from downie_youtube_transcript import process_youtube_url
import uvicorn
import logging
from datetime import datetime

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('youtube_text_api.log')
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="YouTube Text Extractor API",
    description="从YouTube视频中提取文本内容的API服务",
    version="1.0.0"
)

class YouTubeURL(BaseModel):
    url: str

class TextResponse(BaseModel):
    text: str
    status: str = "success"
    timestamp: str = ""
    request_id: str = ""

@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}-{id(request)}"
    start_time = datetime.now()
    logger.info(f"Request {request_id} started - Method: {request.method} Path: {request.url.path}")
    
    try:
        response = await call_next(request)
        process_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"Request {request_id} completed - Status: {response.status_code} Process Time: {process_time:.2f}s")
        return response
    except Exception as e:
        logger.error(f"Request {request_id} failed - Error: {str(e)}")
        raise

@app.post("/extract", response_model=TextResponse)
async def extract_text(youtube_url: YouTubeURL, request: Request):
    request_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}-{id(request)}"
    logger.info(f"Processing YouTube URL: {youtube_url.url} (Request ID: {request_id})")
    
    try:
        text = process_youtube_url(youtube_url.url)
        response = TextResponse(
            text=text,
            status="success",
            timestamp=datetime.now().isoformat(),
            request_id=request_id
        )
        logger.info(f"Successfully processed URL (Request ID: {request_id})")
        return response
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error processing URL (Request ID: {request_id}): {error_msg}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": error_msg,
                "timestamp": datetime.now().isoformat(),
                "request_id": request_id
            }
        )

@app.get("/")
async def root():
    logger.info("Health check endpoint accessed")
    return {"status": "running", "message": "YouTube文本提取服务（Downie）正在运行"}

if __name__ == "__main__":
    logger.info("Starting YouTube Text Extractor API server...")
    uvicorn.run("downie_youtube_transcript_server:app", host="0.0.0.0", port=3200, reload=True)