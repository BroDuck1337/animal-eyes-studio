from dataclasses import dataclass
from typing import Optional


@dataclass
class StoryEvent:
    """
    Sự kiện cốt lõi trong timeline của câu chuyện.
    """
    event: str
    importance: int

    # Metadata mở rộng cho pipeline
    description: str = ""
    duration_hint: Optional[float] = None  # thời lượng gợi ý (giây)
    intensity: int = 1  # 1-10
    location: str = ""
    mood: str = ""
    objective: str = ""
    conflict: str = ""
    resolution_hint: str = ""