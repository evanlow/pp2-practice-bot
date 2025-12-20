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
            id="briefing_01",
            text="Introduced myself to the candidate."
        ),
        EvidenceItem(
            id="briefing_02",
            text="Confirmed the identity of the candidate against the attendance list or assessment records e.g. NRIC."
        ),
        EvidenceItem(
            id="briefing_03",
            text="Put the candidates at ease by adopting a friendly and helpful approach."
        ),
        EvidenceItem(
            id="briefing_04",
            text="Confirmed the Technical Skills and Competency and competency standards/reference to be assessed with the candidate."
        ),
        EvidenceItem(
            id="briefing_05",
            text="Explained the purpose and context of the assessment clearly."
        ),
        EvidenceItem(
            id="briefing_06",
            text="Explained the assessment process, methods and tools clearly."
        ),
        EvidenceItem(
            id="briefing_07",
            text="Established the evidences to be gathered during the assessment."
        ),
        EvidenceItem(
            id="briefing_08",
            text="Informed candidates the duration of the assessment."
        ),
        EvidenceItem(
            id="briefing_09",
            text="Identified and discussed on how to address candidate's special needs."
        ),
        EvidenceItem(
            id="briefing_10",
            text="Explained the process of appeal."
        ),
        EvidenceItem(
            id="briefing_11",
            text="Assured the candidate of the confidentiality of the assessment."
        ),
        EvidenceItem(
            id="briefing_12",
            text="Explained the legal, safety and ethical issues (if applicable)."
        ),
        EvidenceItem(
            id="briefing_13",
            text="Encouraged candidates to seek clarifications if in doubt."
        ),
        EvidenceItem(
            id="briefing_14",
            text="Explained the purpose of my note-taking during the assessment."
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
