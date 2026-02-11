import sys
import os
from z3 import *

# 路径处理
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from models.permission_model import define_permission_model
except ImportError:
    # 兼容性处理：如果还是导入失败，就地定义模型
    def define_permission_model():
        User = DeclareSort('User')
        Tenant = DeclareSort('Tenant')
        Resource = DeclareSort('Resource')
        UserTenant = Function('UserTenant', User, Tenant)
        ResourceTenant = Function('ResourceTenant', Resource, Tenant)
        IsOwner = Function('IsOwner', User, BoolSort())
        IsMember = Function('IsMember', User, BoolSort())
        return {
            'User': User, 'Tenant': Tenant, 'Resource': Resource,
            'UserTenant': UserTenant, 'ResourceTenant': ResourceTenant,
            'IsOwner': IsOwner, 'IsMember': IsMember
        }

def run_verification():
    print("==================================================")
    print("正在执行：MaxKB 权限模型形式化验证")
    print("目标：验证多租户隔离逻辑的安全性")
    print("==================================================\n")
    
    model = define_permission_model()
    s = Solver()

    # --- 修复后的变量定义 ---
    u1 = Const('u1', model['User'])
    t1, t2 = Consts('t1 t2', model['Tenant'])
    r1 = Const('r1', model['Resource'])
    # -----------------------

    # 场景设置
    s.add(model['UserTenant'](u1) == t1)
    s.add(model['ResourceTenant'](r1) == t2)
    s.add(t1 != t2)
    s.add(model['IsOwner'](u1) == True) 

    vulnerability_rule = Or(model['IsOwner'](u1), 
                            And(model['IsMember'](u1), model['UserTenant'](u1) == model['ResourceTenant'](r1)))

    print(">>> [测试 1] 验证原始逻辑 (多租户隔离)...")
    s.push()
    s.add(vulnerability_rule)
    if s.check() == sat:
        print("结果: ❌ 发现逻辑漏洞！Owner 可以跨租户访问资源。")
    else:
        print("结果: ✅ 安全。")
    s.pop()

    fixed_rule = And(model['UserTenant'](u1) == model['ResourceTenant'](r1),
                     Or(model['IsOwner'](u1), model['IsMember'](u1)))

    print("\n>>> [测试 2] 验证修复后的逻辑...")
    s.push()
    s.add(fixed_rule)
    if s.check() == sat:
        print("结果: ❌ 仍然存在漏洞。")
    else:
        print("结果: ✅ 验证通过！逻辑在数学上证明安全 (UNSAT)。")
    s.pop()
    print("\n==================================================")

if __name__ == "__main__":
    run_verification()
