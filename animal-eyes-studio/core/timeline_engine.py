from typing import List

from models.timeline_scene import TimelineScene
from core.story_bible import StoryBible
from models.story_event import StoryEvent
from models.scene_state import SceneState, CameraState


class TimelineEngine:
    """
    Xây dựng timeline có thời gian cụ thể từ StoryBible.
    - Dùng StoryBible.duration (tổng thời lượng, giây).
    - Dùng StoryEvent.duration_hint nếu có, nếu không thì chia đều.
    - Gắn thêm SceneState (weather, lighting, danger, food, health, emotion, camera).
    """

    def _compute_event_durations(self, events: List[StoryEvent], total_duration: int) -> List[float]:
        """
        Tính duration cho từng event dựa trên duration_hint (nếu có),
        nếu không có thì chia đều phần còn lại.
        """
        n = len(events)
        if n == 0:
            return []

        # Tách event có hint và không có hint
        hinted = []
        no_hint = []
        for ev in events:
            if ev.duration_hint and ev.duration_hint > 0:
                hinted.append(ev)
            else:
                no_hint.append(ev)

        sum_hints = sum(ev.duration_hint for ev in hinted if ev.duration_hint)
        remaining = max(total_duration - sum_hints, 0)

        durations: List[float] = []

        if no_hint:
            base = remaining / len(no_hint) if remaining > 0 else 0
        else:
            base = 0

        for ev in events:
            if ev in hinted and ev.duration_hint:
                durations.append(float(ev.duration_hint))
            else:
                durations.append(float(base))

        # Nếu tổng lệch nhẹ do float, scale lại cho khớp total_duration
        total = sum(durations)
        if total > 0 and abs(total - total_duration) > 1e-6:
            scale = total_duration / total
            durations = [d * scale for d in durations]

        return durations

    def _build_scene_state(self, bible: StoryBible, event: StoryEvent) -> SceneState:
        """
        Tạo SceneState đơn giản dựa trên world + event.
        Sau này có thể nâng cấp bằng StateEngine/AI.
        """
        # Weather & lighting lấy từ world
        weather = bible.world.weather
        lighting = bible.world.lighting

        # Heuristic đơn giản cho danger/food/health/emotion theo event name
        name = event.event.lower()

        danger = any(k in name for k in ["predator", "attack", "danger", "threat"])
        food = any(k in name for k in ["food", "eat", "hunting", "forage"])
        # health: mặc định 100, nếu có danger thì giảm nhẹ
        health = 80 if danger else 100

        if "return" in name or "home" in name:
            emotion = "relieved"
        elif danger:
            emotion = "fear"
        elif food:
            emotion = "focused"
        else:
            emotion = "neutral"

        # CameraState đơn giản theo loại event
        if danger:
            camera = CameraState(
                shot_type="close_up",
                angle="low",
                movement="handheld",
                focus_subject="predator_or_ant",
                framing="off_center",
            )
        elif food:
            camera = CameraState(
                shot_type="macro",
                angle="eye_level",
                movement="slow_push_in",
                focus_subject="food_or_ant_mouth",
                framing="center",
            )
        else:
            camera = CameraState(
                shot_type="medium",
                angle="eye_level",
                movement="static",
                focus_subject="ant",
                framing="center",
            )

        return SceneState(
            weather=weather,
            lighting=lighting,
            danger=danger,
            food=food,
            health=health,
            emotion=emotion,
            camera=camera,
        )

    def build(self, bible: StoryBible) -> List[TimelineScene]:
        """
        Từ StoryBible.timeline (list StoryEvent) + duration tổng,
        sinh ra list TimelineScene với start_time, end_time, duration, summary, mood, location, intensity
        và kèm theo SceneState.
        """
        scenes: List[TimelineScene] = []

        events: List[StoryEvent] = bible.timeline
        total_duration = bible.duration

        durations = self._compute_event_durations(events, total_duration)

        current_time = 0.0

        for idx, (event, dur) in enumerate(zip(events, durations)):
            start_time = current_time
            end_time = current_time + dur
            current_time = end_time

            state = self._build_scene_state(bible, event)

            scenes.append(
                TimelineScene(
                    scene_id=idx + 1,
                    time=f"{start_time:.2f}-{end_time:.2f}s",
                    event=event.event,
                    start_time=start_time,
                    end_time=end_time,
                    duration=dur,
                    summary=event.description or event.event,
                    location=event.location or bible.world.ecosystem,
                    mood=event.mood or state.emotion,
                    intensity=event.intensity,
                    state=state,
                )
            )

        return scenes