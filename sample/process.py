import io
import subprocess
import boto3
import tempfile
import os
import asyncio

from getenv import get_dotenv_vars
from task_checker import change_task_status

vars = get_dotenv_vars()    

s3_client = boto3.client(
    "s3",
    endpoint_url='https://' + vars['S3_ENDPOINT_URL'],
    aws_access_key_id=vars['aws_access_key_id'],
    aws_secret_access_key=vars['aws_secret_access_key'],
    region_name=vars['region'],
)

bucket_name = vars['S3_BUCKET']

async def file_process(s3_key, filename, task):
    with tempfile.TemporaryDirectory() as tmp_dir:
        hls_prefix = f"hls/{filename.replace('.mp3', '')}/"

        mp3_obj = s3_client.get_object(Bucket=bucket_name, Key=s3_key)["Body"].read()
        mp3_path = os.path.join(tmp_dir, "input.mp3")
        with open(mp3_path, 'wb') as f:
            f.write(mp3_obj)

        ffmpeg_command = [
            "ffmpeg",
            "-i", mp3_path,
            "-f", "segment",
            "-segment_time", "5",
            "-segment_format", "mpegts",
            "-c:a", "aac",
            "-b:a", "128k",
            "-ar", "44100",
            "-muxdelay", "0",
            "-map", "0:a",
            "-segment_list", os.path.join(tmp_dir, "playlist.m3u8"),
            os.path.join(tmp_dir, "segment_%03d.ts")
        ]

        process = await asyncio.create_subprocess_exec(
            *ffmpeg_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        await process.wait()

        if process.returncode != 0:
            error = await process.stderr.read()
            print(f"FFmpeg error: {error.decode()}")
            change_task_status(task, 'error')
            return
    
        for root, _, files in os.walk(tmp_dir):
            for file in files:
                local_path = os.path.join(root, file)
                with open(local_path, 'rb') as f:
                    content = f.read()

                if file == "playlist.m3u8":
                    file_key = f"{hls_prefix}playlist.m3u8"
                else:
                    file_key = f"{hls_prefix}{file}"

                s3_client.put_object(Bucket=bucket_name, Key=file_key, Body=content)

        change_task_status(task, 'done')
