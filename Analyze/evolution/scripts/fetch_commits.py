#!/usr/bin/env python3
"""
第一阶段：Commit 数据采集脚本
使用 GitHub API 从远程仓库提取所有 Commit 信息
Author:佟雨泽
"""

import json
import argparse
import requests
import os
from datetime import datetime
from pathlib import Path
from github import Github
try:
    from github import Auth  # 新版本 PyGithub
    HAS_AUTH = True
except ImportError:
    HAS_AUTH = False
from typing import List, Dict
from dotenv import load_dotenv

# 直接从 .env.example 文件读取 token
def load_token_from_env_example():
    env_file = Path(__file__).parent.parent.parent / '.env.example'
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('GITHUB_TOKEN='):
                    return line.split('=', 1)[1].strip()
    return None

# 获取 token
default_token = load_token_from_env_example()


def fetch_github_commits(repo_name: str, token: str = None, since: str = None, until: str = None) -> List[Dict]:
    """
    从 GitHub 仓库提取所有 Commit 数据
    
    Args:
        repo_name: GitHub 仓库名称 (格式: owner/repo)
        token: GitHub Personal Access Token (可选，但建议使用以避免速率限制)
        since: 开始日期 (YYYY-MM-DD)
        until: 结束日期 (YYYY-MM-DD)
    
    Returns:
        提取的 Commit 列表
    """
    commits_list = []
    
    print(f"📦 正在从 GitHub 获取仓库数据: {repo_name}")
    
    try:
        # 初始化 GitHub 客户端
        if token:
            if HAS_AUTH:
                # 使用新版本的认证方式
                auth = Auth.Token(token)
                g = Github(auth=auth)
            else:
                # 兼容旧版本
                g = Github(token)
        else:
            g = Github()
            print("⚠️  未提供 GitHub token，可能会遇到 API 速率限制")
        
        # 获取仓库
        repo = g.get_repo(repo_name)
        print(f"✅ 成功连接到仓库: {repo.full_name}")
        print(f"⭐ Star 数量: {repo.stargazers_count}")
        print(f"🍴 Fork 数量: {repo.forks_count}")
        
        # 构建查询参数
        params = {}
        if since:
            # 将字符串转换为 datetime 对象
            since_dt = datetime.strptime(since, '%Y-%m-%d')
            params['since'] = since_dt
        if until:
            # 将字符串转换为 datetime 对象
            until_dt = datetime.strptime(until, '%Y-%m-%d')
            params['until'] = until_dt
            
        # 获取 commits
        print(f"🔍 查询参数: {params}")
        commits = repo.get_commits(**params)
        print(f"📊 API 返回的 commits 对象: {type(commits)}")
        total = 0
        
        print("📥 开始获取 commit 数据...")
        
        for commit in commits:
            total += 1
            
            # 获取详细的 commit 信息
            commit_details = commit.commit
            
            # 构建 Commit 数据
            commit_data = {
                'hash': commit.sha,
                'author': commit_details.author.name if commit_details.author else 'Unknown',
                'author_email': commit_details.author.email if commit_details.author else '',
                'date': commit_details.author.date.isoformat() if commit_details.author else '',
                'message': commit_details.message,
                'committer': commit_details.committer.name if commit_details.committer else 'Unknown',
                'committer_email': commit_details.committer.email if commit_details.committer else '',
                'url': commit.html_url,
                'stats': {},
                'files': []
            }
            
            # 获取文件变更统计（如果可用）
            try:
                if commit.stats:
                    commit_data['stats'] = {
                        'additions': commit.stats.additions,
                        'deletions': commit.stats.deletions,
                        'total': commit.stats.total
                    }
            except:
                pass
            
            # 获取修改的文件
            try:
                files = commit.files
                for file in files:
                    commit_data['files'].append({
                        'filename': file.filename,
                        'status': file.status,
                        'additions': file.additions,
                        'deletions': file.deletions,
                        'changes': file.changes
                    })
            except:
                pass
            
            commits_list.append(commit_data)
            
            # 进度显示
            if total % 50 == 0:
                print(f"  ✓ 已获取 {total} 个 Commit...")
                
        print(f"✅ 总共获取 {total} 个 Commit")
        
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
    
    # 过滤掉无效日期的 commit
    valid_commits = [c for c in commits if c['date']]
    if not valid_commits:
        return {}
    
    dates = [datetime.fromisoformat(c['date']) for c in valid_commits]
    
    # 计算统计数据
    total_additions = sum(c['stats'].get('additions', 0) for c in valid_commits)
    total_deletions = sum(c['stats'].get('deletions', 0) for c in valid_commits)
    total_files = sum(len(c['files']) for c in valid_commits)
    
    summary = {
        'total_commits': len(commits),
        'valid_commits': len(valid_commits),
        'unique_authors': len(set(c['author'] for c in commits)),
        'date_range': {
            'start': min(dates).isoformat() if dates else '',
            'end': max(dates).isoformat() if dates else ''
        },
        'total_additions': total_additions,
        'total_deletions': total_deletions,
        'total_files_changed': total_files,
        'avg_commits_per_author': len(valid_commits) / len(set(c['author'] for c in valid_commits)) if valid_commits else 0
    }
    
    return summary


def main():
    parser = argparse.ArgumentParser(
        description='从 GitHub 仓库提取 Commit 数据'
    )
    parser.add_argument(
        '--repo-name', 
        default='1Panel-dev/MaxKB',  # MaxKB 的 GitHub 仓库
        help='GitHub 仓库名称 (格式: owner/repo, 默认: 1Panel-dev/MaxKB)'
    )
    parser.add_argument(
        '--github-token',
        help='GitHub Personal Access Token (可选，但建议使用)'
    )
    parser.add_argument(
        '--output-file',
        default='data/github_commits.json',
        help='输出文件路径 (默认: data/github_commits.json)'
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
        '--max-commits',
        type=int,
        default=1000,
        help='最大获取的 commit 数量 (默认: 1000)'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🚀 GitHub Commit 数据采集工具")
    print("=" * 60)
    
    # 获取 token (优先级: 命令行参数 > .env.example 文件 > 环境变量)
    token = args.github_token or default_token or os.getenv('GITHUB_TOKEN')
    
    # 显示配置信息
    print(f"📁 目标仓库: {args.repo_name}")
    print(f"📁 输出文件: {args.output_file}")
    print(f"📁 时间范围: {args.since or '开始'} 至 {args.until or '现在'}")
    print(f"📁 最大数量: {args.max_commits}")
    print(f"📁 使用 Token: {'是' if token else '否'}")
    
    if not token:
        print("⚠️  建议提供 GitHub token 以避免 API 速率限制")
        print("💡 可通过 --github-token 参数提供，或确保 .env.example 文件中有正确配置")
    
    # 采集数据
    commits = fetch_github_commits(args.repo_name, token, args.since, args.until)
    
    # 限制最大数量
    if len(commits) > args.max_commits:
        print(f"✂️  限制 commit 数量至 {args.max_commits}")
        commits = commits[:args.max_commits]
    
    # 数据清洗 (简化版)
    print("🧹 正在清洗数据...")
    
    # 过滤机器人提交
    bots = ['dependabot', 'renovate', 'codecov', 'github-actions']
    filtered_commits = [
        c for c in commits 
        if not any(bot in c['author'].lower() for bot in bots)
    ]
    
    if len(filtered_commits) < len(commits):
        print(f"🤖 过滤了 {len(commits) - len(filtered_commits)} 个机器人提交")
        commits = filtered_commits
    
    # 简单的作者去重
    authors = {}
    for commit in commits:
        author = commit['author']
        if author not in authors:
            authors[author] = 0
        authors[author] += 1
    
    print(f"👥 识别出 {len(authors)} 个独立作者")
    
    # 生成摘要
    summary = generate_summary(commits)
    print("\n📊 数据摘要:")
    
    if summary:
        print(f"  • 总 Commit 数: {summary.get('total_commits', 0)}")
        print(f"  • 有效 Commit 数: {summary.get('valid_commits', 0)}")
        print(f"  • 独立作者数: {summary.get('unique_authors', 0)}")
        if summary.get('date_range', {}).get('start'):
            print(f"  • 时间范围: {summary['date_range']['start'][:10]} 至 {summary['date_range']['end'][:10]}")
        print(f"  • 代码增加: {summary.get('total_additions', 0):,} 行")
        print(f"  • 代码删除: {summary.get('total_deletions', 0):,} 行")
        print(f"  • 修改文件数: {summary.get('total_files_changed', 0)}")
        print(f"  • 平均每人提交: {summary.get('avg_commits_per_author', 0):.1f} 次")
    else:
        print("  • 没有获取到任何 commit 数据")
    
    # 保存数据
    save_commits(commits, args.output_file)
    
    # 保存摘要
    summary_file = args.output_file.replace('.json', '_summary.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"💾 摘要已保存到: {summary_file}")
    
    print("\n✅ GitHub 数据采集完成！")


if __name__ == '__main__':
    main()
