#!/usr/bin/env python3
"""
批量按月采集 GitHub Commit 数据
Author: 佟雨泽
"""

import subprocess
import sys
from datetime import datetime, timedelta
import calendar

def get_month_ranges(start_year=2023, start_month=6, end_year=2024, end_month=2):
    """生成月份时间范围列表"""
    ranges = []
    
    year, month = start_year, start_month
    
    while (year < end_year) or (year == end_year and month <= end_month):
        # 计算月末日期
        last_day = calendar.monthrange(year, month)[1]
        
        start_date = f"{year}-{month:02d}-01"
        end_date = f"{year}-{month:02d}-{last_day}"
        
        output_file = f"data/commits_{year}_{month:02d}.json"
        
        ranges.append({
            'start': start_date,
            'end': end_date,
            'output': output_file,
            'label': f"{year}年{month}月"
        })
        
        # 移动到下一个月
        month += 1
        if month > 12:
            month = 1
            year += 1
    
    return ranges

def collect_monthly_data():
    """按月批量采集数据"""
    # 定义时间范围（从 2023年6月 到 2024年2月）
    month_ranges = get_month_ranges()
    
    print("=" * 60)
    print("📅 MaxKB 按月 Commit 数据采集工具")
    print("=" * 60)
    print(f"总计需要采集 {len(month_ranges)} 个月的数据")
    print()
    
    for i, range_info in enumerate(month_ranges, 1):
        print(f"[{i}/{len(month_ranges)}] 采集 {range_info['label']}")
        print(f"  时间范围: {range_info['start']} 至 {range_info['end']}")
        print(f"  输出文件: {range_info['output']}")
        
        # 构建命令
        cmd = [
            sys.executable,
            'evolution/scripts/fetch_commits.py',
            '--since', range_info['start'],
            '--until', range_info['end'],
            '--output-file', range_info['output'],
            '--max-commits', '500'  # 限制每月最大数量
        ]
        
        try:
            # 执行采集
            result = subprocess.run(cmd, capture_output=True, text=True, cwd='.')
            
            if result.returncode == 0:
                print(f"  ✅ {range_info['label']} 采集完成")
            else:
                print(f"  ❌ {range_info['label']} 采集失败:")
                print(f"     {result.stderr}")
                
        except Exception as e:
            print(f"  ❌ 执行出错: {e}")
        
        print("-" * 50)
    
    print("\n🎉 所有月份数据采集完成！")

def show_quick_analysis():
    """显示快速统计信息"""
    print("\n📊 快速数据分析:")
    print("可以使用以下命令查看各月份数据:")
    print("  python analyze_monthly_data.py")
    print("\n或者手动查看生成的 JSON 文件:")
    print("  data/commits_2023_06.json")
    print("  data/commits_2023_07.json")
    print("  ...")

if __name__ == '__main__':
    collect_monthly_data()
    show_quick_analysis()