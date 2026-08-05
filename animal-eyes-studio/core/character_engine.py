from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, is_dataclass
from typing import Any, Dict, List, Optional


class CharacterEngine:
    """
    Full narrative character engine for story generation workflows.

    Responsibilities:
    - Maintain a registry of characters
    - Create/update/delete/fetch characters
    - Track scene-level state such as emotions, goals, conditions, and notes
    - Track relationships between characters
    - Apply story events to characters
    - Evolve character arcs over time

    The engine is intentionally defensive and schema-light so it can work with
    different Character model implementations already present in the project.
    """

    def __init__(self, characters: Optional[List[Any]] = None) -> None:
        self.characters: Dict[str, Dict[str, Any]] = {}
        self.scene_state: Dict[str, Dict[str, Any]] = {}
        self.relationships: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self.arc_history: Dict[str, List[Dict[str, Any]]] = {}

        if characters:
            for character in characters:
                self.add_character(character)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _normalize_character(self, character: Any) -> Dict[str, Any]:
        if isinstance(character, dict):
            data = deepcopy(character)
        elif is_dataclass(character):
            data = asdict(character)
        elif hasattr(character, "__dict__"):
            data = deepcopy(vars(character))
        else:
            raise TypeError("Character must be a dict, dataclass, or object with __dict__")

        character_id = (
            data.get("id")
            or data.get("character_id")
            or data.get("name")
            or data.get("slug")
        )
        if not character_id:
            raise ValueError("Character must include one of: id, character_id, name, or slug")

        data["id"] = str(character_id)
        data.setdefault("name", data["id"])
        data.setdefault("traits", [])
        data.setdefault("goals", [])
        data.setdefault("conflicts", [])
        data.setdefault("relationships", {})
        data.setdefault("arc", [])
        data.setdefault("metadata", {})
        return data

    def _ensure_character_exists(self, character_id: str) -> None:
        if character_id not in self.characters:
            raise KeyError(f"Character '{character_id}' does not exist")

    def _ensure_scene_state(self, character_id: str) -> Dict[str, Any]:
        self._ensure_character_exists(character_id)
        if character_id not in self.scene_state:
            self.scene_state[character_id] = {
                "emotion": None,
                "goals": [],
                "status": "active",
                "conditions": [],
                "location": None,
                "notes": [],
                "last_event": None,
            }
        return self.scene_state[character_id]

    def _ensure_relationship_bucket(self, source_id: str) -> Dict[str, Dict[str, Any]]:
        self._ensure_character_exists(source_id)
        if source_id not in self.relationships:
            self.relationships[source_id] = {}
        return self.relationships[source_id]

    # ------------------------------------------------------------------
    # Registry operations
    # ------------------------------------------------------------------
    def add_character(self, character: Any) -> Dict[str, Any]:
        data = self._normalize_character(character)
        character_id = data["id"]
        self.characters[character_id] = data

        if character_id not in self.arc_history:
            self.arc_history[character_id] = []

        if data.get("relationships"):
            self.relationships[character_id] = deepcopy(data["relationships"])

        self._ensure_scene_state(character_id)
        return deepcopy(self.characters[character_id])

    def create_character(self, **kwargs: Any) -> Dict[str, Any]:
        return self.add_character(kwargs)

    def update_character(self, character_id: str, **updates: Any) -> Dict[str, Any]:
        self._ensure_character_exists(character_id)
        current = self.characters[character_id]
        current.update(deepcopy(updates))
        current["id"] = character_id
        return deepcopy(current)

    def delete_character(self, character_id: str) -> bool:
        self._ensure_character_exists(character_id)

        del self.characters[character_id]
        self.scene_state.pop(character_id, None)
        self.arc_history.pop(character_id, None)
        self.relationships.pop(character_id, None)

        for _, targets in self.relationships.items():
            targets.pop(character_id, None)

        return True

    def get_character(self, character_id: str) -> Optional[Dict[str, Any]]:
        character = self.characters.get(character_id)
        return deepcopy(character) if character else None

    def get_character_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        for character in self.characters.values():
            if character.get("name") == name:
                return deepcopy(character)
        return None

    def list_characters(self) -> List[Dict[str, Any]]:
        return [deepcopy(character) for character in self.characters.values()]

    # ------------------------------------------------------------------
    # Scene state operations
    # ------------------------------------------------------------------
    def update_scene_state(
        self,
        character_id: str,
        emotion: Optional[str] = None,
        goals: Optional[List[str]] = None,
        status: Optional[str] = None,
        conditions: Optional[List[str]] = None,
        location: Optional[str] = None,
        note: Optional[str] = None,
        last_event: Optional[str] = None,
    ) -> Dict[str, Any]:
        state = self._ensure_scene_state(character_id)

        if emotion is not None:
            state["emotion"] = emotion
        if goals is not None:
            state["goals"] = list(goals)
        if status is not None:
            state["status"] = status
        if conditions is not None:
            state["conditions"] = list(conditions)
        if location is not None:
            state["location"] = location
        if note:
            state["notes"].append(note)
        if last_event is not None:
            state["last_event"] = last_event

        return deepcopy(state)

    def get_scene_state(self, character_id: str) -> Dict[str, Any]:
        state = self._ensure_scene_state(character_id)
        return deepcopy(state)

    # ------------------------------------------------------------------
    # Relationship operations
    # ------------------------------------------------------------------
    def update_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: Optional[str] = None,
        intensity: Optional[float] = None,
        status: Optional[str] = None,
        notes: Optional[List[str]] = None,
        bidirectional: bool = False,
    ) -> Dict[str, Any]:
        self._ensure_character_exists(source_id)
        self._ensure_character_exists(target_id)

        source_bucket = self._ensure_relationship_bucket(source_id)
        relation = source_bucket.get(
            target_id,
            {
                "type": relationship_type or "unknown",
                "intensity": 0.0 if intensity is None else intensity,
                "status": status or "active",
                "notes": [],
            },
        )

        if relationship_type is not None:
            relation["type"] = relationship_type
        if intensity is not None:
            relation["intensity"] = intensity
        if status is not None:
            relation["status"] = status
        if notes:
            relation.setdefault("notes", [])
            relation["notes"].extend(notes)

        source_bucket[target_id] = relation

        if bidirectional:
            target_bucket = self._ensure_relationship_bucket(target_id)
            reverse_relation = deepcopy(relation)
            target_bucket[source_id] = reverse_relation

        return deepcopy(relation)

    def get_relationship(self, source_id: str, target_id: str) -> Optional[Dict[str, Any]]:
        self._ensure_character_exists(source_id)
        return deepcopy(self.relationships.get(source_id, {}).get(target_id))

    def get_relationships(self, character_id: str) -> Dict[str, Dict[str, Any]]:
        self._ensure_character_exists(character_id)
        return deepcopy(self.relationships.get(character_id, {}))

    # ------------------------------------------------------------------
    # Narrative evolution
    # ------------------------------------------------------------------
    def apply_story_event(
        self,
        character_id: str,
        event: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Apply a story event to a character.

        Supported event keys:
        - summary / description
        - emotion
        - add_goal
        - remove_goal
        - add_condition
        - remove_condition
        - status
        - location
        - note
        - trait_gain
        - trait_loss
        - conflict_gain
        - conflict_loss
        """
        self._ensure_character_exists(character_id)
        character = self.characters[character_id]
        state = self._ensure_scene_state(character_id)

        summary = event.get("summary") or event.get("description") or "Unnamed event"

        if event.get("emotion") is not None:
            state["emotion"] = event["emotion"]
        if event.get("status") is not None:
            state["status"] = event["status"]
        if event.get("location") is not None:
            state["location"] = event["location"]
        if event.get("note"):
            state["notes"].append(event["note"])
        state["last_event"] = summary

        add_goal = event.get("add_goal")
        if add_goal and add_goal not in state["goals"]:
            state["goals"].append(add_goal)

        remove_goal = event.get("remove_goal")
        if remove_goal in state["goals"]:
            state["goals"].remove(remove_goal)

        add_condition = event.get("add_condition")
        if add_condition and add_condition not in state["conditions"]:
            state["conditions"].append(add_condition)

        remove_condition = event.get("remove_condition")
        if remove_condition in state["conditions"]:
            state["conditions"].remove(remove_condition)

        trait_gain = event.get("trait_gain")
        if trait_gain and trait_gain not in character["traits"]:
            character["traits"].append(trait_gain)

        trait_loss = event.get("trait_loss")
        if trait_loss in character["traits"]:
            character["traits"].remove(trait_loss)

        conflict_gain = event.get("conflict_gain")
        if conflict_gain and conflict_gain not in character["conflicts"]:
            character["conflicts"].append(conflict_gain)

        conflict_loss = event.get("conflict_loss")
        if conflict_loss in character["conflicts"]:
            character["conflicts"].remove(conflict_loss)

        arc_entry = {
            "event": summary,
            "state": deepcopy(state),
        }
        character.setdefault("arc", []).append(arc_entry)
        self.arc_history.setdefault(character_id, []).append(arc_entry)

        return {
            "character": deepcopy(character),
            "scene_state": deepcopy(state),
            "arc_entry": deepcopy(arc_entry),
        }

    def evolve_arc(
        self,
        character_id: str,
        beat: str,
        change: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        self._ensure_character_exists(character_id)
        character = self.characters[character_id]
        state = self._ensure_scene_state(character_id)

        arc_entry = {
            "beat": beat,
            "change": deepcopy(change) if change else {},
            "state_snapshot": deepcopy(state),
        }

        if change:
            if "belief" in change:
                character["metadata"]["belief"] = change["belief"]
            if "need" in change:
                character["metadata"]["need"] = change["need"]
            if "want" in change:
                character["metadata"]["want"] = change["want"]
            if "emotion" in change:
                state["emotion"] = change["emotion"]
            if "status" in change:
                state["status"] = change["status"]

        character.setdefault("arc", []).append(arc_entry)
        self.arc_history.setdefault(character_id, []).append(arc_entry)
        return deepcopy(arc_entry)

    def get_arc_history(self, character_id: str) -> List[Dict[str, Any]]:
        self._ensure_character_exists(character_id)
        return deepcopy(self.arc_history.get(character_id, []))

    # ------------------------------------------------------------------
    # Serialization helpers
    # ------------------------------------------------------------------
    def export_character_profile(self, character_id: str) -> Dict[str, Any]:
        self._ensure_character_exists(character_id)
        return {
            "character": deepcopy(self.characters[character_id]),
            "scene_state": deepcopy(self.scene_state.get(character_id, {})),
            "relationships": deepcopy(self.relationships.get(character_id, {})),
            "arc_history": deepcopy(self.arc_history.get(character_id, [])),
        }

    def export_all(self) -> Dict[str, Any]:
        return {
            "characters": self.list_characters(),
            "scene_state": deepcopy(self.scene_state),
            "relationships": deepcopy(self.relationships),
            "arc_history": deepcopy(self.arc_history),
        }
