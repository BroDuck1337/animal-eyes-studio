# core/story_bible.py

from dataclasses import dataclass
from models.character import Character
from models.world import World
from models.story_event import StoryEvent

@dataclass
class StoryBible:

    title: str

    niche: str

    story_type: str

    duration: int

    character: Character

    world: World

    timeline: list[StoryEvent]


