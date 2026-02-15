import libcst as cst
import libcst.metadata as metadata
import re

class NamingConventionChecker(cst.CSTVisitor):
    METADATA_DEPENDENCIES = (metadata.PositionProvider,)

    def __init__(self, filename):
        self.filename = filename
        self.smells = []
        self.snake_case_re = re.compile(r'^_{0,2}[a-z][a-z0-9_]*_{0,2}$')
        self.constant_case_re = re.compile(r'^_{0,2}[A-Z][A-Z0-9_]*_{0,2}$')

    def add_smell(self, node, detail, fix_suggestion, severity="Low"):
        pos = self.get_metadata(metadata.PositionProvider, node)
        line = pos.start.line if pos else "Unknown"
        self.smells.append({
            "file": self.filename, "line": line, "issue": "命名不规范",
            "detail": detail, "severity": severity,
            "suggested_fix": fix_suggestion
        })

    def visit_FunctionDef(self, node: cst.FunctionDef):
        func_name = node.name.value
        if not self.snake_case_re.match(func_name):
            self.add_smell(node, f"函数名 '{func_name}' 不符合 snake_case", f"将 '{func_name}' 重命名为小写字母加下划线的格式", "Medium")
        return True

    def visit_AssignTarget(self, node: cst.AssignTarget):
        if isinstance(node.target, cst.Name):
            var_name = node.target.value
            if not (self.snake_case_re.match(var_name) or self.constant_case_re.match(var_name)):
                self.add_smell(
                    node, 
                    f"变量/常量名 '{var_name}' 不符合规范", 
                    f"建议将 '{var_name}' 修改为 snake_case (全小写加下划线) 或 CONSTANT_CASE (全大写加下划线)",
                    "Low"
                )
        return True