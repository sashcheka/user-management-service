from fastapi import FastAPI
from users.views import router as users_router
import uvicorn

app = FastAPI()
app.include_router(users_router)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
