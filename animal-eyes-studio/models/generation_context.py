from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from .story import Story
from .timeline_scene import TimelineScene
from .scene_state import SceneState


@dataclass(frozen=True)
class CharacterContext:
    """
    Flattened, scene-specific character info for downstream consumers.
    Derived from Story.character (no per-scene character state yet).
    """
    name: str
    species: Optional[str] = None
    role: Optional[str] = None
    description: Optional[str] = None

    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EnvironmentContext:
    """
    Environment context derived from SceneState + TimelineScene + Story.world.
    """
    location: str
    world_name: str
    mood: str
    intensity: int

    # From SceneState
    weather: str
    lighting: str
    danger: bool
    food: bool
    health: int
    emotion: str

    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CameraContext:
    """
    Camera-related context for visual framing, from SceneState.CameraState.
    """
    shot_type: str
    angle: str
    movement: str
    focus_subject: str
    framing: str

    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StoryContext:
    """
    Narrative context for this scene, combining Story + TimelineScene.
    """
    # Story-level
    story_id: str
    story_title: str
    story_niche: str
    story_type: str
    overall_duration: int

    # Scene-level (from TimelineScene)
    scene_id: int
    time_label: str
    scene_start_time: float
    scene_end_time: float
    scene_duration: float
    scene_event: str
    scene_summary: str
    scene_mood: str
    scene_intensity: int
    scene_location: str

    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RulesContext:
    """
    Resolved rules for this scene, already evaluated by RuleEngine.
    Structure is intentionally generic.
    """
    visual_rules: Dict[str, Any] = field(default_factory=dict)
    narrative_rules: Dict[str, Any] = field(default_factory=dict)
    technical_rules: Dict[str, Any] = field(default_factory=dict)
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GenerationContext:
    """
    Immutable, fully-assembled context for a single scene generation step.

    This is the only object downstream modules (ScenePlanner, PromptGenerator,
    ScriptGenerator) need to consume.
    """
    story: StoryContext
    character: CharacterContext
    environment: EnvironmentContext
    camera: CameraContext
    rules: RulesContext

    # Optional: keep references to original models for traceability.
    _story: Story = field(repr=False, compare=False)
    _timeline_scene: TimelineScene = field(repr=False, compare=False)
    _scene_state: SceneState = field(repr=False, compare=False)
    _resolved_rules: Dict[str, Any] = field(repr=False, compare=False)
