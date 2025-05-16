FROM python:3.12

WORKDIR /some

RUN apt-get update && apt-get install -y ffmpeg

RUN pip install uvicorn
RUN pip install fastapi
RUN pip install asyncio
RUN pip install pydantic
RUN pip install asyncpg
RUN pip install python-dotenv
RUN pip install sqlalchemy
RUN pip install boto3
RUN pip install python-multipart

COPY ./ ./
EXPOSE  8000
CMD ["python", "main.py"]
