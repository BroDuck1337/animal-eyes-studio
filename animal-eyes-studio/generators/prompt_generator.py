from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from generators.scene_generator import ScenePlan
from models.generation_context import GenerationContext


@dataclass(frozen=True)
class PromptBundle:
    """
    Container for all prompts required to generate a single scene.

    This keeps the PromptGenerator output structured and easy to extend
    without changing the public API of PromptGenerator itself.
    """

    visual_prompt: str
    """High-level visual prompt for the video/image generator."""

    narrative_prompt: str
    """Supporting prompt that can be used for narration or script generation."""

    technical_prompt: str
    """Technical guidance for the video generator (camera, pacing, transitions)."""


class PromptGenerator:
    """
    PromptGenerator converts a ScenePlan into concrete prompt strings that
    downstream video or image generators can consume.

    Responsibilities
    ----------------
    - Translate structured planning decisions from ScenePlan into
      human-readable, deterministic prompt text.
    - Keep prompt construction logic centralized and testable.
    - Remain deterministic: no randomness, no external inference.

    Non-responsibilities
    --------------------
    - Does NOT call any LLM.
    - Does NOT modify GenerationContext or ScenePlan.
    - Does NOT perform story planning (that is the responsibility of
      ScenePlanner and upstream engines).

    Design
    ------
    - Uses small helper methods to build different aspects of the prompt.
    - Accepts ScenePlan as the primary input, with optional access to
      GenerationContext for additional metadata when needed.
    - Structured for future extension (e.g., specialized prompt generators
      for wildlife, ocean, documentary, POV, etc.) without changing the
      public API.
    """

    def generate(
        self,
        scene_plan: ScenePlan,
        context: Optional[GenerationContext] = None,
    ) -> PromptBundle:
        """
        Generate a bundle of prompts from a ScenePlan.

        Parameters
        ----------
        scene_plan : ScenePlan
            The production-ready plan describing the intent and structure
            of the scene.
        context : GenerationContext, optional
            Optional context for additional metadata (e.g., story title,
            world name). The generator treats this as read-only.

        Returns
        -------
        PromptBundle
            A structured set of prompts derived deterministically from
            the ScenePlan (and optionally GenerationContext).
        """
        visual_prompt = self._build_visual_prompt(scene_plan, context)
        narrative_prompt = self._build_narrative_prompt(scene_plan, context)
        technical_prompt = self._build_technical_prompt(scene_plan, context)

        return PromptBundle(
            visual_prompt=visual_prompt,
            narrative_prompt=narrative_prompt,
            technical_prompt=technical_prompt,
        )

    # -------------------------------------------------------------------------
    # Visual prompt construction
    # -------------------------------------------------------------------------

    def _build_visual_prompt(
        self,
        scene_plan: ScenePlan,
        context: Optional[GenerationContext],
    ) -> str:
        """
        Build the primary visual prompt from the ScenePlan.

        This prompt focuses on what should be seen on screen, guided by
        the goal, visual focus, and conflict.
        """
        parts: List[str] = []

        # High-level goal.
        if getattr(scene_plan, "goal", None):
            parts.append(scene_plan.goal)

        # Visual focus.
        if getattr(scene_plan, "visual_focus", None):
            parts.append(f"Visually emphasize: {scene_plan.visual_focus}.")

        # Conflict or tension.
        if getattr(scene_plan, "conflict", None):
            parts.append(f"Underlying conflict or tension: {scene_plan.conflict}.")

        # Narrative importance can hint at intensity or emphasis.
        if getattr(scene_plan, "narrative_importance", None):
            parts.append(f"Narrative importance: {scene_plan.narrative_importance}.")

        # Optional context metadata (kept generic and deterministic).
        if context is not None:
            story = getattr(context, "story", None)
            world = getattr(context, "world", None)
            story_title = getattr(story, "title", None) if story is not None else None
            world_name = getattr(world, "name", None) if world is not None else None

            meta_parts: List[str] = []
            if story_title:
                meta_parts.append(f"Story: {story_title}")
            if world_name:
                meta_parts.append(f"World: {world_name}")

            if meta_parts:
                parts.append("Context: " + " | ".join(meta_parts) + ".")

        return " ".join(parts).strip()

    # -------------------------------------------------------------------------
    # Narrative prompt construction
    # -------------------------------------------------------------------------

    def _build_narrative_prompt(
        self,
        scene_plan: ScenePlan,
        context: Optional[GenerationContext],
    ) -> str:
        """
        Build a narrative-oriented prompt.

        This prompt is suitable for narration or script generation stages.
        It focuses on what should happen and what the audience should feel
        or understand after the scene.
        """
        parts: List[str] = []

        if getattr(scene_plan, "goal", None):
            parts.append(f"Scene goal: {scene_plan.goal}.")

        if getattr(scene_plan, "expected_result", None):
            parts.append(
                f"After this scene, the audience should understand: {scene_plan.expected_result}."
            )

        if getattr(scene_plan, "conflict", None):
            parts.append(f"Conflict focus: {scene_plan.conflict}.")

        if getattr(scene_plan, "narrative_importance", None):
            parts.append(f"This scene functions as: {scene_plan.narrative_importance}.")

        # Include planner notes as structured hints, if available.
        if getattr(scene_plan, "notes", None):
            parts.append(f"Planner notes: {scene_plan.notes}.")

        return " ".join(parts).strip()

    # -------------------------------------------------------------------------
    # Technical prompt construction
    # -------------------------------------------------------------------------

    def _build_technical_prompt(
        self,
        scene_plan: ScenePlan,
        context: Optional[GenerationContext],
    ) -> str:
        """
        Build a technical prompt describing camera and transition intent.

        This guides how the scene should be framed and connected to
        neighboring scenes, without specifying exact shot lists.
        """
        parts: List[str] = []

        if getattr(scene_plan, "camera_intent", None):
            parts.append(f"Camera intent: {scene_plan.camera_intent}.")

        if getattr(scene_plan, "transition", None):
            parts.append(f"Preferred transition style: {scene_plan.transition}.")

        # Optional: derive pacing or emphasis hints from narrative importance.
        if getattr(scene_plan, "narrative_importance", None):
            parts.append(
                f"Adjust pacing and emphasis to match the narrative importance: {scene_plan.narrative_importance}."
            )

        return " ".join(parts).strip()