"""
candidate.py
Simulates a PP2 assessment candidate using OpenAI's Chat Completions API.
"""

import os
from openai import OpenAI


def candidate_reply(messages: list[dict], scenario: str, difficulty: str) -> str:
    """
    Generate a candidate reply using OpenAI API.
    
    Args:
        messages: List of message dicts with 'role' and 'content' keys
        scenario: The selected scenario description
        difficulty: One of "Easy", "Medium", or "Hard"
    
    Returns:
        The candidate's response as a plain text string
    """
    # Initialize OpenAI client (API key loaded from environment)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "ERROR: OPENAI_API_KEY not found in environment variables."
    
    client = OpenAI(api_key=api_key)
    model = os.getenv("MODEL", "gpt-4o-mini")
    
    # Build system prompt based on difficulty
    system_prompt = _build_system_prompt(scenario, difficulty)
    
    # Prepare messages for API call
    api_messages = [{"role": "system", "content": system_prompt}]
    api_messages.extend(messages)
    
    try:
        # Call OpenAI Chat Completions API
        response = client.chat.completions.create(
            model=model,
            messages=api_messages,
            temperature=0.8,  # Add some natural variation
            max_tokens=500,   # Keep responses concise
        )
        
        # Extract and return the reply
        reply = response.choices[0].message.content
        return reply if reply else "I'm not sure how to respond to that."
        
    except Exception as e:
        return f"ERROR: Failed to get response from OpenAI API: {str(e)}"


def _build_system_prompt(scenario: str, difficulty: str) -> str:
    """
    Build the system prompt that instructs the AI how to behave.
    
    Args:
        scenario: The scenario description
        difficulty: The difficulty level
    
    Returns:
        System prompt string
    """
    # Base prompt - always included
    base = f"""You are roleplaying as a candidate in a PP2 assessment. The assessor (user) will conduct a professional discussion with you.

SCENARIO: {scenario}

BEHAVIOR GUIDELINES:
- Act as a real professional being assessed
- Be conversational but professional
- Respond naturally to questions
- Never break character or mention being an AI
- Keep responses concise (2-4 sentences typically)
- Show realistic thought processes
"""
    
    # Add difficulty-specific instructions
    if difficulty == "Easy":
        difficulty_instructions = """
DIFFICULTY: Easy
- Provide complete and accurate responses
- Demonstrate good understanding of the scenario
- Volunteer relevant information when appropriate
- Make only minor, easily correctable mistakes (1-2% of responses)
"""
    elif difficulty == "Medium":
        difficulty_instructions = """
DIFFICULTY: Medium
- Occasionally make small omissions or forget minor details
- Sometimes need gentle prompting to provide complete information
- Make realistic mistakes about 10-15% of the time
- Recover well when the assessor probes deeper
- Show you're competent but not perfect
"""
    else:  # Hard
        difficulty_instructions = """
DIFFICULTY: Hard
- Frequently make omissions or provide incomplete initial answers
- Often need specific follow-up questions to reveal full understanding
- Make mistakes or show gaps about 20-30% of the time
- Occasionally misunderstand questions initially
- Sometimes provide vague responses that need clarification
- Show realistic nervousness or uncertainty
- Require skilled assessor questioning to demonstrate competence
"""
    
    return base + difficulty_instructions
