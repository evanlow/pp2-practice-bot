"""
Quick test for pp2_gro module
"""
from pp2_gro import GROEntry, CriterionRecord


def test_gro_entry_creation():
    """Test GROEntry dataclass creation"""
    entry = GROEntry(
        gap="Insufficient detail",
        probe_turn=5,
        probe_text="Can you explain more?",
        response_turn=6,
        response_text="Here's more detail...",
        outcome="Recovered to C",
        completed=True
    )
    
    assert entry.gap == "Insufficient detail"
    assert entry.probe_turn == 5
    assert entry.probe_text == "Can you explain more?"
    assert entry.response_turn == 6
    assert entry.response_text == "Here's more detail..."
    assert entry.outcome == "Recovered to C"
    assert entry.completed is True
    print("✓ GROEntry creation test passed")


def test_gro_entry_defaults():
    """Test GROEntry default values"""
    entry = GROEntry()
    
    assert entry.gap == ""
    assert entry.probe_turn is None
    assert entry.probe_text == ""
    assert entry.response_turn is None
    assert entry.response_text == ""
    assert entry.outcome == ""
    assert entry.completed is False
    print("✓ GROEntry defaults test passed")


def test_criterion_record_creation():
    """Test CriterionRecord dataclass creation"""
    gro = GROEntry(gap="Test gap", completed=False)
    record = CriterionRecord(
        code="A1",
        status="NYC",
        evidence_note="Some evidence",
        gro=gro
    )
    
    assert record.code == "A1"
    assert record.status == "NYC"
    assert record.evidence_note == "Some evidence"
    assert record.gro is not None
    assert record.gro.gap == "Test gap"
    assert record.gro.completed is False
    print("✓ CriterionRecord creation test passed")


def test_criterion_record_defaults():
    """Test CriterionRecord default values"""
    record = CriterionRecord(code="K2")
    
    assert record.code == "K2"
    assert record.status == "C"
    assert record.evidence_note == ""
    assert record.gro is None
    print("✓ CriterionRecord defaults test passed")


if __name__ == "__main__":
    test_gro_entry_creation()
    test_gro_entry_defaults()
    test_criterion_record_creation()
    test_criterion_record_defaults()
    print("\n✅ All pp2_gro tests passed!")
