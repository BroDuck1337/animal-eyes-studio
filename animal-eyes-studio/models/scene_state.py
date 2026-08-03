from dataclasses import dataclass


@dataclass
class CameraState:
    """
    Trạng thái camera tại một thời điểm/cảnh trong timeline.
    """
    shot_type: str = "medium"
    angle: str = "eye_level"
    movement: str = "static"
    focus_subject: str = ""
    framing: str = "center"


@dataclass
class SceneState:
    """
    Trạng thái thế giới/cảm xúc/nhân vật đi kèm với một TimelineScene.
    """
    weather: str
    lighting: str
    danger: bool
    food: bool
    health: int
    emotion: str
    camera: CameraState