"""
evidence_engine.py
Lightweight rule-based evidence detection

Uses keyword heuristics to automatically mark evidence items as met
based on assessor input. Deterministic and transparent.
"""

from rubric import EvidenceItem


# ============================================================================
# KEYWORD MAPPINGS
# ============================================================================
# Map evidence item IDs to lists of detection keywords

EVIDENCE_KEYWORDS = {
    # Briefing stage
    "briefing_identity": ["nric", "identity", "attendance", "name", "confirm who you are"],
    "briefing_purpose": ["purpose", "objective", "why we're here", "goal of this", "assessment is to"],
    "briefing_process": ["process", "role play", "oral questions", "stages", "how this works", "assessment method"],
    "briefing_confidentiality": ["confidential", "privacy", "data protection", "information will be"],
    "briefing_duration": ["minutes", "duration", "time", "how long", "take about"],
    "briefing_questions": ["any questions", "do you have questions", "ask me anything", "clarify"],
    
    # Role Play stage
    "roleplay_context": ["tell me about", "background", "situation", "context", "what's happening"],
    "roleplay_framework": ["skills framework", "competency", "skill set", "career map", "framework"],
    "roleplay_recommendations": ["recommend", "suggest", "advice", "course", "training", "pathway"],
    "roleplay_professionalism": ["professional", "appropriate", "courteous"],  # Harder to detect
    
    # Oral Questions stage
    "oral_directness": ["why did you", "can you explain", "what was your reasoning"],
    "oral_rationale": ["because", "reason", "rationale", "decided to", "approach was"],
    "oral_clarity": ["clarify", "what do you mean", "can you explain", "define"],
    "oral_understanding": ["understand", "knowledge", "aware of", "familiar with"],
    
    # Recovery stage
    "recovery_gaps": ["noticed that", "you didn't mention", "what about", "gap", "missing"],
    "recovery_clarification": ["clarify", "expand on", "tell me more", "elaborate"],
    "recovery_evidence": ["evidence", "example", "demonstrate", "show me"],
    
    # Closing stage
    "closing_summary": ["summary", "overall", "performance", "did well", "areas for"],
    "closing_next_steps": ["next steps", "what happens next", "follow up", "timeline"],
    "closing_confirmation": ["any questions", "understand", "clear", "thank you"],
}


def update_evidence_from_assessor_text(
    stage_checklists: dict[str, list[EvidenceItem]],
    stage: str,
    assessor_text: str,
    turn_index: int
) -> None:
    """
    Update evidence checklist based on assessor's text using keyword detection.
    
    This function modifies the stage_checklists dict in place, marking items
    as met when relevant keywords are detected in the assessor's input.
    
    Args:
        stage_checklists: Dict mapping stage names to lists of EvidenceItems
        stage: Current PP2 stage name (e.g., "Briefing", "Role Play")
        assessor_text: Text typed by the assessor
        turn_index: Current turn/message number for tracking
    """
    # Get checklist for current stage
    if stage not in stage_checklists:
        return  # Stage not found, nothing to update
    
    checklist = stage_checklists[stage]
    assessor_text_lower = assessor_text.lower()
    
    # Check each evidence item in the current stage
    for item in checklist:
        # Skip if already met
        if item.met:
            continue
        
        # Get keywords for this item
        keywords = EVIDENCE_KEYWORDS.get(item.id, [])
        
        # Check if any keyword appears in assessor text
        matched_keywords = [kw for kw in keywords if kw in assessor_text_lower]
        
        if matched_keywords:
            # Mark as met
            item.met = True
            item.evidence_notes = f"Detected keywords: {', '.join(matched_keywords[:3])}"  # Show first 3
            item.last_updated_turn = turn_index


def get_stage_completion_percentage(stage_checklists: dict[str, list[EvidenceItem]], stage: str) -> float:
    """
    Calculate completion percentage for a stage's checklist.
    
    Args:
        stage_checklists: Dict mapping stage names to lists of EvidenceItems
        stage: Stage name to check
    
    Returns:
        Percentage of items met (0.0 to 100.0)
    """
    if stage not in stage_checklists:
        return 0.0
    
    checklist = stage_checklists[stage]
    if not checklist:
        return 0.0
    
    met_count = sum(1 for item in checklist if item.met)
    return (met_count / len(checklist)) * 100.0


def get_all_stages_summary(stage_checklists: dict[str, list[EvidenceItem]]) -> dict[str, dict]:
    """
    Get summary of evidence collection across all stages.
    
    Args:
        stage_checklists: Dict mapping stage names to lists of EvidenceItems
    
    Returns:
        Dict with stage names as keys and summary data as values
        Example: {"Briefing": {"total": 6, "met": 4, "percentage": 66.7}}
    """
    summary = {}
    
    for stage, checklist in stage_checklists.items():
        total = len(checklist)
        met = sum(1 for item in checklist if item.met)
        percentage = (met / total * 100.0) if total > 0 else 0.0
        
        summary[stage] = {
            "total": total,
            "met": met,
            "percentage": round(percentage, 1)
        }
    
    return summary
