from dataclasses import dataclass
from typing import Any, Dict, Optional

from models.scene_state import SceneState
from models.scene import Scene
from models.story_event import StoryEvent
from models.story import Story


@dataclass
class SceneTransitionContext:
    """
    Context object passed into the SenceEngine to compute the next SceneState.

    Attributes:
        previous_state: The previous SceneState (can be None for the very first scene).
        current_event: The current StoryEvent driving the transition.
        story_rules: Arbitrary rules/configuration that influence transitions.
        story: Optional Story object for global narrative context.
        metadata: Extra data (e.g., user choices, external signals).
    """
    previous_state: Optional[SceneState]
    current_event: StoryEvent
    story_rules: Dict[str, Any]
    story: Optional[Story] = None
    metadata: Optional[Dict[str, Any]] = None


class SenceEngine:
    """
    Scene state transition engine.

    Computes:
        Previous SceneState
            +
        Current StoryEvent
            +
        Story Rules
            ↓
        Next SceneState

    In this project, SceneState is defined in models.scene_state.SceneState as:
        - weather: str
        - lighting: str
        - danger: bool
        - food: bool
        - health: int
        - emotion: str
        - camera: CameraState
    """

    def __init__(self, default_rules: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the SenceEngine with optional default rules.

        Args:
            default_rules: A dict of default story/scene rules applied to all transitions.
        """
        self.default_rules = default_rules or {}

    def _merge_rules(self, context: SceneTransitionContext) -> Dict[str, Any]:
        """
        Merge engine-level default rules with per-transition story_rules.
        Per-transition rules override defaults.
        """
        merged = dict(self.default_rules)
        merged.update(context.story_rules or {})
        return merged

    def compute_next_state(self, context: SceneTransitionContext) -> SceneState:
        """
        Compute the next SceneState given the previous state, current event, and rules.

        High-level pipeline:
            1. Merge rules (engine defaults + per-transition).
            2. Derive each field of SceneState:
                - weather
                - lighting
                - danger
                - food
                - health
                - emotion
                - camera (CameraState)
            3. Assemble a new SceneState.

        This method is the main public API of SenceEngine.
        """
        rules = self._merge_rules(context)

        prev_state = context.previous_state

        # Derive each field; for now, placeholder logic that keeps previous values
        # or falls back to simple defaults. Replace with your real rules.

        # Weather & lighting
        weather = getattr(prev_state, "weather", "clear") if prev_state else "clear"
        lighting = getattr(prev_state, "lighting", "day") if prev_state else "day"

        # Danger / food / health / emotion
        danger = getattr(prev_state, "danger", False) if prev_state else False
        food = getattr(prev_state, "food", True) if prev_state else True
        health = getattr(prev_state, "health", 100) if prev_state else 100
        emotion = getattr(prev_state, "emotion", "neutral") if prev_state else "neutral"

        # Camera
        camera = getattr(prev_state, "camera", None)

        # TODO: Replace the above with real transition logic based on:
        #   - context.current_event
        #   - rules
        #   - context.story
        # For example:
        #   if context.current_event.type == "attack":
        #       danger = True
        #       emotion = "fear"
        #       camera.shot_type = "close_up"
        # etc.

        next_state = SceneState(
            weather=weather,
            lighting=lighting,
            danger=danger,
            food=food,
            health=health,
            emotion=emotion,
            camera=camera,
        )

        return next_state

    def build_scene_from_state(
        self,
        state: SceneState,
        event: StoryEvent,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Scene:
        """
        Optional helper to wrap a SceneState into a Scene model.

        Adjust field names to match your Scene model.
        """
        scene = Scene(
            state=state,
            triggering_event=event,
            metadata=metadata or {},
        )
        return scene
