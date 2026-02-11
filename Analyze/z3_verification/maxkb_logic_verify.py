from z3 import *

def run_verification():
    # --- 1. 定义数学域 (Sorts) ---
    # 定义基本实体类型
    User = DeclareSort('User')
    Tenant = DeclareSort('Tenant')
    Resource = DeclareSort('Resource')
    
    # 定义角色枚举：Owner(所有者), Admin(管理员), Member(普通成员)
    Role = Datatype('Role')
    Role.declare('Owner')
    Role.declare('Admin')
    Role.declare('Member')
    Role = Role.create()

    # --- 2. 定义系统关系 (Functions) ---
    # 定义属性映射
    user_tenant = Function('user_tenant', User, Tenant)     # 用户所属租户
    res_tenant = Function('res_tenant', Resource, Tenant)   # 资源所属租户
    user_role = Function('user_role', User, Role)           # 用户的角色
    
    # 定义核心权限判定函数: can_access(user, resource)
    can_access = Function('can_access', User, Resource, BoolSort())

    # --- 3. 建立求解器 ---
    solver = Solver()

    # --- 4. 注入系统逻辑 (Constraints) ---
    u = Const('u', User)
    r = Const('r', Resource)

    # 【模拟 MaxKB 的逻辑实现】
    # 假设开发者写的逻辑如下（这里故意包含一个逻辑瑕疵）：
    # 如果用户是系统级 Owner，或者 用户与资源在同一个租户且是 Admin
    # Bug 点：Owner 应该是租户内的 Owner，但代码里没判断租户，导致 Owner 变成了“上帝视角”
    logic_expr = ForAll([u, r], can_access(u, r) == Or(
        user_role(u) == Role.Owner,  # 潜在 Bug：漏掉了租户一致性检查
        And(user_tenant(u) == res_tenant(r), user_role(u) == Role.Admin),
        And(user_tenant(u) == res_tenant(r), user_role(u) == Role.Member)
    ))
    solver.add(logic_expr)

    # --- 5. 定义安全属性 (The Security Policy) ---
    # 我们期望的安全属性是：绝对不允许跨租户访问 (Multi-tenancy Isolation)
    # 形式化表达：对于任意访问，用户租户必须等于资源租户
    # 我们让 Z3 去寻找“违反”这一属性的情况
    
    # 寻找一个反例 (Counter-example)：
    # 存在一个用户 u1 和 资源 r1，满足：
    # 1. 用户能访问资源
    # 2. 但用户和资源不属于同一个租户
    u1 = Const('u1', User)
    r1 = Const('r1', Resource)
    
    violation_condition = And(
        can_access(u1, r1),
        user_tenant(u1) != res_tenant(r1)
    )
    solver.add(violation_condition)

    # --- 6. 执行验证 ---
    print("正在进行 MaxKB 权限模型形式化验证...")
    result = solver.check()

    if result == sat:
        print("\n[结果]：验证未通过！发现潜在安全风险。")
        print("原因：在当前逻辑定义下，系统允许跨租户访问。")
        
        # 打印 Z3 找到的反例模型
        m = solver.model()
        print("\n--- 风险场景模拟 (Counter-example) ---")
        print(f"用户 U1 属性：")
        print(f"  - 所属租户: {m.evaluate(user_tenant(u1))}")
        print(f"  - 拥有角色: {m.evaluate(user_role(u1))}")
        print(f"资源 R1 属性：")
        print(f"  - 所属租户: {m.evaluate(res_tenant(r1))}")
        print(f"访问结果: {m.evaluate(can_access(u1, r1))}")
        print("\n分析：由于 Owner 角色缺乏租户约束，导致 T1 的 Owner 竟能访问 T2 的资源。")
    else:
        print("\n[结果]：验证通过！逻辑在数学层面是安全的。")

if __name__ == "__main__":
    run_verification()
