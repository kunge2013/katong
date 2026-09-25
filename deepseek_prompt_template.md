# 📋 雪漫画 DeepSeek API 完整提示词模板与变量模块

// [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

---

## 🎯 API 调用基本信息

| 项目 | 值 |
|------|-----|
| **接口地址** | `https://api.deepseek.com/chat/completions` |
| **模型名称** | `deepseek-v4-flash` |
| **HTTP 方法** | POST |
| **Content-Type** | `application/json` |
| **Authorization** | `Bearer <API_KEY>` |
| **HTTP 库** | `requests`（Python） |

---

## 📦 完整请求报文结构

```json
{
  "model": "deepseek-v4-flash",
  "messages": [
    {
      "role": "system",
      "content": "<系统提示词 - 从 prompts 表 Fernet 解密>"
    },
    {
      "role": "user", 
      "content": "<组装的用户消息 - 包含所有变量模块>"
    }
  ],
  "temperature": 0.7,
  "stream": true,
  "max_tokens": 4000
}
```

---

## 🔧 系统提示词模板（System Prompt）

### 来源：prompts 表（Fernet 加密存储）

| ID | 类别 | 标题 | 用途 |
|----|------|------|------|
| 1 | 场景描述 | 小说视频提示词指南 | 定义漫画分镜生成规范 |
| 2 | 角色设定 | 提取角色描述 | 从小说文本提取角色信息 |
| 3 | 角色设定 | 角色生成图像 | 角色视觉描述模板 |
| 4 | 角色设定 | 对话生成视频 | 对话场景处理 |
| 5 | 画风描述 | 图片视频生成默认前缀 | 画风前缀 |
| 6 | 角色设定 | 图片视频生成默认后缀 | 画风后缀 |
| 7 | 角色设定 | 视频视频生成默认前缀 | 视频前缀 |
| 8 | 角色设定 | 视频视频生成默认后缀 | 视频后缀 |
| 9 | 场景描述 | （场景模板1） | 场景描述变体 |
| 10 | 场景描述 | （场景模板2） | 场景描述变体 |
| 11 | 对话生成 | （对话模板） | 对话生成规则 |
| 12 | 情节发展 | （情节模板） | 情节推进规则 |
| 13 | VIP | （VIP专用模板） | VIP功能 |

### 系统提示词示例（推断结构）

```
你是一个专业的漫画分镜提示词生成专家。请根据以下要求生成图像提示词：

【核心规范】
1. 画风：韩系商业条漫画风，2D清透上色，全彩画面
2. 文字UI：统一使用白底黑边黑字的旁白框与对白框
3. 禁止事项：不得出现腾讯动漫、17173等水印
4. 字体规范：正文黑字#1a1a1a，字号常规，不因情绪变色

【构图要求】
- 根据剧情选择合适的分格方式（主格+辅格、蒙太奇、纵向条漫等）
- 说明阅读动线（Z字形、纵向等）
- 标注视觉焦点和情绪转折

【角色一致性】
- 严格遵循角色描述中的外貌、服装、配饰细节
- 保持角色在不同场景中的一致性

【输出格式】
1. 画面描述（场景、人物、构图、光影）
2. 版式说明（分格安排、阅读动线、视觉焦点）
3. 文字UI规范（旁白框、对白框位置和样式）
4. 禁止事项
```

---

## 📝 用户消息模板（User Message）

### 完整组装结构

```
【项目配置】
{PROJECT_CONFIG}

【剧情文本】
{STORY_CONTENT}

【出场角色】
{CHARACTER_LIST}

【角色详细描述】
{CHARACTER_DESCRIPTIONS}

【画风前缀】
{IMG_PROMPT_PREFIX}

【自定义指令】
{CUSTOM_INSTRUCTIONS}

【画风后缀】
{IMG_PROMPT_SUFFIX}
```

---

## 🔍 变量模块详解

### 1️⃣ PROJECT_CONFIG（项目配置）

**来源**：`projects` 表的 `manga_gen_models` 字段（JSON格式）

```json
{
  "manga_inference_model_default": "DeepSeek V4 Flash（思考）",
  "manga_image_provider": "grsai",
  "manga_image_remote_model": "nano-banana-2",
  "manga_image_remote_aspect_ratio": "3:4",
  "manga_image_remote_resolution": "2K",
  "manga_uumoshi_provider_route": "",
  "derive_preset": "plot_manga_fusion_bw"
}
```

**字段说明**：
| 字段 | 说明 | 示例值 |
|------|------|--------|
| `manga_inference_model_default` | 推理模型 | DeepSeek V4 Flash（思考） |
| `manga_image_provider` | 图像生成服务商 | grsai |
| `manga_image_remote_model` | 图像模型 | nano-banana-2 |
| `manga_image_remote_aspect_ratio` | 图像比例 | 3:4 |
| `manga_image_remote_resolution` | 分辨率 | 2K |
| `derive_preset` | 推导预设 | plot_manga_fusion_bw |

---

### 2️⃣ STORY_CONTENT（剧情文本）

**来源**：`scripts_list` 表的 `content` 字段

**示例**：
```
男友家里A8，却格外抠门。恋爱三年，一起吃饭时，连一包餐巾纸的钱都要和我AA。
```

**特点**：
- 每条剧情通常为一句话或一段话
- 包含人物动作、对话、情节推进
- 是生成图像提示词的核心输入

---

### 3️⃣ CHARACTER_LIST（出场角色列表）

**来源**：`scripts_list` 表的 `presets` 字段（JSON数组）

**示例**：
```json
["裴濯", "阿晚", "裴濯"]
```

**说明**：
- 数组元素为角色名称
- 可能有重复（表示同一角色在多个镜头中出现）
- 用于匹配角色详细描述

---

### 4️⃣ CHARACTER_DESCRIPTIONS（角色详细描述）

**来源**：`roles` 表的 `content` 字段（按 `presets` 匹配）

**示例**：

#### 角色：阿晚
```
一个24岁的现代温柔系年轻女性, 天生冷白皮, 皮肤细腻通透泛着柔和光泽, 鹅蛋脸型, 
圆圆的杏眼清澈水润, 眼神温柔干净, 精致淡雅的妆容, 浅番茄色唇色, 黑棕色长发微卷
自然垂落胸前, 几缕发丝别在耳后, 身穿米白色粗花呢小香风外套, 外套镶着金色细边
纽扣, 内搭浅杏色真丝衬衫, 下着浅咖色高腰阔腿裤, 脚穿米白色尖头低跟鞋, 配珍珠
耳钉和细铂金锁骨链, 整个人气质温婉恬静。
```

#### 角色：裴濯
```
一个25岁的现代斯文男性, 冷白皮但略显清瘦, 脸型偏窄长, 下颌线清晰, 细长内双眼型, 
眼神温和却带点疏离, 干净自然的轻裸妆感, 黑色短发梳理整齐侧分, 刘海微遮额头, 
身穿藏青色单排扣羊毛西装外套, 内搭白色挺括衬衫, 领口扣到最上面, 下着黑色西裤, 
裤线笔直, 脚穿黑色系带皮鞋, 手腕佩戴一枚精钢表盘腕表, 整体气质文质彬彬但略显拘谨。
```

#### 角色：林依依
```
一个24岁的现代甜美娇俏女性, 肤色白嫩透粉, 小巧瓜子脸, 桃花眼眼尾微翘, 眼神含情
带俏, 妆容精致明艳, 蜜桃色眼影晕染, 水光粉唇, 睫毛卷翘浓密, 浅棕色长卷发随意
披散在肩, 发尾打卷轻盈, 身穿丁香紫粗花呢小香风短外套, 内搭白色蕾丝吊带背心, 
下着同色系包臀短裙, 裙摆微开叉, 脚穿裸色漆皮细高跟鞋, 颈间一条玫瑰金钻石锁骨
项链, 耳垂坠着细闪耳环, 整体气质娇矜甜媚。
```

**描述结构**：
```
{年龄}岁的{类型}性, 
{皮肤特征}, {脸型}, {眼型}, {眼神}, {妆容}, 
{发型}, {上装}, {内搭}, {下装}, {鞋子}, 
{配饰1}, {配饰2}, {整体气质}
```

---

### 5️⃣ IMG_PROMPT_PREFIX（画风前缀）

**来源**：`projects` 表的 `img_prompt_prefix` 字段

**当前状态**：项目15此字段为空

**推测示例**（基于生成的提示词）：
```
白底黑边黑字漫画分镜，白底黑边黑字的旁白框与对白框作为文字UI，
```

---

### 6️⃣ CUSTOM_INSTRUCTIONS（自定义指令）

**来源**：`settings` 表

| 配置项 | 说明 | 当前值 |
|--------|------|--------|
| `manga_derive_custom_instruction` | 主自定义指令 | （空） |
| `manga_derive_custom_instruction_1` | 自定义指令1 | （空） |
| `manga_derive_custom_instruction_2` | 自定义指令2 | （空） |
| `manga_derive_custom_instruction_3` | 自定义指令3 | （空） |
| `manga_derive_custom_instruction_4` | 自定义指令4 | （空） |
| `manga_derive_custom_instruction_5` | 自定义指令5 | （空） |
| `manga_derive_custom_instruction_6` | 自定义指令6 | （空） |
| `vip_role_derive_custom_prompt_1` | VIP角色自定义提示 | （Fernet加密） |

**用途**：用户可添加额外的生成要求，如：
- 特定画风要求
- 禁止元素
- 特殊效果

---

### 7️⃣ IMG_PROMPT_SUFFIX（画风后缀）

**来源**：`projects` 表的 `img_prompt_suffix` 字段

**当前状态**：项目15此字段为空

**推测示例**（基于生成的提示词）：
```
禁止：图片右下角出现腾讯动漫 17173 等其他机构水印！
```

---

## 🔄 完整数据流

```
┌─────────────────────────────────────────────────────────────────┐
│                    提示词组装流程                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. 用户点击"智能推导"按钮                                        │
│     ↓                                                            │
│  2. 从 scripts_list 读取分镜数据                                  │
│     ├── content (剧情文本)                                       │
│     ├── presets (出场角色列表)                                   │
│     └── shot_id (分镜ID)                                         │
│     ↓                                                            │
│  3. 从 roles 表匹配角色描述                                       │
│     └── content (角色详细描述)                                   │
│     ↓                                                            │
│  4. 从 projects 表读取项目配置                                    │
│     ├── manga_gen_models (模型配置)                              │
│     ├── img_prompt_prefix (画风前缀)                             │
│     └── img_prompt_suffix (画风后缀)                             │
│     ↓                                                            │
│  5. 从 settings 表读取自定义指令                                  │
│     └── manga_derive_custom_instruction_* (6个插槽)              │
│     ↓                                                            │
│  6. 从 prompts 表解密系统提示词                                   │
│     └── Fernet 解密 → 系统提示词模板                             │
│     ↓                                                            │
│  7. 组装完整请求                                                  │
│     {                                                            │
│       "model": "deepseek-v4-flash",                             │
│       "messages": [                                              │
│         {"role": "system", "content": "<系统提示词>"},          │
│         {"role": "user", "content": "<组装的用户消息>"}         │
│       ]                                                          │
│     }                                                            │
│     ↓                                                            │
│  8. 调用 DeepSeek API                                            │
│     └── POST https://api.deepseek.com/chat/completions          │
│     ↓                                                            │
│  9. 接收流式响应                                                  │
│     └── 拼接完整的图像提示词                                     │
│     ↓                                                            │
│ 10. 存储结果                                                     │
│     └── scripts_list.image_prompt 字段                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 实际生成的提示词示例

### 输入

```
【剧情】男友家里A8，却格外抠门。恋爱三年，一起吃饭时，连一包餐巾纸的钱都要和我AA。
【角色】["裴濯", "阿晚", "裴濯"]
【配置】DeepSeek V4 Flash（思考）, 3:4比例, 2K分辨率
```

### 输出（600字）

```
现代都市剧情漫画单页，白底黑边黑字的旁白框与对白框作为文字UI，但本镜不采用固定双格
上下七三分，而采用非对称主格加插格。左侧约三分之二宽幅主格：傍晚高端商圈内餐厅靠窗位，
阿晚从侧后方入前景，肩线略虚化，她穿米白色粗花呢小香风外套、浅杏色真丝衬衫，黑棕色微卷
长发垂落胸前，神情温婉却微微发怔；对面裴濯穿藏青色修身羊毛西装、白衬衫扣到最上，坐姿
笔直，冷白皮单眼皮，眉眼疏离，正低头看手机。桌面有简餐、两杯水、一包未拆白色餐巾纸、
账单和亮着冷光的手机。主格右下竖长插格为桌面俯拍特写：修长手指拿着手机，屏幕显示AA
收款金额，餐巾纸压住账单，金额"餐巾纸 2.00 每人 1.00"清晰可见。左下小插格为阿晚手部
与手机特写，她指腹停在确认键上方，珍珠耳钉和银色锁骨链泛着微光。整体暖灰低饱和，窗外
蓝紫暮色与室内暖黄吊灯对撞，冷白手机光成为视觉焦点，突出亲密关系被一包餐巾纸切割的
荒诞与疏离。

白底黑边黑字旁白框：左上第一框「男友家里A8，却格外抠门。」；主格右上第二框「恋爱三年，
一起吃饭时，连一包餐巾纸的钱都要和我AA。」；桌面插格旁小对白框：裴濯「纸巾两元，一人
一元。」；阿晚无对白，仅一个省略号小框「……」置于左下插格旁。所有文字框均为白底、黑边、
黑字，直角或微圆角，阅读动线从左上旁白到主格桌面，再到右上插格金额，最后落到左下阿晚
手部。

禁止：图片右下角出现腾讯动漫 17173 等其他机构水印！
```

---

## 🎨 提示词结构分析

生成的图像提示词包含以下要素：

| 要素 | 占比 | 说明 | 示例 |
|------|------|------|------|
| **画面描述** | 40% | 场景、人物、构图、光影 | 傍晚高端商圈内餐厅靠窗位... |
| **版式说明** | 40% | 分格安排、阅读动线、视觉焦点 | 左侧约三分之二宽幅主格... |
| **文字UI** | 15% | 旁白框、对白框位置和样式 | 白底黑边黑字旁白框... |
| **禁止事项** | 5% | 排除项 | 禁止水印... |

---

## 🔐 加密保护机制

### Fernet 加密数据格式

```
v2:gAAAAABqtMK5SNECut-AbPM9BED_nsHwI62AjMl5XcrnrWNeAl0UIE08u3xTI-A2aP7L...
```

**结构**：
- `v2:` - 版本标识
- `gAAAAAB...` - Base64编码的加密数据
- 加密算法：Fernet（AES-128-CBC + HMAC-SHA256）
- 密钥：嵌入在 `cinegacha.utils.machine_password_crypto` 模块中

### 加密字段清单

| 表 | 字段 | 说明 |
|----|------|------|
| `settings` | `account_pool_deepseek_api_key` | API密钥 |
| `settings` | `enable_deepseek_service` | 服务开关 |
| `settings` | `manga_inference_model_default` | 模型选择 |
| `settings` | `manga_derive_llm_raw_log` | 日志开关 |
| `settings` | `manga_derive_preset_id` | 预设ID |
| `settings` | `derive_custom_slot_label_*` | 自定义标签 |
| `settings` | `vip_role_derive_custom_prompt_1` | VIP提示 |
| `prompts` | `content` | 系统提示词 |

---

## 📁 关键代码模块

| 模块名 | 功能 |
|--------|------|
| `cinegacha.core.llm_client` | 统一LLM调用接口 |
| `cinegacha.core.context_generator` | 上下文组装器 |
| `cinegacha.core.manga_derive_presets` | 推导预设 |
| `cinegacha.core.manga_derive_prompt_defaults` | 提示词默认值 |
| `cinegacha.core.manga_derive_affix_store` | 前后缀存储 |
| `cinegacha.core.inference_derive_prompt_presets` | 推理提示预设 |
| `cinegacha.utils.machine_password_crypto` | Fernet加密/解密 |
| `cinegacha.core.builtin_prompts_seed` | 内置提示词种子 |
| `cinegacha.core.builtin_prompt_guard` | 提示词保护 |

---

## 🛠️ 技术栈总结

| 组件 | 技术 |
|------|------|
| 编程语言 | Python 3.9 |
| HTTP库 | requests |
| 数据库 | SQLite3 |
| 加密 | cryptography.fernet |
| GUI | PyQt6 |
| 打包 | PyInstaller |
| 代码保护 | PyArmor |
| AI推理 | DeepSeek V4 Flash |
| 图像生成 | nano-banana-2 (grsai) |

---

## 💡 关键发现

1. **模型名称**：`deepseek-v4-flash`（非 `deepseek-chat`）
2. **HTTP库**：`requests`（非 `aiohttp`）
3. **变量模块**：7个核心模块 + 7个自定义指令插槽
4. **角色描述**：标准化格式（年龄+外貌+服装+配饰+气质）
5. **加密保护**：Fernet对称加密，密钥嵌入编译代码
6. **推导质量**：每个分镜455-1270字，包含专业漫画术语

---

// [AGC:END]
