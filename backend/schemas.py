from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional
from decimal import Decimal

# 用户相关Schema
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# 账单相关Schema
class BillBase(BaseModel):
    title: str
    amount: Decimal
    category: str  # 收入/支出
    type: str
    description: Optional[str] = None
    bill_date: date

class BillCreate(BillBase):
    pass

class BillUpdate(BaseModel):
    title: Optional[str] = None
    amount: Optional[Decimal] = None
    category: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    bill_date: Optional[date] = None

class BillResponse(BillBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# 登录相关Schema
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# 统计相关Schema
class BillStatistics(BaseModel):
    total_income: Decimal
    total_expense: Decimal
    balance: Decimal
    count: int

# 图片相关Schema
class BillImageBase(BaseModel):
    filename: str
    file_path: str
    file_size: int
    mime_type: str
    source_type: Optional[str] = None

class BillImageCreate(BillImageBase):
    bill_id: int

class BillImageResponse(BillImageBase):
    id: int
    bill_id: int
    user_id: int
    ocr_result: Optional[dict] = None
    parse_status: str
    parse_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ImageUploadResponse(BaseModel):
    image: Optional[BillImageResponse] = None
    bill: Optional[BillResponse] = None
    parsed_data: Optional[dict] = None

class BatchImageUploadResponse(BaseModel):
    success_count: int
    failed_count: int
    results: list[ImageUploadResponse]
