"""
test_oq_rubric.py
Tests for Oral Questions rubric conversion function

Run with: pytest test_oq_rubric.py -v
"""

import unittest
import yaml
from rubric import get_oral_questions_rubric


class TestGetOralQuestionsRubric(unittest.TestCase):
    """Test get_oral_questions_rubric function"""
    
    def setUp(self):
        """Set up test data"""
        # Sample OQ YAML data
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
        data = yaml.safe_load(oq_yaml)
        self.oq_criteria = data["oral_questions"]
    
    def test_returns_list(self):
        """Function should return a list"""
        result = get_oral_questions_rubric(self.oq_criteria)
        self.assertIsInstance(result, list)
    
    def test_correct_count(self):
        """Should return 3 rubric items"""
        result = get_oral_questions_rubric(self.oq_criteria)
        self.assertEqual(len(result), 3)
    
    def test_required_fields_present(self):
        """Each item should have code, title, instruction"""
        result = get_oral_questions_rubric(self.oq_criteria)
        
        for item in result:
            self.assertIn("code", item)
            self.assertIn("title", item)
            self.assertIn("instruction", item)
    
    def test_oq1_structure(self):
        """OQ1 should have all expected fields"""
        result = get_oral_questions_rubric(self.oq_criteria)
        
        oq1 = next((item for item in result if item["code"] == "OQ1"), None)
        self.assertIsNotNone(oq1)
        
        self.assertEqual(oq1["title"], "Benefits of adopting the Skills Framework")
        self.assertIn("Explain the benefits", oq1["instruction"])
        self.assertEqual(oq1["minimum_points_required"], 3)
        self.assertIn("evidence_guidance", oq1)
        self.assertEqual(len(oq1["evidence_guidance"]), 5)
    
    def test_oq2a_structure(self):
        """OQ2a should have expected_position field"""
        result = get_oral_questions_rubric(self.oq_criteria)
        
        oq2a = next((item for item in result if item["code"] == "OQ2a"), None)
        self.assertIsNotNone(oq2a)
        
        self.assertEqual(oq2a["title"], "Skills Framework usage requirements")
        self.assertIn("expected_position", oq2a)
        self.assertFalse(oq2a["expected_position"])
    
    def test_oq2b_structure(self):
        """OQ2b should have minimum_points_required and evidence_guidance"""
        result = get_oral_questions_rubric(self.oq_criteria)
        
        oq2b = next((item for item in result if item["code"] == "OQ2b"), None)
        self.assertIsNotNone(oq2b)
        
        self.assertEqual(oq2b["title"], "Flexibility of the Skills Framework")
        self.assertEqual(oq2b["minimum_points_required"], 2)
        self.assertIn("evidence_guidance", oq2b)
        self.assertEqual(len(oq2b["evidence_guidance"]), 4)
    
    def test_preserves_yaml_content(self):
        """Should preserve exact titles and instructions from YAML"""
        result = get_oral_questions_rubric(self.oq_criteria)
        
        # Verify titles are preserved exactly
        titles = [item["title"] for item in result]
        self.assertIn("Benefits of adopting the Skills Framework", titles)
        self.assertIn("Skills Framework usage requirements", titles)
        self.assertIn("Flexibility of the Skills Framework", titles)
    
    def test_empty_dict(self):
        """Should handle empty dict gracefully"""
        result = get_oral_questions_rubric({})
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
