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
from rubric import clone_stage_checklists, STAGE_CHECKLISTS
from evidence_engine import update_evidence_from_assessor_text
from pp2_record import Criterion, GRO, AssessmentRow
from pp2_gro import GROEntry, CriterionRecord
import yaml

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

def load_roleplay_criteria() -> list[dict]:
    """
    Load roleplay criteria from YAML in st.secrets.
    
    Returns:
        List of criteria dicts with code, category, title, items, optional any_of
    
    Raises:
        Exception if YAML is missing or invalid
    """
    if not hasattr(st, "secrets") or "ROLEPLAY_CRITERIA_YAML" not in st.secrets:
        raise Exception("ROLEPLAY_CRITERIA_YAML not found in st.secrets")
    
    try:
        criteria_yaml = st.secrets["ROLEPLAY_CRITERIA_YAML"]
        data = yaml.safe_load(criteria_yaml)
        
        if data is None:
            raise Exception("YAML parsing returned None - empty or invalid YAML content")
        
        if not isinstance(data, dict) or "criteria" not in data:
            raise Exception("YAML must contain 'criteria' key with list of criteria")
        
        criteria_list = data["criteria"]
        if not isinstance(criteria_list, list):
            raise Exception("'criteria' must be a list")
        
        # Validate each criterion has required fields
        for criterion in criteria_list:
            if "code" not in criterion:
                raise Exception(f"Criterion missing 'code' field: {criterion}")
            if "title" not in criterion:
                raise Exception(f"Criterion {criterion.get('code')} missing 'title' field")
            if "items" not in criterion:
                raise Exception(f"Criterion {criterion.get('code')} missing 'items' field")
        
        return criteria_list
    except yaml.YAMLError as e:
        raise Exception(f"YAML parsing error: {str(e)}")
    except Exception as e:
        raise Exception(f"Error loading roleplay criteria: {str(e)}")

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
    
    # Migration: Handle old sessions with Recovery stage (now removed)
    if hasattr(st.session_state.pp2, 'current_stage'):
        stage_name = st.session_state.pp2.get_stage_name()
        if stage_name == "Recovery":
            # Migrate Recovery to Oral Questions
            st.session_state.pp2.current_stage = PP2Stage.ORAL_QUESTIONS
    
    # Initialize evidence tracking
    if "evidence" not in st.session_state:
        st.session_state.evidence = clone_stage_checklists()
    
    if "turn_index" not in st.session_state:
        st.session_state.turn_index = 0
    
    # Initialize roleplay_records dict with GRO enforcement structures
    if "roleplay_records" not in st.session_state:
        st.session_state.roleplay_records = {}
    
    # Load criteria from YAML
    try:
        criteria_list = load_roleplay_criteria()
        criteria_codes = [c["code"] for c in criteria_list]
        
        # Remove old RP1-RP4 keys if they exist (obsolete format)
        obsolete_keys = [k for k in st.session_state.roleplay_records.keys() if k.startswith("RP")]
        for old_key in obsolete_keys:
            del st.session_state.roleplay_records[old_key]
        
        # Add missing codes to roleplay_records (keeps existing records)
        for code in criteria_codes:
            if code not in st.session_state.roleplay_records:
                st.session_state.roleplay_records[code] = CriterionRecord(code=code)
        
        # Migration: Convert old "C" defaults to "NYA" if no evidence/GRO exists
        for code, record in st.session_state.roleplay_records.items():
            if record.status == "C" and not record.evidence_note and record.gro is None:
                record.status = "NYA"
    except Exception as e:
        # Don't fall back silently - show error
        st.error(f"❌ Failed to load roleplay criteria: {str(e)}")
        st.stop()
    
    # Initialize active GRO code for automatic capture
    if "active_gro_code" not in st.session_state:
        st.session_state.active_gro_code = None
        # Set to first NYC item missing GRO if any exist
        incomplete = get_nyc_codes_missing_gro()
        if incomplete:
            st.session_state.active_gro_code = incomplete[0]


def get_nyc_codes_missing_gro():
    """Get list of NYC criterion codes with missing or incomplete GRO.
    
    Returns:
        List of criterion codes where status is NYC and GRO is missing or incomplete.
    """
    if "roleplay_records" not in st.session_state:
        return []
    
    missing = []
    for code, record in st.session_state.roleplay_records.items():
        if record.status == "NYC":
            if record.gro is None or not record.gro.completed:
                missing.append(code)
    
    return missing


def update_active_gro_code():
    """Update active_gro_code to next NYC item needing GRO, or None if all complete."""
    incomplete = get_nyc_codes_missing_gro()
    if incomplete:
        st.session_state.active_gro_code = incomplete[0]
    else:
        st.session_state.active_gro_code = None


def can_advance_stage(from_stage: str) -> tuple[bool, list[str]]:
    """Check if can advance from current stage (NYC GRO validation).
    
    Args:
        from_stage: Current stage name
    
    Returns:
        Tuple of (can_advance: bool, missing_codes: list[str])
    """
    # Enforce GRO completion for Role Play and Oral Questions stages
    if from_stage not in ["Role Play", "Oral Questions"]:
        return True, []
    
    missing = get_nyc_codes_missing_gro()
    return len(missing) == 0, missing


def reset_conversation():
    """Clear the conversation history and reset all assessment state"""
    st.session_state.messages = []
    # Reset PP2 stage to Briefing
    if "pp2" in st.session_state:
        st.session_state.pp2.reset()
    # Reset evidence tracking
    st.session_state.evidence = clone_stage_checklists()
    st.session_state.turn_index = 0
    # Clear any pending response flags
    st.session_state.needs_response = False
    st.session_state.pending_user_input = None
    st.rerun()


def reset_roleplay_records():
    """Clear and rebuild roleplay_records from YAML."""
    st.session_state.roleplay_records = {}
    st.session_state.active_gro_code = None
    
    # Rebuild from YAML
    try:
        criteria_list = load_roleplay_criteria()
        criteria_codes = [c["code"] for c in criteria_list]
        
        for code in criteria_codes:
            st.session_state.roleplay_records[code] = CriterionRecord(code=code)
        
        # Set active_gro_code to first NYC if any
        incomplete = get_nyc_codes_missing_gro()
        if incomplete:
            st.session_state.active_gro_code = incomplete[0]
    except Exception:
        pass  # Will show error on next render
    
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
    user_msg_index = len(st.session_state.messages)
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    
    # Auto-capture GRO probe if active GRO exists and probe not yet captured
    if st.session_state.get("active_gro_code"):
        code = st.session_state.active_gro_code
        if code in st.session_state.roleplay_records:
            record = st.session_state.roleplay_records[code]
            if record.gro is not None and not record.gro.probe_text:
                record.gro.probe_text = user_input
                record.gro.probe_turn = user_msg_index
    
    # Store the input for evidence processing during response generation
    st.session_state.pending_user_input = user_input
    
    # Flag that we need to generate a response
    st.session_state.needs_response = True
    
    # Rerun to show user message immediately (no blocking operations before this)
    st.rerun()


def get_incomplete_gro_criteria():
    """Check for NYC criteria with missing or incomplete GRO records.
    
    Returns:
        List of criterion codes (e.g., ['RP1', 'RP3']) that need GRO completion,
        or empty list if all NYC criteria have completed GROs.
    """
    # Use the newer get_nyc_codes_missing_gro() which checks roleplay_records
    return get_nyc_codes_missing_gro()


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
    
    # Get pending GRO codes for Role Play stage
    pending_gro_codes = []
    if current_stage == "Role Play":
        pending_gro_codes = get_nyc_codes_missing_gro()
    
    response = candidate_reply(
        messages=st.session_state.messages,
        scenario_text=scenario_text,
        difficulty=st.session_state.difficulty,
        stage=current_stage,
        pending_gro_codes=pending_gro_codes
    )
    
    # Add candidate response to history
    response_msg_index = len(st.session_state.messages)
    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })
    
    # Auto-capture GRO response if active GRO exists with probe but no response yet
    if st.session_state.get("active_gro_code"):
        code = st.session_state.active_gro_code
        if code in st.session_state.roleplay_records:
            record = st.session_state.roleplay_records[code]
            if record.gro is not None and record.gro.probe_text and not record.gro.response_text:
                record.gro.response_text = response
                record.gro.response_turn = response_msg_index
    
    # Rerun to display updated chat history
    st.rerun()


def generate_summary_text():
    """Generate summary record as plain text."""
    if "roleplay_records" not in st.session_state:
        return "No assessment record available."
    
    # Load criteria for titles
    try:
        criteria_list = load_roleplay_criteria()
        criteria_map = {c["code"]: c for c in criteria_list}
    except Exception:
        criteria_map = {}
    
    lines = []
    lines.append("="*70)
    lines.append("PP2 PRACTICE BOT - ROLE PLAY ASSESSMENT SUMMARY")
    lines.append("="*70)
    lines.append(f"Scenario: {st.session_state.scenario}")
    lines.append(f"Difficulty: {st.session_state.difficulty}")
    lines.append(f"Date: December 22, 2025")
    lines.append("="*70)
    lines.append("")
    
    for code, record in sorted(st.session_state.roleplay_records.items()):
        criterion = criteria_map.get(code, {})
        title = criterion.get("title", "Unknown criterion")
        
        lines.append(f"Criterion: {code}")
        lines.append(f"Description: {title}")
        lines.append(f"Final Status: {record.status}")
        lines.append(f"Evidence Note: {record.evidence_note if record.evidence_note else 'None'}")
        
        if record.status == "NYC" and record.gro is not None and record.gro.gap:
            lines.append("")
            lines.append("  GRO Record:")
            lines.append(f"    Gap: {record.gro.gap}")
            lines.append(f"    Probe: {record.gro.probe_text}")
            reply_excerpt = record.gro.response_text
            lines.append(f"    Candidate Reply: {reply_excerpt[:100]}..." if len(reply_excerpt) > 100 else f"    Candidate Reply: {reply_excerpt}")
            lines.append(f"    Outcome: {record.gro.outcome}")
            lines.append(f"    Completed: {'Yes' if record.gro.completed else 'No'}")
        
        lines.append("-"*70)
        lines.append("")
    
    return "\n".join(lines)


def generate_summary_json():
    """Generate summary record as JSON."""
    import json
    
    if "roleplay_records" not in st.session_state:
        return json.dumps({"error": "No assessment record available"}, indent=2)
    
    # Load criteria for titles
    try:
        criteria_list = load_roleplay_criteria()
        criteria_map = {c["code"]: c for c in criteria_list}
    except Exception:
        criteria_map = {}
    
    summary = {
        "metadata": {
            "scenario": st.session_state.scenario,
            "difficulty": st.session_state.difficulty,
            "date": "2025-12-22",
            "stage": st.session_state.pp2.get_stage_name()
        },
        "criteria": []
    }
    
    for code, record in sorted(st.session_state.roleplay_records.items()):
        criterion = criteria_map.get(code, {})
        
        criterion_data = {
            "code": code,
            "description": criterion.get("title", "Unknown criterion"),
            "status": record.status,
            "evidence_note": record.evidence_note
        }
        
        if record.status == "NYC" and record.gro is not None and record.gro.gap:
            criterion_data["gro"] = {
                "gap": record.gro.gap,
                "probe": record.gro.probe_text,
                "candidate_reply_excerpt": record.gro.response_text,
                "outcome": record.gro.outcome,
                "completed": record.gro.completed,
                "probe_turn": record.gro.probe_turn,
                "response_turn": record.gro.response_turn
            }
        
        summary["criteria"].append(criterion_data)
    
    return json.dumps(summary, indent=2)


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
                current_stage = st.session_state.pp2.get_stage_name()
                
                # Validate GRO completion for Role Play and Oral Questions stages
                can_advance, missing = can_advance_stage(current_stage)
                if not can_advance:
                    st.error(
                        f"❌ Cannot advance from {current_stage} stage. "
                        f"GRO completion required for: {', '.join(missing)}"
                    )
                    if st.session_state.get("active_gro_code"):
                        st.info(f"👉 Suggested: Complete GRO for criterion **{st.session_state.active_gro_code}**")
                    st.stop()
                
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
                current_stage = st.session_state.pp2.get_stage_name()
                
                # Validate GRO completion if leaving Role Play or Oral Questions
                if current_stage in ["Role Play", "Oral Questions"] and selected_stage != current_stage:
                    can_advance, missing = can_advance_stage(current_stage)
                    if not can_advance:
                        st.error(
                            f"❌ Cannot leave {current_stage} stage. "
                            f"GRO completion required for: {', '.join(missing)}"
                        )
                        if st.session_state.get("active_gro_code"):
                            st.info(f"👉 Suggested: Complete GRO for criterion **{st.session_state.active_gro_code}**")
                        st.stop()
                
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
            met = sum(1 for item in checklist if item.status == "C")
            percentage = (met / total * 100.0) if total > 0 else 0.0
            stage_completions[stage_name] = {"met": met, "total": total, "percentage": percentage}
        
        # Display per-stage completion
        for stage_name in ["Briefing", "Role Play", "Oral Questions", "Closing"]:
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
        
        # GRO Recovery Queue - show during Role Play and Oral Questions stages
        current_stage = st.session_state.pp2.get_stage_name()
        if current_stage in ["Role Play", "Oral Questions"]:
            pending_codes = get_nyc_codes_missing_gro()
            if pending_codes:
                st.subheader("🔄 Recovery Queue")
                st.caption(f"{len(pending_codes)} NYC item(s) need recovery")
                
                # Get titles from YAML criteria
                try:
                    criteria_list = load_roleplay_criteria()
                    code_to_title = {}
                    for criterion in criteria_list:
                        code = criterion["code"]
                        title = criterion["title"]
                        # Extract short title (first 30 chars)
                        short_title = title[:30] + "..." if len(title) > 30 else title
                        code_to_title[code] = short_title
                except Exception:
                    code_to_title = {}
                
                active_code = st.session_state.get("active_gro_code")
                
                for code in pending_codes:
                    title = code_to_title.get(code, "Unknown")
                    
                    # Highlight active code
                    if code == active_code:
                        st.info(f"👉 **{code}**: {title}")
                    else:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.caption(f"**{code}**: {title}")
                        with col2:
                            if st.button("Set", key=f"set_active_{code}", use_container_width=True):
                                st.session_state.active_gro_code = code
                                st.rerun()
                
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
        
        if st.button("🗑️ Reset Role Play Record", use_container_width=True):
            reset_roleplay_records()
        
        st.divider()
        
        # Role Play Assessment Record
        st.subheader("📋 Role Play Assessment Record")
        
        if st.session_state.pp2.get_stage_name() == "Role Play":
            st.caption("Track competency assessment with GRO records")
            
            # Load criteria for display
            try:
                criteria_list = load_roleplay_criteria()
            except Exception as e:
                st.error(f"❌ Failed to load criteria: {str(e)}")
                st.stop()
            
            # Warning banner if NYC criteria lack completed GRO
            can_advance, missing = can_advance_stage("Role Play")
            if not can_advance:
                st.warning(
                    f"⚠️ **NYC detected.** You must complete GRO (Gap, Recover, Outcome) for {len(missing)} "
                    f"{'criterion' if len(missing) == 1 else 'criteria'} before proceeding: **{', '.join(missing)}**"
                )
                if st.session_state.get("active_gro_code"):
                    st.info(f"👉 Currently working on: **{st.session_state.active_gro_code}**")
            
            # Show item counter
            total_criteria = len(criteria_list)
            assessed_count = sum(1 for r in st.session_state.roleplay_records.values() if r.status != "NYA")
            competent_count = sum(1 for r in st.session_state.roleplay_records.values() if r.status == "C")
            st.caption(f"**Assessment Progress:** {assessed_count}/{total_criteria} assessed | {competent_count} competent")
            
            # Create criteria map for lookup
            criteria_map = {c["code"]: c for c in criteria_list}
            
            for code, record in sorted(st.session_state.roleplay_records.items()):
                criterion = criteria_map.get(code)
                if not criterion:
                    continue  # Skip if criterion not in YAML
                
                # Determine GRO status for display
                gro_status_label = ""
                if record.status == "NYC":
                    if record.gro is None or record.gro.gap == "":
                        gro_status_label = " | 🔴 GRO: Not started"
                    elif record.gro.completed:
                        gro_status_label = " | 🟢 GRO: Completed"
                    else:
                        gro_status_label = " | 🟡 GRO: In progress"
                
                # Build title with category if present
                title_display = f"{code}: {criterion['title']}"
                if "category" in criterion:
                    title_display = f"{code} ({criterion['category']}): {criterion['title']}"
                
                with st.expander(f"{title_display[:60]}...{gro_status_label}", expanded=False):
                    # Display criterion details
                    st.markdown(f"**{criterion['title']}**")
                    
                    # Show items as bullet list
                    st.markdown("**Items to assess:**")
                    for item in criterion.get("items", []):
                        st.markdown(f"- {item}")
                    
                    # Show any_of requirement if present
                    if "any_of" in criterion:
                        st.caption(f"ℹ️ Need ANY {criterion['any_of']} of the above items")
                    
                    st.divider()
                    # Status selection
                    status_key = f"rp_status_{code}"
                    
                    # Determine current index for 3-option radio
                    if record.status == "NYA":
                        status_index = 0
                    elif record.status == "C":
                        status_index = 1
                    else:  # NYC
                        status_index = 2
                    
                    current_status = st.radio(
                        "Assessment Status",
                        options=["NYA", "C", "NYC"],
                        index=status_index,
                        key=status_key,
                        horizontal=True
                    )
                    
                    # Update status if changed
                    if current_status != record.status:
                        record.status = current_status
                        # If toggled to NYC, set as active GRO code for capture
                        if current_status == "NYC":
                            st.session_state.active_gro_code = code
                            # Initialize GRO if needed
                            if record.gro is None:
                                record.gro = GROEntry()
                        # If toggled to C, update active GRO to next NYC needing GRO
                        elif st.session_state.active_gro_code == code:
                            update_active_gro_code()
                        st.rerun()
                    
                    # Evidence note
                    evidence_key = f"rp_evidence_{code}"
                    evidence_note = st.text_area(
                        "Evidence Note",
                        value=record.evidence_note,
                        key=evidence_key,
                        height=68
                    )
                    record.evidence_note = evidence_note
                    
                    # GRO section for NYC items
                    if record.status == "NYC":
                        st.divider()
                        st.markdown("**Gap-Recovery-Outcome (GRO)**")
                        
                        # Initialize GRO if needed
                        if record.gro is None:
                            record.gro = GROEntry()
                        
                        # Gap field
                        gap_key = f"rp_gap_{code}"
                        gap_text = st.text_area(
                            "1. Gap (Required)",
                            value=record.gro.gap,
                            key=gap_key,
                            height=68,
                            help="Describe what was missing or insufficient"
                        )
                        record.gro.gap = gap_text
                        
                        # Probe field (read-only display)
                        st.markdown("**2. Probe Question**")
                        if record.gro.probe_text:
                            st.text_area(
                                "Probe",
                                value=record.gro.probe_text,
                                key=f"rp_probe_display_{code}",
                                height=68,
                                disabled=True,
                                label_visibility="collapsed"
                            )
                        else:
                            st.info("Not captured yet (ask a probing question in chat)")
                        
                        # Response field (read-only display)
                        st.markdown("**3. Candidate Response**")
                        if record.gro.response_text:
                            st.text_area(
                                "Response",
                                value=record.gro.response_text,
                                key=f"rp_response_display_{code}",
                                height=68,
                                disabled=True,
                                label_visibility="collapsed"
                            )
                        else:
                            st.info("Not captured yet")
                        
                        # Outcome selection
                        st.markdown("**4. Outcome**")
                        outcome_key = f"rp_outcome_{code}"
                        outcome_options = ["Recovered to C", "Still NYC"]
                        outcome_index = 0 if record.gro.outcome == "Recovered to C" else 1
                        outcome = st.radio(
                            "Outcome",
                            options=outcome_options,
                            index=outcome_index,
                            key=outcome_key,
                            horizontal=True,
                            label_visibility="collapsed"
                        )
                        record.gro.outcome = outcome
                        
                        # Mark GRO Complete button
                        st.divider()
                        complete_key = f"rp_complete_{code}"
                        if st.button("✅ Mark GRO Complete", key=complete_key, type="primary"):
                            # Validation
                            errors = []
                            if not record.gro.gap.strip():
                                errors.append("Gap field is required")
                            if not record.gro.probe_text.strip():
                                errors.append("Probe question not captured (ask a probing question in chat)")
                            if not record.gro.response_text.strip():
                                errors.append("Candidate response not captured yet")
                            if not record.gro.outcome:
                                errors.append("Outcome must be selected")
                            
                            if errors:
                                for error in errors:
                                    st.error(f"❌ {error}")
                            else:
                                # Mark as completed
                                record.gro.completed = True
                                if outcome == "Recovered to C":
                                    record.status = "C"
                                # Move to next NYC item needing GRO
                                if st.session_state.active_gro_code == code:
                                    update_active_gro_code()
                                st.success("✅ GRO marked as complete!")
                                st.rerun()
        else:
            st.info("Assessment record available in Role Play stage")
        
        st.divider()
        
        # Generate Summary Record section
        st.subheader("📄 Generate Summary Record")
        
        # Check for incomplete GROs before allowing summary generation
        current_stage = st.session_state.pp2.get_stage_name()
        can_generate, missing = can_advance_stage(current_stage)
        
        if not can_generate:
            st.warning(
                f"⚠️ Cannot generate summary. "
                f"Complete GRO records for: **{', '.join(missing)}**"
            )
        else:
            st.info("✅ All NYC criteria have completed GRO records")
        
        # Generate Summary button
        if st.button("📊 Generate Summary Record", use_container_width=True, type="primary"):
            # Validate GRO completion
            can_generate, missing = can_advance_stage(current_stage)
            if not can_generate:
                st.error(
                    f"❌ Cannot generate summary. "
                    f"GRO completion required for: {', '.join(missing)}"
                )
                st.stop()
            
            # Generate the summaries
            st.session_state.summary_generated = True
            st.session_state.summary_text = generate_summary_text()
            st.session_state.summary_json = generate_summary_json()
            st.success("✅ Summary generated successfully!")
            st.rerun()
        
        # Display summary if generated
        if st.session_state.get("summary_generated", False):
            st.divider()
            
            # Tab view for text and JSON
            tab1, tab2 = st.tabs(["📄 Text Format", "🔧 JSON Format"])
            
            with tab1:
                st.text_area(
                    "Summary (Text)",
                    value=st.session_state.summary_text,
                    height=400,
                    label_visibility="collapsed"
                )
                st.download_button(
                    label="⬇️ Download as TXT",
                    data=st.session_state.summary_text,
                    file_name="pp2_assessment_summary.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with tab2:
                st.code(st.session_state.summary_json, language="json")
                st.download_button(
                    label="⬇️ Download as JSON",
                    data=st.session_state.summary_json,
                    file_name="pp2_assessment_summary.json",
                    mime="application/json",
                    use_container_width=True
                )
        
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
    
    # Role Play stage: Show status summary instead of generic checklist
    current_stage = st.session_state.pp2.get_stage_name()
    if current_stage == "Role Play":
        # Load criteria for counting
        try:
            criteria_list = load_roleplay_criteria()
            total_criteria = len(criteria_list)
            
            # Count statuses
            nya_count = sum(1 for r in st.session_state.roleplay_records.values() if r.status == "NYA")
            c_count = sum(1 for r in st.session_state.roleplay_records.values() if r.status == "C")
            nyc_count = sum(1 for r in st.session_state.roleplay_records.values() if r.status == "NYC")
            
            # Count GRO pending
            pending_gro = get_nyc_codes_missing_gro()
            gro_pending_count = len(pending_gro)
            
            # Status summary
            with st.expander("📊 Role Play Status Summary", expanded=True):
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.metric("Total", total_criteria)
                with col2:
                    st.metric("NYA", nya_count)
                with col3:
                    st.metric("Competent", c_count)
                with col4:
                    st.metric("NYC", nyc_count)
                with col5:
                    st.metric("GRO Pending", gro_pending_count)
                
                # Warning if GRO pending
                if gro_pending_count > 0:
                    st.divider()
                    st.warning(
                        f"⚠️ **{gro_pending_count} NYC {'item' if gro_pending_count == 1 else 'items'} need GRO completion** before you can advance.\n\n"
                        f"Codes: **{', '.join(pending_gro)}**"
                    )
                    if st.session_state.get("active_gro_code"):
                        st.info(f"👉 Currently working on: **{st.session_state.active_gro_code}**")
        except Exception as e:
            st.error(f"Failed to load criteria: {str(e)}")
    
    # Other stages: Show evidence checklist
    elif current_stage in st.session_state.evidence:
        checklist = st.session_state.evidence[current_stage]
        met_count = sum(1 for item in checklist if item.status == "C")
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
                
                # Display status with colored indicator
                if item.status == "C":
                    status_icon = "🟩 **C**"
                else:
                    status_icon = "🟥 **NYC**"
                
                # Show item with status and attempts
                st.markdown(f"{status_icon} {item.text}")
                st.caption(f"Attempts: {item.attempts}/3")
                
                # Show evidence notes only if debug mode enabled
                if st.session_state.get("show_debug", False) and item.evidence_notes:
                    st.caption(f"   *{item.evidence_notes}*")
            
            st.divider()
            
            # Manual evidence adjustment (not nested, just a section)
            st.markdown("**🔧 Manual Evidence Adjustment**")
            st.caption("Override evidence items manually for practice")
            
            for idx, item in enumerate(checklist):
                # Create unique keys for each control
                status_key = f"manual_status_{current_stage}_{item.id}"
                reset_key = f"manual_reset_{current_stage}_{item.id}"
                
                # Create clean layout: item text, status selector, attempts, reset button
                col1, col2, col3 = st.columns([4, 2, 1])
                
                with col1:
                    st.markdown(f"**{item.text[:60]}...**" if len(item.text) > 60 else f"**{item.text}**")
                
                with col2:
                    # Status selector (NYC or C)
                    new_status = st.selectbox(
                        "Status",
                        options=["NYC", "C"],
                        index=0 if item.status == "NYC" else 1,
                        key=status_key,
                        label_visibility="collapsed"
                    )
                    st.caption(f"Attempts: {item.attempts}/3")
                
                with col3:
                    # Reset attempts button
                    if st.button("↺", key=reset_key, help="Reset attempts to 0"):
                        item.attempts = 0
                        st.rerun()
                
                # If status changed, update the item
                if new_status != item.status:
                    item.status = new_status
                    item.evidence_notes = "Manual override" if new_status == "C" else "Manual reset"
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
