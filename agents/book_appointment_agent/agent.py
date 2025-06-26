# =============================================================================
# agents/book_appointment_agent/agent.py
# =============================================================================
# Purpose:
# Implements doctor appointment booking logic:
# - Loads doctors.json
# - Validates doctor ID and date
# - Stores booking in appointment_db.json
# - Can fetch doctor info from session if ID is not given
# - Can parse weekday names and convert to next matching date
# =============================================================================

import json, os
from datetime import datetime, timedelta
from shared.session import load_session
import calendar


class BookAppointmentAgent:
    SUPPORTED_CONTENT_TYPES = ["text/markdown", "text/plain"]

    def __init__(self):
        base = os.path.dirname(__file__)
        doc_file = os.path.join(base, "../doctor_recommendation_agent/doctors.json")
        appt_file = os.path.join(base, "appointment_db.json")

        with open(doc_file, "r", encoding="utf-8") as f:
            self.doctors = json.load(f)["doctors"]

        self.appointment_file = appt_file
        self._load_appointments()

    def _load_appointments(self):
        if os.path.exists(self.appointment_file):
            with open(self.appointment_file, "r") as f:
                self.appointments = json.load(f)
        else:
            self.appointments = []

    def _save_appointments(self):
        with open(self.appointment_file, "w") as f:
            json.dump(self.appointments, f, indent=2)

    def _find_doctor(self, identifier):
        for doc in self.doctors:
            if doc["id"].lower() == identifier.lower() or doc["name"].lower() == identifier.lower():
                return doc
        return None

    def _is_available(self, doctor, date_str):
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            return dt.strftime("%A") in doctor["available_days"]
        except Exception:
            return False

    def _find_next_date_for_day(self, doctor, weekday_name):
        weekday_name = weekday_name.capitalize()
        today = datetime.now()

        for i in range(1, 15):  # Look ahead 2 weeks
            check_date = today + timedelta(days=i)
            if (
                check_date.strftime('%A') == weekday_name
                and weekday_name in doctor["available_days"]
            ):
                return check_date.strftime("%Y-%m-%d")
        return None

    def book(self, user_input, session_id="default"):
        parts = user_input.lower().split()
        doc_id = None
        date_str = None
        weekday = None

        # Extract doc_id and date or weekday
        for p in parts:
            if p.startswith("doc"):
                doc_id = p
            elif "-" in p and len(p) == 10:
                try:
                    datetime.strptime(p, "%Y-%m-%d")
                    date_str = p
                except:
                    continue
            elif p.capitalize() in calendar.day_name:
                weekday = p.capitalize()

        # Resolve doctor
        doctor = None
        if doc_id:
            doctor = self._find_doctor(doc_id)
        else:
            session_data = load_session(session_id)
            if session_data:
                doctor = self._find_doctor(session_data.get("id", ""))
            else:
                return "❗ Doctor ID not provided and no previous doctor found in session."

        if not doctor:
            return f"❗ No doctor found with ID '{doc_id}'." if doc_id else "❗ No valid doctor found."

        # If weekday provided, find next available date
        if not date_str and weekday:
            date_str = self._find_next_date_for_day(doctor, weekday)
            if not date_str:
                return f"❗ {doctor['name']} does not have upcoming availability on {weekday}."

        if not date_str:
            return "❗ Please provide a date in YYYY-MM-DD format or a valid weekday name."

        if not self._is_available(doctor, date_str):
            return f"❗ {doctor['name']} is not available on {date_str}."

        # Create appointment
        appt = {
            "session_id": session_id,
            "doctor_id": doctor["id"],
            "doctor_name": doctor["name"],
            "date": date_str,
            "time": doctor["time"],
            "location": doctor["location"]
        }
        self.appointments.append(appt)
        self._save_appointments()

        return (
            f"✅ Confirmed appointment with *{doctor['name']}* on *{date_str}*\n"
            f"⏰ Time: {doctor['time']}\n"
            f"📍 Location: {doctor['location']}"
        )
