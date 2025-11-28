from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
from database import get_db
from auth import get_current_user
from models import User, Bill
from schemas import BillCreate, BillUpdate, BillResponse, BillStatistics

router = APIRouter(prefix="/api/bills", tags=["账单"])

@router.post("", response_model=BillResponse, status_code=status.HTTP_201_CREATED)
def create_bill(
    bill: BillCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建账单"""
    db_bill = Bill(
        user_id=current_user.id,
        title=bill.title,
        amount=bill.amount,
        category=bill.category,
        type=bill.type,
        description=bill.description,
        bill_date=bill.bill_date
    )
    db.add(db_bill)
    db.commit()
    db.refresh(db_bill)
    return db_bill

@router.get("", response_model=List[BillResponse])
def get_bills(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取账单列表"""
    query = db.query(Bill).filter(Bill.user_id == current_user.id)
    
    if category:
        query = query.filter(Bill.category == category)
    if start_date:
        query = query.filter(Bill.bill_date >= start_date)
    if end_date:
        query = query.filter(Bill.bill_date <= end_date)
    
    bills = query.order_by(Bill.bill_date.desc()).offset(skip).limit(limit).all()
    return bills

@router.get("/{bill_id}", response_model=BillResponse)
def get_bill(
    bill_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取单个账单详情"""
    bill = db.query(Bill).filter(
        Bill.id == bill_id,
        Bill.user_id == current_user.id
    ).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill

@router.put("/{bill_id}", response_model=BillResponse)
def update_bill(
    bill_id: int,
    bill_update: BillUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新账单"""
    bill = db.query(Bill).filter(
        Bill.id == bill_id,
        Bill.user_id == current_user.id
    ).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    
    update_data = bill_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(bill, field, value)
    
    db.commit()
    db.refresh(bill)
    return bill

@router.delete("/{bill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bill(
    bill_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除账单"""
    bill = db.query(Bill).filter(
        Bill.id == bill_id,
        Bill.user_id == current_user.id
    ).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    
    db.delete(bill)
    db.commit()
    return None

@router.get("/statistics/summary", response_model=BillStatistics)
def get_statistics(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取账单统计信息"""
    # 构建基础查询条件
    base_filter = [Bill.user_id == current_user.id]
    
    # 添加日期过滤条件
    if start_date:
        base_filter.append(Bill.bill_date >= start_date)
    if end_date:
        base_filter.append(Bill.bill_date <= end_date)
    
    # 计算总收入
    income_filter = base_filter + [Bill.category == "收入"]
    total_income = db.query(func.sum(Bill.amount)).filter(*income_filter).scalar() or Decimal("0")
    
    # 计算总支出
    expense_filter = base_filter + [Bill.category == "支出"]
    total_expense = db.query(func.sum(Bill.amount)).filter(*expense_filter).scalar() or Decimal("0")
    
    # 计算账单数量
    count = db.query(Bill).filter(*base_filter).count()
    
    # 计算余额
    balance = total_income - total_expense
    
    return BillStatistics(
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
        count=count
    )
