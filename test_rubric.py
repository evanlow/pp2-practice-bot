"""
test_rubric.py
Unit tests for PP2 evidence rubric data structures

Run with: python -m pytest test_rubric.py
Or: python test_rubric.py
"""

import unittest
from copy import deepcopy
from rubric import AssessmentItem, STAGE_CHECKLISTS, clone_stage_checklists


class TestAssessmentItem(unittest.TestCase):
    """Test AssessmentItem dataclass"""
    
    def test_evidence_item_creation_with_defaults(self):
        """Create AssessmentItem with default values"""
        item = AssessmentItem(id="test_id", text="Test item")
        
        self.assertEqual(item.id, "test_id")
        self.assertEqual(item.text, "Test item")
        self.assertEqual(item.status, "NYC")
        self.assertEqual(item.evidence_notes, "")
        self.assertEqual(item.last_updated_turn, 0)
    
    def test_evidence_item_creation_with_all_fields(self):
        """Create AssessmentItem with all fields specified"""
        item = AssessmentItem(
            id="custom_id",
            text="Custom text",
            status="C",
            attempts=2,
            evidence_notes="Some notes",
            last_updated_turn=5
        )
        
        self.assertEqual(item.id, "custom_id")
        self.assertEqual(item.text, "Custom text")
        self.assertEqual(item.status, "C")
        self.assertEqual(item.attempts, 2)
        self.assertEqual(item.evidence_notes, "Some notes")
        self.assertEqual(item.last_updated_turn, 5)
    
    def test_evidence_item_mutability(self):
        """Verify AssessmentItem fields can be modified"""
        item = AssessmentItem(id="test", text="Test")
        
        # Modify fields
        item.status = "C"
        item.evidence_notes = "Updated notes"
        item.last_updated_turn = 10
        
        self.assertEqual(item.status, "C")
        self.assertEqual(item.evidence_notes, "Updated notes")
        self.assertEqual(item.last_updated_turn, 10)


class TestStageChecklists(unittest.TestCase):
    """Test STAGE_CHECKLISTS structure"""
    
    def test_has_all_four_stages(self):
        """Verify STAGE_CHECKLISTS has all 4 PP2 stages"""
        expected_stages = ["Briefing", "Role Play", "Oral Questions", "Closing"]
        
        for stage in expected_stages:
            self.assertIn(stage, STAGE_CHECKLISTS, f"Missing stage: {stage}")
    
    def test_stage_count(self):
        """Verify exactly 4 stages in STAGE_CHECKLISTS"""
        self.assertEqual(len(STAGE_CHECKLISTS), 4)
    
    def test_briefing_checklist_structure(self):
        """Verify Briefing checklist has correct structure"""
        briefing = STAGE_CHECKLISTS["Briefing"]
        
        # Should have 14 items as specified
        self.assertEqual(len(briefing), 14)
        
        # All items should be AssessmentItem instances
        for item in briefing:
            self.assertIsInstance(item, AssessmentItem)
        
        # Check for specific expected items (based on requirements)
        item_ids = [item.id for item in briefing]
        # Verify we have numbered IDs from briefing_01 to briefing_14
        for i in range(1, 15):
            expected_id = f"briefing_{i:02d}"
            self.assertIn(expected_id, item_ids)
    
    def test_role_play_checklist_structure(self):
        """Verify Role Play checklist has correct structure"""
        role_play = STAGE_CHECKLISTS["Role Play"]
        
        # Should have 4 items as specified
        self.assertEqual(len(role_play), 4)
        
        # All items should be AssessmentItem instances
        for item in role_play:
            self.assertIsInstance(item, AssessmentItem)
        
        # Check for specific expected items
        item_ids = [item.id for item in role_play]
        self.assertIn("roleplay_context", item_ids)
        self.assertIn("roleplay_framework", item_ids)
        self.assertIn("roleplay_recommendations", item_ids)
        self.assertIn("roleplay_professionalism", item_ids)
    
    def test_oral_questions_checklist_structure(self):
        """Verify Oral Questions checklist has correct structure"""
        oral = STAGE_CHECKLISTS["Oral Questions"]
        
        # Should have 4 items as specified
        self.assertEqual(len(oral), 4)
        
        # All items should be AssessmentItem instances
        for item in oral:
            self.assertIsInstance(item, AssessmentItem)
        
        # Check for specific expected items
        item_ids = [item.id for item in oral]
        self.assertIn("oral_directness", item_ids)
        self.assertIn("oral_rationale", item_ids)
        self.assertIn("oral_clarity", item_ids)
        self.assertIn("oral_understanding", item_ids)
    
    def test_closing_checklist_structure(self):
        """Verify Closing checklist has correct structure"""
        closing = STAGE_CHECKLISTS["Closing"]
        
        # Should have 3 items as specified
        self.assertEqual(len(closing), 3)
        
        # All items should be AssessmentItem instances
        for item in closing:
            self.assertIsInstance(item, AssessmentItem)
        
        # Check for specific expected items
        item_ids = [item.id for item in closing]
        self.assertIn("closing_summary", item_ids)
        self.assertIn("closing_next_steps", item_ids)
        self.assertIn("closing_confirmation", item_ids)
    
    def test_all_items_have_required_fields(self):
        """Verify all checklist items have non-empty id and text"""
        for stage_name, checklist in STAGE_CHECKLISTS.items():
            for item in checklist:
                self.assertTrue(item.id, f"Empty id in {stage_name}")
                self.assertTrue(item.text, f"Empty text in {stage_name}")
                self.assertIsInstance(item.id, str)
                self.assertIsInstance(item.text, str)
    
    def test_all_items_start_unmet(self):
        """Verify all checklist items start with met=False"""
        for stage_name, checklist in STAGE_CHECKLISTS.items():
            for item in checklist:
                self.assertFalse(item.status == "C", f"Item {item.id} in {stage_name} should start unmet")
    
    def test_item_ids_are_unique_per_stage(self):
        """Verify no duplicate item IDs within each stage"""
        for stage_name, checklist in STAGE_CHECKLISTS.items():
            item_ids = [item.id for item in checklist]
            unique_ids = set(item_ids)
            self.assertEqual(len(item_ids), len(unique_ids), 
                           f"Duplicate IDs found in {stage_name}")


class TestCloneStageChecklists(unittest.TestCase):
    """Test clone_stage_checklists() function"""
    
    def test_returns_dict(self):
        """clone_stage_checklists() should return a dict"""
        cloned = clone_stage_checklists()
        self.assertIsInstance(cloned, dict)
    
    def test_has_same_stages(self):
        """Cloned dict should have same stage names as original"""
        cloned = clone_stage_checklists()
        
        self.assertEqual(set(cloned.keys()), set(STAGE_CHECKLISTS.keys()))
        self.assertEqual(len(cloned), len(STAGE_CHECKLISTS))
    
    def test_has_same_checklist_lengths(self):
        """Cloned checklists should have same lengths as originals"""
        cloned = clone_stage_checklists()
        
        for stage_name in STAGE_CHECKLISTS:
            original_length = len(STAGE_CHECKLISTS[stage_name])
            cloned_length = len(cloned[stage_name])
            self.assertEqual(cloned_length, original_length, 
                           f"Length mismatch for {stage_name}")
    
    def test_creates_deep_copy(self):
        """Modifications to clone should NOT affect original"""
        cloned = clone_stage_checklists()
        
        # Modify the clone
        cloned["Briefing"][0].status = "C"
        cloned["Briefing"][0].evidence_notes = "Modified"
        cloned["Briefing"][0].last_updated_turn = 99
        
        # Original should be unchanged
        original_item = STAGE_CHECKLISTS["Briefing"][0]
        self.assertFalse(original_item.status == "C", "Original was modified!")
        self.assertEqual(original_item.evidence_notes, "")
        self.assertEqual(original_item.last_updated_turn, 0)
    
    def test_multiple_clones_are_independent(self):
        """Multiple clones should be independent of each other"""
        clone1 = clone_stage_checklists()
        clone2 = clone_stage_checklists()
        
        # Modify clone1
        clone1["Role Play"][0].status = "C"
        clone1["Role Play"][0].evidence_notes = "Clone 1 modification"
        
        # Modify clone2 differently
        clone2["Role Play"][0].status = "NYC"
        clone2["Role Play"][0].evidence_notes = "Clone 2 modification"
        
        # Verify they're different
        self.assertEqual(clone1["Role Play"][0].status, "C")
        self.assertEqual(clone2["Role Play"][0].status, "NYC")
        self.assertEqual(clone1["Role Play"][0].evidence_notes, "Clone 1 modification")
        self.assertEqual(clone2["Role Play"][0].evidence_notes, "Clone 2 modification")
    
    def test_cloned_items_have_same_initial_values(self):
        """Cloned items should have same id and text as originals"""
        cloned = clone_stage_checklists()
        
        for stage_name in STAGE_CHECKLISTS:
            original_checklist = STAGE_CHECKLISTS[stage_name]
            cloned_checklist = cloned[stage_name]
            
            for i in range(len(original_checklist)):
                self.assertEqual(cloned_checklist[i].id, original_checklist[i].id)
                self.assertEqual(cloned_checklist[i].text, original_checklist[i].text)
                self.assertEqual(cloned_checklist[i].status == "C", original_checklist[i].status == "C")
    
    def test_clone_is_different_object(self):
        """Cloned dict should be a different object than original"""
        cloned = clone_stage_checklists()
        
        # Different dict object
        self.assertIsNot(cloned, STAGE_CHECKLISTS)
        
        # Different list objects for each stage
        for stage_name in STAGE_CHECKLISTS:
            self.assertIsNot(cloned[stage_name], STAGE_CHECKLISTS[stage_name])
        
        # Different AssessmentItem objects
        self.assertIsNot(cloned["Briefing"][0], STAGE_CHECKLISTS["Briefing"][0])


if __name__ == "__main__":
    # Run tests when script is executed directly
    unittest.main(verbosity=2)
