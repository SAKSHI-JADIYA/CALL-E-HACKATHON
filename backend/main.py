# backend/main.py
import os
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from calle import CalleClient
from security import SECURITY_STATE, analyze_semantic_drift, trip_circuit_breaker

# Load environment variables
load_dotenv()

app = FastAPI(title="VibeGuard Security Core")

# Enable CORS for the premium dashboard frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the official CALL-E client
CALLE_KEY = os.getenv("CALLE_API_KEY")
client = CalleClient(api_key=CALLE_KEY) if CALLE_KEY else None

class ChatRequest(BaseModel):
    message: str
    agent_id: str

@app.get("/api/status")
def get_security_status():
    """Endpoint for our premium frontend to read real-time security state."""
    return SECURITY_STATE

def trigger_calle_out_of_band_mitigation():
    """
    Executes the CALL-E voice session. It commands the AI to announce the leak
    and map physical keypad dial tones back into our cloud infrastructure state.
    """
    if not client:
        print("[WARN] CALL_API_KEY missing. Skipping out-of-band dial loop.")
        return

    admin_phone = os.getenv("ADMIN_PHONE_NUMBER", "")
    
    # The exact, hackish instruction we teach CALL-E to execute on the line
    task_instruction = (
        f"Call the administrator at {admin_phone} immediately. "
        "As soon as they answer, say exactly word-for-word: "
        "'Security Alert. Error 404: Malicious payload execution intercepted on Agent 4. "
        "The live transaction stream has been frozen at HTTP 423. "
        "I need you to triage this incident immediately using your dial pad. "
        "Press 1 to enforce Row-Level Security on the database. "
        "Press 2 to completely burn and revoke the agent's token.'"
        "Wait patiently for them to press a number key on their phone keypad, then hang up."
    )

    try:
        # Call-E handles the speech, wait conditions, and digit extraction natively
        call = client.calls.create_and_wait(
            task=task_instruction,
            result_schema={
                "type": "object",
                "required": ["selected_action"],
                "properties": {
                    "selected_action": {
                        "type": "string", 
                        "enum": ["1", "2", "unknown"],
                        "description": "The exact digit the user pressed on their keypad."
                    },
                },
            },
        )
        
        # Parse the structured return data straight from the phone line
        result = call.get("structured_result")
        if result and "selected_action" in result:
            action = result["selected_action"]
            
            if action == "1":
                SECURITY_STATE["rls_enforced"] = True
                print("[SUCCESS] Phone triage complete: Supabase RLS enforced successfully.")
            elif action == "2":
                SECURITY_STATE["agent_token_active"] = False
                print("[SUCCESS] Phone triage complete: Agent authentication token revoked.")
            else:
                print("[INFO] Call ended without clear remediation keypress.")
                
    except Exception as e:
        print(f"[ERROR] CALL-E execution failed: {str(e)}")

@app.post("/api/chat")
def process_agent_chat(payload: ChatRequest, background_tasks: BackgroundTasks):
    """Simulated streaming backend data channel."""
    # 1. Guard check: has the token been burned?
    if not SECURITY_STATE["agent_token_active"]:
        raise HTTPException(status_code=401, detail="Agent Token Revoked.")
    
    # 2. Guard check: is the circuit breaker tripped?
    if SECURITY_STATE["is_frozen"]:
        raise HTTPException(status_code=423, detail="Stream Frozen: Triage in progress.")
        
    # 3. Process prompt text safety
    if analyze_semantic_drift(payload.message):
        trip_circuit_breaker(payload.message)
        
        # Dispatch the CALL-E dial routine into background execution so the API freezing happens in milliseconds
        background_tasks.add_task(trigger_calle_out_of_band_mitigation)
        
        raise HTTPException(status_code=423, detail="CRITICAL: Prompt Injection Intercepted. Stream Frozen.")

    # 4. Standard secure state check
    if SECURITY_STATE["rls_enforced"]:
        return {"status": "success", "data": [], "message": "200 OK: Empty Set (RLS Enforced)"}

    return {"status": "success", "data": ["Sensitive Row A", "Sensitive Row B"]}
