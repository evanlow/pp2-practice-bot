"""
pp2_state.py
PP2 Stage State Machine

Manages the progression through PP2 assessment stages.
"""

from enum import Enum
from dataclasses import dataclass


class PP2Stage(Enum):
    """PP2 assessment stages in order"""
    BRIEFING = "Briefing"
    ROLE_PLAY = "Role Play"
    ORAL_QUESTIONS = "Oral Questions"
    CLOSING = "Closing"


# Define the order of stages for transitions
STAGE_ORDER = [
    PP2Stage.BRIEFING,
    PP2Stage.ROLE_PLAY,
    PP2Stage.ORAL_QUESTIONS,
    PP2Stage.CLOSING,
]


@dataclass
class PP2Session:
    """
    Manages PP2 assessment session state.
    
    Attributes:
        current_stage: The current PP2 stage (default: Briefing)
    """
    current_stage: PP2Stage = PP2Stage.BRIEFING
    
    def next_stage(self) -> None:
        """Move to the next stage (if not already at the last stage)"""
        current_index = STAGE_ORDER.index(self.current_stage)
        if current_index < len(STAGE_ORDER) - 1:
            self.current_stage = STAGE_ORDER[current_index + 1]
    
    def prev_stage(self) -> None:
        """Move to the previous stage (if not already at the first stage)"""
        current_index = STAGE_ORDER.index(self.current_stage)
        if current_index > 0:
            self.current_stage = STAGE_ORDER[current_index - 1]
    
    def reset(self) -> None:
        """Reset to the first stage (Briefing)"""
        self.current_stage = PP2Stage.BRIEFING
    
    def set_stage(self, stage: PP2Stage) -> None:
        """Jump to a specific stage"""
        if stage in STAGE_ORDER:
            self.current_stage = stage
    
    def get_stage_name(self) -> str:
        """Get the display name of the current stage"""
        return self.current_stage.value
