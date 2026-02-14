# GitHub Commit 数据采集工具使用说明

## 功能介绍
这个脚本可以从 GitHub 仓库直接获取真实的 commit 历史数据，无需本地 Git 仓库。

## 基本用法

### 1. 最简单的方式（采集 MaxKB 官方仓库）
```bash
python fetch_commits.py
```

### 2. 指定其他 GitHub 仓库
```bash
python fetch_commits.py --repo-name "owner/repository"
```

### 3. 使用 GitHub Token（推荐）
```bash
python fetch_commits.py --github-token "your_github_token"
```

### 4. 限制时间范围
```bash
python fetch_commits.py --since "2023-01-01" --until "2024-01-01"
```

### 5. 限制获取数量
```bash
python fetch_commits.py --max-commits 500
```

## 获取 GitHub Token
1. 访问 GitHub Settings → Developer settings → Personal access tokens
2. 点击 "Generate new token"
3. 选择适当的权限（public_repo 即可）
4. 复制生成的 token

## 输出文件
- `data/github_commits.json` - 完整的 commit 数据
- `data/github_commits_summary.json` - 数据统计摘要

## 注意事项
- 未使用 token 时，GitHub API 有速率限制
- 建议对大型仓库使用 token 并限制获取数量
- 数据包含作者、提交时间、文件变更等详细信息