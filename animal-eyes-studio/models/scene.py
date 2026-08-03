from dataclasses import dataclass
from typing import Optional


@dataclass
class Scene:
    """
    Cảnh chi tiết dùng cho bước sinh nội dung, hình ảnh và script.
    """
    scene_id: int
    event: str

    # Thời gian trong video
    start_time: float
    end_time: float

    # Nội dung mô tả
    title: str
    summary: str
    visual_description: str
    audio_description: str

    # Thông tin cinematic
    camera_style: str
    mood: str
    location: str

    # Điều khiển nhịp kể
    intensity: int = 1
    narration: str = ""
    dialogue: Optional[str] = None