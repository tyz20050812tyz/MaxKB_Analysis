# static 模块 - 基于 LibCST 的静态代码分析

## 模块简介

`static` 模块负责第二阶段的静态代码分析工作，通过 LibCST（Concrete Syntax Tree）和相关代码检测工具，在**不运行代码**的前提下发现 MaxKB 中的潜在问题、代码异味和质量缺陷。

## 核心分析方向

### 1. 代码异味检测（Code Smell Detection）
- **目标**：编写 LibCST Visitor 脚本，专门扫描不规范的代码模式
- **重点检测**：
  - 异步/同步混用错误（Django 视图中的同步阻塞调用）
  - 异常处理不当（过于宽泛的 Exception 捕获）
  - 命名不规范（变量、函数命名）
  - 代码重复率
- **产出**：代码异味报告、问题代码片段定位

### 2. 自动重构实验（Automated Refactoring）
- **目标**：编写 LibCST Transformer，批量优化代码
- **示例**：将项目中的旧式字符串格式化转换为 Python 3.6+ f-string
- **支持的重构**：
  - `%` 格式化 → f-string
  - `.format()` → f-string
  - 导入语句整理
  - 过时 API 升级
- **产出**：重构前后代码对比、改进统计

### 3. 复杂度分析（Complexity Analysis）
- **目标**：计算核心业务逻辑的圈复杂度（Cyclomatic Complexity）
- **重点模块**：
  - RAG 检索逻辑
  - 知识库相关函数
  - 权限管理模块
- **产出**：复杂度热力图、最难维护的函数排名

## 依赖工具

| 工具 | 用途 |
|------|------|
| `libcst` | 代码语法树分析和变换 |
| `flake8` | 代码风格检查 |
| `bandit` | 安全漏洞扫描 |
| `ast` | Python 抽象语法树 |
| `radon` | 复杂度测量 |

## 项目结构

```
static/
├── README.md                      # 本文件
├── visitors/                      # LibCST Visitor 脚本
│   ├── __init__.py
│   ├── code_smell_detector.py     # 代码异味检测器
│   ├── async_sync_checker.py      # 异步同步混用检查
│   ├── naming_convention_checker.py # 命名规范检查
│   └── exception_handler_checker.py # 异常处理检查
├── transformers/                  # LibCST Transformer 脚本
│   ├── __init__.py
│   ├── string_formatter_upgrade.py # 字符串格式化升级
│   ├── import_organizer.py        # 导入语句整理
│   └── api_modernizer.py          # API 升级转换
├── analyzers/                     # 复杂度和其他分析
│   ├── __init__.py
│   ├── complexity_analyzer.py     # 圈复杂度计算
│   ├── duplicate_detector.py      # 代码重复检测
│   └── bandit_scanner.py          # 安全扫描
├── config/                        # 配置文件
│   ├── default_rules.yaml         # 默认规则配置
│   └── scan_targets.json          # 扫描目标配置
├── results/                       # 分析结果
│   ├── code_smells.json           # 代码异味报告
│   ├── complexity_report.json     # 复杂度报告
│   ├── security_issues.json       # 安全问题报告
│   └── refactoring_suggestions.md # 重构建议
└── tests/                         # 单元测试
    ├── test_visitors.py
    └── test_transformers.py
```

## 快速开始

### 环境配置

```bash
# 安装依赖
pip install libcst flake8 bandit radon

# 或使用 requirements.txt
pip install -r requirements.txt
```

### 运行代码扫描

```bash
# 1. 执行代码异味检测
python -m visitors.code_smell_detector --path ../../源代码/apps

# 2. 执行安全扫描
python -m analyzers.bandit_scanner --path ../../源代码/apps

# 3. 执行复杂度分析
python -m analyzers.complexity_analyzer --path ../../源代码/apps

# 4. 生成完整分析报告
python analyze_all.py --repo-path ../../源代码 --output-dir ./results
```

### 执行自动重构

```bash
# 1. 预览重构变更（不修改源代码）
python -m transformers.string_formatter_upgrade --path ../../源代码/apps --dry-run

# 2. 执行重构（创建新文件）
python -m transformers.string_formatter_upgrade --path ../../源代码/apps --output-dir ./refactored

# 3. 整理导入语句
python -m transformers.import_organizer --path ../../源代码/apps
```

## LibCST 基础概念

### Visitor 模式
用于**遍历**代码树，检测特定的代码模式：
```python
from libcst import CSTVisitor

class MyCodeAnalyzer(CSTVisitor):
    def visit_FunctionDef(self, node):
        # 对每个函数定义进行处理
        print(f"Found function: {node.name.value}")
```

### Transformer 模式
用于**修改**代码树，自动进行代码变换：
```python
from libcst import CSTTransformer

class MyRefactorer(CSTTransformer):
    def leave_FormattedString(self, original_node, updated_node):
        # 将旧式格式化转换为新格式
        return new_node
```

## 主要产出

### 代码质量报告
- 代码异味清单（位置、严重度、建议修复）
- 函数复杂度排名
- 安全漏洞预警

### 重构建议
- 可自动化重构的代码清单
- 人工审查清单
- 改进前后代码对比

### 数据可视化
- 复杂度热力图（按模块）
- 代码异味分布图
- 重构收益分析图

## 使用建议

1. **优先级排序**：先关注高风险模块（从 evolution 阶段识别）
2. **增量扫描**：定期运行扫描，监控代码质量趋势
3. **自动化集成**：将扫描集成到 CI/CD 流程中
4. **人工审查**：LibCST 检测结果需与人工审查相结合

## 典型应用场景

### 场景 1：检测异步同步混用
```python
# 在 Django 视图中使用了同步 I/O（问题代码）
def my_view(request):
    result = db.query()  # ❌ 同步阻塞
    return JsonResponse(result)

# 修复建议
async def my_view(request):
    result = await db.query()  # ✅ 异步操作
    return JsonResponse(result)
```

### 场景 2：字符串格式化升级
```python
# 旧式格式化
message = "User {} logged in at {}".format(username, timestamp)

# 升级后（自动转换）
message = f"User {username} logged in at {timestamp}"
```

## 参考资源

- [LibCST 官方文档](https://libcst.readthedocs.io/)
- [flake8 官方文档](https://flake8.pycqa.org/)
- [bandit 官方文档](https://bandit.readthedocs.io/)
- [radon 官方文档](https://radon.readthedocs.io/)

## 注意事项

- LibCST 性能：大型代码库分析可能耗时较长，建议分块处理
- 规则定制：根据 MaxKB 的编码规范调整检测规则
- 结果审查：自动检测可能存在误报，需要人工复核关键发现
