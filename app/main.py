from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from db.database import engine
from core.exceptions import custom_http_exception_handler, validation_exception_handler
import models
from routers import auth, users, event, event_task

# Tạo bảng database
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Event Management API")

# Router Authentication
app.include_router(auth.router)

# Router User
app.include_router(users.router)

# Router Event
app.include_router(event.router)

# Router Event Task
app.include_router(event_task.router)

# Xử lý lỗi HTTP
app.add_exception_handler(HTTPException, custom_http_exception_handler)

# Xử lý lỗi validation
app.add_exception_handler(RequestValidationError, validation_exception_handler)

@app.get("/test")
def test():
    return {"message": "API đang hoạt động ổn định"}