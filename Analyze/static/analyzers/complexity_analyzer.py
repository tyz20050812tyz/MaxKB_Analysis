import argparse
import os
import json
from radon.complexity import cc_visit
from pathlib import Path

def analyze_complexity(target_path):
    print(f"开始计算核心业务逻辑圈复杂度: {target_path}")
    target_dir = Path(target_path)
    if not target_dir.exists():
        print("目标路径不存在！")
        return

    results = []
    for py_file in target_dir.rglob("*.py"):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                code = f.read()
            blocks = cc_visit(code)
            for block in blocks:
                results.append({
                    "module": py_file.name,
                    "function": block.name,
                    "complexity": block.complexity
                })
        except Exception:
            pass

    results.sort(key=lambda x: x['complexity'], reverse=True)
    
    os.makedirs('results', exist_ok=True)
    output_file = 'results/complexity_report.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
        
    print(f"复杂度分析完成！报告已保存至 {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", required=True)
    args = parser.parse_args()
    analyze_complexity(args.path)