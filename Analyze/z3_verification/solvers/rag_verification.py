# z3_verification/solvers/rag_verification.py
from z3 import *
from models.rag_logic_model import define_rag_model

def verify_rag_leakage():
    print(">>> 正在验证 RAG 召回安全性...")
    model = define_rag_model()
    s = Solver()
    
    u = Const('u', model['User'])
    d = Const('d', model['Doc'])
    k = Const('k', model['KB'])
    
    # 场景：文档属于 KB，但用户没有该 KB 的权限
    s.add(model['DocInKB'](d) == k)
    s.add(model['UserHasKBPermission'](u, k) == False)
    
    # 漏洞逻辑：如果只检查文档相似度，不检查 KB 权限就返回
    vuln_retrieval = model['DocInKB'](d) == k # 只要在库里就召回
    
    s.add(vuln_retrieval)
    
    if s.check() == sat:
        print("结果: ❌ 发现 RAG 泄露风险！用户可以召回无权限知识库中的文档。")
    else:
        print("结果: ✅ RAG 检索逻辑安全。")

if __name__ == "__main__":
    verify_rag_leakage()
