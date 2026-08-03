from core.story_bible import StoryBible
from core.timeline_engine import TimelineEngine
from models.character import Character
from models.world import World
from models.story_event import StoryEvent

#tạo object worker_ant
worker_ant = Character(
    id="worker_ant_01",
    species="black worker ant",
    appearance="small black forest ant",
    role="forager"
)
#tạo object forest_world
forest_world = World(
    ecosystem="temperate forest",
    season="summer",
    weather="sunny",
    lighting="golden morning light"
)
ant_story = StoryBible(
    title="A Day in the Life of a Wild Ant",

    niche="wildlife",

    story_type="survival",

    duration=60,

    character=worker_ant,

    world=forest_world,

    timeline = [
    StoryEvent("leave_nest", 1),
    StoryEvent("search_food", 2),
    StoryEvent("predator_attack", 5),
    StoryEvent("find_food", 4),
    StoryEvent("return_home", 3)
]
)
engine = TimelineEngine()

timeline = engine.build(ant_story)

print(timeline)