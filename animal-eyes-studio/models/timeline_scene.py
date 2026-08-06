from dataclasses import dataclass
from typing import Optional

from .scene_state import SceneState


@dataclass
class TimelineScene:
    """
    Cảnh timeline mức cao, dùng để phân bổ thời gian và mô tả nhịp câu chuyện.
    """
    scene_id: int
    time: str
    event: str

    # Metadata mở rộng về thời gian & nhịp
    start_time: float = 0.0
    end_time: float = 0.0
    duration: float = 0.0
    summary: str = ""
    location: str = ""
    mood: str = ""
    intensity: int = 1

    # Trạng thái thế giới/cảm xúc/camera tại cảnh này
    state: Optional[SceneState] = None
