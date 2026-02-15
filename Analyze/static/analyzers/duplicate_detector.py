import libcst as cst
import argparse
import os
import json
import hashlib
from collections import defaultdict
from pathlib import Path

def detect_duplicates(target_path):
    print(f"开始进行代码重复率检测: {target_path}")
    target_dir = Path(target_path)
    if not target_dir.exists():
        print("目标路径不存在！")
        return

    function_hashes = defaultdict(list)
    duplicates = []

    for py_file in target_dir.rglob("*.py"):
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                source = f.read()
            module = cst.parse_module(source)
            
            for node in module.children:
                if isinstance(node, cst.FunctionDef):
                    func_code = module.code_for_node(node)
                    if len(func_code.splitlines()) > 10: 
                        code_hash = hashlib.md5(func_code.encode('utf-8')).hexdigest()
                        function_hashes[code_hash].append((py_file.name, node.name.value))
        except Exception:
            pass

    for code_hash, locations in function_hashes.items():
        if len(locations) > 1:
            loc_str = " | ".join([f"{f}->{n}()" for f, n in locations])
            duplicates.append({
                "issue": "高度重复的代码段",
                "locations": loc_str,
                "severity": "High"
            })
            
    print(f"查重完成！发现 {len(duplicates)} 组重复代码。")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", required=True)
    args = parser.parse_args()
    detect_duplicates(args.path)