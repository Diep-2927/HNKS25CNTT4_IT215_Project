from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

# Chuẩn hóa cấu trúc JSON trả về khi có HTTPException 
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error_code": exc.status_code,
            "message": exc.detail
        }
    )

# Chuẩn hóa JSON trả về khi dữ liệu input từ client sai định dạng 
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(    
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "success": False,
            "error_code": 422,
            "message": "Lỗi xác thực dữ liệu",
            "details": exc.errors()
        }
    )

# Các Custom Exception tái sử dụng nhanh trong service
class NotFoundException(HTTPException):
    def __init__(self, detail: str = "Không tìm thấy tài nguyên"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class BadRequestException(HTTPException):
    def __init__(self, detail: str = "Yêu cầu không hợp lệ"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)