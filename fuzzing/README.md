# MaxKB Fuzzing 测试套件

## 目录结构
```
fuzzing/
├── run_all.py                  # 一键运行所有测试
├── file_fuzzers/
│   ├── malformed_generator.py  # 畸形文件生成器 (PDF/Excel/MD/TXT/HTML/DOCX)
│   ├── pdf_fuzzer.py           # 文件上传Fuzzer (含端点自动探测)
│   └── hypothesis_fuzzer.py    # Hypothesis 属性测试
├── api_fuzzers/
│   └── knowledge_base_fuzzer.py # API安全测试 (SQL注入/XSS/未授权/边界值/IDOR)
├── results/                     # 测试报告输出目录
├── malformed_files/             # 生成的畸形文件
└── github_issues/               # Bug截图和Issue记录
```

## 快速运行

### 一键运行全部测试
```bash
cd fuzzing

python run_all.py \
    --base-url http://localhost:8080 \
    --token "Bearer eyJ1c2VybmFtZSI6ImFkbWluIiwiaWQiOiJmMGRkOGY3MS1lNGVlLTExZWUtOGM4NC1hOGExNTk1ODAxYWIiLCJlbWFpbCI6IiIsInR5cGUiOiJTWVNURU1fVVNFUiJ9:1vrWMe:r1qKUUPDpCocaOJT78b9OHuuw1lTL4DJJHDLa5mliFw" \
    --dataset-id "019c602a-3304-75c1-b450-743949461c6b"
```

### 分步运行

**步骤1: 生成畸形文件**
```bash
cd fuzzing/file_fuzzers
python malformed_generator.py
```

**步骤2: 文件上传Fuzzing**
```bash
python pdf_fuzzer.py \
    --base-url http://localhost:8080 \
    --token "Bearer eyJ..." \
    --dataset-id "019c602a-3304-75c1-b450-743949461c6b"
```

**步骤3: API安全测试**
```bash
cd ../api_fuzzers
python knowledge_base_fuzzer.py \
    --base-url http://localhost:8080 \
    --token "Bearer eyJ..." \
    --dataset-id "019c602a-3304-75c1-b450-743949461c6b"
```

**步骤4: Hypothesis属性测试**
```bash
cd ../file_fuzzers
python hypothesis_fuzzer.py \
    --base-url http://localhost:8080 \
    --token "Bearer eyJ..."
```

## 输出报告
- `results/file_fuzzing_report.json` - 文件上传测试报告
- `results/api_fuzzing_report.json` - API安全测试报告
- `results/hypothesis_fuzzing_report.json` - 属性测试报告

## 测试覆盖

| 类别 | 测试项 | 数量 |
|------|--------|------|
| 文件Fuzzing | PDF/XLSX/MD/TXT/HTML/DOCX 畸形文件 | ~32个文件 |
| SQL注入 | GET参数/POST body 注入 | ~33个用例 |
| XSS注入 | 名称/描述/模板注入 | ~22个用例 |
| 未授权访问 | 无Token/无效Token/篡改Token | ~24个用例 |
| 边界值 | 超长输入/特殊字符/无效ID/异常请求体 | ~34个用例 |
| IDOR | 随机UUID/递增ID/用户枚举 | ~28个用例 |
| 属性测试 | Hypothesis随机生成 | ~140个用例 |

## 注意事项
- Token 可能会过期，如果收到401错误，请重新登录MaxKB获取新Token
- 测试间有1秒间隔，避免过载测试环境
- 即使未发现500错误，4xx响应也有分析价值
