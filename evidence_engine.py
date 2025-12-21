"""
evidence_engine.py
Hybrid evidence detection with keyword matching and AI fallback

Uses keyword heuristics first (fast, free), then falls back to OpenAI API
for semantic understanding when keywords don't match.
"""

import os
from rubric import AssessmentItem


# ============================================================================
# CONSTANTS
# ============================================================================

# Maximum recovery attempts before an item is locked as NYC
MAX_ATTEMPTS = 3


# ============================================================================
# PROBE DETECTION
# ============================================================================

def is_good_probe(text: str) -> bool:
    """
    Check if assessor text contains probing language.
    
    Good probes encourage candidates to elaborate, explain, or demonstrate
    their competence with follow-up questions.
    
    Args:
        text: Assessor's text to analyze
        
    Returns:
        True if text contains probing patterns, False otherwise
    """
    text_lower = text.lower()
    
    probe_patterns = [
        "could you explain",
        "can you clarify",
        "walk me through",
        "what evidence",
        "how did you",
        "what would you do if",
        "can you show",
        "demonstrate",
        "why",
        "tell me more",
        "elaborate",
        "can you describe",
        "what do you mean",
        "give me an example"
    ]
    
    return any(pattern in text_lower for pattern in probe_patterns)


# ============================================================================
# KEYWORD MAPPINGS
# ============================================================================
# Map evidence item IDs to lists of detection keywords

EVIDENCE_KEYWORDS = {
    # Briefing stage (14 items)
    "briefing_01": ["my name is", "my name's", "i'm", "i am", "introduce", "assessor", "call me"],
    "briefing_02": ["nric", "identity", "attendance list", "assessment record", "confirm who you are"],
    "briefing_03": ["no worries", "take your time", "comfortable", "at ease", "relax"],
    "briefing_04": ["tsc", "competency", "standards", "skills framework", "criteria"],
    "briefing_05": ["purpose", "context", "today we", "objective"],
    "briefing_06": ["process", "role play", "oral questions", "method", "tools"],
    "briefing_07": ["evidence", "observations", "documents", "records", "notes"],
    "briefing_08": ["minutes", "duration", "time", "how long"],
    "briefing_09": ["special needs", "accommodation", "support", "adjustment"],
    "briefing_10": ["appeal"],
    "briefing_11": ["confidential", "privacy"],
    "briefing_12": ["legal", "safety", "ethical", "consent"],
    "briefing_13": ["questions", "clarify", "ask anytime", "if unclear"],
    "briefing_14": ["note-taking", "taking notes", "write notes", "record"],
    
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


def _ai_semantic_check(assessor_text: str, evidence_item: AssessmentItem) -> tuple[bool, str]:
    """
    Use OpenAI API to semantically check if assessor text addresses evidence item.
    
    Args:
        assessor_text: Text from assessor
        evidence_item: Assessment item to check
        
    Returns:
        Tuple of (is_met: bool, explanation: str)
    """
    try:
        from openai import OpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return False, "No API key"
        
        client = OpenAI(api_key=api_key)
        
        prompt = f"""Analyze if the assessor's statement addresses this PP2 assessment requirement.

Evidence requirement: "{evidence_item.text}"

Assessor's statement: "{assessor_text}"

Does the assessor's statement demonstrate they are addressing this requirement?
Respond with ONLY "YES" or "NO" followed by a brief reason (max 10 words).

Example responses:
YES - Assessor introduced themselves by name
NO - Statement unrelated to this requirement
"""
        
        response = client.chat.completions.create(
            model=os.getenv("MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,  # Deterministic
            max_tokens=30
        )
        
        answer = response.choices[0].message.content.strip()
        
        if answer.upper().startswith("YES"):
            reason = answer[3:].strip(" -")
            return True, f"AI: {reason}" if reason else "AI: Semantic match"
        else:
            return False, ""
            
    except Exception as e:
        # Silently fail - don't break the app if AI fails
        return False, f"AI error: {str(e)[:50]}"


def update_evidence_from_assessor_text(
    stage_checklists: dict[str, list[AssessmentItem]],
    stage: str,
    assessor_text: str,
    turn_index: int,
    use_ai_fallback: bool = True
) -> None:
    """
    Update evidence checklist based on assessor's text using hybrid detection.
    
    First tries keyword matching (fast, free), then falls back to AI semantic
    analysis if keywords don't match.
    
    This function modifies the stage_checklists dict in place, marking items
    as competent when relevant keywords are detected in the assessor's input.
    
    Args:
        stage_checklists: Dict mapping stage names to lists of AssessmentItems
        stage: Current PP2 stage name (e.g., "Briefing", "Role Play")
        assessor_text: Text typed by the assessor
        turn_index: Current turn/message number for tracking
        use_ai_fallback: Enable AI semantic check for items keywords miss (default: True)
    """
    # Get checklist for current stage
    if stage not in stage_checklists:
        return  # Stage not found, nothing to update
    
    checklist = stage_checklists[stage]
    assessor_text_lower = assessor_text.lower()
    
    # Check if assessor is using good probing technique
    is_probing = is_good_probe(assessor_text)
    
    # Phase 1: Keyword detection (fast, free)
    for item in checklist:
        # Skip if already competent
        if item.status == "C":
            continue
        
        # Get keywords for this item
        keywords = EVIDENCE_KEYWORDS.get(item.id, [])
        
        # Check if any keyword appears in assessor text
        matched_keywords = [kw for kw in keywords if kw in assessor_text_lower]
        
        if matched_keywords:
            # Item was mentioned/addressed
            # Check if this is a recovery scenario (item was attempted before)
            if item.attempts > 0:
                # Recovery scenario - need good probe to mark as competent
                if is_probing:
                    if item.attempts >= MAX_ATTEMPTS:
                        # Max attempts reached, cannot mark as competent
                        item.evidence_notes = f"Max recovery attempts reached ({MAX_ATTEMPTS})"
                        item.last_updated_turn = turn_index
                    else:
                        # Mark as competent via recovery probe
                        item.attempts += 1
                        item.status = "C"
                        item.evidence_notes = f"Recovered via probe (attempt {item.attempts})"
                        item.last_updated_turn = turn_index
                else:
                    # Mentioned but not probed - just note it
                    item.evidence_notes = f"Mentioned but not probed: {', '.join(matched_keywords[:2])}"
                    item.last_updated_turn = turn_index
            else:
                # First attempt - mark as competent directly
                item.attempts += 1
                item.status = "C"
                item.evidence_notes = f"Keywords: {', '.join(matched_keywords[:3])}"
                item.last_updated_turn = turn_index
    
    # Phase 2: AI fallback for unmet items (if enabled and text is substantial)
    if use_ai_fallback and len(assessor_text.strip()) > 10:
        for item in checklist:
            if item.status != "C":
                is_met, explanation = _ai_semantic_check(assessor_text, item)
                if is_met:
                    # AI detected semantic match
                    if item.attempts > 0:
                        # Recovery scenario - need good probe
                        if is_probing:
                            if item.attempts >= MAX_ATTEMPTS:
                                item.evidence_notes = f"Max recovery attempts reached ({MAX_ATTEMPTS})"
                                item.last_updated_turn = turn_index
                            else:
                                item.attempts += 1
                                item.status = "C"
                                item.evidence_notes = f"AI: {explanation} (attempt {item.attempts})"
                                item.last_updated_turn = turn_index
                        else:
                            # AI match but no probing - just note it
                            item.evidence_notes = f"AI detected: {explanation} (not probed)"
                            item.last_updated_turn = turn_index
                    else:
                        # First attempt - mark as competent directly
                        item.attempts += 1
                        item.status = "C"
                        item.evidence_notes = explanation
                        item.last_updated_turn = turn_index


def get_stage_completion_percentage(stage_checklists: dict[str, list[AssessmentItem]], stage: str) -> float:
    """
    Calculate completion percentage for a stage's checklist.
    
    Args:
        stage_checklists: Dict mapping stage names to lists of AssessmentItems
        stage: Stage name to check
    
    Returns:
        Percentage of items marked as competent (0.0 to 100.0)
    """
    if stage not in stage_checklists:
        return 0.0
    
    checklist = stage_checklists[stage]
    if not checklist:
        return 0.0
    
    met_count = sum(1 for item in checklist if item.status == "C")
    return (met_count / len(checklist)) * 100.0


def get_all_stages_summary(stage_checklists: dict[str, list[AssessmentItem]]) -> dict[str, dict]:
    """
    Get summary of evidence collection across all stages.
    
    Args:
        stage_checklists: Dict mapping stage names to lists of AssessmentItems
    
    Returns:
        Dict with stage names as keys and summary data as values
        Example: {"Briefing": {"total": 6, "met": 4, "percentage": 66.7}}
    """
    summary = {}
    
    for stage, checklist in stage_checklists.items():
        total = len(checklist)
        met = sum(1 for item in checklist if item.status == "C")
        percentage = (met / total * 100.0) if total > 0 else 0.0
        
        summary[stage] = {
            "total": total,
            "met": met,
            "percentage": round(percentage, 1)
        }
    
    return summary
