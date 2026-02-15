#!/usr/bin/env python3
"""
合并所有月份的 commit 数据
"""

import json
import glob
from pathlib import Path

def merge_monthly_data():
    """合并所有月份的 commit 数据"""
    data_dir = Path('data')
    output_file = 'data/all_commits.json'  # 直接定义输出路径
    
    print("=" * 50)
    print("🔄 合并月度 commit 数据")
    print("=" * 50)
    
    all_commits = []
    file_count = 0
    
    # 查找所有 commits_*.json 文件
    for file_path in sorted(data_dir.glob('commits_*.json')):
        if '_summary.json' not in file_path.name:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    commits = json.load(f)
                    all_commits.extend(commits)
                    file_count += 1
                    print(f"✓ 加载 {file_path.name}: {len(commits)} 个 commit")
            except Exception as e:
                print(f"❌ 读取 {file_path.name} 失败: {e}")
    
    # 保存合并后的数据
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_commits, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 合并完成:")
    print(f"  文件数量: {file_count}")
    print(f"  总 commit 数: {len(all_commits)}")
    print(f"  输出文件: {output_file}")
    
    return output_file

if __name__ == '__main__':
    merge_monthly_data()