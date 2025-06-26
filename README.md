# 🤖 Multi-Agent Hospital Demo – A2A with Google ADK

Welcome to **Multi-Agent Hospital Demo** — a minimal Agent2Agent (A2A) implementation using Google's [Agent Development Kit (ADK)](https://github.com/google/agent-development-kit).

This example demonstrates how to build, serve, and interact with multiple A2A agents:
1. **TellTimeAgent** – replies with the current time.
2. **GreetingAgent** – fetches the time and generates a poetic greeting.
3. **DoctorRecommendationAgent** – recommends doctors based on symptoms and availability.
4. **BookAppointmentAgent** – books appointments with doctors based on user input.
5. **UserInteractionAgent** – acts as a polite hospital counter assistant.
6. **OrchestratorAgent (Host)** – routes requests to the appropriate child agent.

All of them work together seamlessly via A2A discovery and JSON-RPC.

---

## 📦 Project Structure

```bash
version_3_multi_agent/
├── .env                         # Your GOOGLE_API_KEY (not committed)
├── pyproject.toml              # Dependency config
├── README.md                   # You are reading it!
├── app/
│   └── cmd/
│       └── cmd.py              # CLI to interact with the OrchestratorAgent
├── agents/
│   ├── tell_time_agent/
│   │   ├── __main__.py         # Starts TellTimeAgent server
│   │   ├── agent.py            # Gemini-based time agent
│   │   └── task_manager.py     # In-memory task handler for TellTimeAgent
│   ├── greeting_agent/
│   │   ├── __main__.py         # Starts GreetingAgent server
│   │   ├── agent.py            # Orchestrator that calls TellTimeAgent + LLM greeting
│   │   └── task_manager.py     # Task handler for GreetingAgent
│   ├── doctor_recommendation_agent/
│   │   ├── __main__.py         # Starts DoctorRecommendationAgent server
│   │   ├── agent.py            # Recommends doctors based on symptoms
│   │   ├── doctors.json        # Doctor data
│   │   ├── session_store.json  # Session data for recommendations
│   │   └── task_manager.py     # Task handler for DoctorRecommendationAgent
│   ├── book_appointment_agent/
│   │   ├── __main__.py         # Starts BookAppointmentAgent server
│   │   ├── agent.py            # Books appointments with doctors
│   │   ├── appointment_db.json # Stores booked appointments
│   │   └── task_manager.py     # Task handler for BookAppointmentAgent
│   ├── user_interaction_agent/
│   │   ├── __main__.py         # Starts UserInteractionAgent server
│   │   ├── agent.py            # Polite hospital counter assistant
│   │   └── task_manager.py     # Task handler for UserInteractionAgent
│   └── host_agent/
│       ├── entry.py            # CLI to start OrchestratorAgent server
│       ├── orchestrator.py     # LLM router + TaskManager for OrchestratorAgent
│       └── agent_connect.py    # Helper to call child A2A agents
├── server/
│   ├── server.py               # A2A JSON-RPC server implementation
│   └── task_manager.py         # Base in-memory task manager interface
├── shared/
│   ├── session_store.json      # Shared session data
│   └── session.py              # Session utilities
├── models/
│   ├── agent.py                # Agent metadata models
│   ├── json_rpc.py             # JSON-RPC models
│   ├── request.py              # Request models
│   └── task.py                 # Task models
├── utilities/
│   ├── discovery.py            # Finds agents via `agent_registry.json`
│   └── agent_registry.json     # List of child-agent URLs (one per line)
└── client/
    └── client.py               # A2A client implementation
```

---

## 🛠️ Setup

1. **Clone & navigate**

    ```bash
    git clone https://github.com/theailanguage/a2a_samples.git
    cd a2a_samples/version_3_multi_agent
    ```

2. **Create & activate a venv**

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3. **Install dependencies**

    Using [`uv`](https://github.com/astral-sh/uv):

    ```bash
    uv pip install .
    ```

    Or with pip directly:

    ```bash
    pip install .
    ```

4. **Set your API key**

    Create `.env` at the project root:
    ```bash
    echo "GOOGLE_API_KEY=your_api_key_here" > .env
    ```

---

## 🎬 Demo Walkthrough

**Start the TellTimeAgent**
```bash
python3 -m agents.tell_time_agent --host localhost --port 10000
```

**Start the GreetingAgent**
```bash
python3 -m agents.greeting_agent --host localhost --port 10001
```

**Start the DoctorRecommendationAgent**
```bash
python3 -m agents.doctor_recommendation_agent --host localhost --port 10006
```

**Start the BookAppointmentAgent**
```bash
python3 -m agents.book_appointment_agent --host localhost --port 10007
```

**Start the UserInteractionAgent**
```bash
python3 -m agents.user_interaction_agent --host localhost --port 10005
```

**Start the Orchestrator (Host) Agent**
```bash
python3 -m agents.host_agent.entry --host localhost --port 10002
```

**Launch the CLI (cmd.py)**
```bash
python3 -m app.cmd.cmd --agent http://localhost:10002
```

**Try it out!**
```bash
> What time is it?
Agent says: The current time is: 2025-05-05 14:23:10

> Greet me
Agent says: Good afternoon, friend! The golden sun dips low...
```

**Doctor Recommendation & Appointment Booking Example:**
```bash
> I have a headache
Agent says: OK. Here are some available doctors:
1. Dr. Sameer Khan (Neurology)
2. Dr. Tanya Bhatt (Neurology)

Please reply with the number of the doctor you'd like to know more about.

> 2
Agent says: 👨‍⚕️ *Name:* Dr. Tanya Bhatt
🔬 *Specialty:* Neurology
🗓️ *Available Days:* Tuesday, Friday
⏰ *Time:* 02:00 PM - 5:00 PM
📍 *Location:* Neuro Wing, 4th Floor

> Book appointment
Agent says: ❗ Please provide a date in YYYY-MM-DD format or a valid weekday name.

> Book appointment on Friday
Agent says: I need a date to book your appointment. Please specify the date you would like to book your appointment with Dr. Tanya Bhatt.  For example,  "Book appointment with Dr. Tanya Bhatt on 2024-03-15".

> Book appointment with Dr. Tanya Bhatt on 2024-03-15
Agent says: ✅ Confirmed appointment with *Dr. Tanya Bhatt* on *2024-03-15*
⏰ Time: 02:00 PM - 5:00 PM
📍 Location: Neuro Wing, 4th Floor
```

---

## 🔍 How It Works

1. **Discovery**: OrchestratorAgent reads `utilities/agent_registry.json`, fetches each agent's `/​.well-known/agent.json`.
2. **Routing**: Based on intent, the Orchestrator's LLM calls its tools:
   - `list_agents()`