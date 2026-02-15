import libcst as cst
import argparse
import os
import difflib
from pathlib import Path

class ApiModernizerTransformer(cst.CSTTransformer):
    def __init__(self, filename):
        self.filename = filename
        self.upgraded_apis = 0

    def leave_Attribute(self, original_node: cst.Attribute, updated_node: cst.Attribute):
        # 规则 1: 升级 unittest 过时的 assertEquals -> assertEqual
        if updated_node.attr.value == 'assertEquals':
            self.upgraded_apis += 1
            return updated_node.with_changes(attr=cst.Name('assertEqual'))
            
        # 规则 2: 升级 logging 模块过时的 warn -> warning
        if updated_node.attr.value == 'warn' and isinstance(updated_node.value, cst.Name) and updated_node.value.value == 'logging':
            self.upgraded_apis += 1
            return updated_node.with_changes(attr=cst.Name('warning'))
            
        return updated_node

def run_api_modernizer(target_path, is_dry_run):
    print(f"启动过时 API 自动升级 Transformer: {target_path}")
    target_dir = Path(target_path)
    if not target_dir.exists():
        print(f"❌ 找不到目标路径: {target_dir.resolve()}")
        return

    total_upgrades = 0
    diff_results = []

    for py_file in target_dir.rglob("*.py"):
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                original_code = f.read()
            
            tree = cst.parse_module(original_code)
            transformer = ApiModernizerTransformer(py_file.name)
            modified_tree = tree.visit(transformer)
            
            if transformer.upgraded_apis > 0:
                modified_code = modified_tree.code
                total_upgrades += transformer.upgraded_apis
                
                diff = difflib.unified_diff(
                    original_code.splitlines(), modified_code.splitlines(),
                    fromfile=f"a/{py_file.name}", tofile=f"b/{py_file.name}", lineterm=""
                )
                diff_results.append("\n".join(diff))
                
                if not is_dry_run:
                    with open(py_file, "w", encoding="utf-8") as f:
                        f.write(modified_code)
                        
        except Exception as e:
            pass

    # 产出报告
    os.makedirs('results', exist_ok=True)
    report_path = 'results/api_modernization_report.md'
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# API 现代化升级报告\n\n")
        f.write(f"共成功升级了 **{total_upgrades}** 处过时 API 调用。\n\n")
        if diff_results:
            f.write("## 代码修改对比 (Diff)\n```diff\n")
            for diff_text in diff_results:
                f.write(diff_text + "\n\n")
            f.write("```\n")

    print(f"升级扫描完成！共转换 {total_upgrades} 处老旧 API。")
    print(f"详情请查看: {report_path}")
    if is_dry_run:
        print("[Dry Run 模式] 已生成对比报告，未修改源文件。")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", required=True, help="源代码路径")
    parser.add_argument("--dry-run", action="store_true", help="仅预览变更，不直接修改源文件")
    args = parser.parse_args()
    run_api_modernizer(args.path, args.dry_run)