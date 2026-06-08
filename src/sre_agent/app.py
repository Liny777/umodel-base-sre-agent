"""umodel-base-sre-agent · AgentApp 入口 (D1)

基于 AgentScope 2.0 `create_app`,起 FastAPI(uvicorn),提供:
- POST /sessions/{id}/chat  (主动提问)
- GET  /sessions/{id}/stream (SSE 事件流)
- POST /agents              (创建 Agent)
- POST /credentials         (注入 LLM credential)
- ... (其他 AgentScope 内置端点见 /docs)

D1 设计:
- 单 Agent 形态(无 Team System)
- 工具集: 内置 Bash + LocalSkillLoader 加载 47 SKILL.md
- LLM: OpenAI-compatible 内网 gateway(LLM_BASE_URL / LLM_API_KEY env)
- 持久化: Redis (storage + message_bus)
- 沙箱: Local workspace(D2/D3 演示不上 Docker)

环境变量:
- REDIS_HOST / REDIS_PORT  (默认 localhost:6379)
- SKILLS_DIR               (默认 ../../skills/, 即 umodel-base-sre-agent/skills/)
- WORKSPACE_BASEDIR        (默认 ./workspaces)
- LLM_BASE_URL / LLM_API_KEY (D1 之后通过 POST /credentials 注入)
- SERVICE_HOST / SERVICE_PORT (默认 0.0.0.0:8000)
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware

from agentscope.app import create_app
from agentscope.app.message_bus import RedisMessageBus
from agentscope.app.storage import RedisStorage
from agentscope.app.workspace_manager import LocalWorkspaceManager


# ===== 环境 =====
load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = os.getenv("SKILLS_DIR", str(PROJECT_ROOT / "skills"))
WORKSPACE_BASEDIR = os.getenv("WORKSPACE_BASEDIR", str(PROJECT_ROOT / "workspaces"))

# 启动期校验:skill 目录存在
if not Path(SKILLS_DIR).exists():
    raise RuntimeError(
        f"SKILLS_DIR not found: {SKILLS_DIR}\n"
        f"  → P0 创建过 symlink: skills -> ../incidentfox-main/sre-agent/.claude/skills"
    )

# 确保 workspace 基目录存在(LocalWorkspaceManager 不会自动建)
Path(WORKSPACE_BASEDIR).mkdir(parents=True, exist_ok=True)


# ===== AgentApp 构造 =====
app = create_app(
    storage=RedisStorage(host=REDIS_HOST, port=REDIS_PORT),
    message_bus=RedisMessageBus(host=REDIS_HOST, port=REDIS_PORT),
    workspace_manager=LocalWorkspaceManager(
        basedir=WORKSPACE_BASEDIR,
        skill_paths=[SKILLS_DIR],  # ← P0 验证: LocalSkillLoader 零改动加载 44/47 IncidentFox skill
        # default_mcps=[]  # D3 加 MCP
    ),
    extra_middlewares=[
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
            allow_credentials=True,
        ),
    ],
    # extra_agent_middlewares=None,   # P3 加多租户工厂
    # extra_agent_tools=None,         # D1: skill 通过 workspace 自动加载,不需 tool factory
    # extra_credentials=[],           # 默认已含 OpenAI/Anthropic 等
    title="umodel-base-sre-agent",
    version="0.0.1",
)


# ===== uvicorn 入口 =====
def main() -> None:
    import uvicorn

    host = os.getenv("SERVICE_HOST", "0.0.0.0")
    port = int(os.getenv("SERVICE_PORT", "8000"))
    reload = os.getenv("SERVICE_RELOAD", "true").lower() == "true"

    print(f"\n🚀 umodel-base-sre-agent starting on http://{host}:{port}")
    print(f"   ├─ Redis: {REDIS_HOST}:{REDIS_PORT}")
    print(f"   ├─ Workspace basedir: {WORKSPACE_BASEDIR}")
    print(f"   ├─ Skills dir: {SKILLS_DIR}")
    print(f"   └─ API docs: http://{host}:{port}/docs\n")

    uvicorn.run(
        "sre_agent.app:app",
        host=host,
        port=port,
        reload=reload,
    )


if __name__ == "__main__":
    main()
