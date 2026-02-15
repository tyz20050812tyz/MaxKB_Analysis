# MaxKB 前端界面

<div align="center">

[![Vue.js](https://img.shields.io/badge/Vue.js-3.x-4FC08D.svg)](https://vuejs.org/)
[![Vite](https://img.shields.io/badge/Vite-4.x-646CFF.svg)](https://vitejs.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-4.x-3178C6.svg)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/license-GPL--3.0-blue.svg)](../../LICENSE)

</div>

## 📋 项目概述

MaxKB 前端界面基于现代 Web 技术栈构建，采用 Vue 3 + TypeScript + Vite 的组合，为用户提供直观、高效的智能知识库管理体验。界面设计注重用户体验，支持响应式布局，适配各种设备屏幕。

## 🎯 技术特性

### 核心技术栈
- **Vue 3 Composition API**：现代化的组件开发模式
- **TypeScript**：强类型支持，提升代码质量和开发体验
- **Vite**：极速的构建工具和开发服务器
- **Element Plus**：企业级 UI 组件库
- **Pinia**：轻量级状态管理
- **Vue Router**：声明式路由管理

### 功能亮点
- 🌓 **暗黑模式支持**：用户可切换主题模式
- 📱 **响应式设计**：完美适配桌面、平板、手机设备
- ⚡ **性能优化**：懒加载、代码分割、缓存策略
- 🔍 **智能搜索**：实时搜索和筛选功能
- 🎨 **组件化架构**：高内聚低耦合的设计原则

## 📁 项目结构

```
ui/
├── public/                            # 静态资源目录
│   ├── favicon.ico                    # 网站图标
│   └── robots.txt                     # 搜索引擎配置
├── src/                               # 源代码目录
│   ├── assets/                        # 静态资源
│   │   ├── icons/                     # SVG 图标
│   │   ├── images/                    # 图片资源
│   │   └── styles/                    # 全局样式
│   ├── components/                    # 可复用组件
│   │   ├── common/                    # 通用组件
│   │   │   ├── Header.vue            # 顶部导航栏
│   │   │   ├── Sidebar.vue           # 侧边栏菜单
│   │   │   └── Footer.vue            # 底部信息
│   │   ├── business/                  # 业务组件
│   │   │   ├── KnowledgeBaseCard.vue # 知识库卡片
│   │   │   ├── DocumentUploader.vue  # 文档上传组件
│   │   │   └── ChatInterface.vue     # 聊天界面
│   │   └── layout/                    # 布局组件
│   │       ├── MainLayout.vue        # 主布局
│   │       └── AuthLayout.vue        # 认证布局
│   ├── views/                         # 页面视图
│   │   ├── Home.vue                   # 首页
│   │   ├── Login.vue                  # 登录页面
│   │   ├── Register.vue               # 注册页面
│   │   ├── Dashboard.vue              # 仪表板
│   │   ├── KnowledgeBase/             # 知识库相关页面
│   │   │   ├── List.vue               # 知识库列表
│   │   │   ├── Detail.vue             # 知识库详情
│   │   │   └── Create.vue             # 创建知识库
│   │   └── Chat/                      # 聊天相关页面
│   │       ├── Session.vue            # 聊天会话
│   │       └── History.vue            # 历史记录
│   ├── store/                         # 状态管理
│   │   ├── modules/                   # 模块化状态
│   │   │   ├── user.ts                # 用户状态
│   │   │   ├── knowledgeBase.ts       # 知识库状态
│   │   │   └── chat.ts                # 聊天状态
│   │   └── index.ts                   # Store 入口
│   ├── router/                        # 路由配置
│   │   ├── routes/                    # 路由定义
│   │   │   ├── public.ts              # 公共路由
│   │   │   ├── protected.ts           # 受保护路由
│   │   │   └── admin.ts               # 管理员路由
│   │   └── index.ts                   # 路由入口
│   ├── services/                      # API 服务
│   │   ├── api/                       # API 客户端
│   │   │   ├── httpClient.ts          # HTTP 客户端配置
│   │   │   └── interceptors.ts        # 请求拦截器
│   │   ├── modules/                   # 模块化 API
│   │   │   ├── auth.ts                # 认证相关 API
│   │   │   ├── knowledgeBase.ts       # 知识库 API
│   │   │   └── chat.ts                # 聊天 API
│   │   └── index.ts                   # 服务入口
│   ├── utils/                         # 工具函数
│   │   ├── helpers/                   # 辅助函数
│   │   │   ├── date.ts                # 日期处理
│   │   │   ├── string.ts              # 字符串处理
│   │   │   └── validation.ts          # 表单验证
│   │   ├── constants/                 # 常量定义
│   │   │   ├── routes.ts              # 路由常量
│   │   │   └── api.ts                 # API 常量
│   │   └── types/                     # TypeScript 类型
│   │       ├── global.d.ts            # 全局类型声明
│   │       └── components.d.ts        # 组件类型
│   ├── composables/                   # Vue 组合式函数
│   │   ├── useAuth.ts                 # 认证相关组合式函数
│   │   ├── useApi.ts                  # API 调用组合式函数
│   │   └── useTheme.ts                # 主题切换组合式函数
│   ├── App.vue                        # 根组件
│   └── main.ts                        # 应用入口
├── tests/                             # 测试文件
│   ├── unit/                          # 单元测试
│   └── e2e/                           # 端到端测试
├── locales/                           # 国际化文件
│   ├── zh-CN.json                     # 中文翻译
│   └── en-US.json                     # 英文翻译
├── .vscode/                           # VSCode 配置
├── index.html                         # HTML 模板
├── package.json                       # 项目依赖
├── tsconfig.json                      # TypeScript 配置
├── vite.config.ts                     # Vite 配置
├── vitest.config.ts                   # 测试配置
└── README.md                          # 本文档
```

## 🚀 开发环境搭建

### 前置要求

```bash
# Node.js 版本要求
Node.js >= 16.0.0
npm >= 8.0.0

# 推荐使用 nvm 管理 Node.js 版本
nvm install 18.17.0
nvm use 18.17.0
```

### 环境配置

```bash
# 1. 克隆项目
git clone <repository-url>
cd ui

# 2. 安装依赖
npm install

# 3. 环境变量配置
cp .env.example .env.development
cp .env.example .env.production

# 4. 启动开发服务器
npm run dev
```

### 环境变量配置

```bash
# .env.development
VITE_APP_TITLE=MaxKB Dev
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_ENV=development
VITE_ENABLE_MOCK=false

# .env.production
VITE_APP_TITLE=MaxKB
VITE_API_BASE_URL=https://api.maxkb.cn/api
VITE_APP_ENV=production
VITE_ENABLE_MOCK=false
```

## 🛠 核心开发指南

### 组件开发规范

```vue
<!-- 示例：知识库卡片组件 -->
<template>
  <div class="knowledge-base-card" @click="handleClick">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="title">{{ knowledgeBase.name }}</span>
          <el-tag :type="getStatusTagType(knowledgeBase.status)">
            {{ knowledgeBase.status }}
          </el-tag>
        </div>
      </template>
      
      <div class="card-content">
        <p class="description">{{ knowledgeBase.description }}</p>
        <div class="meta-info">
          <span class="documents-count">
            <el-icon><Document /></el-icon>
            {{ knowledgeBase.documentCount }} 文档
          </span>
          <span class="updated-time">
            更新于 {{ formatDate(knowledgeBase.updatedAt) }}
          </span>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Document } from '@element-plus/icons-vue'
import type { KnowledgeBase } from '@/utils/types'

interface Props {
  knowledgeBase: KnowledgeBase
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'select', kb: KnowledgeBase): void
}>()

const handleClick = () => {
  emit('select', props.knowledgeBase)
}

const getStatusTagType = (status: string) => {
  const statusMap: Record<string, 'success' | 'warning' | 'danger'> = {
    active: 'success',
    pending: 'warning',
    archived: 'danger'
  }
  return statusMap[status] || 'info'
}
</script>

<style scoped>
.knowledge-base-card {
  cursor: pointer;
  transition: transform 0.2s ease;
}

.knowledge-base-card:hover {
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-weight: 600;
  font-size: 16px;
}

.description {
  color: var(--el-text-color-secondary);
  margin-bottom: 16px;
  line-height: 1.5;
}

.meta-info {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--el-text-color-placeholder);
}
</style>
```

### 状态管理示例

```typescript
// store/modules/knowledgeBase.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { KnowledgeBase } from '@/utils/types'
import { knowledgeBaseService } from '@/services'

export const useKnowledgeBaseStore = defineStore('knowledgeBase', () => {
  // 状态
  const knowledgeBases = ref<KnowledgeBase[]>([])
  const currentKb = ref<KnowledgeBase | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const activeKnowledgeBases = computed(() => 
    knowledgeBases.value.filter(kb => kb.status === 'active')
  )

  const knowledgeBaseCount = computed(() => 
    knowledgeBases.value.length
  )

  // Actions
  const fetchKnowledgeBases = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await knowledgeBaseService.getList()
      knowledgeBases.value = response.data
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取知识库列表失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const createKnowledgeBase = async (data: Partial<KnowledgeBase>) => {
    try {
      const response = await knowledgeBaseService.create(data)
      knowledgeBases.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = err instanceof Error ? err.message : '创建知识库失败'
      throw err
    }
  }

  const selectKnowledgeBase = (kb: KnowledgeBase) => {
    currentKb.value = kb
  }

  return {
    // 状态
    knowledgeBases,
    currentKb,
    loading,
    error,
    
    // 计算属性
    activeKnowledgeBases,
    knowledgeBaseCount,
    
    // Actions
    fetchKnowledgeBases,
    createKnowledgeBase,
    selectKnowledgeBase
  }
})
```

### API 服务封装

```typescript
// services/modules/knowledgeBase.ts
import { httpClient } from '../api/httpClient'
import type { KnowledgeBase, CreateKnowledgeBaseDto } from '@/utils/types'

class KnowledgeBaseService {
  async getList(params?: { page?: number; size?: number }) {
    const response = await httpClient.get('/knowledge-base', { params })
    return response.data
  }

  async getById(id: string) {
    const response = await httpClient.get(`/knowledge-base/${id}`)
    return response.data
  }

  async create(data: CreateKnowledgeBaseDto) {
    const response = await httpClient.post('/knowledge-base', data)
    return response.data
  }

  async update(id: string, data: Partial<KnowledgeBase>) {
    const response = await httpClient.put(`/knowledge-base/${id}`, data)
    return response.data
  }

  async delete(id: string) {
    const response = await httpClient.delete(`/knowledge-base/${id}`)
    return response.data
  }

  async uploadDocument(kbId: string, formData: FormData) {
    const response = await httpClient.post(
      `/knowledge-base/${kbId}/documents`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    )
    return response.data
  }
}

export const knowledgeBaseService = new KnowledgeBaseService()
```

## 🎨 样式与主题

### CSS 变量系统

```css
/* styles/variables.css */
:root {
  /* 主色调 */
  --primary-color: #409eff;
  --success-color: #67c23a;
  --warning-color: #e6a23c;
  --danger-color: #f56c6c;
  --info-color: #909399;

  /* 文字颜色 */
  --text-primary: #303133;
  --text-regular: #606266;
  --text-secondary: #909399;
  --text-placeholder: #c0c4cc;

  /* 背景色 */
  --bg-color: #ffffff;
  --bg-color-page: #f5f7fa;
  --bg-color-overlay: #ffffff;

  /* 边框 */
  --border-color: #dcdfe6;
  --border-color-light: #e4e7ed;
  --border-color-lighter: #ebeef5;
  --border-color-extra-light: #f2f6fc;

  /* 阴影 */
  --box-shadow-base: 0 2px 4px rgba(0, 0, 0, 0.12), 0 0 6px rgba(0, 0, 0, 0.04);
  --box-shadow-dark: 0 2px 4px rgba(0, 0, 0, 0.12), 0 0 6px rgba(0, 0, 0, 0.12);
}

/* 暗黑模式 */
[data-theme="dark"] {
  --text-primary: #e5eaf3;
  --text-regular: #cfd3dc;
  --text-secondary: #a3a6ad;
  --text-placeholder: #8d9095;
  
  --bg-color: #141414;
  --bg-color-page: #0a0a0a;
  --bg-color-overlay: #1d1e1f;
  
  --border-color: #4c4d4f;
  --border-color-light: #414243;
  --border-color-lighter: #363637;
  --border-color-extra-light: #2b2b2c;
}
```

### 响应式设计

```scss
// mixins/responsive.scss
@mixin respond-to($breakpoint) {
  @if $breakpoint == mobile {
    @media (max-width: 767px) { @content; }
  }
  @if $breakpoint == tablet {
    @media (min-width: 768px) and (max-width: 1023px) { @content; }
  }
  @if $breakpoint == desktop {
    @media (min-width: 1024px) { @content; }
  }
  @if $breakpoint == wide {
    @media (min-width: 1200px) { @content; }
  }
}

// 使用示例
.sidebar {
  width: 240px;
  
  @include respond-to(mobile) {
    width: 100%;
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
  }
}
```

## 🧪 测试策略

### 单元测试

```typescript
// tests/unit/components/KnowledgeBaseCard.spec.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import KnowledgeBaseCard from '@/components/business/KnowledgeBaseCard.vue'
import type { KnowledgeBase } from '@/utils/types'

describe('KnowledgeBaseCard', () => {
  const mockKnowledgeBase: KnowledgeBase = {
    id: '1',
    name: '测试知识库',
    description: '这是一个测试知识库',
    status: 'active',
    documentCount: 10,
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-15T00:00:00Z'
  }

  it('should render knowledge base information correctly', () => {
    const wrapper = mount(KnowledgeBaseCard, {
      props: {
        knowledgeBase: mockKnowledgeBase
      }
    })

    expect(wrapper.find('.title').text()).toBe('测试知识库')
    expect(wrapper.find('.description').text()).toBe('这是一个测试知识库')
    expect(wrapper.find('.documents-count').text()).toContain('10 文档')
  })

  it('should emit select event when clicked', async () => {
    const wrapper = mount(KnowledgeBaseCard, {
      props: {
        knowledgeBase: mockKnowledgeBase
      }
    })

    await wrapper.trigger('click')
    
    expect(wrapper.emitted('select')).toBeTruthy()
    expect(wrapper.emitted('select')?.[0]).toEqual([mockKnowledgeBase])
  })
})
```

### 端到端测试

```typescript
// tests/e2e/specs/knowledge-base.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Knowledge Base Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login')
    await page.fill('[data-testid="username"]', 'testuser')
    await page.fill('[data-testid="password"]', 'password123')
    await page.click('[data-testid="login-button"]')
    await page.waitForURL('/dashboard')
  })

  test('should create new knowledge base', async ({ page }) => {
    await page.click('[data-testid="create-kb-button"]')
    
    await page.fill('[data-testid="kb-name"]', 'E2E 测试知识库')
    await page.fill('[data-testid="kb-description"]', '通过端到端测试创建的知识库')
    
    await page.click('[data-testid="submit-button"]')
    
    await expect(page.locator('[data-testid="kb-card-title"]'))
      .toContainText('E2E 测试知识库')
  })
})
```

## 📈 性能优化

### 代码分割

```typescript
// router/index.ts
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue')
  },
  {
    path: '/knowledge-base',
    name: 'KnowledgeBase',
    component: () => import('@/views/KnowledgeBase/List.vue'),
    children: [
      {
        path: ':id',
        name: 'KnowledgeBaseDetail',
        component: () => import('@/views/KnowledgeBase/Detail.vue')
      }
    ]
  }
]

export const router = createRouter({
  history: createWebHistory(),
  routes
})
```

### 懒加载组件

```vue
<!-- 使用 Suspense 包装异步组件 -->
<template>
  <Suspense>
    <template #default>
      <HeavyComponent />
    </template>
    <template #fallback>
      <div class="loading-spinner">
        <el-spinner />
        <p>加载中...</p>
      </div>
    </template>
  </Suspense>
</template>

<script setup lang="ts">
const HeavyComponent = defineAsyncComponent(() => 
  import('@/components/heavy/HeavyComponent.vue')
)
</script>
```

## 🔧 开发工具配置

### VSCode 推荐插件

```json
{
  "recommendations": [
    "Vue.volar",
    "Vue.vscode-typescript-vue-plugin",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-eslint",
    "formulahendry.auto-rename-tag"
  ]
}
```

### ESLint 配置

```javascript
// .eslintrc.cjs
module.exports = {
  extends: [
    'plugin:vue/vue3-essential',
    '@vue/eslint-config-typescript',
    '@vue/eslint-config-prettier'
  ],
  rules: {
    'vue/multi-word-component-names': 'off',
    '@typescript-eslint/no-explicit-any': 'warn',
    'vue/no-mutating-props': 'error'
  }
}
```

## 🚀 构建与部署

### 生产构建

```bash
# 构建生产版本
npm run build

# 预览构建结果
npm run preview

# 分析打包结果
npm run build -- --report
```

### Docker 部署

```dockerfile
# Dockerfile
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 📚 学习资源

### 官方文档
- [Vue 3 官方文档](https://vuejs.org/guide/)
- [Vite 官方文档](https://vitejs.dev/guide/)
- [TypeScript 官方文档](https://www.typescriptlang.org/docs/)
- [Element Plus 组件库](https://element-plus.org/)

### 最佳实践
- [Vue 3 Composition API 指南](https://learnvue.co/2020/01/4-vue-composition-api-tips-you-should-know/)
- [Vue 3 性能优化](https://web.dev/vue3-performance/)
- [前端架构设计](https://github.com/kamranahmedse/design-patterns-for-humans)

## ⚠️ 注意事项

### 浏览器兼容性
- Chrome >= 88
- Firefox >= 78
- Safari >= 14
- Edge >= 88

### 已知问题
- IE 浏览器不支持
- 某些老旧移动浏览器可能存在兼容性问题

### 性能建议
- 避免在模板中使用复杂表达式
- 合理使用 `v-show` 和 `v-if`
- 对大量列表使用虚拟滚动
- 及时清理事件监听器和定时器

---

<div align="center">

**✨ 让前端开发变得更简单、更高效！**

[![Back to Source](https://img.shields.io/badge/back-Source%20Code-blue)](../README.md)
[![Vue.js](https://img.shields.io/badge/Vue.js-Documentation-green)](https://vuejs.org/)

</div>