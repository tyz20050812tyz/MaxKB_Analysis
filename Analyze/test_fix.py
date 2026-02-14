#!/usr/bin/env python3
"""测试 PyDriller API 兼容性"""

try:
    from pydriller import Repository
    print("✅ PyDriller 导入成功")
    
    # 测试不同参数组合
    repo_path = "../源代码"
    
    print("测试 Repository 初始化...")
    
    # 测试1: 无参数
    try:
        repo = Repository(repo_path)
        print("✅ 无参数初始化成功")
    except Exception as e:
        print(f"❌ 无参数初始化失败: {e}")
    
    # 测试2: 只有 since
    try:
        repo = Repository(repo_path, since="2023-01-01")
        print("✅ since 参数初始化成功")
    except Exception as e:
        print(f"❌ since 参数初始化失败: {e}")
    
    # 测试3: since 和 to
    try:
        repo = Repository(repo_path, since="2023-01-01", to="2024-01-01")
        print("✅ since+to 参数初始化成功")
    except Exception as e:
        print(f"❌ since+to 参数初始化失败: {e}")
        
    print("API 测试完成!")
    
except ImportError as e:
    print(f"❌ 导入失败: {e}")
except Exception as e:
    print(f"❌ 其他错误: {e}")