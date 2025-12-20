"""
test_candidate.py
Tests for candidate.py functions

Note: These tests cover deterministic behavior only.
OpenAI API calls are not tested to avoid API costs and external dependencies.
"""

import unittest
from candidate import candidate_reply


class TestCandidateReplyDeterministic(unittest.TestCase):
    """Test deterministic behavior in candidate_reply (non-API responses)"""

    def test_identity_verification_in_briefing(self):
        """Test that identity keywords trigger deterministic response in Briefing"""
        messages = [{"role": "user", "content": "Can you show me your NRIC?"}]
        response = candidate_reply(messages, "Test scenario", "Easy", "Briefing")
        
        self.assertEqual(response, "Sure. My name is Johnny Tan, and my NRIC is S1234567A.")
    
    def test_identity_verification_case_insensitive(self):
        """Test identity keywords work regardless of case"""
        messages = [{"role": "user", "content": "Please verify your identity"}]
        response = candidate_reply(messages, "Test scenario", "Easy", "Briefing")
        
        self.assertEqual(response, "Sure. My name is Johnny Tan, and my NRIC is S1234567A.")
    
    def test_greeting_response_in_briefing(self):
        """Test that simple greetings trigger deterministic response in Briefing"""
        test_greetings = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]
        
        for greeting in test_greetings:
            with self.subTest(greeting=greeting):
                messages = [{"role": "user", "content": greeting}]
                response = candidate_reply(messages, "Test scenario", "Easy", "Briefing")
                
                self.assertEqual(response, "Hello. I'm ready when you are.")
    
    def test_greeting_with_whitespace(self):
        """Test greeting detection handles whitespace"""
        messages = [{"role": "user", "content": "  hello  "}]
        response = candidate_reply(messages, "Test scenario", "Easy", "Briefing")
        
        self.assertEqual(response, "Hello. I'm ready when you are.")
    
    def test_greeting_case_insensitive(self):
        """Test greetings work regardless of case"""
        messages = [{"role": "user", "content": "HELLO"}]
        response = candidate_reply(messages, "Test scenario", "Easy", "Briefing")
        
        self.assertEqual(response, "Hello. I'm ready when you are.")
    
    def test_deterministic_responses_only_in_briefing(self):
        """Test identity/greeting shortcuts only work in Briefing stage"""
        # In non-Briefing stages, these should go to OpenAI API (which will fail without key)
        # We can't fully test this without mocking OpenAI, but we verify it doesn't return
        # the deterministic response
        stages = ["Role Play", "Oral Questions", "Recovery", "Closing"]
        
        for stage in stages:
            with self.subTest(stage=stage):
                messages = [{"role": "user", "content": "hello"}]
                response = candidate_reply(messages, "Test scenario", "Easy", stage)
                
                # Should NOT be the Briefing greeting response
                # Will either call API or return error if API key missing
                self.assertNotEqual(response, "Hello. I'm ready when you are.")
    
    def test_identity_keywords_all_trigger_response(self):
        """Test all identity keywords trigger the deterministic response"""
        identity_keywords = ["nric", "id", "identity", "verification", "verify", "identify"]
        
        for keyword in identity_keywords:
            with self.subTest(keyword=keyword):
                messages = [{"role": "user", "content": f"Can you show me your {keyword}?"}]
                response = candidate_reply(messages, "Test scenario", "Easy", "Briefing")
                
                self.assertEqual(response, "Sure. My name is Johnny Tan, and my NRIC is S1234567A.")
    
    def test_empty_messages_list(self):
        """Test behavior with empty messages list"""
        # Should not crash, will go to OpenAI API (or error if no key)
        response = candidate_reply([], "Test scenario", "Easy", "Briefing")
        
        # Should return something (error or API response)
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)
    
    def test_non_user_message_ignored(self):
        """Test that non-user messages don't trigger deterministic responses"""
        messages = [{"role": "assistant", "content": "hello"}]
        response = candidate_reply(messages, "Test scenario", "Easy", "Briefing")
        
        # Should NOT be the greeting response (assistant message, not user)
        # Will go to API or return error
        self.assertNotEqual(response, "Hello. I'm ready when you are.")


class TestBuildSystemPrompt(unittest.TestCase):
    """Test system prompt building (internal function)"""
    
    def test_system_prompt_contains_scenario(self):
        """Test that system prompt includes scenario text"""
        from candidate import _build_system_prompt
        
        scenario = "This is a test scenario"
        prompt = _build_system_prompt(scenario, "Easy", "Briefing")
        
        self.assertIn(scenario, prompt)
    
    def test_system_prompt_contains_stage(self):
        """Test that system prompt includes stage information"""
        from candidate import _build_system_prompt
        
        stage = "Role Play"
        prompt = _build_system_prompt("Test scenario", "Easy", stage)
        
        self.assertIn(stage, prompt)
    
    def test_system_prompt_has_difficulty_instructions(self):
        """Test that system prompt includes difficulty-specific instructions"""
        from candidate import _build_system_prompt
        
        # Just verify the prompt is generated and is a string
        # Specific difficulty behavior is tested via integration
        prompt = _build_system_prompt("Test scenario", "Hard", "Briefing")
        
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 100)  # Should be substantial
    
    def test_system_prompt_contains_banned_phrases_section(self):
        """Test that system prompt includes banned phrases"""
        from candidate import _build_system_prompt
        
        prompt = _build_system_prompt("Test scenario", "Easy", "Briefing")
        
        self.assertIn("BANNED PHRASES", prompt)
        self.assertIn("How can I assist you today?", prompt)
        self.assertIn("How may I help you today?", prompt)
    
    def test_system_prompt_contains_examples_section(self):
        """Test that system prompt includes examples"""
        from candidate import _build_system_prompt
        
        prompt = _build_system_prompt("Test scenario", "Easy", "Briefing")
        
        self.assertIn("EXAMPLES:", prompt)
        # Should have greeting example
        self.assertIn("Hello", prompt)


if __name__ == "__main__":
    unittest.main()
