import libcst as cst
import libcst.metadata as metadata

class AsyncSyncChecker(cst.CSTVisitor):
    METADATA_DEPENDENCIES = (metadata.PositionProvider,)

    def __init__(self, filename):
        self.filename = filename
        self.smells = []
        self.in_async = False
        self.blocking_calls = {"sleep", "get", "post", "query", "urlopen", "read"}

    def visit_FunctionDef(self, node: cst.FunctionDef):
        if node.asynchronous is not None:
            self.in_async = True
        return True

    def leave_FunctionDef(self, node: cst.FunctionDef):
        self.in_async = False

    def visit_Call(self, node: cst.Call):
        if self.in_async:
            call_name = None
            if isinstance(node.func, cst.Name):
                call_name = node.func.value
            elif isinstance(node.func, cst.Attribute):
                call_name = node.func.attr.value
            
            if call_name in self.blocking_calls:
                pos = self.get_metadata(metadata.PositionProvider, node)
                line = pos.start.line if pos else "Unknown"
                self.smells.append({
                    "file": self.filename,
                    "line": line,
                    "issue": "异步/同步混用",
                    "detail": f"发现同步阻塞调用 '{call_name}()'",
                    "severity": "High",
                    "suggested_fix": f"请将 '{call_name}()' 替换为对应的异步版本（如使用 aiohttp 或 asyncio.sleep），并加上 await 关键字。"
                })
        return True

