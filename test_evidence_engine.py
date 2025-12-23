"""
test_evidence_engine.py
Unit tests for evidence detection engine

Run with: python -m pytest test_evidence_engine.py
Or: python test_evidence_engine.py
"""

import unittest
from rubric import AssessmentItem, clone_stage_checklists
from evidence_engine import (
    update_evidence_from_assessor_text,
    get_stage_completion_percentage,
    get_all_stages_summary,
    EVIDENCE_KEYWORDS
)


class TestEvidenceKeywords(unittest.TestCase):
    """Test EVIDENCE_KEYWORDS structure"""
    
    def test_has_briefing_keywords(self):
        """Verify briefing stage items have keyword mappings"""
        briefing_ids = [
            "briefing_01", "briefing_02", "briefing_03", "briefing_04",
            "briefing_05", "briefing_06", "briefing_07", "briefing_08",
            "briefing_09", "briefing_10", "briefing_11", "briefing_12",
            "briefing_13", "briefing_14"
        ]
        
        for item_id in briefing_ids:
            self.assertIn(item_id, EVIDENCE_KEYWORDS, f"Missing keywords for {item_id}")
            self.assertIsInstance(EVIDENCE_KEYWORDS[item_id], list)
            self.assertGreater(len(EVIDENCE_KEYWORDS[item_id]), 0)
    
    def test_all_keywords_are_lowercase(self):
        """Verify all keywords are lowercase for case-insensitive matching"""
        for item_id, keywords in EVIDENCE_KEYWORDS.items():
            for keyword in keywords:
                self.assertEqual(keyword, keyword.lower(), 
                               f"Keyword '{keyword}' in {item_id} is not lowercase")


class TestUpdateEvidenceFromAssessorText(unittest.TestCase):
    """Test update_evidence_from_assessor_text() function"""
    
    def setUp(self):
        """Create fresh checklist before each test"""
        self.checklists = clone_stage_checklists()
        self.turn_index = 1
    
    def test_marks_item_met_when_keyword_detected(self):
        """Item should be marked met when keyword appears in text"""
        # Use "nric" keyword for identity check
        update_evidence_from_assessor_text(
            self.checklists,
            "Briefing",
            "Can I see your NRIC for verification?",
            self.turn_index
        )
        
        # Find the identity item
        identity_item = next(
            item for item in self.checklists["Briefing"]
            if item.id == "briefing_02"
        )
        
        self.assertTrue(identity_item.status == "C")
        self.assertIn("nric", identity_item.evidence_notes.lower())
        self.assertEqual(identity_item.last_updated_turn, self.turn_index)
    
    def test_case_insensitive_matching(self):
        """Keywords should match regardless of case"""
        # Try various cases
        texts = [
            "Please show your NRIC",
            "please show your nric",
            "Please Show Your NrIc"
        ]
        
        for text in texts:
            checklists = clone_stage_checklists()
            update_evidence_from_assessor_text(checklists, "Briefing", text, 1)
            
            identity_item = next(
                item for item in checklists["Briefing"]
                if item.id == "briefing_02"
            )
            self.assertTrue(identity_item.status == "C", f"Failed to match: {text}")
    
    def test_only_updates_current_stage(self):
        """Should only update items in the current stage"""
        # Text has keywords for multiple stages
        update_evidence_from_assessor_text(
            self.checklists,
            "Briefing",
            "We'll do role play and oral questions after I check your identity",
            self.turn_index
        )
        
        # Briefing items should be updated
        briefing_met = any(item.status == "C" for item in self.checklists["Briefing"])
        self.assertTrue(briefing_met, "Briefing items should be updated")
        
        # Other stages should NOT be updated
        roleplay_met = any(item.status == "C" for item in self.checklists["Role Play"])
        oral_met = any(item.status == "C" for item in self.checklists["Oral Questions"])
        
        self.assertFalse(roleplay_met, "Role Play items should not be updated")
        self.assertFalse(oral_met, "Oral Questions items should not be updated")
    
    def test_skips_already_met_items(self):
        """Should not update items that are already met"""
        # Mark an item as met manually
        identity_item = self.checklists["Briefing"][0]
        identity_item.status = "C"
        identity_item.evidence_notes = "Manual mark"
        identity_item.last_updated_turn = 5
        
        # Try to update with keyword detection
        update_evidence_from_assessor_text(
            self.checklists,
            "Briefing",
            "Check your NRIC please",
            10
        )
        
        # Should still have manual notes (not overwritten)
        self.assertEqual(identity_item.evidence_notes, "Manual mark")
        self.assertEqual(identity_item.last_updated_turn, 5)
    
    def test_handles_invalid_stage_gracefully(self):
        """Should not crash when stage doesn't exist"""
        # Should not raise exception
        try:
            update_evidence_from_assessor_text(
                self.checklists,
                "NonExistentStage",
                "Some text",
                self.turn_index
            )
        except Exception as e:
            self.fail(f"Should handle invalid stage gracefully, but raised: {e}")
    
    def test_handles_empty_text(self):
        """Should handle empty assessor text without crashing"""
        try:
            update_evidence_from_assessor_text(
                self.checklists,
                "Briefing",
                "",
                self.turn_index
            )
            # No items should be marked met
            met_count = sum(1 for item in self.checklists["Briefing"] if item.status == "C")
            self.assertEqual(met_count, 0)
        except Exception as e:
            self.fail(f"Should handle empty text gracefully, but raised: {e}")
    
    def test_multiple_keywords_detected(self):
        """Multiple items can be marked met from single text"""
        # Text with multiple keywords
        text = "Let me explain the process. This is confidential and will take 60 minutes."
        
        update_evidence_from_assessor_text(
            self.checklists,
            "Briefing",
            text,
            self.turn_index
        )
        
        # Check multiple items were marked
        process_item = next(
            item for item in self.checklists["Briefing"]
            if item.id == "briefing_06"
        )
        confidentiality_item = next(
            item for item in self.checklists["Briefing"]
            if item.id == "briefing_11"
        )
        duration_item = next(
            item for item in self.checklists["Briefing"]
            if item.id == "briefing_08"
        )
        
        self.assertTrue(process_item.status == "C")
        self.assertTrue(confidentiality_item.status == "C")
        self.assertTrue(duration_item.status == "C")
    
    def test_evidence_notes_format(self):
        """Evidence notes should follow expected format"""
        update_evidence_from_assessor_text(
            self.checklists,
            "Briefing",
            "Check your NRIC and identity",
            self.turn_index
        )
        
        identity_item = next(
            item for item in self.checklists["Briefing"]
            if item.id == "briefing_02"
        )
        
        # Should start with "Keywords:" or "AI:"
        self.assertTrue(
            identity_item.evidence_notes.startswith("Keywords:") or 
            identity_item.evidence_notes.startswith("AI:")
        )
    
    def test_turn_index_recorded_correctly(self):
        """Turn index should be recorded when item is marked met"""
        turn = 42
        update_evidence_from_assessor_text(
            self.checklists,
            "Briefing",
            "Show me your NRIC",
            turn
        )
        
        identity_item = next(
            item for item in self.checklists["Briefing"]
            if item.id == "briefing_02"
        )
        
        self.assertEqual(identity_item.last_updated_turn, turn)
    
    def test_role_play_stage_keywords(self):
        """Test keyword detection for Role Play stage"""
        update_evidence_from_assessor_text(
            self.checklists,
            "Role Play",
            "Let me recommend some courses based on the Skills Framework",
            self.turn_index
        )
        
        framework_item = next(
            item for item in self.checklists["Role Play"]
            if item.id == "roleplay_framework"
        )
        recommend_item = next(
            item for item in self.checklists["Role Play"]
            if item.id == "roleplay_recommendations"
        )
        
        self.assertTrue(framework_item.status == "C")
        self.assertTrue(recommend_item.status == "C")
    
    def test_oral_questions_stage_keywords(self):
        """Test keyword detection for Oral Questions stage"""
        update_evidence_from_assessor_text(
            self.checklists,
            "Oral Questions",
            "Can you explain your rationale for that decision?",
            self.turn_index
        )
        
        rationale_item = next(
            item for item in self.checklists["Oral Questions"]
            if item.id == "oral_rationale"
        )
        
        self.assertTrue(rationale_item.status == "C")


class TestGetStageCompletionPercentage(unittest.TestCase):
    """Test get_stage_completion_percentage() function"""
    
    def setUp(self):
        """Create fresh checklist before each test"""
        self.checklists = clone_stage_checklists()
    
    def test_returns_zero_for_empty_stage(self):
        """Should return 0% when no items are met"""
        percentage = get_stage_completion_percentage(self.checklists, "Briefing")
        self.assertEqual(percentage, 0.0)
    
    def test_returns_hundred_when_all_met(self):
        """Should return 100% when all items are met"""
        # Mark all items as met
        for item in self.checklists["Briefing"]:
            item.status = "C"
        
        percentage = get_stage_completion_percentage(self.checklists, "Briefing")
        self.assertEqual(percentage, 100.0)
    
    def test_calculates_partial_completion(self):
        """Should calculate correct percentage for partial completion"""
        # Briefing has 14 items, mark 7 as met (50%)
        for i in range(7):
            self.checklists["Briefing"][i].status = "C"

        percentage = get_stage_completion_percentage(self.checklists, "Briefing")
        self.assertEqual(percentage, 50.0)
    
    def test_handles_invalid_stage(self):
        """Should return 0% for non-existent stage"""
        percentage = get_stage_completion_percentage(self.checklists, "InvalidStage")
        self.assertEqual(percentage, 0.0)
    
    def test_different_stages(self):
        """Test completion calculation for different stages"""
        # Role Play has 4 items, mark 2 as met (50%)
        self.checklists["Role Play"][0].status = "C"
        self.checklists["Role Play"][1].status = "C"
        
        percentage = get_stage_completion_percentage(self.checklists, "Role Play")
        self.assertEqual(percentage, 50.0)


class TestGetAllStagesSummary(unittest.TestCase):
    """Test get_all_stages_summary() function"""
    
    def setUp(self):
        """Create fresh checklist before each test"""
        self.checklists = clone_stage_checklists()
    
    def test_returns_dict(self):
        """Should return a dictionary"""
        summary = get_all_stages_summary(self.checklists)
        self.assertIsInstance(summary, dict)
    
    def test_has_all_stages(self):
        """Summary should include all stages"""
        summary = get_all_stages_summary(self.checklists)
        
        expected_stages = ["Briefing", "Role Play", "Oral Questions", "Closing"]
        for stage in expected_stages:
            self.assertIn(stage, summary)
    
    def test_summary_structure(self):
        """Each stage summary should have total, met, and percentage"""
        summary = get_all_stages_summary(self.checklists)
        
        for stage_name, stage_data in summary.items():
            self.assertIn("total", stage_data)
            self.assertIn("met", stage_data)
            self.assertIn("percentage", stage_data)
    
    def test_correct_totals(self):
        """Summary should show correct total counts for each stage"""
        summary = get_all_stages_summary(self.checklists)
        
        # Based on requirements
        self.assertEqual(summary["Briefing"]["total"], 14)
        self.assertEqual(summary["Role Play"]["total"], 4)
        self.assertEqual(summary["Oral Questions"]["total"], 4)
        self.assertEqual(summary["Closing"]["total"], 3)
    
    def test_met_counts_when_nothing_met(self):
        """Met counts should be 0 initially"""
        summary = get_all_stages_summary(self.checklists)
        
        for stage_data in summary.values():
            self.assertEqual(stage_data["met"], 0)
            self.assertEqual(stage_data["percentage"], 0.0)
    
    def test_met_counts_after_marking(self):
        """Met counts should update when items are marked"""
        # Mark 2 items in Briefing
        self.checklists["Briefing"][0].status = "C"
        self.checklists["Briefing"][1].status = "C"
        
        summary = get_all_stages_summary(self.checklists)
        
        self.assertEqual(summary["Briefing"]["met"], 2)
        self.assertAlmostEqual(summary["Briefing"]["percentage"], 14.3, places=1)
    
    def test_percentage_rounding(self):
        """Percentages should be rounded to 1 decimal place"""
        # Mark 1 out of 14 items (7.142...%)
        self.checklists["Briefing"][0].status = "C"
        
        summary = get_all_stages_summary(self.checklists)
        
        # Should be rounded to 1 decimal
        self.assertIsInstance(summary["Briefing"]["percentage"], float)
        self.assertEqual(summary["Briefing"]["percentage"], 7.1)


if __name__ == "__main__":
    # Run tests when script is executed directly
    unittest.main(verbosity=2)

