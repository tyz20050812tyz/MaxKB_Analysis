#!/usr/bin/env python3
"""
Git 仓库设置脚本
用于初始化或检查 MaxKB 源代码的 Git 仓库
"""

import os
import subprocess
from pathlib import Path

def check_git_repo(repo_path):
    """检查是否为有效的 Git 仓库"""
    git_dir = Path(repo_path) / '.git'
    return git_dir.exists()

def init_git_repo(repo_path):
    """初始化 Git 仓库"""
    try:
        # 进入目录
        os.chdir(repo_path)
        
        # 初始化 Git 仓库
        subprocess.run(['git', 'init'], check=True)
        
        # 添加所有文件
        subprocess.run(['git', 'add', '.'], check=True)
        
        # 创建初始提交
        subprocess.run(['git', 'commit', '-m', 'Initial commit: MaxKB source code'], check=True)
        
        print("✅ Git 仓库初始化成功!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git 操作失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False

def main():
    # 设置路径
    repo_path = Path('../源代码').resolve()
    
    print("=" * 50)
    print("🔍 Git 仓库检查工具")
    print("=" * 50)
    print(f"检查路径: {repo_path}")
    
    # 检查路径是否存在
    if not repo_path.exists():
        print(f"❌ 路径不存在: {repo_path}")
        return
    
    print("✓ 路径存在")
    
    # 检查是否为 Git 仓库
    if check_git_repo(repo_path):
        print("✅ 这是一个有效的 Git 仓库")
        print("可以直接运行 fetch_commits.py")
    else:
        print("❌ 这不是一个 Git 仓库")
        print("\n是否要初始化 Git 仓库? (y/n): ", end="")
        
        # 简单的用户交互
        response = input().strip().lower()
        if response in ['y', 'yes', '是']:
            if init_git_repo(repo_path):
                print("\n🎉 现在可以运行 fetch_commits.py 采集数据了!")
            else:
                print("\n❌ Git 仓库初始化失败")
        else:
            print("请手动初始化 Git 仓库后再运行")

if __name__ == '__main__':
    main()