#!/usr/bin/env python3
"""
第一阶段：Commit 数据采集脚本
使用 PyDriller 从本地 Git 仓库提取所有 Commit 信息
Author:佟雨泽
"""

import json
import argparse
from datetime import datetime
from pathlib import Path
from pydriller import Repository
from typing import List, Dict


def fetch_commits(repo_path: str, since: str = None, until: str = None) -> List[Dict]:
    """
    从 Git 仓库提取所有 Commit 数据
    
    Args:
        repo_path: Git 仓库本地路径
        since: 开始日期 (YYYY-MM-DD)
        until: 结束日期 (YYYY-MM-DD)
    
    Returns:
        提取的 Commit 列表
    """
    commits_list = []
    
    print(f"📦 正在扫描仓库: {repo_path}")
    
    try:
        # 处理时间范围参数
        if since and until:
            repo = Repository(repo_path, since=since, to=until)
        elif since:
            repo = Repository(repo_path, since=since)
        elif until:
            repo = Repository(repo_path, to=until)
        else:
            repo = Repository(repo_path)
        total = 0
        
        # 遍历所有 commits
        for commit in repo.traverse_commits():
            total += 1
            
            # 构建 Commit 数据
            commit_data = {
                'hash': commit.hash,
                'author': commit.author.name,
                'author_email': commit.author.email,
                'date': commit.committer_date.isoformat(),
                'message': commit.msg,
                'insertions': commit.insertions,
                'deletions': commit.deletions,
                'files_changed': len(commit.modified_files),
                'is_merge': commit.merge,
                'files': []
            }
            
            # 提取修改的文件
            for file in commit.modified_files:
                commit_data['files'].append({
                    'filename': file.filename,
                    'added_lines': file.added_lines,
                    'deleted_lines': file.deleted_lines,
                    'change_type': file.change_type.name
                })
            
            commits_list.append(commit_data)
            
            # 进度显示
            if total % 100 == 0:
                print(f"  ✓ 已处理 {total} 个 Commit...")
        
        print(f"✅ 总共提取 {total} 个 Commit")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        raise
    
    return commits_list


def filter_bots(commits: List[Dict]) -> List[Dict]:
    """
    过滤掉机器人账户的提交
    """
    bots = ['dependabot', 'renovate', 'codecov', 'github-actions', 'facebook-github-bot']
    
    filtered = [
        c for c in commits 
        if not any(bot in c['author'].lower() for bot in bots)
    ]
    
    removed = len(commits) - len(filtered)
    if removed > 0:
        print(f"🤖 已过滤 {removed} 个机器人提交")
    
    return filtered


def merge_duplicate_authors(commits: List[Dict]) -> tuple[List[Dict], Dict]:
    """
    合并同一作者的重复邮箱
    返回: (清洁后的提交列表, 作者映射表)
    """
    author_mapping = {}
    
    # 构建作者映射（手动定义已知的重复）
    manual_mapping = {
        # 示例: 'old_email@example.com': 'canonical_name'
    }
    
    # 自动检测：相同邮箱域但不同本地名的作者
    author_by_email = {}
    for commit in commits:
        email = commit['author_email']
        name = commit['author']
        
        if email not in author_by_email:
            author_by_email[email] = name
        else:
            # 同一邮箱，不同名字时合并
            existing_name = author_by_email[email]
            if existing_name != name and email not in manual_mapping:
                print(f"⚠️  发现重复作者: '{name}' 和 '{existing_name}' (邮箱: {email})")
                # 保留最长的名字
                if len(name) > len(existing_name):
                    author_mapping[existing_name] = name
                    author_by_email[email] = name
    
    # 应用映射
    for commit in commits:
        if commit['author'] in author_mapping:
            commit['author'] = author_mapping[commit['author']]
    
    print(f"✓ 合并后的作者映射: {len(author_mapping)} 条")
    
    return commits, author_mapping


def save_commits(commits: List[Dict], output_path: str) -> None:
    """保存 Commit 数据到文件"""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(commits, f, ensure_ascii=False, indent=2)
    
    print(f"💾 数据已保存到: {output_path}")


def generate_summary(commits: List[Dict]) -> Dict:
    """生成 Commit 数据摘要"""
    if not commits:
        return {}
    
    dates = [datetime.fromisoformat(c['date']) for c in commits]
    
    summary = {
        'total_commits': len(commits),
        'unique_authors': len(set(c['author'] for c in commits)),
        'date_range': {
            'start': min(dates).isoformat(),
            'end': max(dates).isoformat()
        },
        'total_insertions': sum(c['insertions'] for c in commits),
        'total_deletions': sum(c['deletions'] for c in commits),
        'files_touched': len(set(f['filename'] for c in commits for f in c['files'])),
        'merge_commits': len([c for c in commits if c['is_merge']])
    }
    
    return summary


def main():
    # 获取项目根目录的绝对路径
    project_root = Path(__file__).parent.parent.parent.absolute()
    default_repo_path = project_root / "源代码"
    
    parser = argparse.ArgumentParser(
        description='从 Git 仓库提取 Commit 数据'
    )
    parser.add_argument(
        '--repo-path', 
        default=str(default_repo_path),  # 默认指向 MaxKB 源代码目录
        help=f'Git 仓库本地路径 (默认: {default_repo_path})'
    )
    parser.add_argument(
        '--output-file',
        default='data/maxkb_commits.json',
        help='输出文件路径 (默认: data/maxkb_commits.json)'
    )
    parser.add_argument(
        '--since',
        help='开始日期 (YYYY-MM-DD), 默认为整个历史'
    )
    parser.add_argument(
        '--until',
        help='结束日期 (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--filter-bots',
        action='store_true',
        default=True,
        help='过滤机器人账户 (默认: True)'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🚀 MaxKB Commit 数据采集工具")
    print("=" * 60)
    
    # 采集数据
    commits = fetch_commits(args.repo_path, args.since, args.until)
    
    # 数据清洗
    if args.filter_bots:
        commits = filter_bots(commits)
    
    commits, author_mapping = merge_duplicate_authors(commits)
    
    # 生成摘要
    summary = generate_summary(commits)
    print("\n📊 数据摘要:")
    print(f"  • 总 Commit 数: {summary['total_commits']}")
    print(f"  • 独立作者数: {summary['unique_authors']}")
    print(f"  • 时间范围: {summary['date_range']['start'][:10]} 至 {summary['date_range']['end'][:10]}")
    print(f"  • 代码增加: {summary['total_insertions']:,} 行")
    print(f"  • 代码删除: {summary['total_deletions']:,} 行")
    print(f"  • 修改文件数: {summary['files_touched']}")
    print(f"  • 合并提交数: {summary['merge_commits']}")
    
    # 保存数据
    save_commits(commits, args.output_file)
    
    # 保存摘要
    summary_file = args.output_file.replace('.json', '_summary.json')
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"💾 摘要已保存到: {summary_file}")
    
    print("\n✅ 数据采集完成！")


if __name__ == '__main__':
    main()
