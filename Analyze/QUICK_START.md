# 快速开始指南

## 环境设置

```bash
# 1. 进入项目目录
cd d:\佟雨泽\大三上\开源软件基础\MaxKB_Analysis\Analyze

# 2. 创建虚拟环境
python -m venv venv
venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt
```

---

## 第一阶段：仓库演化分析

### 1.1 采集 Commit 数据

```bash
# 基础用法
python evolution/scripts/fetch_commits.py \
  --repo-path "../../源代码" \
  --output-file "evolution/data/commits.json"

# 指定时间范围
python evolution/scripts/fetch_commits.py \
  --repo-path "../../源代码" \
  --since "2023-01-01" \
  --until "2024-12-31" \
  --filter-bots true
```

**输出文件**：
- `evolution/data/commits.json` - Commit 数据
- `evolution/data/commits_summary.json` - 数据摘要

---

### 1.2 分析贡献者

```bash
python evolution/scripts/analyze_contributors.py \
  --input-file "evolution/data/commits.json" \
  --output-dir "evolution/results" \
  --recent-months 6
```

**输出文件**：
- `evolution/results/contributors_analysis.json` - 详细分析
- `evolution/results/contributors_ranking.csv` - 排名表（Excel 可用）
- `evolution/results/visualization_data.json` - 图表数据

---

## 第二阶段：静态代码分析

### 2.1 检测代码异味

```bash
# 扫描整个目录
python static/code_smell_detector.py \
  --path "../../源代码/apps" \
  --output "static/results/code_smells.json"

# 扫描单个文件
python static/code_smell_detector.py \
  --path "../../源代码/apps/application/views.py" \
  --output "static/results/single_file_smells.json"
```

**输出文件**：
- `static/results/code_smells.json` - 代码异味报告

**检测内容**：
- ❌ 异步/同步混用（async 中使用 time.sleep）
- ❌ 阻塞式 I/O（async 中使用 requests）
- ⚠️ 命名规范问题（函数名应为 snake_case）
- ⚠️ 过于宽泛的异常捕获（except:）

---

## 第三阶段：模糊测试

### 3.1 API 模糊测试

```bash
# 启动 MaxKB 服务
# 在另一个终端：python manage.py runserver 0.0.0.0:8000

# 运行 API Fuzzer
python fuzzing/api_fuzzer.py \
  --base-url "http://localhost:8000" \
  --token "your_token_here" \
  --iterations 20 \
  --output "fuzzing/results/fuzzer_report.json"
```

**测试项目**：
- 知识库创建 API（边界值、NULL、超长字符串）
- 搜索 API（SQL 注入、超大查询）
- 文件上传 API（畸形文件、路径遍历）
- 认证绕过（无 Token、伪造 Token）

**输出文件**：
- `fuzzing/results/fuzzer_report.json` - 详细报告

---

## 第四阶段：形式化验证

### 4.1 权限模型验证

```bash
python z3_verification/permission_verification.py \
  --verify-permissions \
  --verify-rag \
  --output "z3_verification/results/verification_report.json"
```

**验证项目**：
- ✓ 权限模型一致性
- ✓ 禁止权限提升漏洞
- ✓ 禁止跨租户访问
- ✓ RAG 检索逻辑正确性

**输出文件**：
- `z3_verification/results/verification_report.json` - 验证报告

---

## 完整执行流程（一键运行）

```bash
#!/bin/bash

echo "🚀 开始完整分析..."

# 第一阶段
echo "【第一阶段】采集并分析 Commit 数据..."
python evolution/scripts/fetch_commits.py --repo-path "../../源代码"
python evolution/scripts/analyze_contributors.py

# 第二阶段
echo "【第二阶段】静态代码分析..."
python static/code_smell_detector.py --path "../../源代码/apps"

# 第三阶段
echo "【第三阶段】API 模糊测试..."
echo "⚠️  请先启动 MaxKB 服务！"
python fuzzing/api_fuzzer.py --base-url "http://localhost:8000" --iterations 10

# 第四阶段
echo "【第四阶段】形式化验证..."
python z3_verification/permission_verification.py

echo "✅ 所有分析完成！"
```

---

## 文件结构说明

```
evolution/
├── scripts/
│   ├── fetch_commits.py          # 采集 Commit 数据
│   ├── analyze_contributors.py   # 贡献者分析
│   ├── fetch_issues.py          # GitHub Issue 采集（待实现）
│   └── analyze_modules.py       # 模块稳定性分析（待实现）
├── data/
│   ├── commits.json             # Commit 原始数据
│   └── commits_summary.json     # 摘要
└── results/
    ├── contributors_analysis.json
    ├── contributors_ranking.csv
    └── visualization_data.json

static/
├── code_smell_detector.py        # 代码异味检测
├── visitors/                     # Visitor 脚本（待补充）
├── transformers/                 # Transformer 脚本（待补充）
├── analyzers/                    # 分析器（待补充）
└── results/
    └── code_smells.json

fuzzing/
├── api_fuzzer.py                 # API Fuzzer
├── file_fuzzers/                 # 文件 Fuzzer（待实现）
├── test_data/                    # 测试数据
└── results/
    └── fuzzer_report.json

z3_verification/
├── permission_verification.py    # 权限模型验证
└── results/
    └── verification_report.json
```

---

## 常见问题

### Q: PyDriller 报错 "repository not found"
**A**: 确保 `--repo-path` 指向一个真实的 Git 仓库路径

### Q: GitHub API 速率限制
**A**: 使用 Token 提高限制（5000/小时）
```bash
export GITHUB_TOKEN=your_personal_access_token
```

### Q: libcst 解析错误
**A**: 确保是有效的 Python 文件，可以尝试：
```python
python -m py_compile your_file.py
```

### Q: Z3 求解超时
**A**: 对于大型模型，设置超时：
```python
solver.set('timeout', 10000)  # 10 秒
```

---

## 预期产出

执行完整流程后，应该得到：

1. **evolution/** 
   - ✅ 贡献者排名和活跃度分析
   - ✅ Gini 系数（集中度）
   - ✅ 可视化数据

2. **static/**
   - ✅ 代码异味清单
   - ✅ 复杂度报告
   - ✅ 安全问题列表

3. **fuzzing/**
   - ✅ API 测试报告
   - ✅ 发现的漏洞列表
   - ✅ 崩溃日志

4. **z3_verification/**
   - ✅ 权限模型验证结果
   - ✅ RAG 逻辑验证结果

---

## 下一步

- [ ] 根据第一阶段识别的热点模块，加强第二阶段分析
- [ ] 根据第二阶段发现的异味，编写修复脚本
- [ ] 根据第三阶段发现的 Bug，提交 GitHub Issue
- [ ] 整理所有结果为毕业设计论文

---

**最后更新**：2026 年 2 月 11 日
