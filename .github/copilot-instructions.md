# PP2 Practice Bot - AI Agent Instructions

## Project Overview
Streamlit web app simulating PP2 assessment candidates via OpenAI API. Users play the **assessor** role; AI plays the **candidate** being assessed in professional scenarios.

**Architecture:** 
- [app.py](app.py) - Streamlit UI (password protection, scenario selection, chat interface)
- [candidate.py](candidate.py) - OpenAI integration with difficulty-tuned system prompts
- [.env](.env) - Config (API keys, passwords) - **NEVER commit**

## Critical Development Rules

### 1. Verify Before Coding (from prime_directive.md)
**NEVER assume** method signatures, enum values, or return types. Always:
```python
# ❌ DON'T assume
TimeFrame.DAILY  # Does this exist?

# ✅ DO verify first
# Use grep_search to find enum definition
TimeFrame.DAY_1  # Verified actual value
```

**Research checklist before ANY implementation:**
- [ ] Method signatures (params, types, order) - use `grep_search`
- [ ] Return types (can it be None? Optional?) - check type hints
- [ ] Enum/constant values - read source, don't guess
- [ ] Existing usage examples - use `list_code_usages`

### 2. Defensive Programming Always
```python
# ❌ Crashes if None
position = get_position(symbol)
if position > 0:

# ✅ Safe handling
position = get_position(symbol) or 0
if position > 0:
```

### 3. Test Pass + Zero Warnings (Non-Negotiable)
1. Run tests BEFORE changes (baseline: X passed, 0 warnings)
2. Make changes incrementally
3. Run tests AFTER each change
4. Fix failures/warnings immediately or revert
5. **Warnings are NOT acceptable** - they become breaking errors later

## Project-Specific Patterns

### Streamlit Session State Management
Session state stores conversation history and user config. Always initialize in `initialize_session_state()`:
```python
if "messages" not in st.session_state:
    st.session_state.messages = []
```

Access pattern:
```python
st.session_state.messages.append({"role": "user", "content": text})
```

### OpenAI API Integration
Uses OpenAI's Chat Completions API with **system prompt engineering**:

```python
# System prompt structure (see candidate.py)
system_prompt = base_behavior + difficulty_instructions

# Difficulty tuning:
# - Easy: 1-2% error rate, volunteers info
# - Medium: 10-15% gaps, needs prompting  
# - Hard: 20-30% mistakes, requires skilled questioning
```

**Key config from .env:**
- `OPENAI_API_KEY` - Required for API calls
- `APP_PASSWORD` - Protects app access
- `MODEL` - Default `gpt-4o-mini` (fast, cost-effective)

### Scenario System
Scenarios defined in `SCENARIOS` dict ([app.py#L71-L89](app.py#L71-L89)). Pattern:
```python
SCENARIOS = {
    "Scenario Name": """Context description..."""
}
```

To add scenarios: Extend dict, auto-populated in UI selectbox.

### Password Protection Flow
1. Check `APP_PASSWORD` from `.env` (validates on startup)
2. Store authentication in `st.session_state.authenticated`
3. Use `st.rerun()` to refresh UI after login
4. Block access with `st.stop()` if password fails

## Development Workflows

### Running the App
```powershell
# Activate virtual environment (project uses venv in root)
.\Scripts\Activate.ps1

# Run Streamlit app
streamlit run app.py
```

### Environment Setup
```powershell
# Install dependencies
pip install -r requirements.txt

# Configure .env (copy from .env.example)
# MUST set: OPENAI_API_KEY, APP_PASSWORD
```

### Adding a New Scenario
1. Add entry to `SCENARIOS` dict in [app.py](app.py#L71)
2. Scenario auto-appears in sidebar selectbox
3. No other changes needed - candidate.py injects scenario into system prompt

### Modifying Candidate Behavior
Edit `_build_system_prompt()` in [candidate.py](candidate.py#L54):
- Adjust difficulty instructions (error rates, omission patterns)
- Tune temperature (0.8 default) for response variation
- Modify max_tokens (500 default) for response length

## Common Pitfalls

### 1. API Key Not Set
```python
# candidate.py handles this gracefully:
if not api_key:
    return "ERROR: OPENAI_API_KEY not found..."
```
**Fix:** Ensure `.env` has valid `OPENAI_API_KEY`

### 2. Streamlit Reruns
Streamlit reruns entire script on interaction. Don't put expensive operations outside functions:
```python
# ❌ Runs on every interaction
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ✅ Inside function, only when needed
def candidate_reply(...):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
```

### 3. Session State Persistence
Session state persists across reruns but resets on page refresh. For persistent data, need external storage (not implemented).

## File Structure Conventions

```
/ (project root)
├── app.py              # Main Streamlit app (UI, chat logic)
├── candidate.py        # OpenAI integration (system prompts)
├── .env                # Config (NEVER commit)
├── .env.example        # Template for .env
├── requirements.txt    # Dependencies
├── prime_directive.md  # Development guidelines (READ THIS)
├── Lib/                # Virtual environment (gitignored)
├── Scripts/            # Virtual environment activation
└── __pycache__/        # Python bytecode (gitignored)
```

**Virtual Environment:** Root-level venv (unusual pattern). Activate with `.\Scripts\Activate.ps1` (Windows).

## Key Dependencies
- `streamlit==1.40.2` - Web UI framework
- `openai==1.58.1` - OpenAI API client
- `python-dotenv==1.0.1` - Environment variable management

## Testing & Validation
Currently no automated tests. Manual validation:
1. Test password protection (wrong/right password)
2. Test scenario switching (sidebar)
3. Test difficulty levels (Easy/Medium/Hard behavior differences)
4. Test conversation flow (multi-turn chat)
5. Verify OpenAI API responses (check for errors)

## Prime Directive Alignment
This project follows strict development guidelines in [prime_directive.md](prime_directive.md):
- **Verify first, code second** - Research APIs before implementation
- **Defensive programming** - Handle None, validate inputs
- **Incremental testing** - Test components in isolation
- **Zero warnings tolerance** - All warnings must be resolved

When extending this project, read the Prime Directive for comprehensive best practices on research workflows, common pitfalls, and quality standards.
