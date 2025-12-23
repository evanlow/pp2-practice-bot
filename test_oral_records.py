"""
test_oral_records.py
Tests for Oral Questions assessment records and helper functions

Run with: pytest test_oral_records.py -v
"""

import unittest
from unittest.mock import MagicMock
from pp2_gro import CriterionRecord, GROEntry


class TestOralRecordsHelpers(unittest.TestCase):
    """Test OQ helper functions without Streamlit dependency"""
    
    def test_criterion_record_defaults(self):
        """Test CriterionRecord has correct defaults for OQ"""
        record = CriterionRecord(code="OQ1")
        
        self.assertEqual(record.code, "OQ1")
        self.assertEqual(record.status, "NYA")
        self.assertEqual(record.evidence_note, "")
        self.assertIsNone(record.gro)
    
    def test_criterion_record_with_evidence(self):
        """Test CriterionRecord can store evidence notes"""
        record = CriterionRecord(code="OQ2a")
        record.evidence_note = "Candidate correctly identified that framework is optional"
        record.status = "C"
        
        self.assertEqual(record.status, "C")
        self.assertEqual(record.evidence_note, "Candidate correctly identified that framework is optional")
    
    def test_criterion_record_with_gro(self):
        """Test CriterionRecord can have GRO attached"""
        record = CriterionRecord(code="OQ2b")
        record.status = "NYC"
        record.gro = GROEntry(
            gap="Only mentioned 1 reason instead of 2",
            probe_turn=5,
            probe_text="Can you provide another reason?",
            completed=False
        )
        
        self.assertEqual(record.status, "NYC")
        self.assertIsNotNone(record.gro)
        self.assertEqual(record.gro.gap, "Only mentioned 1 reason instead of 2")
        self.assertFalse(record.gro.completed)
    
    def test_gro_completion(self):
        """Test GRO can be marked as completed"""
        record = CriterionRecord(code="OQ1")
        record.status = "NYC"
        record.gro = GROEntry(
            gap="Only 2 points given, need 3",
            probe_turn=10,
            probe_text="Can you provide one more benefit?",
            response_turn=11,
            response_text="Candidate provided additional benefit",
            outcome="Recovered to C",
            completed=True
        )
        
        self.assertTrue(record.gro.completed)
        self.assertEqual(record.gro.outcome, "Recovered to C")
    
    def test_multiple_oq_records(self):
        """Test creating multiple OQ records"""
        records = {
            "OQ1": CriterionRecord(code="OQ1"),
            "OQ2a": CriterionRecord(code="OQ2a"),
            "OQ2b": CriterionRecord(code="OQ2b"),
        }
        
        self.assertEqual(len(records), 3)
        for code, record in records.items():
            self.assertEqual(record.code, code)
            self.assertEqual(record.status, "NYA")
    
    def test_status_transitions(self):
        """Test status can transition from NYA to C or NYC"""
        record = CriterionRecord(code="OQ1")
        
        # Start as NYA
        self.assertEqual(record.status, "NYA")
        
        # Assess as competent
        record.status = "C"
        self.assertEqual(record.status, "C")
        
        # Another record assessed as NYC
        record2 = CriterionRecord(code="OQ2a")
        record2.status = "NYC"
        self.assertEqual(record2.status, "NYC")
    
    def test_gro_only_required_for_nyc(self):
        """Test GRO is only needed when status is NYC"""
        # Competent record - no GRO needed
        c_record = CriterionRecord(code="OQ1")
        c_record.status = "C"
        self.assertIsNone(c_record.gro)
        
        # NYC record - GRO required
        nyc_record = CriterionRecord(code="OQ2a")
        nyc_record.status = "NYC"
        nyc_record.gro = GROEntry(gap="Some gap", completed=False)
        self.assertIsNotNone(nyc_record.gro)
        
        # NYA record - no GRO needed yet
        nya_record = CriterionRecord(code="OQ2b")
        self.assertEqual(nya_record.status, "NYA")
        self.assertIsNone(nya_record.gro)


if __name__ == "__main__":
    unittest.main(verbosity=2)
