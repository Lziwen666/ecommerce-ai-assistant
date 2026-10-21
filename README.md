# 电商运营 AI 助手

一个简单、易上手、适合开源展示的电商售后 AI 客服 Demo。项目支持两种运行模式：

- **无 API Key 模式**：基于本地 FAQ 知识库进行关键词匹配，开箱即用。
- **大模型模式**：配置 OpenAI 兼容接口后，由大模型结合知识库生成更自然的回答。

适合用于课程作业、毕业设计原型、简历项目、电商客服 Demo、RAG 入门练习。

## 功能特性

- 网页聊天界面
- 常见售后问题快速回复
- 发货、退换货、换货、运费、保修、发票、订单修改等知识库
- 快捷问题按钮
- 本地 JSON 知识库，可直接修改
- 无 API Key 也能完整演示
- 可选接入 OpenAI 兼容大模型接口
- FastAPI 单后端，结构简单，方便二次开发

## 项目结构

```text
ecommerce-ai-assistant/
├── app/
│   ├── __init__.py
│   └── main.py              # FastAPI 后端接口
├── data/
│   └── faq.json             # FAQ 知识库
├── static/
│   ├── index.html           # 聊天页面
│   ├── style.css            # 页面样式
│   └── app.js               # 前端交互逻辑
├── .env.example             # 环境变量示例
├── .gitignore
├── LICENSE
├── requirements.txt
└── README.md
```

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/你的用户名/ecommerce-ai-assistant.git
cd ecommerce-ai-assistant
```

### 2. 创建虚拟环境

Windows：

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS / Linux：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 启动服务

```bash
uvicorn app.main:app --reload
```

浏览器打开：

```text
http://127.0.0.1:8000
```

接口文档：

```text
http://127.0.0.1:8000/docs
```

## 可选：接入大模型

复制环境变量文件：

```bash
copy .env.example .env
```

Windows PowerShell 也可以使用：

```powershell
Copy-Item .env.example .env
```

然后编辑 `.env`：

```env
OPENAI_API_KEY=你的API_KEY
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

如果你使用其他 OpenAI 兼容服务商，只需替换 `OPENAI_BASE_URL` 和 `OPENAI_MODEL`。

没有 API Key 时，系统会自动回退到本地 FAQ 模式。

## 修改知识库

编辑 `data/faq.json`：

```json
{
  "id": "coupon",
  "keywords": ["优惠券", "满减", "折扣"],
  "question": "店铺优惠券怎么使用？",
  "answer": "下单时在结算页选择可用优惠券，系统会自动抵扣符合条件的订单。"
}
```

字段说明：

- `id`：问题唯一标识
- `keywords`：用户可能输入的关键词
- `question`：标准问题
- `answer`：标准回答

修改后重启服务即可生效。

## API 示例

请求：

```bash
curl -X POST http://127.0.0.1:8000/api/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"message\":\"什么时候发货？\",\"history\":[],\"use_ai\":true}"
```

响应示例：

```json
{
  "reply": "现货商品一般在付款后 24 小时内发出……",
  "source": "faq_fallback",
  "matched_faq": "shipping_time"
}
```

## 后续可扩展方向

- 接入真实向量数据库，实现语义检索 RAG
- 增加订单号查询和订单状态接口
- 增加客服后台审核页面
- 增加多店铺知识库配置
- 接入飞书、钉钉、微信客服或网页在线客服
- 增加用户会话存储和数据库
- 容器化部署到 Docker / 云服务器
- 增加回答引用来源和置信度
- 增加敏感词检测与转人工策略

## 技术栈

- Python
- FastAPI
- Pydantic
- 原生 HTML / CSS / JavaScript
- OpenAI Compatible API

## 开源协议

本项目基于 [MIT License](./LICENSE) 开源，可自由学习、修改和用于个人项目。商业使用前请自行评估业务合规性和客服承诺风险。
