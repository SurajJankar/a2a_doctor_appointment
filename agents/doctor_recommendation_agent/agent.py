import json
import os
import openai
from shared.session import save_session
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

SESSION_FILE = os.path.join(os.path.dirname(__file__), "session_store.json")

class DoctorRecommendationAgent:
    SUPPORTED_CONTENT_TYPES = ["text/markdown", "text/plain"]

    def __init__(self):
        doctor_file = os.path.join(os.path.dirname(__file__), "doctors.json")
        with open(doctor_file, "r", encoding="utf-8") as f:
            doctor_data = json.load(f)
            self.doctors = doctor_data["doctors"]

        # Load or initialize session data
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                self.session = json.load(f)
        else:
            self.session = {}

    def _persist_session(self):
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump(self.session, f, indent=2)

    def _match_doctors(self, user_input, preferred_day=None):
        symptom_map = {
            "heart": "Cardiology", "chest": "Cardiology",
            "skin": "Dermatology", "rash": "Dermatology",
            "throat": "ENT", "ear": "ENT", "nose": "ENT",
            "bone": "Orthopedics", "joint": "Orthopedics",
            "headache": "Neurology", "migraine": "Neurology", "dizziness": "Neurology",
            "stomach": "Gastroenterology",
            "cold": "General Medicine", "fever": "General Medicine", "pain": "General Medicine"
        }

        specialty = None
        for keyword, spec in symptom_map.items():
            if keyword in user_input.lower():
                specialty = spec
                break

        if not specialty:
            return []

        normalized_day = preferred_day.strip().capitalize() if preferred_day else None
        results = []

        for doc in self.doctors:
            if doc["specialty"].lower() == specialty.lower():
                if normalized_day:
                    doc_days = [d.strip().capitalize() for d in doc["available_days"]]
                    if normalized_day in doc_days:
                        results.append(doc)
                else:
                    results.append(doc)

        return results

    def _format_doctor(self, doc):
        return (
            f"👨‍⚕️ *Name:* {doc['name']}\n"
            f"🔬 *Specialty:* {doc['specialty']}\n"
            f"🗓️ *Available Days:* {', '.join(doc['available_days'])}\n"
            f"⏰ *Time:* {doc['time']}\n"
            f"📍 *Location:* {doc['location']}"
        )

    def _chatgpt_select_prompt(self, options):
        lines = [f"{i+1}. {doc['name']} ({doc['specialty']})" for i, doc in enumerate(options)]
        return (
            "Here are some available doctors:\n" +
            "\n".join(lines) +
            "\n\nPlease reply with the number of the doctor you'd like to know more about."
        )

    def get_recommendation(self, user_input, session_id="default"):
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        preferred_day = next((day for day in days if day in user_input.lower()), None)

        matches = self._match_doctors(user_input, preferred_day)

        if matches:
            self.session[session_id] = matches
            self._persist_session()

            if len(matches) == 1:
                save_session(session_id, matches[0])
                return self._format_doctor(matches[0])
            else:
                return self._chatgpt_select_prompt(matches[:3])

        # Try without day filtering
        alt_matches = self._match_doctors(user_input)
        if alt_matches:
            self.session[session_id] = alt_matches[:3]
            self._persist_session()
            return self._chatgpt_select_prompt(alt_matches[:3])

        return "I couldn't find any matching doctors for your symptoms. Could you rephrase it?"

    def get_doctor_details_from_selection(self, user_reply, session_id="default"):
        if session_id not in self.session:
            return "No active doctor list. Please describe your symptoms again."

        try:
            idx = int(user_reply.strip()) - 1
            selected = self.session[session_id][idx]
            self.session[session_id] = [selected]  # Overwrite with selected only
            self._persist_session()
            save_session(session_id, selected)
            return self._format_doctor(selected)
        except:
            return "Invalid selection. Please reply with a number (e.g., 1, 2, or 3)."
