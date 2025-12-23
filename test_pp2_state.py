"""
test_pp2_state.py
Unit tests for PP2 stage state machine

Run with: python -m pytest test_pp2_state.py
Or: python test_pp2_state.py
"""

import unittest
from pp2_state import PP2Session, PP2Stage, STAGE_ORDER


class TestPP2Stage(unittest.TestCase):
    """Test PP2Stage enum values"""
    
    def test_stage_enum_values(self):
        """Verify all 4 stages exist with correct names"""
        self.assertEqual(PP2Stage.BRIEFING.value, "Briefing")
        self.assertEqual(PP2Stage.ROLE_PLAY.value, "Role Play")
        self.assertEqual(PP2Stage.ORAL_QUESTIONS.value, "Oral Questions")
        self.assertEqual(PP2Stage.CLOSING.value, "Closing")
    
    def test_stage_order_length(self):
        """Verify STAGE_ORDER has exactly 4 stages"""
        self.assertEqual(len(STAGE_ORDER), 4)
    
    def test_stage_order_sequence(self):
        """Verify stages are in correct order"""
        expected_order = [
            PP2Stage.BRIEFING,
            PP2Stage.ROLE_PLAY,
            PP2Stage.ORAL_QUESTIONS,
            PP2Stage.CLOSING,
        ]
        self.assertEqual(STAGE_ORDER, expected_order)


class TestPP2Session(unittest.TestCase):
    """Test PP2Session state machine"""
    
    def setUp(self):
        """Create a fresh session before each test"""
        self.session = PP2Session()
    
    def test_initial_state_is_briefing(self):
        """New session should start at Briefing stage"""
        self.assertEqual(self.session.current_stage, PP2Stage.BRIEFING)
    
    def test_get_stage_name(self):
        """get_stage_name() should return the stage display name"""
        self.assertEqual(self.session.get_stage_name(), "Briefing")
        
        self.session.current_stage = PP2Stage.ROLE_PLAY
        self.assertEqual(self.session.get_stage_name(), "Role Play")
    
    # ========================================================================
    # next_stage() tests
    # ========================================================================
    
    def test_next_stage_from_briefing(self):
        """next_stage() from Briefing should move to Role Play"""
        self.session.next_stage()
        self.assertEqual(self.session.current_stage, PP2Stage.ROLE_PLAY)
    
    def test_next_stage_from_role_play(self):
        """next_stage() from Role Play should move to Oral Questions"""
        self.session.current_stage = PP2Stage.ROLE_PLAY
        self.session.next_stage()
        self.assertEqual(self.session.current_stage, PP2Stage.ORAL_QUESTIONS)
    
    def test_next_stage_from_oral_questions(self):
        """next_stage() from Oral Questions should move to Closing"""
        self.session.current_stage = PP2Stage.ORAL_QUESTIONS
        self.session.next_stage()
        self.assertEqual(self.session.current_stage, PP2Stage.CLOSING)
    
    def test_next_stage_at_last_stage_does_nothing(self):
        """next_stage() at Closing should stay at Closing (boundary test)"""
        self.session.current_stage = PP2Stage.CLOSING
        self.session.next_stage()
        self.assertEqual(self.session.current_stage, PP2Stage.CLOSING)
    
    def test_next_stage_full_progression(self):
        """Verify complete progression through all stages"""
        # Start at Briefing
        self.assertEqual(self.session.current_stage, PP2Stage.BRIEFING)
        
        # Progress through all stages
        self.session.next_stage()
        self.assertEqual(self.session.current_stage, PP2Stage.ROLE_PLAY)
        
        self.session.next_stage()
        self.assertEqual(self.session.current_stage, PP2Stage.ORAL_QUESTIONS)
        
        self.session.next_stage()
        self.assertEqual(self.session.current_stage, PP2Stage.CLOSING)
        
        # Try to go further (should stay at Closing)
        self.session.next_stage()
        self.assertEqual(self.session.current_stage, PP2Stage.CLOSING)
    
    # ========================================================================
    # prev_stage() tests
    # ========================================================================
    
    def test_prev_stage_from_closing(self):
        """prev_stage() from Closing should move to Oral Questions"""
        self.session.current_stage = PP2Stage.CLOSING
        self.session.prev_stage()
        self.assertEqual(self.session.current_stage, PP2Stage.ORAL_QUESTIONS)
    
    def test_prev_stage_from_oral_questions(self):
        """prev_stage() from Oral Questions should move to Role Play"""
        self.session.current_stage = PP2Stage.ORAL_QUESTIONS
        self.session.prev_stage()
        self.assertEqual(self.session.current_stage, PP2Stage.ROLE_PLAY)
    
    def test_prev_stage_from_role_play(self):
        """prev_stage() from Role Play should move to Briefing"""
        self.session.current_stage = PP2Stage.ROLE_PLAY
        self.session.prev_stage()
        self.assertEqual(self.session.current_stage, PP2Stage.BRIEFING)
    
    def test_prev_stage_at_first_stage_does_nothing(self):
        """prev_stage() at Briefing should stay at Briefing (boundary test)"""
        self.session.prev_stage()
        self.assertEqual(self.session.current_stage, PP2Stage.BRIEFING)
    
    def test_prev_stage_full_regression(self):
        """Verify complete regression through all stages"""
        # Start at Closing
        self.session.current_stage = PP2Stage.CLOSING
        
        # Regress through all stages
        self.session.prev_stage()
        self.assertEqual(self.session.current_stage, PP2Stage.ORAL_QUESTIONS)
        
        self.session.prev_stage()
        self.assertEqual(self.session.current_stage, PP2Stage.ROLE_PLAY)
        
        self.session.prev_stage()
        self.assertEqual(self.session.current_stage, PP2Stage.BRIEFING)
        
        # Try to go further back (should stay at Briefing)
        self.session.prev_stage()
        self.assertEqual(self.session.current_stage, PP2Stage.BRIEFING)
    
    # ========================================================================
    # reset() tests
    # ========================================================================
    
    def test_reset_from_briefing(self):
        """reset() from Briefing should stay at Briefing"""
        self.session.reset()
        self.assertEqual(self.session.current_stage, PP2Stage.BRIEFING)
    
    def test_reset_from_middle_stage(self):
        """reset() from middle stage should return to Briefing"""
        self.session.current_stage = PP2Stage.ORAL_QUESTIONS
        self.session.reset()
        self.assertEqual(self.session.current_stage, PP2Stage.BRIEFING)
    
    def test_reset_from_closing(self):
        """reset() from Closing should return to Briefing"""
        self.session.current_stage = PP2Stage.CLOSING
        self.session.reset()
        self.assertEqual(self.session.current_stage, PP2Stage.BRIEFING)
    
    # ========================================================================
    # set_stage() tests
    # ========================================================================
    
    def test_set_stage_to_briefing(self):
        """set_stage() should jump to Briefing"""
        self.session.current_stage = PP2Stage.CLOSING
        self.session.set_stage(PP2Stage.BRIEFING)
        self.assertEqual(self.session.current_stage, PP2Stage.BRIEFING)
    
    def test_set_stage_to_role_play(self):
        """set_stage() should jump to Role Play"""
        self.session.set_stage(PP2Stage.ROLE_PLAY)
        self.assertEqual(self.session.current_stage, PP2Stage.ROLE_PLAY)
    
    def test_set_stage_to_oral_questions(self):
        """set_stage() should jump to Oral Questions"""
        self.session.set_stage(PP2Stage.ORAL_QUESTIONS)
        self.assertEqual(self.session.current_stage, PP2Stage.ORAL_QUESTIONS)
    
    def test_set_stage_to_closing(self):
        """set_stage() should jump to Closing"""
        self.session.set_stage(PP2Stage.CLOSING)
        self.assertEqual(self.session.current_stage, PP2Stage.CLOSING)
    
    # ========================================================================
    # Integration tests (combining multiple operations)
    # ========================================================================
    
    def test_forward_backward_navigation(self):
        """Test moving forward and backward through stages"""
        # Start at Briefing
        self.assertEqual(self.session.current_stage, PP2Stage.BRIEFING)
        
        # Go forward 3 stages
        self.session.next_stage()
        self.session.next_stage()
        self.session.next_stage()
        self.assertEqual(self.session.current_stage, PP2Stage.CLOSING)
        
        # Go back 2 stages
        self.session.prev_stage()
        self.session.prev_stage()
        self.assertEqual(self.session.current_stage, PP2Stage.ROLE_PLAY)
    
    def test_jump_then_navigate(self):
        """Test jumping to a stage then using next/prev"""
        # Jump to Oral Questions
        self.session.set_stage(PP2Stage.ORAL_QUESTIONS)
        
        # Move forward to Closing
        self.session.next_stage()
        self.assertEqual(self.session.current_stage, PP2Stage.CLOSING)
        
        # Move back to Oral Questions
        self.session.prev_stage()
        self.assertEqual(self.session.current_stage, PP2Stage.ORAL_QUESTIONS)
    
    def test_reset_after_progression(self):
        """Test reset after moving through stages"""
        # Progress to end
        self.session.set_stage(PP2Stage.CLOSING)
        
        # Reset
        self.session.reset()
        self.assertEqual(self.session.current_stage, PP2Stage.BRIEFING)
        
        # Verify can progress again
        self.session.next_stage()
        self.assertEqual(self.session.current_stage, PP2Stage.ROLE_PLAY)


if __name__ == "__main__":
    # Run tests when script is executed directly
    unittest.main(verbosity=2)
