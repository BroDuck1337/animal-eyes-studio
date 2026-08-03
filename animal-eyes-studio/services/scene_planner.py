from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from models.generation_context import GenerationContext
from models.timeline_scene import TimelineScene
from models.scene_state import SceneState
from models.story import Story
from models.story_event import StoryEvent
from models.world import World
from models.character import Character
from generators.scene_generator import ScenePlan  # Assumed location of ScenePlan


@dataclass(frozen=True)
class _ScenePlanningInputs:
    """
    Internal immutable view of the data needed for planning a scene.

    This separates the planner from the full GenerationContext surface area
    and makes it easier to evolve the planner without coupling it to every
    field on GenerationContext.
    """

    context: GenerationContext
    story: Optional[Story]
    timeline_scene: Optional[TimelineScene]
    scene_state: Optional[SceneState]
    world: Optional[World]
    primary_event: Optional[StoryEvent]
    primary_character: Optional[Character]


class ScenePlanner:
    """
    ScenePlanner is responsible for transforming a GenerationContext into a
    production-ready ScenePlan.

    Responsibilities
    ----------------
    - Decide what this scene is trying to achieve (goal).
    - Determine the visual focus.
    - Identify the conflict.
    - Infer the expected outcome.
    - Choose a transition style.
    - Define camera intent.
    - Assess narrative importance.

    Non-responsibilities
    --------------------
    - Does NOT generate prompts.
    - Does NOT call any LLM.
    - Does NOT create scripts.
    - Does NOT modify GenerationContext (treats it as immutable).

    Design
    ------
    - Deterministic: no randomness, no external inference.
    - Uses small, focused private planning methods for each concern.
    - Structured for future extension (e.g., WildlifeScenePlanner, etc.)
      without changing the public API.

    Extension Strategy
    ------------------
    Future specialized planners (e.g., WildlifeScenePlanner, OceanScenePlanner)
    can be implemented by composition: a coordinator can decide which planner
    instance to use based on GenerationContext and still call `plan(context)`
    to obtain a ScenePlan. This class is intentionally lightweight and
    side-effect free to support such composition.
    """

    def plan(self, context: GenerationContext) -> ScenePlan:
        """
        Plan a scene based on the provided GenerationContext.

        The planner derives all information exclusively from GenerationContext
        and related model objects. It does not mutate the context.

        Parameters
        ----------
        context : GenerationContext
            Immutable context containing all information required to plan
            the current scene.

        Returns
        -------
        ScenePlan
            A deterministic, production-ready plan describing the intent and
            structure of the scene.
        """
        inputs = self._extract_inputs(context)

        goal = self._plan_goal(inputs)
        conflict = self._plan_conflict(inputs)
        expected_result = self._plan_expected_result(inputs, goal, conflict)
        transition = self._plan_transition(inputs)
        visual_focus = self._plan_visual_focus(inputs)
        camera_intent = self._plan_camera_intent(inputs, visual_focus)
        narrative_importance = self._plan_narrative_importance(inputs)
        notes = self._plan_notes(
            inputs=inputs,
            goal=goal,
            conflict=conflict,
            expected_result=expected_result,
            transition=transition,
            visual_focus=visual_focus,
            camera_intent=camera_intent,
            narrative_importance=narrative_importance,
        )

        return ScenePlan(
            goal=goal,
            conflict=conflict,
            expected_result=expected_result,
            transition=transition,
            visual_focus=visual_focus,
            camera_intent=camera_intent,
            narrative_importance=narrative_importance,
            notes=notes,
        )

    # -------------------------------------------------------------------------
    # Input extraction
    # -------------------------------------------------------------------------

    def _extract_inputs(self, context: GenerationContext) -> _ScenePlanningInputs:
        """
        Extract and normalize all data needed for planning from GenerationContext.

        This method centralizes how we read from GenerationContext so that
        future changes to the context structure only affect this method.

        The planner only depends on a small, well-defined subset of the
        GenerationContext surface area, which keeps it decoupled and easier
        to extend or replace.
        """
        # The exact attributes depend on GenerationContext's implementation.
        # We defensively use getattr with defaults to keep this planner
        # resilient to missing fields.
        story: Optional[Story] = getattr(context, "story", None)
        timeline_scene: Optional[TimelineScene] = getattr(context, "timeline_scene", None)
        scene_state: Optional[SceneState] = getattr(context, "scene_state", None)
        world: Optional[World] = getattr(context, "world", None)

        primary_event: Optional[StoryEvent] = None
        if timeline_scene is not None:
            # Prefer a clearly named primary event, fall back to a generic event.
            primary_event = getattr(timeline_scene, "primary_event", None) or getattr(
                timeline_scene, "event", None
            )

        primary_character: Optional[Character] = getattr(context, "primary_character", None)
        if primary_character is None and timeline_scene is not None:
            # Fallback: try to infer a main character from the timeline scene.
            characters = getattr(timeline_scene, "characters", None)
            if characters:
                primary_character = characters[0]

        return _ScenePlanningInputs(
            context=context,
            story=story,
            timeline_scene=timeline_scene,
            scene_state=scene_state,
            world=world,
            primary_event=primary_event,
            primary_character=primary_character,
        )

    # -------------------------------------------------------------------------
    # Individual planning responsibilities
    # -------------------------------------------------------------------------

    def _plan_goal(self, inputs: _ScenePlanningInputs) -> str:
        """
        Determine what this scene is trying to achieve.

        The goal is a concise, production-oriented description of the
        narrative or informational purpose of the scene.
        """
        if inputs.primary_event is not None:
            event_type = getattr(inputs.primary_event, "type", None)
            summary = getattr(inputs.primary_event, "summary", None)
            if event_type and summary:
                return f"Show the '{event_type}' event where {summary}"
            if summary:
                return f"Advance the story by depicting: {summary}"

        if inputs.timeline_scene is not None:
            intent = getattr(inputs.timeline_scene, "intent", None)
            if intent:
                return f"Realize the scene intent: {intent}"

        if inputs.scene_state is not None:
            phase = getattr(inputs.scene_state, "phase", None)
            if phase:
                return f"Establish the scene during the '{phase}' phase of the story"

        # Fallback: generic but deterministic goal.
        return "Advance the narrative by visually depicting the current story beat"

    def _plan_conflict(self, inputs: _ScenePlanningInputs) -> str:
        """
        Identify the central conflict or tension in the scene.

        Conflict can be external (character vs environment), interpersonal,
        or internal (character vs self). If no explicit conflict is present,
        we still provide a neutral description to keep the plan complete.
        """
        if inputs.primary_event is not None:
            conflict = getattr(inputs.primary_event, "conflict", None)
            if conflict:
                return conflict

        if inputs.timeline_scene is not None:
            tension = getattr(inputs.timeline_scene, "tension", None)
            if tension:
                return tension

        if inputs.scene_state is not None:
            stakes = getattr(inputs.scene_state, "stakes", None)
            if stakes:
                return f"Highlight the stakes: {stakes}"

        # Fallback: low-conflict or expository scene.
        return "Minimal explicit conflict; focus on atmosphere, context, and continuity"

    def _plan_expected_result(
        self,
        inputs: _ScenePlanningInputs,
        goal: str,
        conflict: str,
    ) -> str:
        """
        Infer the expected narrative or informational outcome of the scene.

        This is not a script; it is a high-level description of what should
        be true after the scene concludes.
        """
        if inputs.primary_event is not None:
            outcome = getattr(inputs.primary_event, "outcome", None)
            if outcome:
                return outcome

        if inputs.timeline_scene is not None:
            result = getattr(inputs.timeline_scene, "expected_result", None)
            if result:
                return result

        if inputs.scene_state is not None:
            progression = getattr(inputs.scene_state, "progression", None)
            if progression:
                return f"Move the story to the next progression: {progression}"

        # Deterministic fallback derived from goal and conflict.
        if "Minimal explicit conflict" in conflict:
            return "Audience gains clearer understanding of the setting and situation"
        return "Conflict is advanced or partially resolved while maintaining narrative momentum"

    def _plan_transition(self, inputs: _ScenePlanningInputs) -> str:
        """
        Decide the transition style into or out of this scene.

        This is a conceptual description (e.g., 'hard cut', 'crossfade',
        'match cut') rather than a low-level editing instruction.
        """
        if inputs.timeline_scene is not None:
            transition = getattr(inputs.timeline_scene, "transition", None)
            if transition:
                return transition

        position = getattr(inputs.timeline_scene, "position", None) if inputs.timeline_scene else None
        if position == 0:
            return "Opening transition from title or previous sequence"
        if position is not None:
            return "Standard cut maintaining temporal continuity"

        # Fallback when no structural information is available.
        return "Simple cut aligned with the surrounding scenes"

    def _plan_visual_focus(self, inputs: _ScenePlanningInputs) -> str:
        """
        Determine the primary visual focus of the scene.

        This guides what should be emphasized visually (e.g., character,
        environment, action, object).
        """
        if inputs.primary_character is not None:
            name = getattr(inputs.primary_character, "name", None) or "the main character"
            role = getattr(inputs.primary_character, "role", None)
            if role:
                return f"Focus on {name} as the {role} within the environment"
            return f"Focus on {name} and their interaction with the surroundings"

        if inputs.world is not None:
            biome = getattr(inputs.world, "biome", None)
            location = getattr(inputs.world, "location", None)
            if biome or location:
                descriptor = ", ".join(filter(None, [biome, location]))
                return f"Emphasize the environment: {descriptor}"

        if inputs.timeline_scene is not None:
            subject = getattr(inputs.timeline_scene, "subject", None)
            if subject:
                return f"Highlight the main subject: {subject}"

        # Fallback: balanced focus.
        return "Balanced focus between characters and environment to support the story beat"

    def _plan_camera_intent(
        self,
        inputs: _ScenePlanningInputs,
        visual_focus: str,
    ) -> str:
        """
        Define the high-level camera intent for the scene.

        This is not a shot list; it is a conceptual guideline such as
        'intimate and close', 'wide and observational', etc.
        """
        if inputs.timeline_scene is not None:
            camera_style = getattr(inputs.timeline_scene, "camera_style", None)
            if camera_style:
                return camera_style

        if "environment" in visual_focus.lower():
            return "Wide and observational framing to showcase the environment and spatial context"

        if "main character" in visual_focus.lower() or "focus on" in visual_focus.lower():
            return "Character-centric framing with medium and close shots to capture emotion and reaction"

        # Fallback: neutral camera intent.
        return "Neutral, story-driven framing that adapts to character and environment needs"

    def _plan_narrative_importance(self, inputs: _ScenePlanningInputs) -> str:
        """
        Assess the narrative importance of the scene.

        This is a qualitative label (e.g., 'key turning point', 'setup',
        'transition') that helps downstream systems prioritize effort.
        """
        if inputs.timeline_scene is not None:
            importance = getattr(inputs.timeline_scene, "importance", None)
            if importance:
                return importance

        if inputs.primary_event is not None:
            is_climax = getattr(inputs.primary_event, "is_climax", False)
            is_reveal = getattr(inputs.primary_event, "is_reveal", False)
            if is_climax:
                return "Major turning point in the narrative"
            if is_reveal:
                return "Important reveal that changes audience understanding"

        if inputs.scene_state is not None:
            phase = getattr(inputs.scene_state, "phase", None)
            if phase in {"setup", "introduction"}:
                return "Foundational setup scene introducing key elements"
            if phase in {"climax", "confrontation"}:
                return "High-impact scene resolving or escalating core conflict"
            if phase in {"resolution", "denouement"}:
                return "Resolution scene tying together prior events"

        # Fallback: mid-level importance.
        return "Standard narrative beat supporting overall story progression"

    def _plan_notes(
        self,
        inputs: _ScenePlanningInputs,
        goal: str,
        conflict: str,
        expected_result: str,
        transition: str,
        visual_focus: str,
        camera_intent: str,
        narrative_importance: str,
    ) -> str:
        """
        Provide additional structured notes for downstream systems.

        Notes are deterministic, human-readable hints that summarize key
        planning decisions and relevant context. They are not prompts and
        should not contain scripting instructions.
        """
        # Collect simple, deterministic metadata from the context.
        story_title = getattr(inputs.story, "title", None) if inputs.story else None
        world_name = getattr(inputs.world, "name", None) if inputs.world else None
        scene_index = getattr(inputs.timeline_scene, "position", None) if inputs.timeline_scene else None

        parts = []

        if story_title:
            parts.append(f"Story: {story_title}")
        if world_name:
            parts.append(f"World: {world_name}")
        if scene_index is not None:
            parts.append(f"Timeline position: {scene_index}")

        if inputs.primary_character is not None:
            char_name = getattr(inputs.primary_character, "name", None)
            if char_name:
                parts.append(f"Primary character: {char_name}")

        # Summarize planning decisions in a compact, structured way.
        parts.append(f"Goal: {goal}")
        parts.append(f"Conflict: {conflict}")
        parts.append(f"Expected result: {expected_result}")
        parts.append(f"Transition: {transition}")
        parts.append(f"Visual focus: {visual_focus}")
        parts.append(f"Camera intent: {camera_intent}")
        parts.append(f"Narrative importance: {narrative_importance}")

        # Join with a deterministic separator.
        return " | ".join(parts)