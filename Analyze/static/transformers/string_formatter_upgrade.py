import libcst as cst
import argparse
import os
import difflib
from pathlib import Path

class StringUpgradeTransformer(cst.CSTTransformer):
    def __init__(self, filename):
        self.filename = filename
        self.auto_refactored = 0
        self.manual_review_needed = []

    # 转换 "{}".format(var) 为 f"{var}" 
    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call):
        if isinstance(original_node.func, cst.Attribute) and original_node.func.attr.value == "format":
            if isinstance(original_node.func.value, cst.SimpleString):
                try:
                    new_node = cst.parse_expression(f'f{original_node.func.value.value}')
                    self.auto_refactored += 1
                    return new_node
                except Exception:
                    self.manual_review_needed.append(f"复杂的 `.format()` 结构，建议人工审查。行号：未知")
        return updated_node

    # 转换 "%s" % var
    def leave_BinaryOperation(self, original_node: cst.BinaryOperation, updated_node: cst.BinaryOperation):
        if isinstance(original_node.operator, cst.Modulo) and isinstance(original_node.left, cst.SimpleString):
            self.manual_review_needed.append("发现旧式 `%` 格式化，因涉及类型符(%s, %d)，建议人工升级为 f-string。")
        return updated_node

def run_transformer(target_path):
    print(f"启动代码自动重构 Transformer: {target_path}")
    target_dir = Path(target_path)
    
    diff_results = []
    manual_reviews = []
    auto_count = 0

    for py_file in target_dir.rglob("*.py"):
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                original_code = f.read()
            
            tree = cst.parse_module(original_code)
            transformer = StringUpgradeTransformer(py_file.name)
            modified_tree = tree.visit(transformer)
            
            modified_code = modified_tree.code
            auto_count += transformer.auto_refactored
            
            if transformer.manual_review_needed:
                manual_reviews.extend([(py_file.name, msg) for msg in transformer.manual_review_needed])

            # 生成代码改进前后对比 (Diff)
            if original_code != modified_code:
                diff = difflib.unified_diff(
                    original_code.splitlines(), modified_code.splitlines(),
                    fromfile=f"a/{py_file.name}", tofile=f"b/{py_file.name}", lineterm=""
                )
                diff_results.append("\n".join(diff))
                
        except Exception:
            pass

    # 产出报告
    os.makedirs('results', exist_ok=True)
    report_path = 'results/refactoring_suggestions.md'
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# 代码重构建议与对比报告\n\n")
        
        f.write("## 1. 可自动化重构的代码清单\n")
        f.write(f"共发现并尝试自动转换了 **{auto_count}** 处简单的 `.format()` 为 f-string。\n\n")
        
        f.write("## 2. 人工审查清单\n")
        if manual_reviews:
            for file, msg in manual_reviews:
                f.write(f"- **{file}**: {msg}\n")
        else:
            f.write("暂无需要人工审查的复杂格式化。\n\n")
            
        f.write("\n## 3. 改进前后代码对比 (Diff)\n```diff\n")
        for diff_text in diff_results:
            f.write(diff_text + "\n\n")
        f.write("```\n")

    print(f"重构分析完成！前后代码对比已生成至 {report_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", required=True)
    args = parser.parse_args()
    run_transformer(args.path)