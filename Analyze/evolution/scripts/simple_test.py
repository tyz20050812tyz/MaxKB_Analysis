#!/usr/bin/env python3
"""
简化版的单月数据采集脚本
用于测试和验证基本功能
"""

import json
import argparse
from datetime import datetime
from pathlib import Path
from github import Github

def simple_fetch_test():
    """简化的数据采集测试"""
    print("=" * 50)
    print("🧪 简化版 GitHub 数据采集测试")
    print("=" * 50)
    
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
        print("❌ 未找到 GitHub token")
        return
    
    print(f"✅ 找到 token，长度: {len(token)}")
    
    try:
        # 初始化 GitHub 客户端
        g = Github(token)
        print("✅ GitHub 客户端初始化成功")
        
        # 获取仓库
        repo = g.get_repo('1Panel-dev/MaxKB')
        print(f"✅ 成功连接到仓库: {repo.full_name}")
        print(f"⭐ Stars: {repo.stargazers_count}")
        
        # 测试获取少量 commits
        print("\n📥 开始获取测试数据...")
        commits = repo.get_commits(per_page=10)  # 只获取10个
        
        commit_list = []
        for i, commit in enumerate(commits):
            commit_details = commit.commit
            commit_data = {
                'hash': commit.sha[:8],  # 只取前8位
                'author': commit_details.author.name if commit_details.author else 'Unknown',
                'date': commit_details.author.date.strftime('%Y-%m-%d') if commit_details.author else '',
                'message': commit_details.message[:50] + '...' if len(commit_details.message) > 50 else commit_details.message
            }
            commit_list.append(commit_data)
            print(f"  {i+1}. {commit_data['hash']} - {commit_data['author']} - {commit_data['date']}")
        
        # 保存测试数据
        output_file = "data/simple_test_commits.json"
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(commit_list, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 测试数据已保存到: {output_file}")
        print(f"📊 共获取 {len(commit_list)} 个 commit")
        
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    simple_fetch_test()