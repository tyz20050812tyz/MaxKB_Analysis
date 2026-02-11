# 提交规范（Analyze 目录）

本文件为 `Analyze` 目录下代码与文档的提交规范，旨在保持提交历史清晰、可追溯，并提高代码审查效率。

## 目的
- 统一提交信息格式，便于自动化变更日志生成与审计。
- 帮助评审者快速理解变更意图与影响范围。

## 提交信息格式
建议使用如下格式：

```
<type>(<scope>): <简短描述>

可选的详细说明（wrap 在 72 个字符），说明为什么修改、设计考虑、替代方案等。

Footer: 关联 issue 或 破坏性变更说明（例如：Closes #123）
```

- type：变更类型，常用值：
  - feat: 新增功能/分析脚本
  - fix: 修复 bug
  - docs: 文档变更
  - style: 代码风格（不影响逻辑）
  - refactor: 重构（不新增功能、修复 bug）
  - perf: 性能优化
  - test: 添加或调整测试
  - chore: 构建/工具/依赖变更
- scope：变更影响的模块或子目录，例如 `pipeline`, `scripts`, `reports`。对 `Analyze` 全局的改动可写 `Analyze`。
- 简短描述：一句话说明变更，限制在 50 个字符以内，首字母小写，不以句号结尾。
- 详细说明：解释为什么做此更改，列出重要实现细节与兼容性注意点，必要时给出示例、命令或配置项。
- Footer：用于列出关联 issue、BREAKING CHANGE 等。

示例：

```
feat(pipeline): 支持并行处理多个数据源

增加了基于线程池的并行处理逻辑以提高处理速度。测试覆盖并发场景，配置项为 `MAX_WORKERS`。

Closes #456
```

## 分支命名
- 功能分支：`feat/analyze-<简短描述>`
- 修复分支：`fix/analyze-<简短描述>`
- 文档分支：`docs/analyze-<简短描述>`
- 示例：`feat/analyze-parallel-sources`。

## PR 标题与描述
- PR 标题应与主要提交保持一致，使用 `type(scope): summary` 格式。
- PR 描述应包含：变更摘要、动机、主要实现点、影响范围、回归风险、如何测试（包含必要命令）、关联 issue。

## 提交前检查清单（必须）
- 运行并通过相关测试（如果有）：例如 `pytest` 或自定义脚本。
- 格式化代码并通过 linter（若项目有配置）。
- 确认没有将敏感信息提交（密钥、凭证等）。
- 更新相关文档/README（如接口、配置、使用方法发生变化）。
- 在提交消息或 PR 中关联对应的 issue（若有）。

## 提交实践与约定
- 小而频繁的提交优于一次性大提交。
- 每个提交应关注单一目的（修复一个 bug、增加一个小功能等）。
- 对于需要逐步审查的大改动，请考虑拆分为多个 PR。
- 主分支（`main`/`master`）上不直接提交，所有改动通过 PR 合并并要求至少一名审阅者通过。

## 关于破坏性变更
- 若变更包含破坏性 API/接口修改，必须在提交或 PR footer 中标注 `BREAKING CHANGE: <描述>` 并在 PR 描述中详述迁移步骤。

## 提交命令示例
```
git add path/to/file
git commit -m "feat(pipeline): 支持并行处理多个数据源"
git push origin feat/analyze-parallel-sources
```

## 复现与测试说明（如果适用）
在 PR 中请提供能重现变更验证的最小步骤或命令示例，例如：

```
python Analyze/scripts/run_analysis.py --input tests/data/sample.csv --workers 4
```

## 其他建议
- 提交正文尽量写清楚“为什么”而非仅描述“做了什么”。
- 对于数据或模型影响的变更，注明是否需要迁移或重新生成数据/索引。

---

谢谢使用本规范。如需调整或补充，请发起 PR 修改本文件。
