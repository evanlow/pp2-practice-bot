"""
rubric.py
Evidence tracking rubric for PP2 assessment stages

Defines checklists of evidence items to track during assessment.
"""

from dataclasses import dataclass, field
from copy import deepcopy


@dataclass
class AssessmentItem:
    """
    Represents a single assessment item to track during assessment.
    
    Attributes:
        id: Unique identifier for the item
        text: Description of the evidence to look for
        status: Assessment status - "NYC" (Not Yet Competent) or "C" (Competent)
        attempts: Number of times this item has been attempted
        evidence_notes: Notes about where/how evidence was observed
        last_updated_turn: Turn number when this item was last updated
    """
    id: str
    text: str
    status: str = "NYC"
    attempts: int = 0
    evidence_notes: str = ""
    last_updated_turn: int = 0


# ============================================================================
# STAGE CHECKLISTS
# ============================================================================
# Public-safe, generic evidence items for each PP2 stage

STAGE_CHECKLISTS = {
    "Briefing": [
        AssessmentItem(
            id="briefing_01",
            text="Introduced myself to the candidate."
        ),
        AssessmentItem(
            id="briefing_02",
            text="Confirmed the identity of the candidate against the attendance list or assessment records e.g. NRIC."
        ),
        AssessmentItem(
            id="briefing_03",
            text="Put the candidates at ease by adopting a friendly and helpful approach."
        ),
        AssessmentItem(
            id="briefing_04",
            text="Confirmed the Technical Skills and Competency and competency standards/reference to be assessed with the candidate."
        ),
        AssessmentItem(
            id="briefing_05",
            text="Explained the purpose and context of the assessment clearly."
        ),
        AssessmentItem(
            id="briefing_06",
            text="Explained the assessment process, methods and tools clearly."
        ),
        AssessmentItem(
            id="briefing_07",
            text="Established the evidences to be gathered during the assessment."
        ),
        AssessmentItem(
            id="briefing_08",
            text="Informed candidates the duration of the assessment."
        ),
        AssessmentItem(
            id="briefing_09",
            text="Identified and discussed on how to address candidate's special needs."
        ),
        AssessmentItem(
            id="briefing_10",
            text="Explained the process of appeal."
        ),
        AssessmentItem(
            id="briefing_11",
            text="Assured the candidate of the confidentiality of the assessment."
        ),
        AssessmentItem(
            id="briefing_12",
            text="Explained the legal, safety and ethical issues (if applicable)."
        ),
        AssessmentItem(
            id="briefing_13",
            text="Encouraged candidates to seek clarifications if in doubt."
        ),
        AssessmentItem(
            id="briefing_14",
            text="Explained the purpose of my note-taking during the assessment."
        ),
    ],
    
    "Role Play": [
        AssessmentItem(
            id="roleplay_context",
            text="Gathered relevant context and background information"
        ),
        AssessmentItem(
            id="roleplay_framework",
            text="Applied Skills Framework concepts appropriately"
        ),
        AssessmentItem(
            id="roleplay_recommendations",
            text="Provided clear, relevant recommendations"
        ),
        AssessmentItem(
            id="roleplay_professionalism",
            text="Maintained professional tone and appropriate communication"
        ),
    ],
    
    "Oral Questions": [
        AssessmentItem(
            id="oral_directness",
            text="Responded directly to questions asked"
        ),
        AssessmentItem(
            id="oral_rationale",
            text="Explained reasoning and rationale for decisions"
        ),
        AssessmentItem(
            id="oral_clarity",
            text="Clarified terms and concepts when needed"
        ),
        AssessmentItem(
            id="oral_understanding",
            text="Demonstrated clear understanding of subject matter"
        ),
    ],
    
    "Recovery": [
        AssessmentItem(
            id="recovery_gaps",
            text="Responded to probing questions about gaps or weaknesses"
        ),
        AssessmentItem(
            id="recovery_clarification",
            text="Clarified or expanded on previous responses"
        ),
        AssessmentItem(
            id="recovery_evidence",
            text="Provided additional evidence when prompted"
        ),
    ],
    
    "Closing": [
        AssessmentItem(
            id="closing_summary",
            text="Acknowledged summary of performance"
        ),
        AssessmentItem(
            id="closing_next_steps",
            text="Understood explanation of next steps"
        ),
        AssessmentItem(
            id="closing_confirmation",
            text="Confirmed understanding and asked final questions if any"
        ),
    ],
}


def clone_stage_checklists() -> dict[str, list[AssessmentItem]]:
    """
    Create a deep copy of the stage checklists.
    
    Returns a completely independent copy so each assessment session
    can track evidence without affecting the original template or other sessions.
    
    Returns:
        Deep copy of STAGE_CHECKLISTS dict
    """
    return deepcopy(STAGE_CHECKLISTS)
