#!/usr/bin/env python3
"""路径调试脚本"""

from pathlib import Path

# 模拟 fetch_commits.py 中的路径计算
script_path = Path("evolution/scripts/fetch_commits.py")
project_root = script_path.parent.parent.parent.absolute()
default_repo_path = project_root / "源代码"

print("=" * 50)
print("路径调试信息")
print("=" * 50)
print(f"脚本路径: {script_path}")
print(f"项目根目录: {project_root}")
print(f"默认仓库路径: {default_repo_path}")
print(f"仓库路径存在: {default_repo_path.exists()}")
print(f"是 Git 仓库: {(default_repo_path / '.git').exists()}")

# 测试相对路径
relative_path = "../源代码"
resolved_relative = Path(relative_path).resolve()
print(f"\n相对路径 '../源代码' 解析为: {resolved_relative}")
print(f"相对路径存在: {resolved_relative.exists()}")