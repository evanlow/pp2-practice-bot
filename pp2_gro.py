"""
pp2_gro.py
GRO enforcement data structures for PP2 Role Play assessment

Defines dataclasses for tracking Gap-Recovery-Outcome (GRO) records
and criterion assessment status.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class GROEntry:
    """
    Gap-Recovery-Outcome entry for tracking a single recovery attempt.
    
    Attributes:
        gap: Description of what was missing or insufficient
        probe_turn: Index of the assessor probing question in chat history
        probe_text: The probing question text
        response_turn: Index of candidate response after probe
        response_text: The candidate's response text
        outcome: Result of recovery ("Recovered to C" or "Still NYC")
        completed: Whether this GRO record is finalized
    """
    gap: str = ""
    probe_turn: Optional[int] = None
    probe_text: str = ""
    response_turn: Optional[int] = None
    response_text: str = ""
    outcome: str = ""
    completed: bool = False


@dataclass
class CriterionRecord:
    """
    Assessment record for a single criterion.
    
    Attributes:
        code: Criterion code (e.g., "A1", "K2", "RP1")
        status: Assessment status - "C" (Competent) or "NYC" (Not Yet Competent)
        evidence_note: Notes about evidence observed
        gro: Optional GRO entry if recovery was attempted
    """
    code: str
    status: str = "C"
    evidence_note: str = ""
    gro: Optional[GROEntry] = None
