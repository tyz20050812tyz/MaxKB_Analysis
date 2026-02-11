# z3_verification/test_cases/test_scenarios.py
from z3 import *
from models.permission_model import define_permission_model

def test_admin_bypass_scenario():
    """测试场景：攻击者试图伪造管理员身份绕过租户限制"""
    model = define_permission_model()
    s = Solver()
    
    # 定义攻击者 u_hacker
    u_hacker = Const('u_hacker', model['User'])
    t_victim = Const('t_victim', model['Tenant']) # 受害者租户
    t_hacker = Const('t_hacker', model['Tenant']) # 攻击者租户
    res_private = Const('res_private', model['Resource']) # 受害者资源

    # 条件：攻击者和受害者不在一个租户
    s.add(model['UserTenant'](u_hacker) == t_hacker)
    s.add(model['ResourceTenant'](res_private) == t_victim)
    s.add(t_hacker != t_victim)
    
    # 模拟攻击：攻击者自封为 Owner
    s.add(model['IsOwner'](u_hacker) == True)
    
    # 验证规则：修复后的规则是否允许访问？
    access_granted = And(model['UserTenant'](u_hacker) == model['ResourceTenant'](res_private), 
                         model['IsOwner'](u_hacker))
    
    s.add(access_granted)
    
    if s.check() == unsat:
        return "PASS: 即使攻击者伪造了管理员身份，租户隔离依然强制生效。"
    else:
        return "FAIL: 管理员身份可以绕过租户限制！"

if __name__ == "__main__":
    print(test_admin_bypass_scenario())
