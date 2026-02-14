#!/usr/bin/env python3
"""
按月批量提取 GitHub Commit 数据
调用 fetch_commits.py 按月份采集数据，每月最多250个commit
Author: 佟雨泽
"""

import subprocess
import sys
import calendar
from datetime import datetime
from pathlib import Path

def get_monthly_ranges(start_year=2023, start_month=6, end_year=2024, end_month=2):
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
            'year': year,
            'month': month,
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

def collect_monthly_commits():
    """按月批量采集commit数据"""
    # 定义时间范围
    month_ranges = get_monthly_ranges()
    
    print("=" * 60)
    print("📅 MaxKB 按月 Commit 数据采集工具")
    print("=" * 60)
    print(f"总计需要采集 {len(month_ranges)} 个月的数据")
    print("每月限制: 最多 250 个 commit")
    print()
    
    success_count = 0
    failed_count = 0
    
    for i, range_info in enumerate(month_ranges, 1):
        print(f"[{i}/{len(month_ranges)}] 采集 {range_info['label']}")
        print(f"  时间范围: {range_info['start']} 至 {range_info['end']}")
        print(f"  输出文件: {range_info['output']}")
        
        # 构建调用 fetch_commits.py 的命令
        cmd = [
            sys.executable,
            'fetch_commits.py',
            '--since', range_info['start'],
            '--until', range_info['end'],
            '--output-file', range_info['output'],
            '--max-commits', '250'
        ]
        
        try:
            # 执行采集（指定编码避免Windows乱码）
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                cwd=Path(__file__).parent,
                encoding='utf-8',
                errors='ignore',
                timeout=300  # 5分钟超时
            )
            
            if result.returncode == 0:
                print(f"  ✅ {range_info['label']} 采集完成")
                success_count += 1
            else:
                print(f"  ❌ {range_info['label']} 采集失败:")
                print(f"     错误信息: {result.stderr[:200]}...")
                failed_count += 1
                
        except subprocess.TimeoutExpired:
            print(f"  ⏱️  {range_info['label']} 采集超时")
            failed_count += 1
        except Exception as e:
            print(f"  ❌ {range_info['label']} 执行出错: {e}")
            failed_count += 1
        
        print("-" * 50)
    
    # 显示汇总结果
    print(f"\n🎯 采集完成统计:")
    print(f"  ✅ 成功: {success_count} 个月")
    print(f"  ❌ 失败: {failed_count} 个月")
    print(f"  📊 成功率: {success_count/(success_count+failed_count)*100:.1f}%")
    
    if success_count > 0:
        print(f"\n📂 数据文件位置:")
        for range_info in month_ranges:
            if Path(range_info['output']).exists():
                summary_file = range_info['output'].replace('.json', '_summary.json')
                print(f"  • {range_info['label']}: {range_info['output']}")
                if Path(summary_file).exists():
                    print(f"    摘要文件: {summary_file}")

def main():
    """主函数"""
    try:
        collect_monthly_commits()
        print("\n🎉 所有月份数据采集任务完成！")
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断了采集过程")
    except Exception as e:
        print(f"\n❌ 发生未知错误: {e}")

if __name__ == '__main__':
    main()