"""
pp2_record.py
Assessment record data structures for PP2 assessment tracking

Defines dataclasses for criteria, GRO (Gap-Recovery-Outcome), and assessment rows.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Criterion:
    """
    Represents a single criterion from the assessment rubric.
    
    Attributes:
        id: Unique identifier for the criterion
        code: Short code (e.g., "RP1", "OQ2")
        text: Description of the criterion
    """
    id: str
    code: str
    text: str


@dataclass
class GRO:
    """
    Gap-Recovery-Outcome record for tracking recovery attempts.
    
    Attributes:
        gap: Description of what was missing or insufficient
        probe: The probing question asked to recover
        outcome: Result of the recovery attempt
        completed: Whether recovery was successful
        linked_turn_index: Turn number when this GRO was created
        candidate_reply_excerpt: Candidate's response to the probe
    """
    gap: str = ""
    probe: str = ""
    outcome: str = ""
    completed: bool = False
    linked_turn_index: int = 0
    candidate_reply_excerpt: str = ""


@dataclass
class AssessmentRow:
    """
    Single row in the assessment record.
    
    Attributes:
        criterion: The criterion being assessed
        status: Assessment status - "C" (Competent) or "NYC" (Not Yet Competent)
        evidence_note: Notes about evidence observed
        gro: Optional GRO record if recovery was attempted
    """
    criterion: Criterion
    status: str = "NYC"
    evidence_note: str = ""
    gro: Optional[GRO] = None


# ============================================================================
# CRITERIA DEFINITIONS
# ============================================================================

def get_roleplay_criteria() -> list[Criterion]:
    """
    Get the list of criteria for Role Play assessment stage.
    
    Returns:
        List of Criterion objects for role play assessment
    """
    return [
        Criterion(
            id="rp_01",
            code="RP1",
            text="Establishes rapport and creates a comfortable environment for the interaction"
        ),
        Criterion(
            id="rp_02",
            code="RP2",
            text="Gathers relevant background information through effective questioning"
        ),
        Criterion(
            id="rp_03",
            code="RP3",
            text="Demonstrates understanding of applicable competency frameworks"
        ),
        Criterion(
            id="rp_04",
            code="RP4",
            text="Provides clear and appropriate recommendations based on assessment context"
        ),
        Criterion(
            id="rp_05",
            code="RP5",
            text="Maintains professionalism and appropriate communication throughout"
        ),
    ]
