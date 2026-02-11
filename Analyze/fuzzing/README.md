# fuzzing 模块 - 动态分析与模糊测试

## 模块简介

`fuzzing` 模块负责第三阶段的动态分析与模糊测试工作，通过构造边界情况和随机输入来探测 MaxKB 的鲁棒性和安全性问题。这是**最容易通过发现真实 Bug 获得加分**的环节，发现的 Bug 可直接提交 GitHub Issue。

## 核心分析方向

### 1. 文件解析测试（File Parsing Fuzzing）
- **目标**：测试 MaxKB 支持的各种文件格式的解析鲁棒性
- **支持格式**：PDF、Markdown、Excel、Word、TXT
- **测试策略**：
  - 构造畸形文件（错误的文件头、损坏的内容）
  - 超大文件测试（内存溢出风险）
  - 特殊字符和编码测试（Unicode、BOM 等）
  - 递归结构测试（嵌套的表格、列表）
- **风险指标**：
  - 服务崩溃（500 错误）
  - 内存泄漏
  - 无限循环
- **产出**：Bug 报告、复现脚本、补丁建议

### 2. API 随机压力测试（API Fuzzing）
- **目标**：针对关键 API 进行随机参数探测
- **测试对象**：
  - Knowledge Base 创建/检索 API
  - 文档上传 API
  - 搜索/检索 API
  - 权限管理 API
- **测试策型**：
  - 边界值测试（NULL、空字符串、极限值）
  - 类型混淆（字符串传整数、列表传对象）
  - SQL 注入/XSS 测试
  - 未授权访问测试
  - 权限越权测试
- **产出**：安全漏洞清单、漏洞重现脚本

### 3. 状态机测试（State Machine Testing）
- **目标**：测试 MaxKB 的多步骤工作流
- **关键工作流**：
  - 知识库创建→文档上传→索引→搜索→删除
  - 用户登录→权限设置→资源访问→退出登录
- **产出**：状态转移缺陷、边界情况发现

## 依赖工具

| 工具 | 用途 |
|------|------|
| `Atheris` | Python 原生 Fuzzer（基于 libFuzzer）|
| `Hypothesis` | 属性式测试框架 |
| `Requests` | HTTP 客户端库 |
| `Faker` | 随机数据生成 |
| `Locust` | 压力测试工具 |

## 项目结构

```
fuzzing/
├── README.md                          # 本文件
├── file_fuzzers/                      # 文件解析 Fuzzer
│   ├── __init__.py
│   ├── pdf_fuzzer.py                  # PDF 文件 Fuzzer
│   ├── markdown_fuzzer.py             # Markdown 文件 Fuzzer
│   ├── excel_fuzzer.py                # Excel 文件 Fuzzer
│   └── malformed_generator.py         # 畸形文件生成器
├── api_fuzzers/                       # API Fuzzer
│   ├── __init__.py
│   ├── knowledge_base_fuzzer.py       # 知识库 API Fuzzer
│   ├── document_upload_fuzzer.py      # 文档上传 API Fuzzer
│   ├── search_fuzzer.py               # 搜索 API Fuzzer
│   └── auth_fuzzer.py                 # 认证/权限 API Fuzzer
├── test_cases/                        # 测试用例集合
│   ├── file_test_cases.py             # 文件测试用例
│   ├── api_test_cases.py              # API 测试用例
│   └── workflow_test_cases.py         # 工作流测试用例
├── test_data/                         # 测试数据
│   ├── malformed_files/               # 畸形文件样本
│   │   ├── invalid.pdf
│   │   ├── corrupted.xlsx
│   │   └── broken.md
│   ├── payloads/                      # 注入测试 Payload
│   │   ├── sql_injection_payloads.txt
│   │   ├── xss_payloads.txt
│   │   └── authentication_bypass.txt
│   └── seeds/                         # Fuzzer 种子文件
├── results/                           # 测试结果
│   ├── crash_reports/                 # 崩溃报告
│   ├── vulnerability_reports.json     # 漏洞报告
│   ├── bug_reproduction_scripts/      # Bug 复现脚本
│   └── coverage_report.html           # 代码覆盖率报告
├── github_issues/                     # 提交的 GitHub Issues
│   └── issues_submitted.md            # Issue 提交记录（关键！）
└── tests/                             # 测试脚本单元测试
    ├── test_fuzzers.py
    └── test_generators.py
```

## 快速开始

### 环境配置

```bash
# 安装依赖
pip install atheris hypothesis requests faker locust

# 或使用 requirements.txt
pip install -r requirements.txt
```

### 运行文件解析 Fuzzer

```bash
# 1. PDF 文件 Fuzzing
python -m file_fuzzers.pdf_fuzzer --output-dir ./results --duration 300

# 2. Excel 文件 Fuzzing
python -m file_fuzzers.excel_fuzzer --output-dir ./results --duration 300

# 3. Markdown 文件 Fuzzing
python -m file_fuzzers.markdown_fuzzer --output-dir ./results --duration 300

# 4. 生成畸形文件进行手动上传测试
python malformed_generator.py --format pdf --count 10 --output-dir ./test_data/malformed_files
```

### 运行 API Fuzzer

```bash
# 1. 知识库 API Fuzzing（需要运行的 MaxKB 服务）
python -m api_fuzzers.knowledge_base_fuzzer --base-url http://localhost:8000 --duration 600

# 2. 文档上传 API Fuzzing
python -m api_fuzzers.document_upload_fuzzer --base-url http://localhost:8000 --file-dir ./test_data/malformed_files

# 3. 认证/权限 API Fuzzing（寻找越权漏洞）
python -m api_fuzzers.auth_fuzzer --base-url http://localhost:8000 --duration 300

# 4. 搜索 API Fuzzing
python -m api_fuzzers.search_fuzzer --base-url http://localhost:8000 --duration 600
```

### 运行端到端工作流测试

```bash
# 执行完整的工作流测试（创建→上传→索引→搜索）
python -m test_cases.workflow_test_cases --base-url http://localhost:8000 --iterations 100
```

### 压力测试

```bash
# 使用 Locust 进行并发压力测试
locust -f api_fuzzers/load_test.py --host http://localhost:8000 -u 100 -r 10 -t 5m
```

## 关键发现提交流程

### ⭐ 重要：Bug 提交最佳实践

发现 Bug 后，**立即在 GitHub 提交 Issue** 是获得加分的关键！

#### 步骤 1：复现 Bug

```python
# 在 bug_reproduction_scripts/ 目录创建复现脚本
# 脚本应该能完整复现问题

import requests
import json

# 例：重现知识库创建 API 的越权漏洞
def reproduce_kb_auth_bypass():
    """复现：低权限用户可以访问他人的知识库"""
    
    # 使用低权限账户 Token
    headers = {'Authorization': f'Bearer {LOW_PRIV_TOKEN}'}
    
    # 尝试访问其他用户的私密知识库
    response = requests.get(
        'http://localhost:8000/api/knowledge_base/private_kb_id/',
        headers=headers
    )
    
    # 预期：403 Forbidden，实际：200 OK（Bug！）
    assert response.status_code == 403, f"Expected 403, got {response.status_code}"
```

#### 步骤 2：记录 Issue 信息

```markdown
# Issue 模板

**标题**：[Security] 低权限用户可以绕过权限检查访问他人知识库

**类型**：Bug / Security Issue

**描述**：
在使用低权限账户访问他人知识库时，系统未进行正确的权限验证，导致越权访问。

**复现步骤**：
1. 使用低权限账户登录
2. 调用知识库检索 API（见附件脚本）
3. 观察能够访问他人的私密知识库

**预期行为**：
返回 403 Forbidden 错误

**实际行为**：
返回 200 OK，能够访问知识库内容

**环境**：
- MaxKB 版本：[版本号]
- Python 版本：3.10+
- 复现脚本：[见 bug_reproduction_scripts/]

**附件**：
- 复现脚本：bug_reproduction_scripts/auth_bypass_poc.py
- 详细日志：logs/issue_xxx.log
```

#### 步骤 3：提交到 GitHub

```bash
# 1. 在 MaxKB GitHub 仓库创建 Issue
# URL: https://github.com/1Panel-dev/MaxKB/issues/new

# 2. 附加复现脚本和日志文件
# 3. 设置标签：bug、security（如果是安全问题）

# 4. 在本地记录 Issue 链接
# 编辑 github_issues/issues_submitted.md
```

#### 步骤 4：记录提交信息

```markdown
# github_issues/issues_submitted.md

## 已提交 Issues 清单

| Issue ID | 标题 | 严重度 | 类型 | 链接 | 日期 |
|---------|------|-------|------|------|------|
| #123 | 低权限越权访问 | 高 | Security | [Link](https://github.com/1Panel-dev/MaxKB/issues/123) | 2024-12-15 |
| #124 | PDF 解析内存泄漏 | 中 | Bug | [Link](https://github.com/1Panel-dev/MaxKB/issues/124) | 2024-12-16 |
```

## 典型漏洞类型和测试策略

### 1. SQL 注入（SQL Injection）
```python
# 测试知识库搜索功能
payloads = [
    "' OR '1'='1",
    "'; DROP TABLE users; --",
    "admin'--",
]

for payload in payloads:
    response = requests.get(
        f'http://localhost:8000/api/search/?q={payload}',
        headers=headers
    )
    # 检查响应是否包含数据库错误信息
```

### 2. 越权访问（Unauthorized Access）
```python
# 使用不同用户 Token 访问同一资源
kb_id = 'shared_kb_123'

for user_token in [user1_token, user2_token, guest_token]:
    response = requests.get(
        f'http://localhost:8000/api/knowledge_base/{kb_id}/',
        headers={'Authorization': f'Bearer {user_token}'}
    )
    # 验证权限检查是否生效
```

### 3. 文件上传漏洞（File Upload Vulnerability）
```python
# 上传畸形文件
malformed_files = [
    ('large_file.pdf', create_large_pdf(1000)),  # 超大文件
    ('invalid.pdf', b'Not a PDF file'),  # 伪造内容
    ('script.pdf', b'<?php system($_GET["cmd"]); ?>'),  # 注入脚本
]

for filename, content in malformed_files:
    with open(filename, 'wb') as f:
        f.write(content)
    
    files = {'file': (filename, open(filename, 'rb'))}
    response = requests.post(
        'http://localhost:8000/api/upload/',
        files=files,
        headers=headers
    )
```

## 测试前准备

1. **部署测试环境**：在本地或测试服务器上运行 MaxKB
2. **创建测试账户**：多个权限级别的账户（Admin、User、Guest）
3. **记录基线**：测试前的系统状态、日志、内存占用
4. **监控工具**：准备 CPU、内存、网络监控工具

## 结果分析

### 关键指标

- **Crash 发现**：系统完全崩溃的次数
- **Memory Leak**：内存持续增长（泄漏风险）
- **Security Issues**：发现的安全漏洞数
- **Code Coverage**：Fuzzing 达到的代码覆盖率

### 优先级判断

| 严重度 | 条件 | 示例 |
|-------|------|------|
| 🔴 Critical | 服务崩溃、数据丢失、完全绕过认证 | 远程代码执行、完全越权 |
| 🟠 High | 功能异常、部分数据泄露 | 信息泄露、有限越权 |
| 🟡 Medium | 非关键功能异常 | 非关键 API 异常 |
| 🔵 Low | 边界情况、性能问题 | 特殊字符处理不当 |

## 参考资源

- [Atheris 官方文档](https://github.com/google/atheris)
- [Hypothesis 官方文档](https://hypothesis.readthedocs.io/)
- [OWASP 测试指南](https://owasp.org/www-project-web-security-testing-guide/)
- [CWE Top 25](https://cwe.mitre.org/top25/)

## 注意事项

- **法律合规**：仅在授权环境中测试，不对生产环境进行未授权测试
- **数据保护**：测试中使用虚拟数据，不包含真实用户信息
- **环境隔离**：使用独立的测试环境，防止污染生产数据
- **日志保存**：保存所有测试日志和崩溃转储，用于分析
