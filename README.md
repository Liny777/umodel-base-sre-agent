# umodel-base-sre-agent

> 基于 **AgentScope 2.0 Python + Runtime** 构建的多租户 SRE Agent 平台。
> 三层 Agent 编排（入口→业务→Planner+SubAgents）+ 应用ID/本体底图模型 + 确定性告警路由 + 隔离沙箱。

---

## 项目状态

| 阶段 | 描述 | 状态 |
|------|------|:---:|
| **P0** 地基 PoC ＆ API 核实 | venv · 1 个 Agent · 47 skill 验证加载 | ✅ 部分完成 |
| **P1** 三层 Team + 确定性路由 + SSE | HTTP/SSE · Team System · 确定性路由 | 🟡 进行中 |
| **P2** per-Agent skill/MCP 隔离 | 不同业务 Agent 用不同工具集 | ⬜ |
| **P3** 数据模型 + 多租户 + 发布门禁 ⭐ | 5 幕用户旅程跑通(MVP 里程碑) | ⬜ |
| **P4** Sandbox + 密钥 + 外部 A2A | Docker/gVisor · per-user 密钥 · A2A | ⬜ |
| **P5** 生产化 🚀 | 可观测 · K8s · Resumable Streams | ⬜ |

详细架构演进图：`../agent-redesign/architecture-evolution.html` · 需求 v1：`../agent-redesign/requirements-v1.md`

---

## 设计要点

- **三层 Agent (Team System)**: 入口Agent(Leader) → 业务Agent(Worker) → 业务Agent 内 Planner+SubAgents
- **应用ID + 本体底图**: 每个业务Agent 绑定一个本体底图(1~N 个 AppID 的独占集合)
- **确定性告警路由**: 按告警 AppID 查表唯一命中业务Agent(纯 Python，无 LLM)
- **per-Agent 工具隔离**: 每个 Agent 独立 Toolkit/skill/MCP 子集
- **显式发布门禁**: 应用状态 draft → published，未发布拒服务
- **复用 IncidentFox 47 个 skill 脚本**: 通过 `skills/` symlink 接入(P0 实测 `LocalSkillLoader` 零改动加载 44/47)

---

## 目录结构

```
umodel-base-sre-agent/
├── README.md                ← 本文件
├── pyproject.toml           ← 依赖 (agentscope 2.0)
├── .env.example             ← 环境变量样例
├── docker-compose.yml       ← redis + postgres (本地起)
├── src/sre_agent/
│   ├── app.py               ← create_app() 入口 (P1)
│   ├── routing/             ← 确定性路由 middleware (P1)
│   ├── agents/              ← Leader/Worker 定义 (P1)
│   ├── skills_adapter.py    ← LocalSkillLoader 包装 (P0/P1)
│   ├── models/              ← Application/OntologyBaseMap/... (P3)
│   ├── workspace/           ← Docker sandbox 配置 (P4)
│   └── observability/       ← OTel + Prom (P5)
├── skills/                  ← symlink → ../incidentfox-main/sre-agent/.claude/skills/
├── tests/
├── docs/                    ← 项目内部技术文档
└── deploy/k8s/              ← K8s manifests (P5)
```

---

## 快速开始

### 安装

```bash
# Python 3.11+
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 配置环境

```bash
cp .env.example .env
# 编辑 .env 填入 ANTHROPIC_API_KEY 等
```

### 启动本地依赖 (P1+)

```bash
docker-compose up -d redis postgres
```

### 跑 Agent (P0 验证)

```bash
python -m sre_agent.app  # 待 P1 完成后可用
```

---

## 相关项目

- **IncidentFox** (`../incidentfox-main/`) - 参考实现 / skill 脚本来源(只读)
- **agent-redesign** (`../agent-redesign/`) - 需求设计 · UI 原型 · 架构演进图 · P0 spike 报告

## License

待定
