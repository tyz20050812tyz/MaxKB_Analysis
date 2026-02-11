# evolution 模块 - 仓库演化与社区画像分析

## 模块简介

`evolution` 模块负责第一阶段的仓库演化与社区画像分析，通过数据层面深入挖掘 MaxKB 项目的发展轨迹和社区特征。

## 核心分析方向

### 1. 贡献者分布分析
- **目标**：分析 Commit 记录，绘制贡献者活跃度曲线
- **产出**：
  - 核心开发者识别
  - 社区代码控制模式分析（集中式 vs 去中心化）
  - 贡献者活跃度时间序列图表

### 2. 模块稳定性分析
- **目标**：统计不同模块（backend、frontend、ui 等）的修改频率
- **关键发现**：**频率最高的地方通常是 Bug 密集的"热点区域"**
- **产出**：
  - 模块修改热力图
  - 稳定性评分表
  - 风险区域预警

### 3. Issue 生命周期分析
- **目标**：爬取 GitHub Issue 数据，计算 Bug 从提出到关闭的平均时长
- **产出**：
  - 问题响应速度统计
  - 维护团队响应效率评分
  - 问题解决时间趋势图

## 依赖工具

| 工具 | 用途 |
|------|------|
| `PyDriller` | 高效 Git 仓库分析 |
| `GitPython` | Git 操作和 Commit 数据获取 |
| `Pandas` | 数据处理和分析 |
| `Matplotlib` / `Seaborn` | 数据可视化 |
| `requests` / `PyGithub` | GitHub API 调用 |

## 项目结构

```
evolution/
├── README.md                 # 本文件
├── scripts/                  # 数据采集脚本
│   ├── fetch_commits.py      # 获取 Commit 数据
│   ├── analyze_contributors.py  # 贡献者分析
│   ├── fetch_issues.py       # GitHub Issue 爬取
│   └── analyze_modules.py    # 模块稳定性分析
├── data/                     # 原始数据存储
│   ├── commits.json          # Commit 记录
│   ├── contributors.json     # 贡献者信息
│   └── issues.json           # Issue 数据
└── reports/                  # 分析报告和图表
    ├── contributors_chart.png
    ├── module_heatmap.png
    └── issue_lifecycle.png
```

## 快速开始

### 环境配置

```bash
# 安装依赖
pip install PyDriller GitPython pandas matplotlib seaborn PyGithub

# 配置 GitHub Token（可选，用于提高 API 速率限制）
export GITHUB_TOKEN=your_token_here
```

### 运行数据采集

```bash
# 采集 Commit 数据
python scripts/fetch_commits.py --repo https://github.com/1Panel-dev/MaxKB

# 分析贡献者
python scripts/analyze_contributors.py

# 爬取 GitHub Issues
python scripts/fetch_issues.py --repo 1Panel-dev/MaxKB

# 模块稳定性分析
python scripts/analyze_modules.py
```

## 主要产出

### 可视化图表
- 贡献者活跃度时间序列图
- 模块修改频率热力图
- Issue 解决时间分布直方图

### 数据报告
- 核心贡献者排名
- 高风险模块识别
- 社区维护效率评分

## 使用建议

1. **数据更新频率**：建议每月更新一次数据，追踪项目最新进展
2. **关键指标监控**：重点关注热点模块，为后续静态分析和模糊测试指明方向
3. **社区对标**：与同类项目（如 LangChain、RAGFlow）的社区指标进行对比

## 参考资源

- [PyDriller 官方文档](https://pydriller.readthedocs.io/)
- [PyGithub 官方文档](https://pygithub.readthedocs.io/)
- [MaxKB GitHub 仓库](https://github.com/1Panel-dev/MaxKB)

## 注意事项

- GitHub API 速率限制：未认证请求 60 次/小时，认证请求 5000 次/小时
- 大型仓库数据采集可能耗时较长，建议在后台运行
- 数据文件应定期备份，避免重复采集
