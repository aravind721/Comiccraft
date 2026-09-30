from typing import List
from app.schemas import StoryPanel


def build_comic_layout(story_panels: List[StoryPanel], image_paths: List[str]):
    if len(story_panels) != len(image_paths):
        raise ValueError("The number of panels and images must match.")

    return [
        {
            "panel_number": panel.panel_number,
            "title": panel.title,
            "image": image_paths[index],
            "scene_description": panel.scene_description,
            "caption": panel.caption,
            "narration": panel.narration,
            "dialogue": panel.dialogue,
            "image_prompt": panel.image_prompt,
        }
        for index, panel in enumerate(story_panels)
    ]
