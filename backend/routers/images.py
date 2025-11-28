"""
图片上传和账单解析路由
"""
import os
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import datetime
from decimal import Decimal

from database import get_db
from auth import get_current_user
from models import User, Bill, BillImage
from schemas import (
    BillImageResponse, 
    ImageUploadResponse, 
    BatchImageUploadResponse,
    BillCreate,
    BillResponse
)
from utils.ocr_parser import parse_bill_image

router = APIRouter(prefix="/api/images", tags=["图片"])

# 上传目录配置
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def save_uploaded_file(file: UploadFile, user_id: int) -> tuple[str, str]:
    """
    保存上传的文件
    返回: (file_path, filename)
    """
    # 检查文件扩展名
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式，仅支持: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # 生成唯一文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"{user_id}_{timestamp}{file_ext}"
    file_path = UPLOAD_DIR / str(user_id) / filename
    
    # 创建用户目录
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 保存文件
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return str(file_path), filename

@router.post("/upload", response_model=ImageUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    auto_create_bill: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    上传单张图片并解析账单
    - auto_create_bill: 是否自动创建账单（如果解析成功）
    """
    try:
        # 检查文件大小
        file.file.seek(0, 2)  # 移动到文件末尾
        file_size = file.file.tell()
        file.file.seek(0)  # 重置到开头
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"文件大小超过限制（最大 {MAX_FILE_SIZE / 1024 / 1024}MB）"
            )
        
        # 保存文件
        file_path, filename = save_uploaded_file(file, current_user.id)
        
        # OCR解析
        parse_result = parse_bill_image(file_path)
        
        # 创建图片记录（先不关联账单）
        bill_image = BillImage(
            user_id=current_user.id,
            bill_id=0,  # 临时值，解析成功后会更新
            filename=filename,
            file_path=file_path,
            file_size=file_size,
            mime_type=file.content_type or "image/jpeg",
            source_type=parse_result.get("bill_type", "unknown"),
            ocr_result=parse_result,
            parse_status="success" if parse_result.get("success") else "failed",
            parse_error=parse_result.get("error")
        )
        db.add(bill_image)
        db.flush()  # 获取ID但不提交
        
        bill = None
        parsed_data = None
        
        # 如果解析成功且自动创建账单
        if parse_result.get("success") and auto_create_bill:
            parsed = parse_result.get("parsed_data", {})
            parsed_data = parsed
            
            # 创建账单
            bill = Bill(
                user_id=current_user.id,
                title=parsed.get("merchant") or f"账单-{datetime.now().strftime('%Y%m%d')}",
                amount=parsed.get("amount") or Decimal("0.00"),
                category=parsed.get("category", "支出"),
                type=parsed.get("type", "其他"),
                description=parsed.get("description", ""),
                bill_date=datetime.strptime(parsed.get("date"), "%Y-%m-%d").date() if parsed.get("date") else datetime.now().date()
            )
            db.add(bill)
            db.flush()
            
            # 更新图片记录的bill_id
            bill_image.bill_id = bill.id
        
        db.commit()
        db.refresh(bill_image)
        if bill:
            db.refresh(bill)
        
        return ImageUploadResponse(
            image=BillImageResponse.model_validate(bill_image),
            bill=BillResponse.model_validate(bill) if bill else None,
            parsed_data=parsed_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"上传失败: {str(e)}"
        )

@router.post("/upload/batch", response_model=BatchImageUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_images_batch(
    files: List[UploadFile] = File(...),
    auto_create_bill: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    批量上传多张图片并解析
    """
    if len(files) > 20:
        raise HTTPException(
            status_code=400,
            detail="一次最多上传20张图片"
        )
    
    results = []
    success_count = 0
    failed_count = 0
    
    for file in files:
        try:
            # 检查文件大小
            file.file.seek(0, 2)
            file_size = file.file.tell()
            file.file.seek(0)
            
            if file_size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"文件 {file.filename} 大小超过限制"
                )
            
            # 保存文件
            file_path, filename = save_uploaded_file(file, current_user.id)
            
            # OCR解析
            parse_result = parse_bill_image(file_path)
            
            # 创建图片记录
            bill_image = BillImage(
                user_id=current_user.id,
                bill_id=0,
                filename=filename,
                file_path=file_path,
                file_size=file_size,
                mime_type=file.content_type or "image/jpeg",
                source_type=parse_result.get("bill_type", "unknown"),
                ocr_result=parse_result,
                parse_status="success" if parse_result.get("success") else "failed",
                parse_error=parse_result.get("error")
            )
            db.add(bill_image)
            db.flush()
            
            bill = None
            parsed_data = None
            
            # 如果解析成功且自动创建账单
            if parse_result.get("success") and auto_create_bill:
                parsed = parse_result.get("parsed_data", {})
                parsed_data = parsed
                
                bill = Bill(
                    user_id=current_user.id,
                    title=parsed.get("merchant") or f"账单-{datetime.now().strftime('%Y%m%d')}",
                    amount=parsed.get("amount") or Decimal("0.00"),
                    category=parsed.get("category", "支出"),
                    type=parsed.get("type", "其他"),
                    description=parsed.get("description", ""),
                    bill_date=datetime.strptime(parsed.get("date"), "%Y-%m-%d").date() if parsed.get("date") else datetime.now().date()
                )
                db.add(bill)
                db.flush()
                
                bill_image.bill_id = bill.id
            
            db.commit()
            db.refresh(bill_image)
            if bill:
                db.refresh(bill)
            
            result = ImageUploadResponse(
                image=BillImageResponse.model_validate(bill_image),
                bill=BillResponse.model_validate(bill) if bill else None,
                parsed_data=parsed_data
            )
            results.append(result)
            
            if bill_image.parse_status == "success":
                success_count += 1
            else:
                failed_count += 1
                
        except HTTPException:
            db.rollback()
            failed_count += 1
            results.append(ImageUploadResponse(
                image=None,
                bill=None,
                parsed_data=None
            ))
        except Exception as e:
            db.rollback()
            failed_count += 1
            results.append(ImageUploadResponse(
                image=None,
                bill=None,
                parsed_data=None
            ))
    
    return BatchImageUploadResponse(
        success_count=success_count,
        failed_count=failed_count,
        results=results
    )

@router.get("/{image_id}", response_model=BillImageResponse)
def get_image(
    image_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取图片信息
    """
    image = db.query(BillImage).filter(
        BillImage.id == image_id,
        BillImage.user_id == current_user.id
    ).first()
    
    if not image:
        raise HTTPException(status_code=404, detail="图片不存在")
    
    return image

@router.get("/{image_id}/file")
def get_image_file(
    image_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取图片文件
    """
    image = db.query(BillImage).filter(
        BillImage.id == image_id,
        BillImage.user_id == current_user.id
    ).first()
    
    if not image:
        raise HTTPException(status_code=404, detail="图片不存在")
    
    if not os.path.exists(image.file_path):
        raise HTTPException(status_code=404, detail="图片文件不存在")
    
    return FileResponse(
        image.file_path,
        media_type=image.mime_type,
        filename=image.filename
    )

@router.get("/bill/{bill_id}/images", response_model=List[BillImageResponse])
def get_bill_images(
    bill_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取账单关联的所有图片
    """
    # 验证账单所有权
    bill = db.query(Bill).filter(
        Bill.id == bill_id,
        Bill.user_id == current_user.id
    ).first()
    
    if not bill:
        raise HTTPException(status_code=404, detail="账单不存在")
    
    images = db.query(BillImage).filter(
        BillImage.bill_id == bill_id,
        BillImage.user_id == current_user.id
    ).all()
    
    return images

@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_image(
    image_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除图片
    """
    image = db.query(BillImage).filter(
        BillImage.id == image_id,
        BillImage.user_id == current_user.id
    ).first()
    
    if not image:
        raise HTTPException(status_code=404, detail="图片不存在")
    
    # 删除文件
    if os.path.exists(image.file_path):
        try:
            os.remove(image.file_path)
        except:
            pass  # 忽略删除文件错误
    
    db.delete(image)
    db.commit()
    
    return None

@router.post("/{image_id}/reparse")
async def reparse_image(
    image_id: int,
    auto_create_bill: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    重新解析图片
    """
    image = db.query(BillImage).filter(
        BillImage.id == image_id,
        BillImage.user_id == current_user.id
    ).first()
    
    if not image:
        raise HTTPException(status_code=404, detail="图片不存在")
    
    if not os.path.exists(image.file_path):
        raise HTTPException(status_code=404, detail="图片文件不存在")
    
    # 重新解析
    parse_result = parse_bill_image(image.file_path)
    
    # 更新图片记录
    image.ocr_result = parse_result
    image.parse_status = "success" if parse_result.get("success") else "failed"
    image.parse_error = parse_result.get("error")
    image.source_type = parse_result.get("bill_type", "unknown")
    
    bill = None
    parsed_data = None
    
    # 如果解析成功且需要创建账单
    if parse_result.get("success") and auto_create_bill:
        parsed = parse_result.get("parsed_data", {})
        parsed_data = parsed
        
        bill = Bill(
            user_id=current_user.id,
            title=parsed.get("merchant") or f"账单-{datetime.now().strftime('%Y%m%d')}",
            amount=parsed.get("amount") or Decimal("0.00"),
            category=parsed.get("category", "支出"),
            type=parsed.get("type", "其他"),
            description=parsed.get("description", ""),
            bill_date=datetime.strptime(parsed.get("date"), "%Y-%m-%d").date() if parsed.get("date") else datetime.now().date()
        )
        db.add(bill)
        db.flush()
        
        image.bill_id = bill.id
    
    db.commit()
    if bill:
        db.refresh(bill)
    db.refresh(image)
    
    return ImageUploadResponse(
        image=BillImageResponse.model_validate(image),
        bill=BillResponse.model_validate(bill) if bill else None,
        parsed_data=parsed_data
    )
