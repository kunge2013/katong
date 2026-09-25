# 雪漫画 DeepSeek API 调用分析

## 📊 调用概览

**功能名称**：智能推导（分镜推导）  
**API 端点**：`https://api.deepseek.com/chat/completions`  
**使用模型**：`DeepSeek V4 Flash（思考）`  
**远程 IP**：`119.96.17.175`

---

## 🔍 Fiddler 捕获结果

### TLS 连接信息
```
目标域名：api.deepseek.com
目标 IP：119.96.17.175
协议版本：TLS 1.2 / TLS 1.3
ALPN：http/1.1
加密套件：TLS_AES_256_GCM_SHA384（推荐）
```

### 连接特征
- 建立了 **4 个独立 TLS 连接**（会话 ID: 47, 49, 50, 51）
- 连接时间：14:15:31 - 14:15:43（约 12 秒内）
- 可能用于并发请求或重试机制

---

## 📦 请求报文结构（推断）

基于数据库分析和架构文档，发送给 DeepSeek 的请求格式如下：

```json
{
  "model": "deepseek-chat",  // 或 "deepseek-reasoner"（思考模式）
  "messages": [
    {
      "role": "system",
      "content": "<系统提示词 - 从 prompts 表解密>"
    },
    {
      "role": "user",
      "content": "<组装的上下文内容>"
    }
  ],
  "temperature": 0.7-1.0,  // 推测值
  "stream": true,  // 可能启用流式响应
  "max_tokens": 2000-4000  // 推测值
}
```

---

## 🎯 上下文组装内容

### 1️⃣ **小说/剧情文本**
从 `novels` 表读取，包含：
- 项目 ID 15《富门铁公鸡》的剧情大纲
- 分镜文本（storyboard_text）

**示例内容**：
```
女主阿晚与男友裴濯相恋三年，裴濯家境优渥却事事AA，还纵容女兄弟林依依暧昧。
见家长途中，他又提出彩礼AA，阿晚意外看到弹幕得知是"考验"，便留在服务区改上
裴濯好友江辞之的车并提分手...
```

### 2️⃣ **角色视觉描述**
从 `roles` 表读取，包含详细的外貌、服装、气质描述：

**示例角色**：
```json
{
  "name": "纪澄青年",
  "description": "古代南州飒爽女子，18岁，体态匀称矫健，鹅蛋脸线条利落，
    肤色深蜜色且油亮健康，像常年凫水晒出的小黑鱼般紧致有光泽；
    一双杏眼大而明亮，眼尾微微上挑，乌黑瞳仁目光灼灼...
    服装是石榴红暗纹窄袖短襦..."
}
```

### 3️⃣ **系统提示词**（从 prompts 表，Fernet 加密）
- **Prompt ID 1**: 场景描述指令（"小说视频提示词指令"）
- **Prompt ID 2-8**: 角色设定指令（"获取人物形象"、"角色三视图"等）
- **Prompt ID 5**: 图片推导词前缀（"图片推导词默认前缀"）

### 4️⃣ **项目配置参数**
```json
{
  "manga_inference_model_default": "DeepSeek V4 Flash（思考）",
  "manga_image_provider": "grsai",
  "manga_image_remote_model": "nano-banana-2",
  "manga_image_remote_aspect_ratio": "3:4",
  "manga_image_remote_resolution": "2K",
  "derive_preset": "plot_manga_fusion_bw"
}
```

### 5️⃣ **自定义指令**（可选）
- `manga_derive_custom_instruction`（主指令）
- `manga_derive_custom_instruction_1` 到 `_6`（6 个额外插槽）
- `vip_role_derive_custom_prompt_1`（VIP 角色自定义提示）

---

## 🔐 加密保护机制

### 三层防护
1. **PyArmor 字节码加密**：所有 Python 源码加密
2. **Fernet 对称加密**：敏感数据（API Key、提示词）加密存储
3. **原生模块守卫**：`xmh_guard.pyd` 反调试/反篡改

### 加密数据示例
```
API Key: v2:gAAAAABqtMJmeO8Q8bncpDHIN7Na-6nab8mg...
系统提示词: v2:gAAAAABqtMK5SNECut-AbPM9BED_nsHwI62AjMl5X...
```

**加密密钥**：嵌入在编译后的应用代码中（`cinegacha.utils.machine_password_crypto`）

---

## 🔄 完整工作流程

```
1. 用户点击"智能推导"按钮
   ↓
2. 应用从 SQLite 读取：
   - 项目配置（模型、画幅、分辨率）
   - 小说/剧情文本
   - 角色描述
   - 系统提示词（Fernet 解密）
   - API Key（Fernet 解密）
   ↓
3. context_generator 模块组装上下文：
   - 拼接剧情 + 角色 + 提示词 + 自定义指令
   ↓
4. llm_client 模块发送 HTTPS POST 请求：
   - 目标：https://api.deepseek.com/chat/completions
   - Header: Authorization: Bearer <解密后的 API Key>
   - Body: JSON 格式（model + messages + params）
   ↓
5. DeepSeek 返回生成的分镜提示词
   ↓
6. 应用解析响应，用于后续图片生成（grsai）
```

---

## 📋 数据库关键字段

### settings 表
| 键名 | 用途 | 加密 |
|------|------|------|
| `account_pool_deepseek_api_key` | DeepSeek API 密钥 | ✅ Fernet |
| `enable_deepseek_service` | 是否启用 DeepSeek | ✅ Fernet |
| `manga_inference_model_default` | 默认推理模型 | ✅ Fernet |
| `manga_derive_llm_raw_log` | 原始日志开关 | ✅ Fernet |

### prompts 表
| ID | 分类 | 用途 |
|----|------|------|
| 1 | 场景描述 | 小说视频提示词指令 |
| 2-4,6-8 | 角色设定 | 人物形象/三视图提示 |
| 5 | 画风描述 | 图片推导词前缀 |

### projects 表
存储项目级配置（JSON 格式在 `config` 字段）

---

## 🛠️ 技术栈

- **HTTP 客户端**：`aiohttp` + `asyncio`（异步并发）
- **加密库**：`cryptography.fernet`
- **数据库**：SQLite3
- **打包工具**：PyInstaller
- **代码保护**：PyArmor

---

## 💡 关键发现

1. **多连接策略**：短时间内建立多个 TLS 连接，可能用于并发处理多个分镜
2. **深度加密**：从源码到数据全链路加密，难以逆向
3. **模块化设计**：
   - `llm_client`：统一 LLM 调用接口
   - `context_generator`：上下文组装
   - `manga_derive_*`：推导专用模块
4. **OpenAI 兼容协议**：使用标准 `/chat/completions` 端点
5. **思考模式**：使用 `DeepSeek V4 Flash（思考）`，可能启用 extended thinking

---

## 🔧 调试建议

如需查看完整报文，可尝试：

1. **启用应用内日志**：
   - 修改 `manga_derive_llm_raw_log` 设置（需 Fernet 密钥）

2. **运行时 Hook**：
   - 注入 `cinegacha.core.llm_client` 模块记录请求

3. **内存转储**：
   - PyArmor 运行时解密后提取字节码

4. **证书固定绕过**：
   - 应用可能使用 certifi 或自定义 CA bundle
   - 需修改应用的 SSL 验证逻辑

---

**生成时间**：2026-09-25  
**分析工具**：Fiddler Everywhere + SQLite3 + 代码库分析
