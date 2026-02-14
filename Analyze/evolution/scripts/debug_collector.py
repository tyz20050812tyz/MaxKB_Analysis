#!/usr/bin/env python3
"""
调试版本的按月采集脚本
显示完整的错误信息以便诊断问题
"""

import subprocess
import sys
import calendar
from datetime import datetime
from pathlib import Path

def test_single_month():
    """测试单个月份采集以查看完整错误信息"""
    print("=" * 60)
    print("🔍 调试模式：测试单个月份采集")
    print("=" * 60)
    
    # 测试 2023年6月
    start_date = "2023-06-01"
    end_date = "2023-06-30"
    output_file = "data/debug_commits_2023_06.json"
    
    print(f"测试采集: 2023年6月")
    print(f"时间范围: {start_date} 至 {end_date}")
    print(f"输出文件: {output_file}")
    print()
    
    # 构建命令
    cmd = [
        sys.executable,
        'fetch_commits.py',
        '--since', start_date,
        '--until', end_date,
        '--output-file', output_file,
        '--max-commits', '50'  # 减少数量便于测试
    ]
    
    print("执行命令:", ' '.join(cmd))
    print("\n开始执行...")
    print("-" * 50)
    
    try:
        # 执行并捕获完整输出
        result = subprocess.run(
            cmd,
            capture_output=False,  # 直接显示输出
            text=True,
            cwd=Path(__file__).parent,
            encoding='utf-8',
            errors='ignore'
        )
        
        print("-" * 50)
        if result.returncode == 0:
            print("✅ 采集成功!")
        else:
            print(f"❌ 采集失败，返回码: {result.returncode}")
            
    except Exception as e:
        print(f"❌ 执行出错: {e}")

def show_current_setup():
    """显示当前配置信息"""
    print("\n" + "=" * 60)
    print("📋 当前环境配置检查")
    print("=" * 60)
    
    # 检查必要文件
    files_to_check = [
        'fetch_commits.py',
        '../../.env.example'
    ]
    
    for file_path in files_to_check:
        full_path = Path(__file__).parent / file_path
        if full_path.exists():
            print(f"✅ {file_path} - 存在")
        else:
            print(f"❌ {file_path} - 不存在")
    
    # 检查 Python 环境
    print(f"\n🐍 Python 版本: {sys.version}")
    print(f"📁 当前目录: {Path.cwd()}")
    print(f"📁 脚本目录: {Path(__file__).parent}")

if __name__ == '__main__':
    show_current_setup()
    print()
    test_single_month()