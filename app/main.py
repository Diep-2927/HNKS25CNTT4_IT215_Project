from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from db.database import engine
from core.exceptions import custom_http_exception_handler, validation_exception_handler
import models  

from routers import auth, users

models.Base.metadata.create_all(bind=engine)

app=FastAPI()
app.include_router(auth.router)
app.include_router(users.router)

app.add_exception_handler(HTTPException, custom_http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

@app.get("/test")
def test():
    return {
        "message": "API đang hoạt động ổn định"
    }