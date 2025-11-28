"""
OCR账单解析工具
支持解析支付宝和微信账单图片
"""
import re
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, List
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from paddleocr import PaddleOCR

# 初始化PaddleOCR（只初始化一次，提高性能）
ocr = PaddleOCR(use_angle_cls=True, lang='ch', use_gpu=False)

def preprocess_image(image_path: str) -> np.ndarray:
    """
    图像预处理：增强对比度、去噪等
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"无法读取图片: {image_path}")
    
    # 转换为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 增强对比度
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    # 去噪
    denoised = cv2.fastNlMeansDenoising(enhanced, None, 10, 7, 21)
    
    return denoised

def extract_text_from_image(image_path: str) -> List[Dict]:
    """
    从图片中提取文本（OCR）
    返回格式: [{"text": "文本", "confidence": 0.95, "bbox": [x1, y1, x2, y2]}]
    """
    try:
        # 预处理图像
        processed_img = preprocess_image(image_path)
        
        # OCR识别
        result = ocr.ocr(processed_img, cls=True)
        
        # 格式化结果
        texts = []
        if result and result[0]:
            for line in result[0]:
                if line:
                    bbox, (text, confidence) = line
                    texts.append({
                        "text": text,
                        "confidence": confidence,
                        "bbox": [int(coord[0]) for coord in bbox] + [int(coord[1]) for coord in bbox]
                    })
        
        return texts
    except Exception as e:
        raise Exception(f"OCR识别失败: {str(e)}")

def detect_bill_type(texts: List[Dict]) -> str:
    """
    检测账单类型（支付宝/微信）
    """
    full_text = " ".join([item["text"] for item in texts])
    
    # 检测支付宝关键词
    alipay_keywords = ["支付宝", "Alipay", "收款", "付款", "余额", "账单"]
    alipay_count = sum(1 for keyword in alipay_keywords if keyword in full_text)
    
    # 检测微信关键词
    wechat_keywords = ["微信支付", "WeChat", "微信", "收款", "付款", "零钱"]
    wechat_count = sum(1 for keyword in wechat_keywords if keyword in full_text)
    
    if alipay_count > wechat_count:
        return "alipay"
    elif wechat_count > 0:
        return "wechat"
    else:
        return "unknown"

def parse_alipay_bill(texts: List[Dict]) -> Dict:
    """
    解析支付宝账单
    """
    full_text = "\n".join([item["text"] for item in texts])
    
    result = {
        "amount": None,
        "date": None,
        "merchant": None,
        "category": "支出",
        "type": "其他",
        "description": ""
    }
    
    # 提取金额（匹配 ¥123.45 或 123.45 元）
    amount_patterns = [
        r'[¥￥]\s*(\d+\.?\d*)',
        r'(\d+\.?\d*)\s*元',
        r'金额[：:]\s*[¥￥]?\s*(\d+\.?\d*)',
        r'(\d+\.?\d*)\s*[元块]'
    ]
    for pattern in amount_patterns:
        match = re.search(pattern, full_text)
        if match:
            try:
                result["amount"] = Decimal(match.group(1))
                break
            except:
                continue
    
    # 提取日期（匹配 2024-01-01 或 2024/01/01 或 2024年1月1日）
    date_patterns = [
        r'(\d{4})[年\-/](\d{1,2})[月\-/](\d{1,2})[日]?',
        r'(\d{4})-(\d{2})-(\d{2})',
        r'(\d{4})/(\d{2})/(\d{2})'
    ]
    for pattern in date_patterns:
        match = re.search(pattern, full_text)
        if match:
            try:
                year, month, day = match.groups()
                result["date"] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                break
            except:
                continue
    
    # 如果没有找到日期，使用当前日期
    if not result["date"]:
        result["date"] = datetime.now().strftime("%Y-%m-%d")
    
    # 提取商户名称（通常在"收款方"、"商户"等关键词后）
    merchant_patterns = [
        r'收款方[：:]\s*([^\n]+)',
        r'商户[：:]\s*([^\n]+)',
        r'商家[：:]\s*([^\n]+)',
        r'收款人[：:]\s*([^\n]+)'
    ]
    for pattern in merchant_patterns:
        match = re.search(pattern, full_text)
        if match:
            result["merchant"] = match.group(1).strip()
            result["description"] = match.group(1).strip()
            break
    
    # 判断收入/支出（支付宝通常显示"收款"为收入，"付款"为支出）
    if "收款" in full_text or "收入" in full_text:
        result["category"] = "收入"
    elif "付款" in full_text or "支出" in full_text:
        result["category"] = "支出"
    
    # 提取类型（餐饮、交通等）
    type_keywords = {
        "餐饮": ["餐饮", "餐厅", "饭店", "美食", "外卖"],
        "交通": ["交通", "打车", "地铁", "公交", "滴滴", "出租车"],
        "购物": ["购物", "商城", "超市", "商店", "购买"],
        "娱乐": ["娱乐", "电影", "KTV", "游戏"],
        "工资": ["工资", "薪资", "收入"],
        "奖金": ["奖金", "奖励"]
    }
    
    for bill_type, keywords in type_keywords.items():
        if any(keyword in full_text for keyword in keywords):
            result["type"] = bill_type
            break
    
    # 如果没有找到商户名，尝试从描述中提取
    if not result["merchant"]:
        # 尝试提取第一行非金额、非日期的文本作为商户名
        for item in texts[:5]:  # 前5行
            text = item["text"].strip()
            if text and not re.match(r'^[¥￥]?\d+\.?\d*', text) and not re.match(r'^\d{4}', text):
                result["merchant"] = text
                result["description"] = text
                break
    
    return result

def parse_wechat_bill(texts: List[Dict]) -> Dict:
    """
    解析微信账单
    """
    full_text = "\n".join([item["text"] for item in texts])
    
    result = {
        "amount": None,
        "date": None,
        "merchant": None,
        "category": "支出",
        "type": "其他",
        "description": ""
    }
    
    # 提取金额
    amount_patterns = [
        r'[¥￥]\s*(\d+\.?\d*)',
        r'(\d+\.?\d*)\s*元',
        r'金额[：:]\s*[¥￥]?\s*(\d+\.?\d*)',
        r'(\d+\.?\d*)\s*[元块]'
    ]
    for pattern in amount_patterns:
        match = re.search(pattern, full_text)
        if match:
            try:
                result["amount"] = Decimal(match.group(1))
                break
            except:
                continue
    
    # 提取日期
    date_patterns = [
        r'(\d{4})[年\-/](\d{1,2})[月\-/](\d{1,2})[日]?',
        r'(\d{4})-(\d{2})-(\d{2})',
        r'(\d{4})/(\d{2})/(\d{2})'
    ]
    for pattern in date_patterns:
        match = re.search(pattern, full_text)
        if match:
            try:
                year, month, day = match.groups()
                result["date"] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                break
            except:
                continue
    
    if not result["date"]:
        result["date"] = datetime.now().strftime("%Y-%m-%d")
    
    # 提取商户名称
    merchant_patterns = [
        r'收款方[：:]\s*([^\n]+)',
        r'商户[：:]\s*([^\n]+)',
        r'商家[：:]\s*([^\n]+)',
        r'收款人[：:]\s*([^\n]+)',
        r'对方[：:]\s*([^\n]+)'
    ]
    for pattern in merchant_patterns:
        match = re.search(pattern, full_text)
        if match:
            result["merchant"] = match.group(1).strip()
            result["description"] = match.group(1).strip()
            break
    
    # 判断收入/支出
    if "收款" in full_text or "收入" in full_text or "收到" in full_text:
        result["category"] = "收入"
    elif "付款" in full_text or "支出" in full_text or "支付" in full_text:
        result["category"] = "支出"
    
    # 提取类型
    type_keywords = {
        "餐饮": ["餐饮", "餐厅", "饭店", "美食", "外卖"],
        "交通": ["交通", "打车", "地铁", "公交", "滴滴", "出租车"],
        "购物": ["购物", "商城", "超市", "商店", "购买"],
        "娱乐": ["娱乐", "电影", "KTV", "游戏"],
        "工资": ["工资", "薪资", "收入"],
        "奖金": ["奖金", "奖励"]
    }
    
    for bill_type, keywords in type_keywords.items():
        if any(keyword in full_text for keyword in keywords):
            result["type"] = bill_type
            break
    
    # 如果没有找到商户名，尝试从描述中提取
    if not result["merchant"]:
        for item in texts[:5]:
            text = item["text"].strip()
            if text and not re.match(r'^[¥￥]?\d+\.?\d*', text) and not re.match(r'^\d{4}', text):
                result["merchant"] = text
                result["description"] = text
                break
    
    return result

def parse_bill_image(image_path: str) -> Dict:
    """
    解析账单图片的主函数
    返回解析结果和账单类型
    """
    try:
        # OCR识别
        texts = extract_text_from_image(image_path)
        
        if not texts:
            return {
                "success": False,
                "error": "未能识别到任何文本",
                "bill_type": "unknown"
            }
        
        # 检测账单类型
        bill_type = detect_bill_type(texts)
        
        # 根据类型解析
        if bill_type == "alipay":
            parsed_data = parse_alipay_bill(texts)
        elif bill_type == "wechat":
            parsed_data = parse_wechat_bill(texts)
        else:
            # 未知类型，尝试通用解析
            parsed_data = parse_alipay_bill(texts)  # 使用支付宝解析器作为默认
        
        # 验证必要字段
        if not parsed_data.get("amount"):
            return {
                "success": False,
                "error": "未能识别到金额信息",
                "bill_type": bill_type,
                "raw_texts": [item["text"] for item in texts]
            }
        
        return {
            "success": True,
            "bill_type": bill_type,
            "parsed_data": parsed_data,
            "raw_texts": [item["text"] for item in texts],
            "ocr_results": texts
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "bill_type": "unknown"
        }
