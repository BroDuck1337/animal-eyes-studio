from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional


class WorldEngine:
    """
    Engine responsible for managing world-building data for the story.

    Responsibilities:
    - Maintain core world metadata (name, description, themes)
    - Track locations, regions, and important entities
    - Track world rules (physics, magic, constraints)
    - Provide export helpers for use by other engines/services
    """

    def __init__(self, world_data: Optional[Dict[str, Any]] = None) -> None:
        # Internal canonical world representation
        self.world: Dict[str, Any] = {
            "id": None,
            "name": None,
            "description": None,
            "themes": [],
            "tone": None,
            "locations": [],
            "factions": [],
            "rules": {},
            "metadata": {},
        }
        if world_data:
            self.update_world(**world_data)

    # ------------------------------------------------------------------
    # Core world metadata
    # ------------------------------------------------------------------
    def set_identity(
        self,
        world_id: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        if world_id is not None:
            self.world["id"] = world_id
        if name is not None:
            self.world["name"] = name
        if description is not None:
            self.world["description"] = description
        return deepcopy(self.world)

    def set_themes(self, themes: List[str]) -> Dict[str, Any]:
        self.world["themes"] = list(themes)
        return deepcopy(self.world)

    def set_tone(self, tone: str) -> Dict[str, Any]:
        self.world["tone"] = tone
        return deepcopy(self.world)

    def update_world(self, **updates: Any) -> Dict[str, Any]:
        """
        Generic update for top-level world fields.
        """
        for key, value in updates.items():
            if key in self.world:
                if isinstance(self.world[key], list) and isinstance(value, list):
                    self.world[key] = list(value)
                elif isinstance(self.world[key], dict) and isinstance(value, dict):
                    self.world[key].update(deepcopy(value))
                else:
                    self.world[key] = deepcopy(value)
            else:
                # store unknown keys in metadata
                self.world["metadata"][key] = deepcopy(value)
        return deepcopy(self.world)

    def get_world(self) -> Dict[str, Any]:
        return deepcopy(self.world)

    # ------------------------------------------------------------------
    # Location management
    # ------------------------------------------------------------------
    def add_location(
        self,
        name: str,
        description: Optional[str] = None,
        region: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        location = {
            "name": name,
            "description": description,
            "region": region,
            "tags": list(tags) if tags else [],
            "metadata": deepcopy(metadata) if metadata else {},
        }
        self.world.setdefault("locations", [])
        self.world["locations"].append(location)
        return deepcopy(location)

    def list_locations(self) -> List[Dict[str, Any]]:
        return deepcopy(self.world.get("locations", []))

    def find_location(self, name: str) -> Optional[Dict[str, Any]]:
        for loc in self.world.get("locations", []):
            if loc.get("name") == name:
                return deepcopy(loc)
        return None

    # ------------------------------------------------------------------
    # Faction / entity management
    # ------------------------------------------------------------------
    def add_faction(
        self,
        name: str,
        description: Optional[str] = None,
        goals: Optional[List[str]] = None,
        territory: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        faction = {
            "name": name,
            "description": description,
            "goals": list(goals) if goals else [],
            "territory": territory,
            "metadata": deepcopy(metadata) if metadata else {},
        }
        self.world.setdefault("factions", [])
        self.world["factions"].append(faction)
        return deepcopy(faction)

    def list_factions(self) -> List[Dict[str, Any]]:
        return deepcopy(self.world.get("factions", []))

    def find_faction(self, name: str) -> Optional[Dict[str, Any]]:
        for faction in self.world.get("factions", []):
            if faction.get("name") == name:
                return deepcopy(faction)
        return None

    # ------------------------------------------------------------------
    # World rules
    # ------------------------------------------------------------------
    def set_rule(self, key: str, value: Any) -> Dict[str, Any]:
        self.world.setdefault("rules", {})
        self.world["rules"][key] = deepcopy(value)
        return deepcopy(self.world["rules"])

    def get_rule(self, key: str, default: Any = None) -> Any:
        return deepcopy(self.world.get("rules", {}).get(key, default))

    def update_rules(self, **rules: Any) -> Dict[str, Any]:
        self.world.setdefault("rules", {})
        for key, value in rules.items():
            self.world["rules"][key] = deepcopy(value)
        return deepcopy(self.world["rules"])

    def list_rules(self) -> Dict[str, Any]:
        return deepcopy(self.world.get("rules", {}))

    # ------------------------------------------------------------------
    # Export helpers
    # ------------------------------------------------------------------
    def export_world_package(self) -> Dict[str, Any]:
        """
        Export a world package suitable for feeding into other engines
        (e.g., ConsistencyEngine, ScenePlanner, PromptGenerator).
        """
        return deepcopy(self.world)
