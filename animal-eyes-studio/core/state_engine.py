from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional


class StateEngine:
    """
    Engine responsible for tracking mutable story state across scenes.

    Responsibilities:
    - Maintain global story state
    - Maintain per-scene snapshots
    - Track flags, variables, and active conditions
    - Apply scene updates and event-driven changes
    """

    def __init__(self, initial_state: Optional[Dict[str, Any]] = None) -> None:
        self.global_state: Dict[str, Any] = deepcopy(initial_state) if initial_state else {}
        self.scene_snapshots: List[Dict[str, Any]] = []
        self.flags: Dict[str, bool] = {}
        self.conditions: List[str] = []

    # ------------------------------------------------------------------
    # Global state operations
    # ------------------------------------------------------------------
    def set_value(self, key: str, value: Any) -> Dict[str, Any]:
        self.global_state[key] = deepcopy(value)
        return deepcopy(self.global_state)

    def get_value(self, key: str, default: Any = None) -> Any:
        return deepcopy(self.global_state.get(key, default))

    def update_state(self, **updates: Any) -> Dict[str, Any]:
        for key, value in updates.items():
            self.global_state[key] = deepcopy(value)
        return deepcopy(self.global_state)

    def get_state(self) -> Dict[str, Any]:
        return deepcopy(self.global_state)

    # ------------------------------------------------------------------
    # Flag operations
    # ------------------------------------------------------------------
    def set_flag(self, name: str, value: bool = True) -> Dict[str, bool]:
        self.flags[name] = bool(value)
        return deepcopy(self.flags)

    def get_flag(self, name: str) -> bool:
        return bool(self.flags.get(name, False))

    def clear_flag(self, name: str) -> Dict[str, bool]:
        self.flags.pop(name, None)
        return deepcopy(self.flags)

    def list_flags(self) -> Dict[str, bool]:
        return deepcopy(self.flags)

    # ------------------------------------------------------------------
    # Condition operations
    # ------------------------------------------------------------------
    def add_condition(self, condition: str) -> List[str]:
        if condition not in self.conditions:
            self.conditions.append(condition)
        return deepcopy(self.conditions)

    def remove_condition(self, condition: str) -> List[str]:
        if condition in self.conditions:
            self.conditions.remove(condition)
        return deepcopy(self.conditions)

    def list_conditions(self) -> List[str]:
        return deepcopy(self.conditions)

    # ------------------------------------------------------------------
    # Scene snapshot operations
    # ------------------------------------------------------------------
    def snapshot_scene(
        self,
        scene_id: Optional[str] = None,
        scene_index: Optional[int] = None,
        scene_state: Optional[Dict[str, Any]] = None,
        note: Optional[str] = None,
    ) -> Dict[str, Any]:
        snapshot = {
            "scene_id": scene_id,
            "scene_index": scene_index,
            "state": deepcopy(scene_state) if scene_state is not None else deepcopy(self.global_state),
            "flags": deepcopy(self.flags),
            "conditions": deepcopy(self.conditions),
            "note": note,
        }
        self.scene_snapshots.append(snapshot)
        return deepcopy(snapshot)

    def get_scene_snapshots(self) -> List[Dict[str, Any]]:
        return deepcopy(self.scene_snapshots)

    def get_latest_snapshot(self) -> Optional[Dict[str, Any]]:
        if not self.scene_snapshots:
            return None
        return deepcopy(self.scene_snapshots[-1])

    # ------------------------------------------------------------------
    # Event application
    # ------------------------------------------------------------------
    def apply_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply a generic story/state event.

        Supported keys:
        - set: dict of key/value pairs to write into global_state
        - flags_on: list[str]
        - flags_off: list[str]
        - add_conditions: list[str]
        - remove_conditions: list[str]
        - note: optional note for the returned result
        """
        updates = event.get("set") or {}
        for key, value in updates.items():
            self.global_state[key] = deepcopy(value)

        for flag in event.get("flags_on", []) or []:
            self.flags[flag] = True

        for flag in event.get("flags_off", []) or []:
            self.flags[flag] = False

        for condition in event.get("add_conditions", []) or []:
            if condition not in self.conditions:
                self.conditions.append(condition)

        for condition in event.get("remove_conditions", []) or []:
            if condition in self.conditions:
                self.conditions.remove(condition)

        return {
            "state": deepcopy(self.global_state),
            "flags": deepcopy(self.flags),
            "conditions": deepcopy(self.conditions),
            "note": event.get("note"),
        }

    # ------------------------------------------------------------------
    # Export helpers
    # ------------------------------------------------------------------
    def export_state_package(self) -> Dict[str, Any]:
        return {
            "global_state": deepcopy(self.global_state),
            "flags": deepcopy(self.flags),
            "conditions": deepcopy(self.conditions),
            "scene_snapshots": deepcopy(self.scene_snapshots),
        }
