"""Skills adapter — load IncidentFox-style SKILL.md skills via AgentScope LocalSkillLoader.

P0 spike 已实测:LocalSkillLoader 可零改动加载 IncidentFox 44/47 skill。
缺 frontmatter 的 3 个(observability-loki 等)会被警告跳过。
"""

from __future__ import annotations

import os
from pathlib import Path

from agentscope.skill import LocalSkillLoader, Skill


DEFAULT_SKILLS_DIR = os.getenv(
    "SKILLS_DIR",
    str(Path(__file__).resolve().parents[2] / "skills"),
)


def make_skill_loader(directory: str | Path | None = None) -> LocalSkillLoader:
    """Create a LocalSkillLoader pointing at the SKILL.md tree."""
    skills_dir = str(directory or DEFAULT_SKILLS_DIR)
    return LocalSkillLoader(skills_dir, scan_subdir=True)


async def list_available_skills(directory: str | Path | None = None) -> list[Skill]:
    """List all SKILL.md skills under `directory` (or DEFAULT_SKILLS_DIR)."""
    loader = make_skill_loader(directory)
    return await loader.list_skills()
