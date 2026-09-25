# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**雪漫画 (CineGacha)** — Converts web novels into manga storyboard images via an AI pipeline. This repo is a **reimplementation** of an existing PyQt6 desktop app as a **Flask web application**.

Input: Web novel text (Zhihu paid columns) → Output: Manga storyboard images ready for comic production.

Design docs in root `.md` files are the authoritative spec — always consult them before implementation.

## Tech Stack

- **Runtime**: Python ≥ 3.10
- **Web Framework**: Flask
- **Database**: SQLite3 via SQLAlchemy
- **Task Queue**: Background jobs for long-running AI tasks (LLM calls, image generation)
- **AI Models**: DeepSeek V4 Flash (image prompt derivation), Seed Evolving / Volcengine (storyboard splitting), nano-banana-2 via GRSai (image generation)
- **Cloud Storage**: Cloudflare R2 via GRSai relay (asset upload, signed URLs)
- **Encryption**: Fernet for API keys and prompt templates

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
flask db init

# Run development server
flask run --debug

# Run with specific host/port
flask run --host=0.0.0.0 --port=5000

# Run a single test
pytest tests/test_module.py::test_function -v

# Run all tests
pytest -v

# Export prompts for debugging
python scripts/export_prompts.py --project-id 15
```

## Architecture

### Pipeline (7 Stages)

```
1. Novel Input      → novels table (original_text, content)
2. Text Cleaning     → 4-step pipeline (format→serial→punct→shot)
3. Asset Preparation → roles table: characters/scenes/props (parallel, all share same table)
4. Storyboard Split  → scripts_list table (Seed Evolving, chunked×6, parallel×4, ≤900 chars/block)
5. Image Derivation  → scripts_list.image_prompt (DeepSeek V4 Flash, serial per shot)
6. Image Generation  → local PNG (nano-banana-2 via GRSai)
7. Cloud Linking     → Cloudflare R2 → signed URL (72h expiry, AWS4-HMAC-SHA256)
```

Stages 3 (character/scene/prop extraction) runs in parallel. Stage 5 depends on both stages 4 and 3 completing.

### Flask Application Structure

```
cinegacha/
├── __init__.py          # Flask app factory
├── models/              # SQLAlchemy models
│   ├── novel.py         # novels table
│   ├── project.py       # projects table
│   ├── role.py          # roles + role_tags tables
│   ├── script.py        # scripts_list + scripts_camera tables
│   ├── prompt.py        # prompts table (Fernet encrypted content)
│   └── settings.py      # settings table (key-value, some encrypted)
├── routes/              # Flask blueprints
│   ├── novel.py         # Novel CRUD, import, download
│   ├── project.py       # Project management
│   ├── role.py          # Asset management (characters/scenes/props)
│   ├── script.py        # Storyboard editor
│   ├── generate.py      # Trigger AI generation tasks
│   └── settings.py      # Configuration, API keys
├── services/            # Business logic
│   ├── novel_downloader.py    # Zhihu/Lofter scraping
│   ├── text_cleaner.py        # 4-step cleaning pipeline
│   ├── llm_client.py          # Unified LLM API client
│   ├── image_generator.py     # Image generation via GRSai
│   ├── asset_uploader.py      # Cloud upload (GRSai → R2)
│   ├── prompt_assembler.py    # Context assembly for LLM prompts
│   └── crypto.py              # Fernet encrypt/decrypt
├── tasks/               # Background task workers
│   ├── storyboard_split.py    # Text → storyboard (chunked parallel)
│   ├── image_derive.py        # Storyboard → image prompt
│   └── asset_extract.py       # Character/scene/prop extraction
└── utils/
    ├── file_helper.py
    └── db.py              # Database session management
```

### Database Schema (Key Tables)

| Table | Purpose | Key Relationships |
|-------|---------|-------------------|
| `novels` | Novel content + processing state | 1:N → projects |
| `projects` | Project config, art style, model settings | N:1 → novels, 1:N → scripts_list |
| `roles` | Unified asset store (characters + scenes + props) | N:1 → novels, 1:N → role_tags |
| `role_tags` | Asset type labels (`tag_category`: 性别/时代/小说) | N:1 → roles |
| `scripts_list` | Storyboard shots (manga mode) | N:1 → projects |
| `scripts_camera` | Storyboard shots (camera/video mode) | N:1 → projects |
| `prompts` | Prompt templates (Fernet encrypted) | — |
| `settings` | System config K/V (some Fernet encrypted) | — |
| `image_tasks` | Image generation task tracking | N:1 → scripts_list |

### Three Asset Types (Unified `roles` Table)

Distinguished by `role_tags.tag_category`:

| Type | Content Length | Naming Convention |
|------|---------------|-------------------|
| Character (角色) | 150-250 chars | `{角色名}` e.g. "明溪" |
| Scene (场景) | 74-130 chars | `{地点}{时间}` e.g. "明家祠堂夜晚" |
| Prop (道具) | 37-58 chars | `{归属}的{物品}` e.g. "林依依的项链" |

Each asset has two description layers:
- `content`: Chinese base description (always present)
- `content_word2`: English enhanced description for image generation (optional, higher quality)

### Prompt Derivation Flow

```
scripts_list.presets = ["明家祠堂夜晚", "明溪", "婚书"]
    ↓ match against roles.name
roles.content → extract asset descriptions
    ↓ assemble into User Message template
User Message:
    {{IMG_PROMPT_PREFIX}}          # from projects.img_prompt_prefix
    {{STORY_CONTENT}}              # scripts_list.content
    {{CHARACTER_LIST}}             # matched character names
    {{CHARACTER_DESCRIPTIONS}}     # matched roles.content
    {{SCENE_DESCRIPTION}}          # matched scene roles.content
    {{IMG_PROMPT_SUFFIX}}          # from projects.img_prompt_suffix
    ↓ DeepSeek V4 Flash
scripts_list.image_prompt (455-1270 chars)
```

### Image Prompt Output Structure

Every generated `image_prompt` follows this 4-part format:
1. **画面描述** (40%): Visual content — characters, poses, composition, environment
2. **版式说明** (40%): Panel layout — grid arrangement, reading direction, proportions
3. **文字 UI 规范** (15%): Text overlay — white bg, black outline `#1a1a1a`, narration box style
4. **禁止事项** (5%): Prohibitions — no watermarks, no platform logos

### Text Cleaning Pipeline (4 Steps)

```
original_text
  → [格式清洗] is_format_cleaned = 1   (formatting normalization)
  → [串行清洗] is_serial_cleaned = 1   (serialization markers removal)
  → [标点清洗] is_punct_cleaned = 1    (punctuation correction)
  → [分镜清洗] is_shot_cleaned = 0     (storyboard-oriented cleanup, NOT YET IMPLEMENTED)
= content (final cleaned text)
```

## AI Model Integration

| Model | Endpoint | Task | Concurrency |
|-------|----------|------|-------------|
| Seed Evolving | Volcengine/Doubao API | Storyboard text splitting | Chunked×6, parallel×4 |
| DeepSeek V4 Flash | `https://api.deepseek.com/chat/completions` | Image prompt derivation | Serial per shot, streaming=true |
| nano-banana-2 | GRSai API | Image generation | Async queue |

### Encrypted Settings (Fernet)

Keys stored in `settings` table with `v2:gAAAAAB...` format:
- `account_pool_deepseek_api_key`
- `account_pool_grsai_api_key`
- `account_pool_volcengine_api_key`
- `prompts.content` (all system prompt templates)

## Cloud Storage (One-Click Link)

```
Local PNG → POST GRSai /v1/images/upload
         → Cloudflare R2 (UUID v4 filename, converted to JPEG)
         → Signed URL: AWS4-HMAC-SHA256, X-Amz-Expires=259200 (72h)
         → Write URL to roles.role_url
```

Base URL pattern: `https://grsai.2fe8d3f9338cf149e24da1d4bd590dd1.r2.cloudflarestorage.com/{UUID}.jpeg?...`

## Design Documentation Reference

| Document | Content |
|----------|---------|
| `整体设计.md` | Complete system design overview with data flow diagrams |
| `分析设计文档.md` | Detailed role/scene/prompt system analysis with real examples |
| `小说下载设计.md` | Novel download engine, text cleaning pipeline, DB schema |
| `智能角色提示词.md` | Character extraction prompts and three-view generation |
| `智能场景提示词.md` | Scene identification and environment description |
| `智能道具提示词.md` | Prop extraction and appearance description |
| `分镜提示词.md` | Storyboard splitting prompts (Seed Evolving) |
| `提示词设计.md` | Image prompt derivation (DeepSeek V4 Flash) full templates |
| `一键链接设计.md` | Cloud upload, URL signing, GRSai API spec |
| `doc/architecture_analysis.md` | Original PyQt6 app architecture analysis (reference only) |
| `doc/一键链接接口说明.md` | GRSai upload API interface specification |

## Code Generation Conventions

All generated code must follow the AGC tagging convention (see `~/.claude/CLAUDE.md`):

```python
# [AGC:FILE] tool=Cc author=fangkun date=YYYY-MM-DD
...
# [AGC:START] tool=Cc author=fangkun
def my_function():
    ...
# [AGC:END]
```

## Key Implementation Notes

- **Stages 1-2** are novel import/cleaning — no AI calls needed for cleaning steps 1-3
- **Storyboard splitting** (stage 4) must chunk text into ≤900-char blocks, process 4 blocks in parallel
- **Image derivation** (stage 5) is serial per shot — inject matched asset descriptions from `roles` table
- **Asset injection** matches `scripts_list.presets` JSON array entries against `roles.name`
- **`is_shot_cleaned`** is always 0 — the 4th cleaning step is not yet implemented
- **Two creation modes**: `manga` (multi-panel, `scripts_list`) and `camera` (single-shot video, `scripts_camera`) — separate tables, not polymorphic
- **Signed URLs expire in 72 hours** — need refresh mechanism
