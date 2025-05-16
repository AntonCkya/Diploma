import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import boto3
from botocore.exceptions import ClientError
from uvicorn import run
from fastapi.responses import HTMLResponse

from config import settings

app = FastAPI()

S3_BUCKET = settings.S3_BUCKET

# все данные лежат в енвах, в репозитории их нет :(
s3_client = boto3.client(
    "s3",
    endpoint_url=f'https://{settings.S3_ENDPOINT_URL}',
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
    region_name=settings.region_name,
)

@app.get("/stream/{foldername}/{filename}")
async def stream_audio_hls(foldername: str, filename: str):
    file_key = f"hls/{foldername}/{filename}"

    try:
        s3_response = s3_client.get_object(Bucket=S3_BUCKET, Key=file_key)
    except ClientError as e:
        raise HTTPException(status_code=404, detail=f"Audio file not found: {e}")

    if filename.endswith(".m3u8"):
        media_type = "application/vnd.apple.mpegurl"
    elif filename.endswith(".ts"):
        media_type = "audio/mp2t"
    else:
        media_type = "application/octet-stream"

    return StreamingResponse(
        content=s3_response['Body'].iter_chunks(),
        media_type=media_type,
        headers={
            "Cache-Control": "no-cache",
            "Access-Control-Allow-Origin": "*"
        }
    )

@app.get("/")
async def dummy():
    # дамми используется только для тестирования HLS плеера
    with open("dummy.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    run(
        "main:app",
        host="0.0.0.0",
        port=8004,
        log_level="debug",
        timeout_keep_alive=60
    )