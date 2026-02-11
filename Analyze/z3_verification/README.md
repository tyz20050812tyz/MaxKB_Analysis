# MaxKB 形式化验证模块 (Z3)

本模块利用 Microsoft Z3 定理证明器，对 MaxKB 系统中的关键安全逻辑进行数学建模和形式化验证。

## 🎯 验证目标
1.  **多租户隔离 (Multi-tenancy Isolation)**：证明在任何情况下，非本租户成员无法通过越权访问私有资源。
2.  **RAG 检索安全性 (RAG Logic Security)**：验证知识库检索过程中，召回的文档必须符合权限约束，防止敏感信息泄露。

## 🏗 目录结构
- `models/`: 定义系统的逻辑实体（用户、租户、资源、知识库）和数学约束。
- `solvers/`: 验证脚本，执行具体的 SAT/UNSAT 求解。
- `test_cases/`: 具体的测试场景配置，用于模拟真实的攻击向量。
- `proofs/`: 存放验证生成的数学证明过程或结果截图。

## 🚀 如何运行
确保已安装 z3-solver:
`pip install z3-solver`

在 `z3_verification` 根目录下运行：
```bash
### 验证权限模型
python -m solvers.permission_verification

### 验证 RAG 逻辑
python -m solvers.rag_verification
```
## 📊 验证原理：
SAT (Satisfiable): 逻辑表达式有解。在验证中，如果发现漏洞攻击路径成立（有解），则说明存在安全风险。
UNSAT (Unsatisfiable): 逻辑表达式无解。在验证中，如果证明“攻击逻辑”在任何情况下都无法成立，则证明系统是数学级安全的。