from dataclasses import dataclass
from typing import List, Optional

from .character import Character
from .world import World
from .story_event import StoryEvent
from .timeline_scene import TimelineScene  #đã đổi tên file


@dataclass
class Scene:
    """
    Cảnh chi tiết trong câu chuyện (cao hơn TimelineScene, dùng cho nội dung/script).
    """
    scene_id: int
    event: StoryEvent

    # Thời gian trong video
    start_time: float  # giây
    end_time: float    # giây

    # Nội dung mô tả
    title: str
    summary: str
    visual_description: str
    audio_description: str

    # Thông tin cinematic
    camera_style: str
    mood: str
    location: str

    # Độ quan trọng / cao trào
    intensity: int


@dataclass
class ScriptSegment:
    """
    Một đoạn script (voice-over / thoại) gắn với một scene.
    """
    scene_id: int
    order: int
    text: str
    speaker: str  # narrator, character id, v.v.
    emphasis: Optional[str] = None  # ví dụ: "dramatic", "calm"


@dataclass
class Script:
    """
    Toàn bộ script cho câu chuyện.
    """
    story_id: str
    segments: List[ScriptSegment]

    @property
    def full_text(self) -> str:
        return "\n".join(segment.text for segment in self.segments)


@dataclass
class SEOData:
    """
    Dữ liệu SEO cho video/bài viết.
    """
    title: str
    description: str
    keywords: List[str]
    tags: List[str]


@dataclass
class ThumbnailSpec:
    """
    Thông số cho thumbnail (để sinh prompt hoặc brief cho designer).
    """
    main_subject: str
    background: str
    mood: str
    color_palette: List[str]
    text_overlay: Optional[str] = None
    style: Optional[str] = None  # ví dụ: "cinematic", "cartoon", "realistic"


@dataclass
class Story:
    """
    Đối tượng tổng hợp toàn bộ pipeline của một câu chuyện.
    """
    story_id: str

    # Cốt lõi
    title: str
    niche: str
    story_type: str
    duration: int  # tổng thời lượng dự kiến (giây)

    # Thế giới & nhân vật
    character: Character
    world: World

    # Timeline & scene
    events: List[StoryEvent]
    timeline: List[TimelineScene]
    scenes: List[Scene]

    # Output nội dung
    script: Script
    seo: SEOData
    thumbnail: ThumbnailSpec