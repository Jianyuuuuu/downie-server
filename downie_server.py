#!/usr/bin/env python

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from downie_youtube_transcript import process_youtube_url
from downie_core import downie_download
import uvicorn
import logging
from datetime import datetime
import os

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('downie_server.log')
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Downie Server API",
    description="Downie服务器API，支持YouTube视频下载和字幕文本提取功能",
    version="1.0.0"
)

class YouTubeURL(BaseModel):
    url: str

class DownloadRequest(BaseModel):
    url: str
    destination: str = os.path.expanduser("~/Downloads/downie")

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

@app.post("/download")
async def download_video(download_req: DownloadRequest, request: Request):
    request_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}-{id(request)}"
    logger.info(f"Processing download request for URL: {download_req.url} (Request ID: {request_id})")
    
    try:
        # 确保下载目录存在，并获取绝对路径
        destination = os.path.abspath(os.path.expanduser(download_req.destination))
        os.makedirs(destination, exist_ok=True)
        logger.info(f"确保下载目录存在: {destination}")
        
        # 调用下载功能
        success, message = downie_download(
            url=download_req.url,
            format_type="mp4",
            destination=destination
        )
        
        if not success:
            raise Exception(message)
            
        response = {
            "status": "success",
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id,
            "destination": destination
        }
        logger.info(f"Successfully initiated download (Request ID: {request_id})")
        return response
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error processing download (Request ID: {request_id}): {error_msg}")
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
    return {"status": "running", "message": "Downie服务器正在运行"}

if __name__ == "__main__":
    logger.info("Downie服务器正在运行...")
    uvicorn.run("downie_server:app", host="0.0.0.0", port=3200, reload=True)