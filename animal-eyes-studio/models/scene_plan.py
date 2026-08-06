from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List


@dataclass
class ScenePlan:
    """
    High-level planning model for a scene, derived from timeline + story bible.

    This is a pure planning module (no engines), meant to sit between:
    - TimelineScene (time-based events)
    - Scene (generation-ready detailed scene)
    """

    # Identity / ordering
    id: str
    index: int
    timeline_scene_id: int

    # Narrative
    title: str
    beat: str
    summary: str

    # World / environment
    location: str
    mood: str
    intensity: int

    # Characters (by id or name)
    main_characters: List[str]
    supporting_characters: List[str]

    # State hooks
    danger: bool
    food: bool
    health: int
    emotion: str

    # Camera / visual hints
    camera_shot_type: str
    camera_angle: str
    camera_movement: str
    camera_focus_subject: str
    camera_framing: str

    # Extra arbitrary metadata for future use
    extra: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)