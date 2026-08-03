from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List, Protocol

from models.story import Story
from models.timeline_scene import TimelineScene
from models.scene_state import SceneState
from models.generation_context import (
    GenerationContext,
    StoryContext,
    CharacterContext,
    EnvironmentContext,
    CameraContext,
    RulesContext,
)


class ContextValidationError(Exception):
    """Raised when required fields for GenerationContext are missing or invalid."""
    pass


class ContextNormalizer(Protocol):
    """
    Extension point for normalization strategies.

    Implementations can adjust raw values before building the context.
    They MUST NOT mutate the input objects.
    """

    def normalize(
        self,
        story: Story,
        timeline_scene: TimelineScene,
        scene_state: SceneState,
        resolved_rules: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Return a dict of normalized overrides or derived values.

        Convention:
        {
            "story": {...},
            "character": {...},
            "environment": {...},
            "camera": {...},
            "rules": {...},
        }
        """
        ...


class ContextValidator(Protocol):
    """
    Extension point for additional validation rules.
    """

    def validate(self, context: GenerationContext) -> None:
        """
        Raise ContextValidationError if invalid.
        """
        ...


class DefaultContextValidator:
    """
    Minimal built-in validation for critical fields.
    """

    def validate(self, context: GenerationContext) -> None:
        missing: List[str] = []

        if not context.story.story_title:
            missing.append("story.story_title")
        if context.story.scene_id is None:
            missing.append("story.scene_id")
        if not context.character.name:
            missing.append("character.name")

        if missing:
            raise ContextValidationError(
                f"Missing required fields in GenerationContext: {', '.join(missing)}"
            )


class ContextBuilder:
    """
    Service responsible for constructing a GenerationContext from upstream models.

    Responsibilities:
    - Assemble data from Story, TimelineScene, SceneState, ResolvedRules
    - Normalize values (via optional normalizers)
    - Validate required fields (via validators)
    - Return an immutable GenerationContext

    It MUST NOT:
    - Generate prompts
    - Call GPT or external LLMs
    - Modify Story, TimelineScene, SceneState, or ResolvedRules
    """

    def __init__(
        self,
        normalizers: List[ContextNormalizer] | None = None,
        validators: List[ContextValidator] | None = None,
    ) -> None:
        self._normalizers = normalizers or []
        self._validators = validators or [DefaultContextValidator()]

    def build(
        self,
        story: Story,
        timeline_scene: TimelineScene,
        scene_state: SceneState,
        resolved_rules: Dict[str, Any],
    ) -> GenerationContext:
        """
        Public API: build a GenerationContext for a single scene.
        """
        # 1. Collect normalized overrides (non-mutating)
        normalized_overrides: Dict[str, Any] = {}
        for normalizer in self._normalizers:
            overrides = normalizer.normalize(
                story=story,
                timeline_scene=timeline_scene,
                scene_state=scene_state,
                resolved_rules=resolved_rules,
            )
            normalized_overrides.update(overrides or {})

        # 2. Assemble sub-contexts
        story_ctx = self._build_story_context(
            story=story,
            timeline_scene=timeline_scene,
            overrides=normalized_overrides.get("story", {}),
        )
        character_ctx = self._build_character_context(
            story=story,
            overrides=normalized_overrides.get("character", {}),
        )
        environment_ctx = self._build_environment_context(
            story=story,
            timeline_scene=timeline_scene,
            scene_state=scene_state,
            overrides=normalized_overrides.get("environment", {}),
        )
        camera_ctx = self._build_camera_context(
            scene_state=scene_state,
            overrides=normalized_overrides.get("camera", {}),
        )
        rules_ctx = self._build_rules_context(
            resolved_rules=resolved_rules,
            overrides=normalized_overrides.get("rules", {}),
        )

        # 3. Create immutable GenerationContext
        context = GenerationContext(
            story=story_ctx,
            character=character_ctx,
            environment=environment_ctx,
            camera=camera_ctx,
            rules=rules_ctx,
            _story=story,
            _timeline_scene=timeline_scene,
            _scene_state=scene_state,
            _resolved_rules=resolved_rules,
        )

        # 4. Validate
        for validator in self._validators:
            validator.validate(context)

        return context

    # ---- Internal builders (no business logic, just mapping/normalization) ----

    def _build_story_context(
        self,
        story: Story,
        timeline_scene: TimelineScene,
        overrides: Dict[str, Any],
    ) -> StoryContext:
        ctx = StoryContext(
            story_id=story.story_id,
            story_title=story.title.strip(),
            story_niche=story.niche,
            story_type=story.story_type,
            overall_duration=story.duration,
            scene_id=timeline_scene.scene_id,
            time_label=timeline_scene.time,
            scene_start_time=timeline_scene.start_time,
            scene_end_time=timeline_scene.end_time,
            scene_duration=timeline_scene.duration,
            scene_event=timeline_scene.event,
            scene_summary=timeline_scene.summary,
            scene_mood=timeline_scene.mood,
            scene_intensity=timeline_scene.intensity,
            scene_location=timeline_scene.location,
            extra={},
        )

        return StoryContext(**{**asdict(ctx), **overrides})

    def _build_character_context(
        self,
        story: Story,
        overrides: Dict[str, Any],
    ) -> CharacterContext:
        character_model = story.character

        name = getattr(character_model, "name", None)
        species = getattr(character_model, "species", None)
        role = getattr(character_model, "role", None)
        description = getattr(character_model, "description", None)

        ctx = CharacterContext(
            name=(name or "").strip(),
            species=species,
            role=role,
            description=description,
            extra={},
        )

        return CharacterContext(**{**asdict(ctx), **overrides})

    def _build_environment_context(
        self,
        story: Story,
        timeline_scene: TimelineScene,
        scene_state: SceneState,
        overrides: Dict[str, Any],
    ) -> EnvironmentContext:
        world_model = story.world

        ctx = EnvironmentContext(
            location=timeline_scene.location,
            world_name=getattr(world_model, "name", ""),
            mood=timeline_scene.mood,
            intensity=timeline_scene.intensity,
            weather=scene_state.weather,
            lighting=scene_state.lighting,
            danger=scene_state.danger,
            food=scene_state.food,
            health=scene_state.health,
            emotion=scene_state.emotion,
            extra={},
        )

        return EnvironmentContext(**{**asdict(ctx), **overrides})

    def _build_camera_context(
        self,
        scene_state: SceneState,
        overrides: Dict[str, Any],
    ) -> CameraContext:
        cam_state = scene_state.camera

        ctx = CameraContext(
            shot_type=cam_state.shot_type,
            angle=cam_state.angle,
            movement=cam_state.movement,
            focus_subject=cam_state.focus_subject,
            framing=cam_state.framing,
            extra={},
        )

        return CameraContext(**{**asdict(ctx), **overrides})

    def _build_rules_context(
        self,
        resolved_rules: Dict[str, Any],
        overrides: Dict[str, Any],
    ) -> RulesContext:
        visual = resolved_rules.get("visual", {})
        narrative = resolved_rules.get("narrative", {})
        technical = resolved_rules.get("technical", {})

        ctx = RulesContext(
            visual_rules=visual,
            narrative_rules=narrative,
            technical_rules=technical,
            raw=resolved_rules,
        )

        return RulesContext(**{**asdict(ctx), **overrides})
