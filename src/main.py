import logging
import os

import uvicorn
from fastapi import FastAPI

from auth.views import router as auth_router
from core.logging import configure_logging
from healthcheck.views import router as healthcheck_router
from users.views import router as users_router

app = FastAPI()

configure_logging()
logging.info("Application started")

app.include_router(healthcheck_router)
app.include_router(auth_router)
app.include_router(users_router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.environ["UVICORN_HOST"],
        port=int(os.environ["UVICORN_PORT"]),
        reload=True,
    )
