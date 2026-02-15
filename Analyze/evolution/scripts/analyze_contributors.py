#!/usr/bin/env python3
"""
第一阶段：贡献者分析脚本
分析贡献者分布、活跃度、Gini 系数等指标
Author:佟雨泽
"""

import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple


def load_commits(input_file: str) -> List[Dict]:
    """加载 Commit 数据"""
    print(f"📂 加载数据文件: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def calculate_gini(values: List[int]) -> float:
    """
    计算 Gini 系数 (衡量不平等度)
    0 = 完全平等，1 = 完全不平等
    """
    sorted_vals = sorted(values)
    n = len(values)
    cumsum = sum((i + 1) * val for i, val in enumerate(sorted_vals))
    return (2 * cumsum) / (n * sum(values)) - (n + 1) / n


def analyze_contributors(commits: List[Dict], recent_months: int = 6) -> Dict:
    """
    分析贡献者指标
    
    Args:
        commits: Commit 列表
        recent_months: 计算活跃贡献者的时间窗口 (月)
    
    Returns:
        分析结果字典
    """
    print("\n🔍 分析贡献者数据...")
    
    # 构建 DataFrame
    df = pd.DataFrame(commits)
    df['date'] = pd.to_datetime(df['date'])
    
    # 提取 stats 中的代码变更数据
    df['insertions'] = df['stats'].apply(lambda x: x.get('additions', 0) if isinstance(x, dict) else 0)
    df['deletions'] = df['stats'].apply(lambda x: x.get('deletions', 0) if isinstance(x, dict) else 0)
    
    # 基础统计
    total_commits = len(df)
    unique_authors = df['author'].nunique()
    
    # 作者统计
    author_stats = df.groupby('author').agg({
        'hash': 'count',  # Commit 数
        'insertions': 'sum',
        'deletions': 'sum',
        'date': ['min', 'max']
    }).round(2)
    
    author_stats.columns = ['commits', 'insertions', 'deletions', 'first_commit', 'last_commit']
    author_stats['code_change'] = author_stats['insertions'] + author_stats['deletions']
    author_stats = author_stats.sort_values('commits', ascending=False)
    
    # 活跃贡献者 (最近 N 个月)
    # 处理时区问题：将 naive datetime 转换为 UTC
    recent_date = datetime.now() - timedelta(days=30*recent_months)
    recent_date_utc = recent_date.replace(tzinfo=None)  # 移除时区信息以匹配数据
    recent_df = df[df['date'].dt.tz_localize(None) > recent_date_utc]
    active_authors = recent_df['author'].nunique()
    
    # 核心团队分析 (前 5% 贡献者)
    core_team_size = max(1, int(unique_authors * 0.05))
    top_authors = author_stats.head(core_team_size)
    top_commits = top_authors['commits'].sum()
    top_concentration = (top_commits / total_commits) * 100
    
    # Gini 系数
    gini = calculate_gini(author_stats['commits'].tolist())
    
    # 贡献分布分析
    commit_counts = author_stats['commits'].tolist()
    
    analysis = {
        'summary': {
            'total_commits': int(total_commits),
            'unique_authors': int(unique_authors),
            'active_authors_6m': int(active_authors),
            'core_team_size': int(core_team_size),
            'avg_commits_per_author': round(total_commits / unique_authors, 2),
            'gini_coefficient': round(gini, 3)
        },
        'top_contributors': []
    }
    
    # Top 20 贡献者
    for rank, (author, row) in enumerate(author_stats.head(20).iterrows(), 1):
        analysis['top_contributors'].append({
            'rank': rank,
            'author': author,
            'commits': int(row['commits']),
            'percentage': round((row['commits'] / total_commits) * 100, 2),
            'insertions': int(row['insertions']),
            'deletions': int(row['deletions']),
            'code_change': int(row['code_change']),
            'first_commit': row['first_commit'].isoformat()[:10],
            'last_commit': row['last_commit'].isoformat()[:10]
        })
    
    # 浓度指标
    analysis['concentration'] = {
        'top_5_percent_size': int(core_team_size),
        'top_5_percent_commits': int(top_commits),
        'top_5_percent_concentration': round(top_concentration, 2),
        'interpretation': 'High' if top_concentration > 70 else ('Medium' if top_concentration > 50 else 'Low')
    }
    
    print(f"✓ 总贡献者数: {unique_authors}")
    print(f"✓ 近 6 个月活跃贡献者: {active_authors}")
    print(f"✓ Gini 系数: {gini:.3f}")
    print(f"✓ 前 5% ({core_team_size} 人) 贡献率: {top_concentration:.1f}%")
    
    return analysis, author_stats


def generate_visualization_data(author_stats: pd.DataFrame) -> Dict:
    """
    生成可视化数据
    """
    print("\n📊 生成可视化数据...")
    
    viz_data = {
        'pareto': {
            'authors': [],
            'commits': [],
            'cumulative_percent': []
        },
        'distribution': {
            'bins': [0, 1, 5, 10, 20, 50, 100, 500, 1000, 5000],
            'counts': []
        }
    }
    
    # Pareto 数据 (前 50 个贡献者)
    total = author_stats['commits'].sum()
    cumsum = 0
    for author, row in author_stats.head(50).iterrows():
        cumsum += row['commits']
        viz_data['pareto']['authors'].append(author)
        viz_data['pareto']['commits'].append(int(row['commits']))
        viz_data['pareto']['cumulative_percent'].append(
            round((cumsum / total) * 100, 2)
        )
    
    # 分布直方图数据
    commits_list = author_stats['commits'].tolist()
    bins = [0, 1, 5, 10, 20, 50, 100, 500, 1000, 5000]
    for i in range(len(bins) - 1):
        count = len([c for c in commits_list if bins[i] <= c < bins[i+1]])
        viz_data['distribution']['counts'].append({
            'range': f"{bins[i]}-{bins[i+1]}",
            'count': count
        })
    
    # 最后一个 bin (5000+)
    count = len([c for c in commits_list if c >= bins[-1]])
    viz_data['distribution']['counts'].append({
        'range': f"{bins[-1]}+",
        'count': count
    })
    
    return viz_data


def save_analysis(analysis: Dict, author_stats: pd.DataFrame, 
                  output_dir: str = 'evolution/results') -> None:
    """保存分析结果"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 保存 JSON 格式
    with open(f'{output_dir}/contributors_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    print(f"💾 分析结果已保存: {output_dir}/contributors_analysis.json")
    
    # 保存 CSV 格式 (便于 Excel 查看)
    author_stats.to_csv(f'{output_dir}/contributors_ranking.csv', encoding='utf-8')
    print(f"💾 排名表已保存: {output_dir}/contributors_ranking.csv")
    
    # 保存可视化数据
    viz_data = generate_visualization_data(author_stats)
    with open(f'{output_dir}/visualization_data.json', 'w', encoding='utf-8') as f:
        json.dump(viz_data, f, ensure_ascii=False, indent=2)
    print(f"💾 可视化数据已保存: {output_dir}/visualization_data.json")


def print_report(analysis: Dict) -> None:
    """打印分析报告"""
    print("\n" + "=" * 70)
    print("📈 贡献者分析报告")
    print("=" * 70)
    
    summary = analysis['summary']
    print(f"\n【基础统计】")
    print(f"  总 Commit 数:        {summary['total_commits']:,}")
    print(f"  独立贡献者数:        {summary['unique_authors']}")
    print(f"  近 6 个月活跃贡献者:  {summary['active_authors_6m']}")
    print(f"  平均提交数/人:        {summary['avg_commits_per_author']}")
    
    print(f"\n【集中度指标】")
    print(f"  Gini 系数:           {summary['gini_coefficient']} " + 
          f"({'低平等' if summary['gini_coefficient'] > 0.7 else ('中等' if summary['gini_coefficient'] > 0.5 else '高平等')})")
    
    conc = analysis['concentration']
    print(f"  核心团队规模:        {conc['top_5_percent_size']} 人")
    print(f"  核心团队贡献率:      {conc['top_5_percent_concentration']}%")
    
    print(f"\n【Top 10 贡献者】")
    print(f"  {'排名':<5} {'作者':<20} {'提交数':<10} {'占比':<8} {'代码量':<10}")
    print(f"  {'-'*60}")
    for contributor in analysis['top_contributors'][:10]:
        print(f"  {contributor['rank']:<5} {contributor['author']:<20} "
              f"{contributor['commits']:<10} {contributor['percentage']:<7}% "
              f"{contributor['code_change']:<10}")
    
    print("\n" + "=" * 70)


def main():
    # 直接定义输入输出路径
    INPUT_FILE = 'data/all_commits.json'  # 合并后的所有 commit 数据
    OUTPUT_DIR = 'results'                # 分析结果输出目录
    RECENT_MONTHS = 6                     # 活跃贡献者时间窗口(月)
    
    print("=" * 60)
    print("📊 MaxKB 贡献者分析")
    print("=" * 60)
    print(f"📁 输入文件: {INPUT_FILE}")
    print(f"📁 输出目录: {OUTPUT_DIR}")
    print(f"🕐 活跃期: 最近 {RECENT_MONTHS} 个月")
    print()
    
    # 加载数据
    commits = load_commits(INPUT_FILE)
    
    # 分析
    analysis, author_stats = analyze_contributors(commits, RECENT_MONTHS)
    
    # 保存结果
    save_analysis(analysis, author_stats, OUTPUT_DIR)
    
    # 打印报告
    print_report(analysis)
    
    print("\n✅ 贡献者分析完成！")


if __name__ == '__main__':
    main()
