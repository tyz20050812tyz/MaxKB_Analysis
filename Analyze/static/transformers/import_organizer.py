import libcst as cst
import argparse
import os
import difflib
from pathlib import Path


class ImportOrganizerTransformer(cst.CSTTransformer):
    def __init__(self, filename):
        self.filename = filename
        self.changes_made = 0

    def leave_ImportFrom(self, original_node: cst.ImportFrom, updated_node: cst.ImportFrom):
        # 仅处理包含多个导入项的情况 (例如 from module import B, A)
        if isinstance(updated_node.names, tuple) or isinstance(updated_node.names, list):
            # 提取原有的名称顺序
            original_names = [alias.name.value for alias in updated_node.names]
            # 按照字母顺序重新排序
            sorted_aliases = tuple(
                sorted(updated_node.names, key=lambda alias: alias.name.value))
            sorted_names = [alias.name.value for alias in sorted_aliases]

            # 如果排序后与原来不同，说明发生了重构
            if original_names != sorted_names:
                self.changes_made += 1
                return updated_node.with_changes(names=sorted_aliases)

        return updated_node


def run_import_organizer(target_path, is_dry_run):
    print(f"启动导入语句整理 Transformer: {target_path}")
    target_dir = Path(target_path)
    if not target_dir.exists():
        print(f"找不到目标路径: {target_dir.resolve()}")
        return

    total_changes = 0
    diff_results = []

    for py_file in target_dir.rglob("*.py"):
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                original_code = f.read()

            tree = cst.parse_module(original_code)
            transformer = ImportOrganizerTransformer(py_file.name)
            modified_tree = tree.visit(transformer)

            if transformer.changes_made > 0:
                modified_code = modified_tree.code
                total_changes += transformer.changes_made

                # 生成重构对比
                diff = difflib.unified_diff(
                    original_code.splitlines(), modified_code.splitlines(),
                    fromfile=f"a/{py_file.name}", tofile=f"b/{py_file.name}", lineterm=""
                )
                diff_results.append("\n".join(diff))

                # 如果不是 dry-run，则将重构后的代码写回文件
                if not is_dry_run:
                    with open(py_file, "w", encoding="utf-8") as f:
                        f.write(modified_code)

        except Exception as e:
            pass

    # 产出报告
    os.makedirs('results', exist_ok=True)
    report_path = 'results/import_organizer_report.md'
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# 导入语句整理报告\n\n")
        f.write(f"共自动整理了 **{total_changes}** 处导入语句。\n\n")
        if diff_results:
            f.write("## 代码修改对比 (Diff)\n```diff\n")
            for diff_text in diff_results:
                f.write(diff_text + "\n\n")
            f.write("```\n")

    print(f"整理完成！共优化 {total_changes} 处导入。")
    print(f"详情请查看: {report_path}")
    if is_dry_run:
        print("[Dry Run 模式] 已生成对比报告，未修改源文件。")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", required=True, help="源代码路径")
    parser.add_argument("--dry-run", action="store_true",
                        help="仅预览变更，不直接修改源文件")
    args = parser.parse_args()
    run_import_organizer(args.path, args.dry_run)
