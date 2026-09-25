# 雪漫画 Flask 实现设计规格书

**版本**: v1.0  
**日期**: 2026-09-25  
**状态**: 📋 设计中 → ⏳ 待实现

---

## 目录

1. [系统架构](#1-系统架构)
2. [数据库设计](#2-数据库设计)
3. [API 设计](#3-api-设计)
4. [模块接口设计](#4-模块接口设计)
5. [子项目实现计划](#5-子项目实现计划)
6. [错误处理策略](#6-错误处理策略)
7. [测试策略](#7-测试策略)
8. [安全考虑](#8-安全考虑)
9. [进度追踪](#9-进度追踪)

---

## 1. 系统架构

### 1.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                     Flask Web Application                    │
│                    (Python 3.10+, WSGI)                      │
├─────────────────────────────────────────────────────────────┤
│  HTTP Layer (Flask Blueprints)                              │
│  ├── /api/novels        小说管理                            │
│  ├── /api/projects      项目管理                            │
│  ├── /api/roles         资产管理（角色/场景/道具）           │
│  ├── /api/scripts       分镜管理                            │
│  ├── /api/generate      生成任务触发                        │
│  └── /api/settings      系统配置                            │
├─────────────────────────────────────────────────────────────┤
│  Service Layer (业务逻辑)                                    │
│  ├── novel_service      小说下载 + 清洗                     │
│  ├── asset_service      资产提取 + 管理                     │
│  ├── storyboard_service 分镜拆分                            │
│  ├── derivation_service 图像推导（prompt 组装 + LLM）       │
│  ├── generation_service 图像生成（nano-banana-2）           │
│  └── upload_service     云端上传（GRSai → R2）              │
├─────────────────────────────────────────────────────────────┤
│  Task Queue (后台任务)                                       │
│  ├── APScheduler 3.x (轻量级，进程内调度)                   │
│  └── 任务：LLM 调用、图像生成、上传                         │
├─────────────────────────────────────────────────────────────┤
│  Data Layer                                                  │
│  ├── SQLAlchemy ORM (models/)                               │
│  ├── SQLite (data/cinegacha.db)                             │
│  └── 文件存储 (Output/, roles/)                             │
├─────────────────────────────────────────────────────────────┤
│  External APIs                                               │
│  ├── DeepSeek V4 Flash (图像推导)                           │
│  ├── Seed Evolving / Volcengine (分镜拆分)                  │
│  ├── nano-banana-2 via GRSai (图像生成)                     │
│  └── Cloudflare R2 (云存储)                                 │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 技术栈

| 组件 | 技术 | 版本 | 用途 |
|------|------|------|------|
| Runtime | Python | ≥3.10 | 运行环境 |
| Web Framework | Flask | 3.x | HTTP 服务 |
| Database | SQLite | 3 | 数据持久化 |
| ORM | SQLAlchemy | 2.x | 数据库访问 |
| Task Queue | APScheduler | 3.x | 轻量后台任务（进程内，适合单机部署） |
| HTTP Client | httpx | 0.27+ | 异步 HTTP 请求 |
| Encryption | cryptography (Fernet) | 44.x | API keys 加密 |
| Testing | pytest | 8.x | 单元测试 + 集成测试 |
| Mock | pytest-mock | 3.x | Mock 外部 API |

### 1.3 目录结构

```
cinegacha-flask/
├── cinegacha/
│   ├── __init__.py              # Flask app factory
│   ├── config.py                # 配置管理
│   ├── models/                  # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── base.py              # Base model + mixins
│   │   ├── novel.py             # novels 表
│   │   ├── project.py           # projects 表
│   │   ├── role.py              # roles + role_tags 表
│   │   ├── script.py            # scripts_list + scripts_camera 表
│   │   ├── prompt.py            # prompts 表
│   │   └── settings.py          # settings 表
│   ├── services/                # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── novel_service.py     # 小说下载 + 清洗
│   │   ├── text_cleaner.py      # 4 步清洗流水线
│   │   ├── asset_service.py     # 资产管理
│   │   ├── storyboard_service.py # 分镜拆分
│   │   ├── derivation_service.py # 图像推导
│   │   ├── generation_service.py # 图像生成
│   │   ├── upload_service.py    # 云端上传
│   │   ├── llm_client.py        # LLM API 统一客户端
│   │   └── crypto.py            # Fernet 加解密
│   ├── tasks/                   # 后台任务
│   │   ├── __init__.py
│   │   ├── scheduler.py         # 任务调度器
│   │   ├── storyboard_task.py   # 分镜任务
│   │   ├── derivation_task.py   # 推导任务
│   │   └── generation_task.py   # 生成任务
│   ├── routes/                  # Flask Blueprints
│   │   ├── __init__.py
│   │   ├── novel.py
│   │   ├── project.py
│   │   ├── role.py
│   │   ├── script.py
│   │   ├── generate.py
│   │   └── settings.py
│   └── utils/                   # 工具函数
│       ├── __init__.py
│       ├── file_helper.py
│       └── validators.py
├── tests/                       # 测试
│   ├── __init__.py
│   ├── conftest.py              # pytest fixtures
│   ├── test_models/             # Model 测试
│   ├── test_services/           # Service 测试
│   └── test_routes/             # Route 测试
├── data/                        # 数据目录
│   ├── cinegacha.db             # SQLite 数据库
│   └── reference.db             # 参考数据库（原 data.db）
├── Output/                      # 生成输出
├── requirements/
│   ├── base.txt                 # 基础依赖
│   ├── dev.txt                  # 开发依赖
│   └── test.txt                 # 测试依赖
├── pyproject.toml               # 项目配置
├── README.md
└── docs/
    └── superpowers/specs/       # 设计文档
```

### 1.4 数据流（7 阶段流水线）

```
Stage 1: Novel Input
  └─ 用户提交 URL 或文本 → novels 表 (original_text, share_url)

Stage 2: Text Cleaning (4 步)
  ├─ 格式清洗 → is_format_cleaned = 1
  ├─ 串行清洗 → is_serial_cleaned = 1
  ├─ 标点清洗 → is_punct_cleaned = 1
  └─ 分镜清洗 → is_shot_cleaned = 1 (待实现)
  └─ 输出: novels.content

Stage 3: Asset Preparation (并行)
  ├─ 角色提取 → roles 表 (type=角色, content, content_word2)
  ├─ 场景识别 → roles 表 (type=场景, content, content_word2)
  └─ 道具提取 → roles 表 (type=道具, content, content_word2)

Stage 4: Storyboard Split
  └─ Seed Evolving (分块×6, 并行×4, ≤900字/块)
  └─ 输出: scripts_list 表 (content, presets)

Stage 5: Image Derivation
  └─ DeepSeek V4 Flash (串行, 注入资产描述)
  └─ 输出: scripts_list.image_prompt (455-1270字)

Stage 6: Image Generation
  └─ nano-banana-2 via GRSai
  └─ 输出: 本地 PNG → Output/<project_id>/<episode>/image/

Stage 7: Cloud Linking
  └─ GRSai → R2 → 签名 URL (72h)
  └─ 输出: roles.role_url
```

---

## 2. 数据库设计

### 2.1 核心表 Schema

#### novels 表

```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    content TEXT,                          -- 清洗后文本
    original_text TEXT DEFAULT '',         -- 原始文本
    character_text TEXT DEFAULT '',        -- 角色提取文本
    revised_text TEXT DEFAULT '',          -- 修订后文本
    script_text TEXT DEFAULT '',           -- 剧本化文本
    storyboard_text TEXT DEFAULT '',       -- 分镜文本
    opening_text TEXT DEFAULT '',          -- 开头文本
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 来源
    share_url TEXT DEFAULT '',
    word_count INTEGER DEFAULT 0,
    
    -- 清洗状态
    is_format_cleaned INTEGER DEFAULT 0,
    is_serial_cleaned INTEGER DEFAULT 0,
    is_punct_cleaned INTEGER DEFAULT 0,
    is_shot_cleaned INTEGER DEFAULT 0,     -- 待实现
    
    -- 评分
    score_value REAL,
    score_report TEXT
);
```

#### projects 表

```sql
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    novel_id INTEGER NOT NULL,
    mode TEXT DEFAULT 'manga',             -- 'manga' | 'camera'
    
    -- 画风配置
    manga_derive_preset_id TEXT,
    img_prompt_prefix TEXT,
    img_prompt_suffix TEXT,
    
    -- 模型配置 (JSON)
    manga_gen_models TEXT DEFAULT '{}',
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (novel_id) REFERENCES novels(id)
);
```

#### roles 表（统一存储角色/场景/道具）

```sql
CREATE TABLE roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    novel_id INTEGER NOT NULL,
    project_id INTEGER,
    
    -- 双层描述
    content TEXT,                          -- 中文基础描述 (37-250字)
    content_word2 TEXT,                    -- 英文增强描述 (可选)
    
    -- 资产 URL
    cover_url TEXT,                        -- 封面图
    role_url TEXT,                         -- 云端参考图 (签名 URL, 72h)
    reference_image_url TEXT,              -- 本地参考图
    portrait_preview_json TEXT,            -- 肖像预览 (JSON)
    
    -- 元数据
    role_kind TEXT DEFAULT 'library',
    asset_art_style_json TEXT,             -- 艺术风格 (JSON)
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (novel_id) REFERENCES novels(id),
    FOREIGN KEY (project_id) REFERENCES projects(id)
);
```

#### role_tags 表

```sql
CREATE TABLE role_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_id INTEGER NOT NULL,
    tag_category TEXT NOT NULL,            -- '性别' | '时代' | '小说' | '类型'
    tag_value TEXT NOT NULL,               -- '男' | '古代' | '明溪' | '角色' | '场景' | '道具'
    
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
);
```

#### scripts_list 表（manga 模式）

```sql
CREATE TABLE scripts_list (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    shot_id INTEGER,
    shot_index INTEGER NOT NULL,           -- 排序索引
    
    -- 内容
    content TEXT,                          -- 分镜文本
    presets TEXT,                          -- 出场资产 JSON ["明溪", "明家祠堂夜晚", "婚书"]
    image_prompt TEXT,                     -- 图像提示词 (455-1270字)
    video_prompt TEXT,
    screen_prompt TEXT,
    
    -- 图像
    main_image TEXT,                       -- 生成的图像路径
    candidate_images TEXT,                 -- 候选图 JSON
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);
```

#### scripts_camera 表（camera 模式）

```sql
CREATE TABLE scripts_camera (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    shot_index INTEGER NOT NULL,
    
    content TEXT,
    image_prompt TEXT,
    
    -- 视频帧
    first_frame_path TEXT,
    last_frame_path TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);
```

#### prompts 表（Fernet 加密）

```sql
CREATE TABLE prompts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    category TEXT,                         -- '角色设定' | '场景生成' | '对话生成'
    content TEXT NOT NULL,                 -- Fernet 加密: v2:gAAAAAB...
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### settings 表（部分 Fernet 加密）

```sql
CREATE TABLE settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    value TEXT,                            -- 敏感值加密: v2:gAAAAAB...
    is_encrypted INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 加密字段示例:
-- account_pool_deepseek_api_key
-- account_pool_grsai_api_key
-- account_pool_volcengine_api_key
```

#### image_tasks 表

```sql
CREATE TABLE image_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    script_id INTEGER NOT NULL,
    status TEXT DEFAULT 'pending',         -- 'pending' | 'running' | 'success' | 'failed'
    image_path TEXT,
    image_url TEXT,
    error_message TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (script_id) REFERENCES scripts_list(id) ON DELETE CASCADE
);
```

### 2.2 表关系图

```
novels (1) ──→ (N) projects
                  │
                  ├──→ (N) scripts_list (manga)
                  │         │
                  │         └──→ (N) image_tasks
                  │
                  └──→ (N) scripts_camera (camera)

novels (1) ──→ (N) roles
                  │
                  └──→ (N) role_tags
```

---

## 3. API 设计

### 3.1 RESTful API 端点

#### 小说管理 `/api/novels`

```
POST   /api/novels              创建小说（文本或 URL）
GET    /api/novels              列表
GET    /api/novels/:id          详情
PUT    /api/novels/:id          更新
DELETE /api/novels/:id          删除
POST   /api/novels/:id/clean    触发清洗流水线
GET    /api/novels/:id/status   清洗状态
```

#### 项目管理 `/api/projects`

```
POST   /api/projects            创建项目
GET    /api/projects            列表
GET    /api/projects/:id        详情
PUT    /api/projects/:id        更新
DELETE /api/projects/:id        删除
```

#### 资产管理 `/api/roles`

```
POST   /api/roles               创建资产
GET    /api/roles               列表 (?project_id=X&type=角色)
GET    /api/roles/:id           详情
PUT    /api/roles/:id           更新
DELETE /api/roles/:id           删除
POST   /api/roles/extract       从小说提取资产
POST   /api/roles/:id/upload    上传到云端
```

#### 分镜管理 `/api/scripts`

```
POST   /api/scripts             创建分镜
GET    /api/scripts             列表 (?project_id=X)
GET    /api/scripts/:id         详情
PUT    /api/scripts/:id         更新
DELETE /api/scripts/:id         删除
POST   /api/scripts/split       触发分镜拆分
```

#### 生成任务 `/api/generate`

```
POST   /api/generate/derive     触发图像推导 (project_id)
POST   /api/generate/image      触发图像生成 (project_id)
GET    /api/generate/status     任务状态 (?project_id=X)
```

#### 系统配置 `/api/settings`

```
GET    /api/settings            列表
PUT    /api/settings/:key       更新
```

### 3.2 API 响应格式

#### 成功响应

```json
{
  "success": true,
  "data": { ... },
  "message": "操作成功"
}
```

#### 列表响应

```json
{
  "success": true,
  "data": [ ... ],
  "total": 100,
  "page": 1,
  "per_page": 20
}
```

#### 错误响应

```json
{
  "success": false,
  "error": {
    "code": "NOVEL_NOT_FOUND",
    "message": "小说不存在"
  }
}
```

---

## 4. 模块接口设计

### 4.1 Service 层接口

#### novel_service.py

```python
class NovelService:
    def create_novel(self, name: str, text: str = None, url: str = None) -> Novel:
        """创建小说（文本或 URL）"""
        
    def clean_text(self, novel_id: int) -> Novel:
        """执行 4 步清洗流水线"""
        
    def get_novel(self, novel_id: int) -> Novel:
        """获取小说详情"""
        
    def list_novels(self, page: int = 1, per_page: int = 20) -> tuple[list[Novel], int]:
        """列表分页"""
```

#### text_cleaner.py

```python
class TextCleaner:
    def clean(self, text: str) -> CleanResult:
        """执行完整清洗流水线"""
        
    def format_clean(self, text: str) -> str:
        """格式清洗：标准化换行、空格"""
        
    def serial_clean(self, text: str) -> str:
        """串行清洗：移除连载标记"""
        
    def punct_clean(self, text: str) -> str:
        """标点清洗：修正标点"""
        
    def shot_clean(self, text: str) -> str:
        """分镜清洗：待实现"""
```

#### asset_service.py

```python
class AssetService:
    def extract_assets(self, novel_id: int, project_id: int) -> list[Role]:
        """从小说提取角色/场景/道具"""
        
    def create_role(self, name: str, novel_id: int, project_id: int, 
                    content: str, role_type: str) -> Role:
        """创建资产"""
        
    def upload_to_cloud(self, role_id: int) -> Role:
        """上传到 R2，返回签名 URL"""
```

#### storyboard_service.py

```python
class StoryboardService:
    def split_to_shots(self, novel_id: int, project_id: int) -> list[Script]:
        """拆分小说为分镜（Seed Evolving, 分块×6, 并行×4）"""
        
    def _chunk_text(self, text: str, chunk_size: int = 900) -> list[str]:
        """文本分块"""
        
    def _call_seed_evolving(self, chunk: str) -> str:
        """调用 Seed Evolving API"""
```

#### derivation_service.py

```python
class DerivationService:
    def derive_image_prompts(self, project_id: int) -> list[Script]:
        """为所有分镜生成图像提示词（DeepSeek V4 Flash）"""
        
    def _assemble_prompt(self, script: Script, roles: list[Role]) -> str:
        """组装提示词（注入资产描述）"""
        
    def _call_deepseek(self, prompt: str) -> str:
        """调用 DeepSeek API"""
```

#### generation_service.py

```python
class GenerationService:
    def generate_images(self, project_id: int) -> list[ImageTask]:
        """批量生成图像（nano-banana-2）"""
        
    def _call_grsai(self, image_prompt: str) -> str:
        """调用 GRSai API，返回本地图像路径"""
```

#### upload_service.py

```python
class UploadService:
    def upload_image(self, local_path: str) -> str:
        """上传到 R2，返回签名 URL（72h）"""
        
    def _sign_url(self, object_key: str) -> str:
        """生成 AWS4-HMAC-SHA256 签名 URL"""
```

### 4.2 LLM Client 接口

#### llm_client.py

```python
class LLMClient:
    def __init__(self, config: dict):
        """初始化，加载加密 API keys"""
        
    async def call_deepseek(self, system_prompt: str, user_message: str, 
                           stream: bool = True) -> str:
        """调用 DeepSeek V4 Flash"""
        
    async def call_seed_evolving(self, prompt: str) -> str:
        """调用 Seed Evolving (Volcengine)"""
        
    def _decrypt_api_key(self, encrypted_key: str) -> str:
        """Fernet 解密 API key"""
```

---

## 5. 子项目实现计划

### Spec 1: Foundation 基础骨架

**目标**: Flask app factory、完整 database schema、pytest 配置、目录结构  
**依赖**: 无  
**状态**: ⏳ 待实现

#### 任务清单

| # | 任务 | 状态 | 依赖 | 验收标准 |
|---|------|------|------|----------|
| 1.1 | 创建项目目录结构 | ⏳ | - | 所有目录存在 |
| 1.2 | 创建 `pyproject.toml` + `requirements/*.txt` | ⏳ | 1.1 | `pip install -e .` 成功 |
| 1.3 | 实现 Flask app factory (`cinegacha/__init__.py`) | ⏳ | 1.2 | `flask run` 启动成功 |
| 1.4 | 实现 config.py (开发/测试/生产配置) | ⏳ | 1.2 | 配置加载正确 |
| 1.5 | 实现 models/base.py (Base + mixins) | ⏳ | 1.3 | Base 可继承 |
| 1.6 | 实现所有 models (novel, project, role, script, prompt, settings) | ⏳ | 1.5 | Schema 与参考 DB 一致 |
| 1.7 | 配置 pytest + conftest.py | ⏳ | 1.3 | `pytest` 运行成功 |
| 1.8 | 编写 model 单元测试 | ⏳ | 1.6, 1.7 | 所有 model CRUD 测试通过 |
| 1.9 | 初始化 git + .gitignore | ⏳ | 1.1 | `git init` + commit |

#### TDD 测试用例

```python
# tests/test_models/test_novel.py
def test_create_novel(client):
    """创建小说"""
    novel = Novel(name="测试小说", original_text="测试内容")
    db.session.add(novel)
    db.session.commit()
    assert novel.id is not None
    assert novel.is_format_cleaned == 0

def test_novel_cleaning_flags(client):
    """清洗状态标记"""
    novel = Novel(name="测试", content="内容")
    novel.is_format_cleaned = 1
    assert novel.is_format_cleaned == 1

# tests/test_models/test_role.py
def test_create_character(client):
    """创建角色"""
    role = Role(name="明溪", novel_id=1, content="12岁女孩...", role_type="角色")
    db.session.add(role)
    assert role.name == "明溪"

def test_role_tags(client):
    """角色标签"""
    role = Role(name="明溪", ...)
    tag = RoleTag(role_id=role.id, tag_category="性别", tag_value="女")
    assert tag.tag_value == "女"
```

---

### Spec 2: Novel Ingestion + Cleaning 小说输入与清洗

**目标**: 小说下载器抽象、4 步清洗流水线、novels CRUD  
**依赖**: Spec 1  
**状态**: ⏳ 待实现

#### 任务清单

| # | 任务 | 状态 | 依赖 | 验收标准 |
|---|------|------|------|----------|
| 2.1 | 实现 text_cleaner.py (4 步流水线) | ⏳ | 1.6 | 清洗前后文本对比测试通过 |
| 2.2 | 实现 novel_service.py (CRUD + clean) | ⏳ | 2.1 | API 端点可用 |
| 2.3 | 实现 routes/novel.py (REST API) | ⏳ | 2.2 | POST/GET/PUT/DELETE 测试通过 |
| 2.4 | 编写清洗流水线测试 | ⏳ | 2.1 | 4 步清洗单元测试 |
| 2.5 | 编写 API 集成测试 | ⏳ | 2.3 | 端到端 API 测试 |

#### TDD 测试用例

```python
# tests/test_services/test_text_cleaner.py
def test_format_clean():
    """格式清洗：标准化换行"""
    cleaner = TextCleaner()
    text = "第一行\r\n第二行\n\n\n第三行"
    result = cleaner.format_clean(text)
    assert result == "第一行\n第二行\n第三行"

def test_serial_clean():
    """串行清洗：移除连载标记"""
    cleaner = TextCleaner()
    text = "第1章 开头 [连载] ..."
    result = cleaner.serial_clean(text)
    assert "[连载]" not in result

def test_full_clean_pipeline():
    """完整清洗流水线"""
    cleaner = TextCleaner()
    result = cleaner.clean("原始文本...")
    assert result.is_format_cleaned
    assert result.is_serial_cleaned
    assert result.is_punct_cleaned

# tests/test_routes/test_novel_api.py
def test_create_novel_api(client):
    """POST /api/novels"""
    response = client.post("/api/novels", json={
        "name": "测试小说",
        "text": "测试内容"
    })
    assert response.status_code == 201
    assert response.json["success"] is True

def test_clean_novel_api(client):
    """POST /api/novels/:id/clean"""
    novel_id = 1
    response = client.post(f"/api/novels/{novel_id}/clean")
    assert response.json["data"]["is_format_cleaned"] == 1
```

---

### Spec 3: Asset System 资产系统

**目标**: roles CRUD、三类型资产提取、双层描述  
**依赖**: Spec 2  
**状态**: ⏳ 待实现

#### 任务清单

| # | 任务 | 状态 | 依赖 | 验收标准 |
|---|------|------|------|----------|
| 3.1 | 实现 asset_service.py (CRUD) | ⏳ | 2.2 | roles CRUD 测试通过 |
| 3.2 | 实现资产提取逻辑（调用 LLM） | ⏳ | 3.1 | Mock LLM 返回，提取成功 |
| 3.3 | 实现 routes/role.py | ⏳ | 3.1 | API 端点可用 |
| 3.4 | 编写资产提取测试（mock LLM） | ⏳ | 3.2 | 提取结果符合预期 |
| 3.5 | 编写 API 测试 | ⏳ | 3.3 | 端到端测试通过 |

#### TDD 测试用例

```python
# tests/test_services/test_asset_service.py
def test_extract_characters(mocker):
    """提取角色"""
    mock_llm = mocker.patch("LLMClient.call_deepseek")
    mock_llm.return_value = "角色1: 明溪, 12岁女孩..."
    
    service = AssetService()
    roles = service.extract_assets(novel_id=1, project_id=1)
    
    assert len(roles) > 0
    assert roles[0].role_type == "角色"
    assert roles[0].name == "明溪"

def test_create_role_with_tags(client):
    """创建角色 + 标签"""
    role = Role(name="明溪", novel_id=1, content="12岁女孩...")
    tag = RoleTag(role=role, tag_category="性别", tag_value="女")
    
    assert role.name == "明溪"
    assert tag.tag_value == "女"
```

---

### Spec 4: Storyboard + Derivation 分镜与推导

**目标**: Seed Evolving 分块并行、DeepSeek 推导、提示词组装  
**依赖**: Spec 2, 3  
**状态**: ⏳ 待实现

#### 任务清单

| # | 任务 | 状态 | 依赖 | 验收标准 |
|---|------|------|------|----------|
| 4.1 | 实现 storyboard_service.py (分块 + 并行) | ⏳ | 2.2 | 分块逻辑正确 |
| 4.2 | 实现 derivation_service.py (prompt 组装) | ⏳ | 3.1 | 提示词格式正确 |
| 4.3 | 实现 LLM mock (测试用) | ⏳ | - | Mock 返回固定格式 |
| 4.4 | 实现 routes/script.py + routes/generate.py | ⏳ | 4.1, 4.2 | API 可用 |
| 4.5 | 编写分镜拆分测试 | ⏳ | 4.1 | 分块 + 并行测试 |
| 4.6 | 编写推导测试（mock LLM） | ⏳ | 4.2, 4.3 | 提示词输出断言 |

#### TDD 测试用例

```python
# tests/test_services/test_storyboard_service.py
def test_chunk_text():
    """文本分块"""
    service = StoryboardService()
    text = "a" * 2000  # 2000 字
    chunks = service._chunk_text(text, chunk_size=900)
    assert len(chunks) == 3
    assert all(len(c) <= 900 for c in chunks)

def test_split_to_shots(mocker):
    """分镜拆分（mock Seed Evolving）"""
    mock_call = mocker.patch("StoryboardService._call_seed_evolving")
    mock_call.return_value = "1. 第一幕\n2. 第二幕\n3. 第三幕"
    
    service = StoryboardService()
    scripts = service.split_to_shots(novel_id=1, project_id=1)
    
    assert len(scripts) == 3
    assert scripts[0].content == "第一幕"

# tests/test_services/test_derivation_service.py
def test_assemble_prompt():
    """组装提示词"""
    script = Script(content="明溪走进祠堂", presets='["明溪", "明家祠堂夜晚"]')
    roles = [
        Role(name="明溪", content="12岁女孩..."),
        Role(name="明家祠堂夜晚", content="古色古香的祠堂...")
    ]
    
    service = DerivationService()
    prompt = service._assemble_prompt(script, roles)
    
    assert "明溪" in prompt
    assert "12岁女孩" in prompt
    assert "祠堂" in prompt

def test_derive_image_prompts(mocker):
    """图像推导（mock DeepSeek）"""
    mock_call = mocker.patch("LLMClient.call_deepseek")
    mock_call.return_value = "韩系漫画风格，明溪站在祠堂前..."
    
    service = DerivationService()
    scripts = service.derive_image_prompts(project_id=1)
    
    assert scripts[0].image_prompt.startswith("韩系漫画风格")
```

---

### Spec 5: Image Generation + Cloud Link 图像生成与上传

**目标**: nano-banana-2 调用、GRSai 上传、R2 签名 URL  
**依赖**: Spec 4  
**状态**: ⏳ 待实现

#### 任务清单

| # | 任务 | 状态 | 依赖 | 验收标准 |
|---|------|------|------|----------|
| 5.1 | 实现 generation_service.py | ⏳ | 4.2 | Mock GRSai 返回图像路径 |
| 5.2 | 实现 upload_service.py (R2 签名) | ⏳ | - | URL 格式正确 |
| 5.3 | 实现后台任务 (APScheduler) | ⏳ | 5.1 | 任务异步执行 |
| 5.4 | 编写生成测试（mock GRSai） | ⏳ | 5.1 | 图像路径断言 |
| 5.5 | 编写上传测试 | ⏳ | 5.2 | URL 签名验证 |

#### TDD 测试用例

```python
# tests/test_services/test_upload_service.py
def test_sign_url():
    """生成签名 URL"""
    service = UploadService()
    url = service._sign_url("32ea8411-3894-4d47-8433-52f1f190d9d0.jpeg")
    
    assert "cloudflarestorage.com" in url
    assert "X-Amz-Algorithm=AWS4-HMAC-SHA256" in url
    assert "X-Amz-Expires=259200" in url  # 72h

def test_upload_image(mocker, tmp_path):
    """上传图像到 R2"""
    mock_upload = mocker.patch("UploadService._upload_to_r2")
    mock_upload.return_value = "32ea8411.jpeg"
    
    service = UploadService()
    local_path = tmp_path / "test.png"
    local_path.write_bytes(b"fake image")
    
    url = service.upload_image(str(local_path))
    assert url.startswith("https://")
```

---

### Spec 6: Web UI + Integration 界面与集成

**目标**: 前端界面、端到端流程、完整测试  
**依赖**: Spec 1-5  
**状态**: ⏳ 待实现

#### 任务清单

| # | 任务 | 状态 | 依赖 | 验收标准 |
|---|------|------|------|----------|
| 6.1 | 实现前端 (Jinja2 + HTMX, 无需构建工具) | ⏳ | 1-5 | 界面可用，API 联通 |
| 6.2 | 实现端到端流程测试 | ⏳ | 6.1 | 小说→漫画全流程 |
| 6.3 | 性能优化 + 错误处理完善 | ⏳ | 6.2 | 无阻塞 bug |
| 6.4 | 编写 E2E 测试 | ⏳ | 6.2 | Playwright smoke test |

---

## 6. 错误处理策略

### 6.1 错误分类

| 类别 | HTTP 状态码 | 示例 |
|------|------------|------|
| 客户端错误 | 400 | 参数验证失败 |
| 未授权 | 401 | API key 无效 |
| 未找到 | 404 | 资源不存在 |
| 服务端错误 | 500 | 数据库错误、LLM 调用失败 |
| 外部服务错误 | 502 | DeepSeek/GRSai API 超时 |

### 6.2 错误处理原则

1. **Fail Fast**: 参数验证在 route 层完成
2. **详细日志**: service 层记录完整错误上下文
3. **用户友好**: API 返回简洁错误信息
4. **重试机制**: LLM 调用失败自动重试 3 次

### 6.3 错误响应格式

```python
# 统一错误处理
@app.errorhandler(ValidationError)
def handle_validation_error(e):
    return jsonify({
        "success": False,
        "error": {
            "code": "VALIDATION_ERROR",
            "message": str(e)
        }
    }), 400

@app.errorhandler(Exception)
def handle_exception(e):
    logger.exception("Unhandled exception")
    return jsonify({
        "success": False,
        "error": {
            "code": "INTERNAL_ERROR",
            "message": "服务器内部错误"
        }
    }), 500
```

---

## 7. 测试策略

### 7.1 测试层次

| 层次 | 工具 | 覆盖目标 |
|------|------|----------|
| 单元测试 | pytest + pytest-mock | Service 层逻辑 |
| 集成测试 | pytest + test client | API 端点 |
| E2E 测试 | Playwright | 前端流程 |

### 7.2 Mock 策略

- **LLM APIs**: 使用 pytest-mock 模拟返回
- **图像生成**: Mock GRSai 返回本地图像路径
- **云存储**: Mock R2 上传，返回 fake URL

### 7.3 测试数据

- `data/reference.db`: 参考数据库（原 data.db）
- `tests/fixtures/`: 测试用的 JSON/文本文件

### 7.4 覆盖率目标

- **最低**: 80%
- **关键模块**: 100% (text_cleaner, prompt_assembler)

---

## 8. 安全考虑

### 8.1 加密

- **API Keys**: Fernet 对称加密，存储在 settings 表
- **提示词模板**: Fernet 加密，存储在 prompts 表
- **加密密钥**: 环境变量 `FERNET_KEY`，不硬编码

### 6.2 认证（MVP 阶段）

- 无认证（内部工具，单机部署）
- API 调用通过本地 settings 表的加密 key 鉴权到外部服务

### 生产阶段（后续）

- 添加 Flask-Login 用户认证
- 启用 CSRF token

### 8.3 输入验证

- **SQL 注入**: SQLAlchemy ORM 参数化查询防止
- **XSS**: Jinja2 自动转义 + HTMX 安全策略
- **CSRF**: 生产环境启用 Flask-WTF CSRF token

---

## 9. 进度追踪

### 9.1 整体进度

| 子项目 | 状态 | 进度 |
|--------|------|------|
| Spec 1: Foundation | ⏳ 待实现 | 0% |
| Spec 2: Novel + Cleaning | ⏳ 待实现 | 0% |
| Spec 3: Asset System | ⏳ 待实现 | 0% |
| Spec 4: Storyboard + Derivation | ⏳ 待实现 | 0% |
| Spec 5: Image Gen + Cloud | ⏳ 待实现 | 0% |
| Spec 6: Web UI | ⏳ 待实现 | 0% |
| **总计** | **⏳** | **0%** |

### 9.2 详细任务状态

**Spec 1 (9 tasks)**: ⏳⏳⏳⏳⏳⏳⏳⏳⏳  
**Spec 2 (5 tasks)**: ⏳⏳⏳⏳⏳  
**Spec 3 (5 tasks)**: ⏳⏳⏳⏳⏳  
**Spec 4 (6 tasks)**: ⏳⏳⏳⏳⏳⏳  
**Spec 5 (5 tasks)**: ⏳⏳⏳⏳⏳  
**Spec 6 (4 tasks)**: ⏳⏳⏳⏳  

**总计**: 34 tasks, 0 completed, 0 in progress, 34 pending

### 9.3 状态标记说明

- ✅ 已完成
- 🔄 进行中
- ⏳ 待实现
- ❌ 阻塞
- ⏸️ 暂停

---

## 附录

### A. 参考资料

- `整体设计.md`: 系统整体设计
- `分析设计文档.md`: 角色场景系统分析
- `提示词设计.md`: 图像推导提示词模板
- `分镜提示词.md`: 文本分镜提示词
- `doc/architecture_analysis.md`: 原 PyQt6 架构分析

### B. 术语表

| 术语 | 含义 |
|------|------|
| 分镜 | Storyboard shot, 独立的漫画画面单元 |
| 资产 | Roles (角色/场景/道具) |
| 推导 | Derivation, 从分镜文本生成图像提示词 |
| 双层描述 | content (中文) + content_word2 (英文增强) |

---

**文档版本**: 1.0  
**最后更新**: 2026-09-25  
**作者**: Claude Code (fangkun)
