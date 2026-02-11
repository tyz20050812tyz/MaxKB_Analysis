# Analyze/z3_verification/models/permission_model.py
from z3 import *

def define_permission_model():
    """定义 MaxKB 权限系统的基础 Z3 模型实体"""
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
