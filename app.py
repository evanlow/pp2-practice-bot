"""
app.py
PP2 Practice Bot - Streamlit Web Application

Run with: streamlit run app.py
"""

import os
import streamlit as st
from dotenv import load_dotenv
from candidate import candidate_reply
from pp2_state import PP2Session, PP2Stage, STAGE_ORDER


# ============================================================================
# CONFIGURATION & INITIALIZATION
# ============================================================================

# Load environment variables from .env file
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="PP2 Practice Bot",
    page_icon="🎯",
    layout="centered"
)


# ============================================================================
# PASSWORD PROTECTION
# ============================================================================

def check_password() -> bool:
    """
    Display password input and validate against APP_PASSWORD from .env
    
    Returns:
        True if password is correct, False otherwise
    """
    # Get expected password from environment
    expected_password = os.getenv("APP_PASSWORD")
    
    if not expected_password:
        st.error("ERROR: APP_PASSWORD not set in .env file")
        st.stop()
    
    # Check if already authenticated in session
    if st.session_state.get("authenticated", False):
        return True
    
    # Show password input
    st.title("🔐 PP2 Practice Bot")
    st.write("Please enter the password to access the practice bot.")
    
    password = st.text_input("Password", type="password", key="password_input")
    
    if st.button("Login"):
        if password == expected_password:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password. Please try again.")
    
    return False


# ============================================================================
# SCENARIO DEFINITIONS
# ============================================================================

SCENARIOS = {
    "Project Management Scenario": """
You are a project manager who recently completed a challenging software migration project. 
The project had tight deadlines, multiple stakeholders, and some unexpected technical issues.
You successfully delivered the project on time but had to make several compromises along the way.
""",
    
    "Team Leadership Scenario": """
You are a team leader managing a cross-functional team of 8 people. 
Recently, you had to handle a conflict between two team members that was affecting team morale.
You implemented a resolution approach and have been monitoring the situation since then.
""",
    
    "Process Improvement Scenario": """
You identified inefficiencies in your organization's deployment process.
You proposed and led an initiative to implement automated CI/CD pipelines.
The initiative faced some resistance from senior team members who preferred the old manual process.
You eventually gained buy-in and successfully implemented the changes.
"""
}


# ============================================================================
# CHAT INTERFACE FUNCTIONS
# ============================================================================

def initialize_session_state():
    """Initialize session state variables if they don't exist"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "scenario" not in st.session_state:
        st.session_state.scenario = list(SCENARIOS.keys())[0]
    
    if "difficulty" not in st.session_state:
        st.session_state.difficulty = "Medium"
    
    # Initialize PP2 session state machine
    if "pp2" not in st.session_state:
        st.session_state.pp2 = PP2Session()


def reset_conversation():
    """Clear the conversation history"""
    st.session_state.messages = []
    # Also reset PP2 stage to Briefing
    if "pp2" in st.session_state:
        st.session_state.pp2.reset()
    st.rerun()


def display_chat_history():
    """Display all messages in the chat history"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def handle_user_input(user_input: str):
    """
    Process user input and generate candidate response
    
    Args:
        user_input: The assessor's message/question
    """
    # Add user message to history
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Generate candidate response
    with st.chat_message("assistant"):
        with st.spinner("Candidate is thinking..."):
            # Get current PP2 stage
            current_stage = st.session_state.pp2.get_stage_name()
            
            response = candidate_reply(
                messages=st.session_state.messages,
                scenario=SCENARIOS[st.session_state.scenario],
                difficulty=st.session_state.difficulty,
                stage=current_stage
            )
        
        st.markdown(response)
    
    # Add candidate response to history
    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application logic"""
    
    # Check password first
    if not check_password():
        return
    
    # Initialize session state
    initialize_session_state()
    
    # ========================================================================
    # SIDEBAR - Configuration Controls
    # ========================================================================
    
    with st.sidebar:
        st.title("⚙️ Configuration")
        
        # Scenario selector
        st.subheader("Scenario")
        scenario = st.selectbox(
            "Choose a practice scenario:",
            options=list(SCENARIOS.keys()),
            key="scenario_selector"
        )
        st.session_state.scenario = scenario
        
        # Show scenario description
        with st.expander("View scenario details"):
            st.write(SCENARIOS[scenario])
        
        st.divider()
        
        # Difficulty selector
        st.subheader("Difficulty")
        difficulty = st.radio(
            "Select difficulty level:",
            options=["Easy", "Medium", "Hard"],
            key="difficulty_selector",
            help="""
            Easy: Candidate provides complete, accurate responses
            Medium: Some omissions, needs occasional prompting
            Hard: Frequent gaps, requires skilled questioning
            """
        )
        st.session_state.difficulty = difficulty
        
        st.divider()
        
        # PP2 Stage controls
        st.subheader("PP2 Stage")
        
        # Display current stage
        st.info(f"**Current Stage:** {st.session_state.pp2.get_stage_name()}")
        
        # Stage navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Prev Stage", use_container_width=True):
                st.session_state.pp2.prev_stage()
                st.rerun()
        with col2:
            if st.button("Next Stage ➡️", use_container_width=True):
                st.session_state.pp2.next_stage()
                st.rerun()
        
        # Optional: Stage dropdown for jumping to specific stage
        with st.expander("Jump to specific stage"):
            selected_stage = st.selectbox(
                "Select stage:",
                options=[stage.value for stage in STAGE_ORDER],
                index=STAGE_ORDER.index(st.session_state.pp2.current_stage),
                key="stage_jump_selector"
            )
            if st.button("Jump to Stage", use_container_width=True):
                # Find the matching PP2Stage enum
                for stage in STAGE_ORDER:
                    if stage.value == selected_stage:
                        st.session_state.pp2.set_stage(stage)
                        st.rerun()
                        break
        
        st.divider()
        
        # Reset button
        st.subheader("Controls")
        if st.button("🔄 Reset Conversation", use_container_width=True):
            reset_conversation()
        
        # Info section
        st.divider()
        st.caption("💡 **Tip:** You are the assessor. Ask probing questions to evaluate the candidate's experience and competence.")
    
    # ========================================================================
    # MAIN AREA - Chat Interface
    # ========================================================================
    
    st.title("🎯 PP2 Practice Bot")
    st.caption("Practice your PP2 assessment skills - You play the ASSESSOR")
    
    # Display current configuration
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"**Scenario:** {st.session_state.scenario}")
    with col2:
        st.info(f"**Difficulty:** {st.session_state.difficulty}")
    with col3:
        st.info(f"**Stage:** {st.session_state.pp2.get_stage_name()}")
    
    st.divider()
    
    # Display chat history
    display_chat_history()
    
    # Chat input - always at the bottom
    if prompt := st.chat_input("Type your question or comment as the assessor..."):
        handle_user_input(prompt)


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()
