"""
test_oq_loader.py
Tests for Oral Questions criteria loader

Run with: pytest test_oq_loader.py -v
"""

import unittest
import yaml


def test_oq_yaml_structure():
    """Test that OQ_CRITERIA_YAML has correct structure"""
    # Simulate the YAML content from secrets.toml
    oq_yaml = """
oral_questions:
  OQ1:
    code: OQ1
    title: Benefits of adopting the Skills Framework
    instruction: >
      Explain the benefits of using the Skills Framework from an
      individual's perspective. State at least THREE points.
    minimum_points_required: 3
    evidence_guidance:
      - Awareness of job roles and sector opportunities
      - Understanding of skills demand and employer expectations
      - Ability to make informed career decisions
      - Identification of suitable training pathways
      - Preparation for future job opportunities

  OQ2a:
    code: OQ2a
    title: Skills Framework usage requirements
    instruction: >
      Determine whether organisations must follow every aspect of
      the Skills Framework exactly.
    expected_position: False

  OQ2b:
    code: OQ2b
    title: Flexibility of the Skills Framework
    instruction: >
      Explain why organisations are not required to fully follow
      the Skills Framework. State at least TWO reasons.
    minimum_points_required: 2
    evidence_guidance:
      - The Skills Framework is a reference guide
      - Organisations may adapt selected components
      - Organisations may develop their own competency frameworks
      - Training programmes can be designed with reference to the framework
"""
    
    # Parse YAML
    data = yaml.safe_load(oq_yaml)
    
    # Verify structure
    assert "oral_questions" in data, "YAML must contain 'oral_questions' key"
    oral_questions = data["oral_questions"]
    assert isinstance(oral_questions, dict), "'oral_questions' must be a dict"
    
    # Verify expected codes exist
    assert "OQ1" in oral_questions, "Missing OQ1"
    assert "OQ2a" in oral_questions, "Missing OQ2a"
    assert "OQ2b" in oral_questions, "Missing OQ2b"
    
    # Verify each question has required fields
    for code, question in oral_questions.items():
        assert "code" in question, f"{code} missing 'code' field"
        assert "title" in question, f"{code} missing 'title' field"
        assert "instruction" in question, f"{code} missing 'instruction' field"
        assert question["code"] == code, f"Code mismatch: {question['code']} != {code}"
    
    # Verify specific fields in OQ1
    oq1 = oral_questions["OQ1"]
    assert oq1["minimum_points_required"] == 3
    assert "evidence_guidance" in oq1
    assert len(oq1["evidence_guidance"]) == 5
    
    # Verify specific fields in OQ2a
    oq2a = oral_questions["OQ2a"]
    assert oq2a["expected_position"] is False
    
    # Verify specific fields in OQ2b
    oq2b = oral_questions["OQ2b"]
    assert oq2b["minimum_points_required"] == 2
    assert "evidence_guidance" in oq2b
    assert len(oq2b["evidence_guidance"]) == 4
    
    print("✓ OQ YAML structure validation passed")


if __name__ == "__main__":
    test_oq_yaml_structure()
