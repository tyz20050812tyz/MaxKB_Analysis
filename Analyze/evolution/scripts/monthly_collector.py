#!/usr/bin/env python3
"""
按月批量提取 GitHub Commit 数据
调用 fetch_commits.py 按月份采集数据，每月最多250个commit
Author: 佟雨泽
"""

import subprocess
import sys
import calendar
import json
import os
from datetime import datetime
from pathlib import Path
from github import Github
try:
    from github import Auth  # 新版本 PyGithub
    HAS_AUTH = True
except ImportError:
    HAS_AUTH = False

def get_existing_data_info():
    """检测已存在的数据文件，返回最新的采集时间"""
    data_dir = Path('data')
    if not data_dir.exists():
        return None
    
    existing_months = []
    
    # 查找已有的 commit 数据文件
    for file in data_dir.glob('commits_*.json'):
        if file.name.startswith('commits_') and file.name.endswith('.json'):
            try:
                # 解析文件名: commits_2023_06.json
                parts = file.stem.split('_')
                if len(parts) == 3 and parts[0] == 'commits':
                    year = int(parts[1])
                    month = int(parts[2])
                    existing_months.append((year, month))
            except:
                continue
    
    # 返回最新的月份
    if existing_months:
        latest_year, latest_month = max(existing_months)
        return {'year': latest_year, 'month': latest_month}
    
    return None

def check_token_status():
    """检查 token 配置状态"""
    env_file = Path(__file__).parent.parent.parent / '.env.example'
    if not env_file.exists():
        return False
    
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('GITHUB_TOKEN='):
                token = line.split('=', 1)[1].strip()
                return len(token) > 20  # 简单验证 token 长度
    return False

def get_latest_commit_date():
    """获取 GitHub 上最新的 commit 日期"""
    try:
        # 读取 token
        token = None
        env_file = Path(__file__).parent.parent.parent / '.env.example'
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('GITHUB_TOKEN='):
                        token = line.split('=', 1)[1].strip()
                        break
        
        if not token:
            print("⚠️  无法获取 GitHub token，使用当前日期作为参考")
            return datetime.now()
        
        # 初始化 GitHub 客户端
        if HAS_AUTH:
            # 使用新版本的认证方式
            auth = Auth.Token(token)
            g = Github(auth=auth)
        else:
            # 兼容旧版本
            g = Github(token)
        repo = g.get_repo('1Panel-dev/MaxKB')
        
        # 获取最新的 commit
        default_branch = repo.default_branch
        branch = repo.get_branch(default_branch)
        latest_commit = repo.get_commit(branch.commit.sha)
        
        # 返回最新的 commit 日期
        return latest_commit.commit.author.date
        
    except Exception as e:
        print(f"⚠️  获取最新 commit 日期失败: {e}")
        return datetime.now()

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
    """按月批量采集commit数据（智能增量采集）"""
    print("=" * 60)
    print("📅 MaxKB 智能 Commit 数据采集工具")
    print("=" * 60)
    
    # 检测已存在的数据
    existing_info = get_existing_data_info()
    latest_commit_date = get_latest_commit_date()
    
    # 确定采集范围
    if existing_info:
        print(f"📊 检测到已有数据到: {existing_info['year']}年{existing_info['month']}月")
        start_year = existing_info['year']
        start_month = existing_info['month'] + 1
        if start_month > 12:
            start_month = 1
            start_year += 1
    else:
        print("📊 未检测到已有数据，从项目开始采集")
        start_year = 2023
        start_month = 6
    
    # 确定结束时间
    end_date = latest_commit_date
    end_year = end_date.year
    end_month = end_date.month
    
    print(f"📈 最新 commit 日期: {end_date.strftime('%Y-%m-%d')}")
    print(f"🎯 采集范围: {start_year}年{start_month}月 至 {end_year}年{end_month}月")
    
    # 生成需要采集的月份范围
    month_ranges = get_monthly_ranges(start_year, start_month, end_year, end_month)
    
    if not month_ranges:
        print("✅ 所有数据都已采集完成，无需额外采集！")
        return
    
    print(f"📦 总计需要采集 {len(month_ranges)} 个月的数据")
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
            print(f"  🚀 开始采集... (使用 {'Token' if check_token_status() else '无Token'})")
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
                # 尝试读取采集结果统计
                summary_file = range_info['output'].replace('.json', '_summary.json')
                commit_count = 0
                if Path(summary_file).exists():
                    try:
                        with open(summary_file, 'r', encoding='utf-8') as f:
                            summary = json.load(f)
                            commit_count = summary.get('total_commits', 0)
                    except:
                        pass
                
                print(f"  ✅ {range_info['label']} 采集完成")
                print(f"     提取了 {commit_count} 个 commit")
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