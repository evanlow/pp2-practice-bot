"""
rubric.py
Evidence tracking rubric for PP2 assessment stages

Defines checklists of evidence items to track during assessment.
"""

from dataclasses import dataclass, field
from copy import deepcopy


@dataclass
class EvidenceItem:
    """
    Represents a single evidence item to track during assessment.
    
    Attributes:
        id: Unique identifier for the item
        text: Description of the evidence to look for
        met: Whether this evidence has been observed (default: False)
        evidence_notes: Notes about where/how evidence was observed
        last_updated_turn: Turn number when this item was last updated
    """
    id: str
    text: str
    met: bool = False
    evidence_notes: str = ""
    last_updated_turn: int = 0


# ============================================================================
# STAGE CHECKLISTS
# ============================================================================
# Public-safe, generic evidence items for each PP2 stage

STAGE_CHECKLISTS = {
    "Briefing": [
        EvidenceItem(
            id="briefing_identity",
            text="Confirmed candidate identity and role"
        ),
        EvidenceItem(
            id="briefing_purpose",
            text="Explained purpose and objectives of assessment"
        ),
        EvidenceItem(
            id="briefing_process",
            text="Described assessment process and methods to be used"
        ),
        EvidenceItem(
            id="briefing_confidentiality",
            text="Covered confidentiality and data handling"
        ),
        EvidenceItem(
            id="briefing_duration",
            text="Informed candidate of expected duration"
        ),
        EvidenceItem(
            id="briefing_questions",
            text="Invited and answered candidate's questions"
        ),
    ],
    
    "Role Play": [
        EvidenceItem(
            id="roleplay_context",
            text="Gathered relevant context and background information"
        ),
        EvidenceItem(
            id="roleplay_framework",
            text="Applied Skills Framework concepts appropriately"
        ),
        EvidenceItem(
            id="roleplay_recommendations",
            text="Provided clear, relevant recommendations"
        ),
        EvidenceItem(
            id="roleplay_professionalism",
            text="Maintained professional tone and appropriate communication"
        ),
    ],
    
    "Oral Questions": [
        EvidenceItem(
            id="oral_directness",
            text="Responded directly to questions asked"
        ),
        EvidenceItem(
            id="oral_rationale",
            text="Explained reasoning and rationale for decisions"
        ),
        EvidenceItem(
            id="oral_clarity",
            text="Clarified terms and concepts when needed"
        ),
        EvidenceItem(
            id="oral_understanding",
            text="Demonstrated clear understanding of subject matter"
        ),
    ],
    
    "Recovery": [
        EvidenceItem(
            id="recovery_gaps",
            text="Responded to probing questions about gaps or weaknesses"
        ),
        EvidenceItem(
            id="recovery_clarification",
            text="Clarified or expanded on previous responses"
        ),
        EvidenceItem(
            id="recovery_evidence",
            text="Provided additional evidence when prompted"
        ),
    ],
    
    "Closing": [
        EvidenceItem(
            id="closing_summary",
            text="Acknowledged summary of performance"
        ),
        EvidenceItem(
            id="closing_next_steps",
            text="Understood explanation of next steps"
        ),
        EvidenceItem(
            id="closing_confirmation",
            text="Confirmed understanding and asked final questions if any"
        ),
    ],
}


def clone_stage_checklists() -> dict[str, list[EvidenceItem]]:
    """
    Create a deep copy of the stage checklists.
    
    Returns a completely independent copy so each assessment session
    can track evidence without affecting the original template or other sessions.
    
    Returns:
        Deep copy of STAGE_CHECKLISTS dict
    """
    return deepcopy(STAGE_CHECKLISTS)
