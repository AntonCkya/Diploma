from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run

from routes import list_of_routes

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for route in list_of_routes:
    app.include_router(route)

if __name__ == "__main__":
    run(
        "main:app",
        host="127.0.0.1",
        port=8001,
        log_level="debug",
        timeout_keep_alive=60
    )
