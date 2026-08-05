from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional, Tuple


class ConsistencyIssue:
    """
    Simple data holder for a consistency issue detected in story data.
    """

    def __init__(
        self,
        code: str,
        message: str,
        severity: str = "warning",
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.code = code
        self.message = message
        self.severity = severity  # "info" | "warning" | "error"
        self.context = context or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
            "context": deepcopy(self.context),
        }


class ConsistencyEngine:
    """
    Engine responsible for checking narrative consistency across:
    - World data
    - Character data and arcs
    - Scene and timeline state

    This engine is schema-light and expects high-level dict structures, so it
    can be used together with WorldEngine, StateEngine, CharacterEngine, etc.
    """

    def __init__(self, rules: Optional[Dict[str, Any]] = None) -> None:
        # rules can hold thresholds, toggles, etc.
        self.rules: Dict[str, Any] = rules or {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def check_story_package(
        self,
        world: Optional[Dict[str, Any]] = None,
        characters: Optional[Dict[str, Any]] = None,
        scenes: Optional[List[Dict[str, Any]]] = None,
        timeline: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Run a suite of consistency checks over the full story package.

        Parameters:
        - world: world data (e.g., from WorldEngine.export_world)
        - characters: character data (e.g., CharacterEngine.export_all()["characters"])
        - scenes: list of scene dicts
        - timeline: list of timeline events / scenes

        Returns:
        {
            "issues": [ ... list of issue dicts ... ],
            "summary": {
                "total": int,
                "by_severity": {"info": int, "warning": int, "error": int},
            },
        }
        """
        issues: List[ConsistencyIssue] = []

        issues.extend(self._check_world_internal_consistency(world or {}))
        issues.extend(self._check_character_internal_consistency(characters or {}))
        issues.extend(self._check_scene_consistency(scenes or []))
        issues.extend(self._check_timeline_consistency(timeline or []))

        return self._build_result(issues)

    # ------------------------------------------------------------------
    # World checks
    # ------------------------------------------------------------------
    def _check_world_internal_consistency(
        self, world: Dict[str, Any]
    ) -> List[ConsistencyIssue]:
        issues: List[ConsistencyIssue] = []

        if not world:
            return issues

        # Example: check that required keys exist
        required_keys = ["name", "description"]
        for key in required_keys:
            if key not in world:
                issues.append(
                    ConsistencyIssue(
                        code="WORLD_MISSING_FIELD",
                        message=f"World is missing required field '{key}'.",
                        severity="warning",
                        context={"field": key},
                    )
                )

        # Example: check that regions/locations have unique names
        locations = world.get("locations") or []
        seen_names = set()
        for loc in locations:
            name = loc.get("name")
            if not name:
                continue
            if name in seen_names:
                issues.append(
                    ConsistencyIssue(
                        code="WORLD_DUPLICATE_LOCATION",
                        message=f"Duplicate location name '{name}' in world.",
                        severity="warning",
                        context={"location": name},
                    )
                )
            else:
                seen_names.add(name)

        return issues

    # ------------------------------------------------------------------
    # Character checks
    # ------------------------------------------------------------------
    def _check_character_internal_consistency(
        self, characters: Dict[str, Any]
    ) -> List[ConsistencyIssue]:
        issues: List[ConsistencyIssue] = []

        # characters may be a dict keyed by id, or a list
        if isinstance(characters, list):
            char_list = characters
        else:
            char_list = list(characters.values())

        ids = set()
        for char in char_list:
            cid = char.get("id") or char.get("name")
            if not cid:
                issues.append(
                    ConsistencyIssue(
                        code="CHAR_MISSING_ID",
                        message="Character is missing an 'id' or 'name'.",
                        severity="error",
                        context={"character": char},
                    )
                )
                continue

            if cid in ids:
                issues.append(
                    ConsistencyIssue(
                        code="CHAR_DUPLICATE_ID",
                        message=f"Duplicate character id/name '{cid}'.",
                        severity="error",
                        context={"id": cid},
                    )
                )
            else:
                ids.add(cid)

            # Example: check arc ordering or empty arc
            arc = char.get("arc") or []
            if not arc:
                issues.append(
                    ConsistencyIssue(
                        code="CHAR_EMPTY_ARC",
                        message=f"Character '{cid}' has no arc entries.",
                        severity="info",
                        context={"id": cid},
                    )
                )

        return issues

    # ------------------------------------------------------------------
    # Scene checks
    # ------------------------------------------------------------------
    def _check_scene_consistency(
        self, scenes: List[Dict[str, Any]]
    ) -> List[ConsistencyIssue]:
        issues: List[ConsistencyIssue] = []

        # Example: check that scene ids are unique and ordered by index if present
        seen_ids = set()
        last_index: Optional[int] = None

        for scene in scenes:
            sid = scene.get("id") or scene.get("scene_id")
            if sid:
                if sid in seen_ids:
                    issues.append(
                        ConsistencyIssue(
                            code="SCENE_DUPLICATE_ID",
                            message=f"Duplicate scene id '{sid}'.",
                            severity="error",
                            context={"id": sid},
                        )
                    )
                else:
                    seen_ids.add(sid)

            index = scene.get("index")
            if isinstance(index, int):
                if last_index is not None and index < last_index:
                    issues.append(
                        ConsistencyIssue(
                            code="SCENE_INDEX_ORDER",
                            message="Scene indices are not in non-decreasing order.",
                            severity="warning",
                            context={"previous_index": last_index, "current_index": index},
                        )
                    )
                last_index = index

        return issues

    # ------------------------------------------------------------------
    # Timeline checks
    # ------------------------------------------------------------------
    def _check_timeline_consistency(
        self, timeline: List[Dict[str, Any]]
    ) -> List[ConsistencyIssue]:
        issues: List[ConsistencyIssue] = []

        # Example: check chronological order if timestamps exist
        last_time: Optional[str] = None
        for event in timeline:
            ts = event.get("timestamp")
            if ts is None:
                continue
            if last_time is not None and str(ts) < str(last_time):
                issues.append(
                    ConsistencyIssue(
                        code="TIMELINE_OUT_OF_ORDER",
                        message="Timeline events are out of chronological order.",
                        severity="warning",
                        context={"previous_timestamp": last_time, "current_timestamp": ts},
                    )
                )
            last_time = ts

        return issues

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _build_result(self, issues: List[ConsistencyIssue]) -> Dict[str, Any]:
        by_severity: Dict[str, int] = {"info": 0, "warning": 0, "error": 0}
        for issue in issues:
            if issue.severity not in by_severity:
                by_severity[issue.severity] = 0
            by_severity[issue.severity] += 1

        return {
            "issues": [issue.to_dict() for issue in issues],
            "summary": {
                "total": len(issues),
                "by_severity": by_severity,
            },
        }
