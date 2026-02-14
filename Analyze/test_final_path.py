#!/usr/bin/env python3
"""测试最终的路径配置"""

from pathlib import Path

# 模拟最终的路径计算
script_file = Path("D:/佟雨泽/大三上/开源软件基础/MaxKB_Analysis/Analyze/evolution/scripts/fetch_commits.py")
project_root = script_file.parent.parent.parent.parent.absolute()
default_repo_path = project_root / "源代码"

print("=" * 60)
print("最终路径配置测试")
print("=" * 60)
print(f"脚本文件路径: {script_file}")
print(f"项目根目录: {project_root}")
print(f"默认仓库路径: {default_repo_path}")
print(f"仓库路径存在: {default_repo_path.exists()}")
print(f"包含 .git 目录: {(default_repo_path / '.git').exists()}")

# 如果仓库不存在，显示正确的路径
if not default_repo_path.exists():
    print(f"\n💡 正确的仓库路径应该是:")
    print(f"   {project_root}")
    print(f"\n请确保 MaxKB 源代码位于:")
    print(f"   {default_repo_path}")