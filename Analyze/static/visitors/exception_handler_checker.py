import libcst as cst
import libcst.metadata as metadata


class ExceptionHandlerChecker(cst.CSTVisitor):
    METADATA_DEPENDENCIES = (metadata.PositionProvider,)

    def __init__(self, filename):
        self.filename = filename
        self.smells = []

    def visit_ExceptHandler(self, node: cst.ExceptHandler):
        pos = self.get_metadata(metadata.PositionProvider, node)
        line = pos.start.line if pos else "Unknown"

        if node.type is None:
            self.smells.append({
                "file": self.filename, "line": line, "issue": "异常处理不当",
                "detail": "捕获了全量异常 (裸 except:)", "severity": "High",
                "suggested_fix": "明确指定需要捕获的异常类型，例如 'except ValueError:'"
            })
        elif isinstance(node.type, cst.Name) and node.type.value in ('Exception', 'BaseException'):
            self.smells.append({
                "file": self.filename, "line": line,
                "issue": "异常处理不当", "detail": f"过于宽泛的异常捕获: except {node.type.value}:", "severity": "Medium"
            })
        return True
