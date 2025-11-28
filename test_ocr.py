#!/usr/bin/env python3
"""
OCR账单解析测试脚本
不依赖数据库，可以直接测试图片上传和解析功能

使用方法:
    python test_ocr.py <图片路径>
    或
    python test_ocr.py <图片路径1> <图片路径2> ...
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from decimal import Decimal

# 添加backend目录到路径
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from utils.ocr_parser import parse_bill_image, extract_text_from_image, detect_bill_type

def print_separator():
    """打印分隔线"""
    print("=" * 80)

def format_result(result):
    """格式化解析结果"""
    if not result.get("success"):
        return f"""
❌ 解析失败
错误信息: {result.get('error', '未知错误')}
账单类型: {result.get('bill_type', 'unknown')}
"""
    
    parsed = result.get("parsed_data", {})
    return f"""
✅ 解析成功
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 账单信息:
   💰 金额: ¥{parsed.get('amount', 'N/A')}
   📅 日期: {parsed.get('date', 'N/A')}
   🏪 商户: {parsed.get('merchant', 'N/A')}
   📊 分类: {parsed.get('category', 'N/A')}
   🏷️  类型: {parsed.get('type', 'N/A')}
   📝 描述: {parsed.get('description', 'N/A')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 识别文本:
{format_ocr_texts(result.get('raw_texts', []))}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

def format_ocr_texts(texts):
    """格式化OCR识别的文本"""
    if not texts:
        return "   (无识别文本)"
    
    formatted = []
    for i, text in enumerate(texts[:20], 1):  # 最多显示20行
        formatted.append(f"   {i:2d}. {text}")
    
    if len(texts) > 20:
        formatted.append(f"   ... (还有 {len(texts) - 20} 行)")
    
    return "\n".join(formatted)

def test_single_image(image_path):
    """测试单张图片"""
    print_separator()
    print(f"📸 测试图片: {image_path}")
    print_separator()
    
    if not os.path.exists(image_path):
        print(f"❌ 错误: 文件不存在 - {image_path}")
        return False
    
    if not os.path.isfile(image_path):
        print(f"❌ 错误: 不是文件 - {image_path}")
        return False
    
    # 检查文件扩展名
    valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif'}
    file_ext = Path(image_path).suffix.lower()
    if file_ext not in valid_extensions:
        print(f"❌ 错误: 不支持的文件格式 - {file_ext}")
        print(f"   支持的格式: {', '.join(valid_extensions)}")
        return False
    
    print(f"📁 文件大小: {os.path.getsize(image_path) / 1024:.2f} KB")
    print(f"🔍 开始OCR识别...")
    print()
    
    try:
        # 解析图片
        start_time = datetime.now()
        result = parse_bill_image(image_path)
        end_time = datetime.now()
        
        elapsed = (end_time - start_time).total_seconds()
        print(f"⏱️  识别耗时: {elapsed:.2f} 秒")
        print()
        
        # 显示结果
        print(format_result(result))
        
        return result.get("success", False)
        
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_batch_images(image_paths):
    """批量测试多张图片"""
    print("\n" + "=" * 80)
    print(f"📦 批量测试 {len(image_paths)} 张图片")
    print("=" * 80 + "\n")
    
    results = []
    success_count = 0
    failed_count = 0
    
    for i, image_path in enumerate(image_paths, 1):
        print(f"\n[{i}/{len(image_paths)}] ", end="")
        success = test_single_image(image_path)
        results.append((image_path, success))
        
        if success:
            success_count += 1
        else:
            failed_count += 1
    
    # 显示汇总
    print("\n" + "=" * 80)
    print("📊 测试汇总")
    print("=" * 80)
    print(f"✅ 成功: {success_count} 张")
    print(f"❌ 失败: {failed_count} 张")
    print(f"📈 成功率: {success_count / len(image_paths) * 100:.1f}%")
    print("=" * 80)
    
    return results

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("""
使用方法:
    python test_ocr.py <图片路径>
    或
    python test_ocr.py <图片路径1> <图片路径2> ...

示例:
    python test_ocr.py test_images/alipay_bill.jpg
    python test_ocr.py test_images/*.jpg

支持的图片格式: JPG, JPEG, PNG, BMP, GIF
        """)
        sys.exit(1)
    
    image_paths = sys.argv[1:]
    
    # 过滤存在的文件
    valid_paths = []
    for path in image_paths:
        if os.path.exists(path):
            valid_paths.append(path)
        else:
            print(f"⚠️  警告: 文件不存在，已跳过 - {path}")
    
    if not valid_paths:
        print("❌ 错误: 没有有效的图片文件")
        sys.exit(1)
    
    # 测试图片
    if len(valid_paths) == 1:
        success = test_single_image(valid_paths[0])
        sys.exit(0 if success else 1)
    else:
        results = test_batch_images(valid_paths)
        all_success = all(success for _, success in results)
        sys.exit(0 if all_success else 1)

if __name__ == "__main__":
    main()
