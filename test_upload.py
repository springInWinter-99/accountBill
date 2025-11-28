#!/usr/bin/env python3
"""
图片上传和解析测试脚本（模拟上传流程）
不依赖数据库，可以测试完整的图片上传和解析流程

使用方法:
    python test_upload.py <图片路径>
    或
    python test_upload.py <图片路径1> <图片路径2> ...
"""

import sys
import os
import shutil
from pathlib import Path
from datetime import datetime
from decimal import Decimal

# 添加backend目录到路径
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from utils.ocr_parser import parse_bill_image

# 模拟上传目录
TEST_UPLOAD_DIR = Path("test_uploads")
TEST_UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def save_test_file(source_path, user_id=1):
    """模拟保存上传的文件"""
    # 检查文件扩展名
    file_ext = Path(source_path).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"不支持的文件格式: {file_ext}")
    
    # 检查文件大小
    file_size = os.path.getsize(source_path)
    if file_size > MAX_FILE_SIZE:
        raise ValueError(f"文件大小超过限制: {file_size / 1024 / 1024:.2f}MB > 10MB")
    
    # 生成唯一文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"{user_id}_{timestamp}{file_ext}"
    file_path = TEST_UPLOAD_DIR / str(user_id) / filename
    
    # 创建用户目录
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 复制文件
    shutil.copy2(source_path, file_path)
    
    return str(file_path), filename, file_size

def simulate_upload(image_path, auto_create_bill=True):
    """模拟图片上传流程"""
    print(f"\n{'='*80}")
    print(f"📤 模拟上传: {image_path}")
    print(f"{'='*80}\n")
    
    # 1. 验证文件
    if not os.path.exists(image_path):
        print(f"❌ 错误: 文件不存在")
        return None
    
    file_ext = Path(image_path).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        print(f"❌ 错误: 不支持的文件格式: {file_ext}")
        return None
    
    file_size = os.path.getsize(image_path)
    if file_size > MAX_FILE_SIZE:
        print(f"❌ 错误: 文件大小超过限制")
        return None
    
    print(f"✅ 文件验证通过")
    print(f"   - 文件名: {Path(image_path).name}")
    print(f"   - 文件大小: {file_size / 1024:.2f} KB")
    print(f"   - 文件类型: {file_ext}")
    
    # 2. 保存文件
    try:
        file_path, filename, saved_size = save_test_file(image_path)
        print(f"\n✅ 文件保存成功")
        print(f"   - 保存路径: {file_path}")
        print(f"   - 保存文件名: {filename}")
    except Exception as e:
        print(f"❌ 文件保存失败: {str(e)}")
        return None
    
    # 3. OCR解析
    print(f"\n🔍 开始OCR识别...")
    try:
        start_time = datetime.now()
        parse_result = parse_bill_image(file_path)
        end_time = datetime.now()
        elapsed = (end_time - start_time).total_seconds()
        
        print(f"⏱️  识别耗时: {elapsed:.2f} 秒")
        
        if not parse_result.get("success"):
            print(f"\n❌ OCR识别失败")
            print(f"   错误信息: {parse_result.get('error', '未知错误')}")
            print(f"   账单类型: {parse_result.get('bill_type', 'unknown')}")
            return {
                "image": {
                    "filename": filename,
                    "file_path": file_path,
                    "file_size": saved_size,
                    "parse_status": "failed",
                    "source_type": parse_result.get("bill_type", "unknown"),
                    "parse_error": parse_result.get("error")
                },
                "bill": None,
                "parsed_data": None
            }
        
        print(f"✅ OCR识别成功")
        print(f"   账单类型: {parse_result.get('bill_type', 'unknown')}")
        
    except Exception as e:
        print(f"❌ OCR识别异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
    
    # 4. 解析结果
    parsed = parse_result.get("parsed_data", {})
    
    print(f"\n📋 解析结果:")
    print(f"   💰 金额: ¥{parsed.get('amount', 'N/A')}")
    print(f"   📅 日期: {parsed.get('date', 'N/A')}")
    print(f"   🏪 商户: {parsed.get('merchant', 'N/A')}")
    print(f"   📊 分类: {parsed.get('category', 'N/A')}")
    print(f"   🏷️  类型: {parsed.get('type', 'N/A')}")
    print(f"   📝 描述: {parsed.get('description', 'N/A')}")
    
    # 5. 模拟创建账单（如果启用）
    bill = None
    if auto_create_bill and parse_result.get("success"):
        if parsed.get("amount"):
            bill = {
                "id": 1,  # 模拟ID
                "title": parsed.get("merchant") or f"账单-{datetime.now().strftime('%Y%m%d')}",
                "amount": float(parsed.get("amount", 0)),
                "category": parsed.get("category", "支出"),
                "type": parsed.get("type", "其他"),
                "description": parsed.get("description", ""),
                "bill_date": parsed.get("date") or datetime.now().strftime("%Y-%m-%d")
            }
            print(f"\n✅ 自动创建账单:")
            print(f"   - 标题: {bill['title']}")
            print(f"   - 金额: ¥{bill['amount']}")
            print(f"   - 分类: {bill['category']}")
            print(f"   - 类型: {bill['type']}")
            print(f"   - 日期: {bill['bill_date']}")
    
    # 6. 返回结果
    result = {
        "image": {
            "filename": filename,
            "file_path": file_path,
            "file_size": saved_size,
            "parse_status": "success" if parse_result.get("success") else "failed",
            "source_type": parse_result.get("bill_type", "unknown"),
            "parse_error": parse_result.get("error"),
            "ocr_result": parse_result
        },
        "bill": bill,
        "parsed_data": parsed
    }
    
    print(f"\n{'='*80}")
    print(f"✅ 上传流程完成")
    print(f"{'='*80}\n")
    
    return result

def simulate_batch_upload(image_paths, auto_create_bill=True):
    """模拟批量上传"""
    print(f"\n{'='*80}")
    print(f"📦 批量上传 {len(image_paths)} 张图片")
    print(f"{'='*80}\n")
    
    results = []
    success_count = 0
    failed_count = 0
    
    for i, image_path in enumerate(image_paths, 1):
        print(f"\n[{i}/{len(image_paths)}] ", end="")
        result = simulate_upload(image_path, auto_create_bill)
        
        if result:
            results.append(result)
            if result["image"]["parse_status"] == "success":
                success_count += 1
            else:
                failed_count += 1
        else:
            failed_count += 1
            results.append(None)
    
    # 显示汇总
    print(f"\n{'='*80}")
    print(f"📊 批量上传汇总")
    print(f"{'='*80}")
    print(f"✅ 成功: {success_count} 张")
    print(f"❌ 失败: {failed_count} 张")
    print(f"📈 成功率: {success_count / len(image_paths) * 100:.1f}%")
    print(f"{'='*80}\n")
    
    return {
        "success_count": success_count,
        "failed_count": failed_count,
        "results": results
    }

def cleanup_test_files():
    """清理测试文件"""
    if TEST_UPLOAD_DIR.exists():
        try:
            shutil.rmtree(TEST_UPLOAD_DIR)
            print(f"🧹 已清理测试文件目录: {TEST_UPLOAD_DIR}")
        except Exception as e:
            print(f"⚠️  清理测试文件失败: {str(e)}")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="图片上传和解析测试脚本（模拟上传流程）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python test_upload.py test_images/alipay_bill.jpg
  python test_upload.py test_images/*.jpg
  python test_upload.py test_images/*.jpg --no-auto-bill
  python test_upload.py test_images/*.jpg --cleanup
        """
    )
    
    parser.add_argument(
        "images",
        nargs="+",
        help="图片文件路径（支持多个）"
    )
    
    parser.add_argument(
        "--no-auto-bill",
        action="store_true",
        help="不自动创建账单"
    )
    
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="测试完成后清理测试文件"
    )
    
    args = parser.parse_args()
    
    # 过滤存在的文件
    valid_paths = []
    for path in args.images:
        if os.path.exists(path):
            valid_paths.append(path)
        else:
            print(f"⚠️  警告: 文件不存在，已跳过 - {path}")
    
    if not valid_paths:
        print("❌ 错误: 没有有效的图片文件")
        sys.exit(1)
    
    try:
        # 测试上传
        if len(valid_paths) == 1:
            result = simulate_upload(valid_paths[0], not args.no_auto_bill)
            if not result or result["image"]["parse_status"] != "success":
                sys.exit(1)
        else:
            batch_result = simulate_batch_upload(valid_paths, not args.no_auto_bill)
            if batch_result["success_count"] == 0:
                sys.exit(1)
    
    finally:
        # 清理测试文件
        if args.cleanup:
            cleanup_test_files()
        else:
            print(f"💡 提示: 测试文件保存在 {TEST_UPLOAD_DIR}")
            print(f"   使用 --cleanup 参数可以清理测试文件")

if __name__ == "__main__":
    main()
