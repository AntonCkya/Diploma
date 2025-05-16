FROM python:3.12

WORKDIR /some

RUN pip install uvicorn
RUN pip install fastapi
RUN pip install asyncio
RUN pip install pydantic
RUN pip install pydantic_settings
RUN pip install python-dotenv
RUN pip install boto3
RUN pip install python-multipart

COPY ./ ./
EXPOSE  8004
CMD ["python", "main.py"]
