from fastapi import FastAPI
from users.views import router as users_router
from auth.views import router as auth_router
import uvicorn

app = FastAPI()
app.include_router(users_router)
app.include_router(auth_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
