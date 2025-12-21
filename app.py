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
from rubric import clone_stage_checklists
from evidence_engine import update_evidence_from_assessor_text

# Import scenarios: try private file first, fall back to public
try:
    from scenarios_private import SCENARIOS
except ImportError:
    from scenarios import SCENARIOS


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
# SCENARIOS imported from scenarios.py (or scenarios_private.py if it exists)


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
    
    # Initialize evidence tracking
    if "evidence" not in st.session_state:
        st.session_state.evidence = clone_stage_checklists()
    
    if "turn_index" not in st.session_state:
        st.session_state.turn_index = 0


def reset_conversation():
    """Clear the conversation history"""
    st.session_state.messages = []
    # Also reset PP2 stage to Briefing
    if "pp2" in st.session_state:
        st.session_state.pp2.reset()
    # Reset evidence tracking
    st.session_state.evidence = clone_stage_checklists()
    st.session_state.turn_index = 0
    st.rerun()


def display_chat_history():
    """Display all messages in the chat history"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Show "thinking" indicator if response is pending
    if st.session_state.get("needs_response", False):
        with st.chat_message("assistant"):
            st.markdown("*Thinking...*")


def handle_user_input(user_input: str):
    """
    Process user input and generate candidate response
    
    Args:
        user_input: The assessor's message/question
    """
    # Increment turn index
    st.session_state.turn_index += 1
    
    # Add user message to history immediately (defer evidence processing)
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    
    # Store the input for evidence processing during response generation
    st.session_state.pending_user_input = user_input
    
    # Flag that we need to generate a response
    st.session_state.needs_response = True
    
    # Rerun to show user message immediately (no blocking operations before this)
    st.rerun()


def generate_pending_response():
    """Generate candidate response if one is pending"""
    if not st.session_state.get("needs_response", False):
        return
    
    # Clear the flag
    st.session_state.needs_response = False
    
    # Process evidence from the pending user input (deferred from handle_user_input)
    if st.session_state.get("pending_user_input"):
        current_stage = st.session_state.pp2.get_stage_name()
        update_evidence_from_assessor_text(
            st.session_state.evidence,
            current_stage,
            st.session_state.pending_user_input,
            st.session_state.turn_index
        )
        st.session_state.pending_user_input = None  # Clear after processing
    
    # Generate candidate response (thinking indicator already shown in chat)
    current_stage = st.session_state.pp2.get_stage_name()
    scenario_text = SCENARIOS[st.session_state.scenario]["summary"]
    
    response = candidate_reply(
        messages=st.session_state.messages,
        scenario_text=scenario_text,
        difficulty=st.session_state.difficulty,
        stage=current_stage
    )
    
    # Add candidate response to history
    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })
    
    # Rerun to display updated chat history
    st.rerun()


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
        
        # Get scenario text (summary field from scenario dict)
        scenario_text = SCENARIOS[scenario]["summary"]
        
        # Show scenario description
        with st.expander("View scenario details"):
            st.write(scenario_text)
        
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
        
        # Readiness Indicator
        st.subheader("📊 Readiness Indicator")
        
        # Calculate completion for each stage
        stage_completions = {}
        for stage_name, checklist in st.session_state.evidence.items():
            total = len(checklist)
            met = sum(1 for item in checklist if item.met)
            percentage = (met / total * 100.0) if total > 0 else 0.0
            stage_completions[stage_name] = {"met": met, "total": total, "percentage": percentage}
        
        # Display per-stage completion
        for stage_name in ["Briefing", "Role Play", "Oral Questions", "Recovery", "Closing"]:
            if stage_name in stage_completions:
                comp = stage_completions[stage_name]
                st.caption(f"**{stage_name}:** {comp['met']}/{comp['total']} ({comp['percentage']:.0f}%)")
        
        st.divider()
        
        # Overall readiness indicator
        # Check if key stages (Briefing, Role Play, Oral Questions) are >= 70% complete
        key_stages = ["Briefing", "Role Play", "Oral Questions"]
        key_stages_ready = all(
            stage_completions.get(stage, {}).get("percentage", 0) >= 70
            for stage in key_stages
        )
        
        if key_stages_ready:
            st.success("✅ **On track** - Key stages well covered")
        else:
            st.warning("⚠️ **Needs work** - Focus on key evidence")
        
        st.divider()
        
        # Debug options
        st.subheader("Debug")
        show_debug = st.checkbox(
            "Show detection debug details",
            value=False,
            key="show_debug_details",
            help="Display keyword detection details for met evidence items"
        )
        st.session_state.show_debug = show_debug
        
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
    
    # Display current configuration banner
    st.caption(f"📋 **{st.session_state.scenario}** | 🎯 Stage: **{st.session_state.pp2.get_stage_name()}** | 💪 Difficulty: **{st.session_state.difficulty}**")
    
    st.divider()
    
    # Evidence checklist in expander (collapsible)
    current_stage = st.session_state.pp2.get_stage_name()
    if current_stage in st.session_state.evidence:
        checklist = st.session_state.evidence[current_stage]
        met_count = sum(1 for item in checklist if item.met)
        total_count = len(checklist)
        
        with st.expander(f"📋 Evidence Checklist - {current_stage} ({met_count}/{total_count} items)", expanded=False):
            # Show progress
            st.progress(met_count / total_count if total_count > 0 else 0)
            st.caption(f"**Completion: {met_count}/{total_count}** items")
            
            st.divider()
            
            # Display each checklist item
            for idx, item in enumerate(checklist):
                # Add subheaders for Briefing stage to group 14 items
                if current_stage == "Briefing":
                    if idx == 0:
                        st.markdown("**Opening & Comfort**")
                    elif idx == 3:
                        st.markdown("**Assessment Scope & Process**")
                    elif idx == 8:
                        st.markdown("**Support, Rights & Assurance**")
                
                checkbox_icon = "✅" if item.met else "⬜"
                st.markdown(f"{checkbox_icon} {item.text}")
                
                # Show evidence notes if debug mode enabled and item is met
                if st.session_state.get("show_debug", False) and item.met and item.evidence_notes:
                    st.caption(f"   *{item.evidence_notes}*")
            
            st.divider()
            
            # Manual evidence adjustment (not nested, just a section)
            st.markdown("**🔧 Manual Evidence Adjustment**")
            st.caption("Override evidence items manually for practice")
            
            for idx, item in enumerate(checklist):
                # Create unique key for each checkbox
                checkbox_key = f"manual_{current_stage}_{item.id}"
                
                # Checkbox for manual toggle
                new_state = st.checkbox(
                    item.text,
                    value=item.met,
                    key=checkbox_key
                )
                
                # If state changed, update the item
                if new_state != item.met:
                    item.met = new_state
                    item.evidence_notes = "Manual toggle"
                    item.last_updated_turn = st.session_state.turn_index
    
    st.divider()
    
    # Display chat history FIRST (so user sees their message immediately)
    display_chat_history()
    
    # Generate pending response if needed (shows spinner AFTER chat displays)
    generate_pending_response()
    
    # Chat input - placed outside columns at the bottom for proper positioning
    if prompt := st.chat_input("Type your question or comment as the assessor..."):
        handle_user_input(prompt)


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()
