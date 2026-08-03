from dataclasses import dataclass
from typing import Any, Dict, Optional

from models.scene_state import SceneState
from models.story_event import StoryEvent
from models.story import Story


@dataclass
class RuleContext:
    """
    Context object passed into the RuleEngine to compute effective transition rules.
    """
    previous_state: Optional[SceneState]
    current_event: StoryEvent
    story: Optional[Story] = None
    metadata: Optional[Dict[str, Any]] = None


class RuleEngine:
    """
    Resolves the effective rules for a scene transition.

    Responsibility:
        Previous State
            +
        Current Event
            +
        Story / Metadata / Base Rules
            ↓
        Effective Rules
    """

    def __init__(self, base_rules: Optional[Dict[str, Any]] = None) -> None:
        self.base_rules = base_rules or {}

    def compute_rules(self, context: RuleContext) -> Dict[str, Any]:
        """
        Compute the effective rules for this transition.

        Start from base_rules and allow future overrides based on:
        - story
        - current_event
        - previous_state
        - metadata
        """
        rules: Dict[str, Any] = dict(self.base_rules)

        # TODO: Add real rule resolution logic here.
        # Example ideas:
        # - derive pacing from story genre
        # - derive camera defaults from event type
        # - derive continuity constraints from previous_state
        # - apply user or template overrides from metadata

        return rules