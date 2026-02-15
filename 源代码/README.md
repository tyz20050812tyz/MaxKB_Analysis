# MaxKB 源代码分析副本

<div align="center">

[![MaxKB](https://img.shields.io/badge/project-MaxKB-blue.svg)](https://github.com/1Panel-dev/MaxKB)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](#)
[![License](https://img.shields.io/badge/license-GPL--3.0-orange.svg)](https://github.com/1Panel-dev/MaxKB/blob/main/LICENSE)

</div>

## 📋 项目概述

这是 [MaxKB](https://github.com/1Panel-dev/MaxKB) 开源项目的完整源代码副本，专门用于 MaxKB_Analysis 分析框架的研究和测试。MaxKB 是一个强大的企业级智能体平台，集成了检索增强生成(RAG)管道、稳健的工作流和先进的MCP工具使用能力。

## 🎯 项目特色

### 核心功能
- **🧠 RAG Pipeline**：支持直接上传文档/自动爬取在线文档，具备自动文本分割、向量化功能
- **⚡ Agentic Workflow**：配备强大的工作流引擎、函数库和MCP工具使用能力
- **🔗 Seamless Integration**：零编码快速集成到第三方业务系统
- **🔄 Model-Agnostic**：支持各种大模型，包括私有模型和公共模型
- **🎨 Multi Modal**：原生支持文本、图像、音频和视频输入输出

### 技术架构
- **前端**：[Vue.js](https://vuejs.org/) - 现代化用户界面
- **后端**：[Python/Django](https://www.djangoproject.com/) - 稳健的服务端框架
- **LLM框架**：[LangChain](https://www.langchain.com/) - 强大的语言模型集成
- **数据库**：[PostgreSQL + pgvector](https://www.postgresql.org/) - 高性能向量数据库

## 📁 目录结构

```
源代码/
├── apps/                              # Django 应用模块
│   ├── application/                   # 应用管理模块
│   │   ├── chat_pipeline/             # 对话处理管道
│   │   ├── flow/                      # 工作流引擎
│   │   ├── models/                    # 数据模型定义
│   │   └── views/                     # 视图控制器
│   ├── dataset/                       # 数据集管理
│   │   ├── models/                    # 数据集模型
│   │   ├── views/                     # 数据集接口
│   │   └── task/                      # 异步任务处理
│   ├── embedding/                     # 向量嵌入模块
│   │   ├── models/                    # 嵌入模型
│   │   ├── vector/                    # 向量计算
│   │   └── task/                      # 嵌入任务
│   ├── users/                         # 用户管理系统
│   │   ├── models/                    # 用户模型
│   │   ├── views/                     # 用户接口
│   │   └── serializers/               # 序列化器
│   └── common/                        # 通用工具模块
│       ├── auth/                      # 认证授权
│       ├── cache/                     # 缓存管理
│       ├── chunk/                     # 文本分块
│       └── util/                      # 工具函数
├── ui/                                # Vue 前端代码
│   ├── src/                           # 前端源码
│   │   ├── components/                # 组件库
│   │   ├── views/                     # 页面视图
│   │   ├── store/                     # 状态管理
│   │   └── router/                    # 路由配置
│   ├── public/                        # 静态资源
│   └── package.json                   # 前端依赖
├── installer/                         # 部署安装脚本
│   ├── Dockerfile                     # Docker 镜像构建
│   ├── config.yaml                    # 配置文件模板
│   ├── init.sql                       # 数据库初始化
│   └── run-maxkb.sh                   # 启动脚本
├── main.py                            # 应用入口文件
├── pyproject.toml                     # Python 项目配置
├── requirements.txt                   # Python 依赖列表
└── README.md                          # 本文档
```

## 🚀 开发环境搭建

### 后端环境配置

```bash
# 1. 创建虚拟环境
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 数据库配置
# 创建 PostgreSQL 数据库
createdb maxkb_dev

# 初始化数据库
python manage.py migrate

# 4. 启动开发服务器
python manage.py runserver 0.0.0.0:8000
```

### 前端环境配置

```bash
# 1. 进入前端目录
cd ui

# 2. 安装依赖
npm install

# 3. 启动开发服务器
npm run dev

# 4. 构建生产版本
npm run build
```

### Docker 部署（推荐）

```bash
# 使用提供的 Dockerfile
docker build -t maxkb-analysis .

# 运行容器
docker run -d \
  --name maxkb \
  -p 8080:8080 \
  -v ~/.maxkb:/var/lib/postgresql/data \
  maxkb-analysis
```

## 🔧 配置说明

### 环境变量配置

```bash
# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/maxkb

# Redis 配置（可选）
REDIS_URL=redis://localhost:6379/0

# API 密钥配置
OPENAI_API_KEY=your_openai_key
QWEN_API_KEY=your_qwen_key

# 安全配置
SECRET_KEY=your_secret_key_here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 配置文件模板

```yaml
# config.yaml
database:
  host: localhost
  port: 5432
  name: maxkb
  user: postgres
  password: password

redis:
  host: localhost
  port: 6379
  db: 0

llm:
  default_model: qwen-plus
  api_timeout: 30
  max_tokens: 2048

embedding:
  model: text-embedding-ada-002
  dimensions: 1536
```

## 🧪 测试与质量保证

### 运行测试

```bash
# 后端测试
python manage.py test

# 前端测试
cd ui && npm run test:unit

# 集成测试
python -m pytest tests/integration/
```

### 代码质量检查

```bash
# 代码风格检查
flake8 apps/

# 类型检查
mypy apps/

# 安全扫描
bandit -r apps/

# 复杂度分析
radon cc apps/
```

## 📊 API 文档

### 主要 API 端点

```bash
# 知识库管理
POST   /api/knowledge-base/           # 创建知识库
GET    /api/knowledge-base/{id}/      # 获取知识库详情
PUT    /api/knowledge-base/{id}/      # 更新知识库
DELETE /api/knowledge-base/{id}/      # 删除知识库

# 文档管理
POST   /api/documents/upload/         # 上传文档
GET    /api/documents/{id}/           # 获取文档
POST   /api/documents/{id}/process/   # 处理文档

# 对话接口
POST   /api/chat/                     # 发起对话
GET    /api/chat/history/             # 获取对话历史

# 用户管理
POST   /api/users/register/           # 用户注册
POST   /api/users/login/              # 用户登录
GET    /api/users/profile/            # 用户信息
```

### API 使用示例

```python
import requests

# 基础配置
BASE_URL = "http://localhost:8000"
HEADERS = {"Authorization": "Bearer your_token"}

# 创建知识库
response = requests.post(
    f"{BASE_URL}/api/knowledge-base/",
    json={
        "name": "测试知识库",
        "description": "用于测试的知识库",
        "visibility": "private"
    },
    headers=HEADERS
)

print(response.json())
```

## 🔒 安全考虑

### 认证与授权

```python
# JWT Token 验证示例
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

class SecureAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # 只有认证用户可以访问
        return Response({"message": "安全访问"})
```

### 输入验证

```python
# 数据验证示例
from rest_framework import serializers

class DocumentUploadSerializer(serializers.Serializer):
    file = serializers.FileField(
        validators=[validate_file_extension, validate_file_size]
    )
    knowledge_base_id = serializers.IntegerField(min_value=1)
```

## 📈 性能优化

### 数据库优化

```sql
-- 创建索引优化查询性能
CREATE INDEX idx_documents_knowledge_base ON documents(knowledge_base_id);
CREATE INDEX idx_chat_sessions_user ON chat_sessions(user_id);

-- 分区表处理大数据量
CREATE TABLE documents_2024 PARTITION OF documents
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

### 缓存策略

```python
from django.core.cache import cache

# 缓存热门查询结果
def get_popular_knowledge_bases():
    cache_key = "popular_kbs"
    result = cache.get(cache_key)
    
    if result is None:
        result = KnowledgeBase.objects.filter(is_popular=True)
        cache.set(cache_key, result, timeout=3600)  # 缓存1小时
    
    return result
```

## 🤝 贡献指南

### 开发流程

1. **Fork 项目** → 2. **创建分支** → 3. **开发功能** → 4. **提交PR**

### 代码规范

```bash
# 遵循 PEP 8 标准
# 使用类型注解
# 编写单元测试
# 更新相关文档
```

### 分支命名规范

```bash
feature/user-authentication    # 新功能开发
fix/document-processing-bug    # Bug 修复
docs/api-documentation         # 文档更新
refactor/database-optimization # 代码重构
```

## 📚 学习资源

### 官方文档
- [MaxKB 官方文档](https://maxkb.cn/docs/)
- [Django 官方文档](https://docs.djangoproject.com/)
- [Vue.js 官方文档](https://vuejs.org/guide/)
- [PostgreSQL 文档](https://www.postgresql.org/docs/)

### 技术博客
- [RAG 技术实践](https://maxkb.cn/blog/rag-practice)
- [向量数据库优化](https://maxkb.cn/blog/vector-db-optimization)
- [微服务架构设计](https://maxkb.cn/blog/microservices-architecture)

## 📞 技术支持

### 获取帮助

- **GitHub Issues**：提交问题和功能请求
- **官方论坛**：参与技术讨论
- **微信群**：扫码加入开发者群
- **邮箱支持**：support@maxkb.cn

### 社区资源

- [GitHub 仓库](https://github.com/1Panel-dev/MaxKB)
- [Gitee 镜像](https://gitee.com/1Panel/MaxKB)
- [Docker Hub](https://hub.docker.com/r/1panel/maxkb)

## 📄 许可证

本项目采用 GNU General Public License v3.0 许可证。详情请参见 [LICENSE](LICENSE) 文件。

---

<div align="center">

**🌟 MaxKB - 让知识更有价值！**

[![GitHub stars](https://img.shields.io/github/stars/1Panel-dev/MaxKB?style=social)](https://github.com/1Panel-dev/MaxKB)
[![Docker pulls](https://img.shields.io/docker/pulls/1panel/maxkb)](https://hub.docker.com/r/1panel/maxkb)

</div>