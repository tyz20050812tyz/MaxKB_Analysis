# z3_verification/models/rag_logic_model.py
from z3 import *

def define_rag_model():
    """定义 RAG 检索逻辑的 Z3 模型"""
    Doc = DeclareSort('Document')
    KB = DeclareSort('KnowledgeBase')
    User = DeclareSort('User')
    
    # 文档属于知识库
    DocInKB = Function('DocInKB', Doc, KB)
    # 用户对知识库有权限
    UserHasKBPermission = Function('UserHasKBPermission', User, KB, BoolSort())
    # 文档是否包含敏感词
    IsSensitive = Function('IsSensitive', Doc, BoolSort())
    
    return {
        'Doc': Doc, 'KB': KB, 'User': User,
        'DocInKB': DocInKB, 
        'UserHasKBPermission': UserHasKBPermission,
        'IsSensitive': IsSensitive
    }
