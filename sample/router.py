from fastapi import APIRouter, Query, Depends, HTTPException, File, UploadFile, BackgroundTasks
import asyncio

import boto3

from getenv import get_dotenv_vars
from process import file_process
from task_checker import cron_remove_tasks, get_task, make_task

vars = get_dotenv_vars()

s3_client = boto3.client(
    "s3",
    endpoint_url='https://' + vars['S3_ENDPOINT_URL'],
    aws_access_key_id=vars['aws_access_key_id'],
    aws_secret_access_key=vars['aws_secret_access_key'],
    region_name=vars['region'],
)
bucket_name = vars['S3_BUCKET']

api_router = APIRouter(tags=["v1"])


@api_router.on_event("startup")
async def startup_event():
    asyncio.create_task(cron_remove_tasks())


@api_router.get("/sample/check")
async def check(
    task_id: str = Query(default=None)
):  
    task = get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=404, 
            detail="Task not found"
        )
    return {
        'status': task.status
    }


@api_router.post("/sample/upload")
async def upload(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    if not file.filename.endswith(".mp3"):
        raise HTTPException(
            status_code=400, 
            detail="Only MP3 files are allowed"
        )

    task = make_task("pending")

    s3_key = f"uploads/{file.filename}"
    s3_client.upload_fileobj(file.file, bucket_name, s3_key, ExtraArgs={"ContentType": "audio/mpeg"})

    background_tasks.add_task(file_process, s3_key, file.filename, task)

    return {
        'id': task
    }
