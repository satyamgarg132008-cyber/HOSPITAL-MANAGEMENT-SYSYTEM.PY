"""
=============================================================================
MEDNOVA AI — INTELLIGENT HOSPITAL MANAGEMENT SYSTEM
Module: voice_engine.py
Description: Asynchronous offline speech synthesizer using pyttsx3, worker queue,
             audio state toggle, and J.A.R.V.I.S.-style vocal announcements.
=============================================================================
"""

import threading
import queue
import logging

# Configure silent fallback logging
logger = logging.getLogger("MedNovaVoice")


class VoiceAssistant:
    """
    Offline text-to-speech assistant modeled after Stark J.A.R.V.I.S.
    Operates in a background daemon thread to avoid blocking the Tkinter event loop.
    """

    def __init__(self):
        self.enabled = True
        self.speech_queue = queue.Queue()
        self.engine = None
        self.is_initialized = False

        # Attempt to initialize pyttsx3 in the worker thread
        self.worker_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.worker_thread.start()

    def _init_engine(self):
        """Initialize TTS engine inside worker thread for COM compatibility on Windows."""
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            # Set rate and volume
            self.engine.setProperty("rate", 175)    # Slightly brisk, intelligent cadence
            self.engine.setProperty("volume", 0.95)

            # Attempt to select a clear voice if available
            voices = self.engine.getProperty("voices")
            if voices:
                # Prefer English voice
                for v in voices:
                    if "david" in v.name.lower() or "george" in v.name.lower() or "zira" in v.name.lower():
                        self.engine.setProperty("voice", v.id)
                        break
            self.is_initialized = True
        except Exception as e:
            logger.warning(f"Voice synthesizer could not be initialized: {e}")
            self.engine = None
            self.is_initialized = False

    def _speech_worker(self):
        """Worker loop processing speech queue continuously."""
        self._init_engine()

        while True:
            text = self.speech_queue.get()
            if text is None:
                break

            if self.enabled and self.is_initialized and self.engine:
                try:
                    self.engine.say(text)
                    self.engine.runAndWait()
                except Exception as e:
                    logger.warning(f"Speech playback error: {e}")
            self.speech_queue.task_done()

    def speak(self, text: str):
        """Queue text to be spoken aloud."""
        if not self.enabled or not text:
            return
        # Add to background queue
        self.speech_queue.put(text)

    def toggle(self) -> bool:
        """Toggle voice assistant mute state. Returns new enabled status."""
        self.enabled = not self.enabled
        return self.enabled

    def welcome_user(self, full_name: str, role: str):
        """Vocal greeting upon successful authentication."""
        greeting = f"Welcome to Med Nova AI Command Center, {full_name}. Security authorization level: {role}. All hospital systems online."
        self.speak(greeting)

    def announce_patient_registered(self, patient_name: str, uid: str):
        """Announce patient registration."""
        self.speak(f"Patient registration confirmed for {patient_name}. Record identifier {uid}.")

    def announce_appointment_booked(self, patient_name: str, doctor_name: str, apt_date: str):
        """Announce appointment booking."""
        self.speak(f"Appointment confirmed for {patient_name} with {doctor_name} on {apt_date}.")

    def announce_bill_generated(self, invoice_no: str, total_str: str):
        """Announce invoice generation."""
        self.speak(f"Invoice {invoice_no} generated. Total amount: {total_str}.")

    def announce_dashboard_summary(self, patients_count: int, doctors_count: int, appointments_today: int, revenue_str: str):
        """Vocal briefing of current hospital operations."""
        summary = (
            f"Med Nova AI Operational Status: Currently monitoring {patients_count} registered patients "
            f"across {doctors_count} specialist staff. "
            f"There are {appointments_today} clinical appointments scheduled for today. "
            f"Total hospital gross revenue stands at {revenue_str}."
        )
        self.speak(summary)


# Global singleton instance of voice assistant
voice_assistant = VoiceAssistant()
