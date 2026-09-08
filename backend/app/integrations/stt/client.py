from typing import List, Dict, Any


class SpeechToTextClient:
    """
    Interface for M2 (Whisper / Speaker-Diarized STT Pipeline).
    """

    async def transcribe_audio(self, audio_file_path: str, language: str = "en") -> List[Dict[str, Any]]:
        # Placeholder simulation for M2 integration
        return [
            {
                "speaker": "doctor",
                "text": "Namaste Ramesh ji. Please tell me what health issues you have been facing.",
                "start": 0.0,
                "end": 4.5,
            },
            {
                "speaker": "patient",
                "text": "Doctor, for the past 3 days I have severe throat pain, difficulty swallowing, and dry cough with mild fever.",
                "start": 5.0,
                "end": 11.2,
            },
            {
                "speaker": "doctor",
                "text": "Do you have any existing medical conditions or known drug allergies?",
                "start": 12.0,
                "end": 15.8,
            },
            {
                "speaker": "patient",
                "text": "I take Telmisartan 40mg for high BP. Also, I am strictly allergic to Penicillin.",
                "start": 16.2,
                "end": 21.0,
            },
        ]
