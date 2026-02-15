import libcst as cst
import libcst.metadata as metadata
import argparse
import os
import json
from pathlib import Path

# 导入写好的具体规则
from visitors.async_sync_checker import AsyncSyncChecker
from visitors.naming_convention_checker import NamingConventionChecker
from visitors.exception_handler_checker import ExceptionHandlerChecker


def detect_code_smells(target_path):
    print(f"启动代码异味模块化扫描: {target_path}")
    target_dir = Path(target_path)

    if not target_dir.exists():
        print(f"错误: 找不到目标路径 '{target_dir.resolve()}'")
        return

    all_smells = []

    for py_file in target_dir.rglob("*.py"):
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                source = f.read()

            module = cst.parse_module(source)
            wrapper = metadata.MetadataWrapper(module)

            # 初始化所有检查器
            filename = py_file.name
            checkers = [
                AsyncSyncChecker(filename),
                NamingConventionChecker(filename),
                ExceptionHandlerChecker(filename)
            ]

            # 依次执行遍历
            for checker in checkers:
                wrapper.visit(checker)
                all_smells.extend(checker.smells)

        except Exception as e:
            print(f"解析文件 {py_file.name} 失败: {e}")

    os.makedirs('results', exist_ok=True)
    output_path = 'results/code_smells.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_smells, f, ensure_ascii=False, indent=4)

    print(f"扫描完成！共发现 {len(all_smells)} 处异味。报告保存至: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", required=True, help="源代码路径")
    args = parser.parse_args()
    detect_code_smells(args.path)
