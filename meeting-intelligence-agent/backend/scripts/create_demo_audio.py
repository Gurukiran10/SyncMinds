"""
Create a demo audio file for testing meeting upload
This creates a simple WAV file with spoken text using text-to-speech
"""
import sys
from pathlib import Path

try:
    # Try to use pyttsx3 (offline TTS)
    import pyttsx3
    import wave
    import io
    
    def create_demo_audio():
        """Create demo audio file with sample meeting content"""
        output_path = Path(__file__).parent.parent.parent / "demo_meeting.wav"
        
        # Sample meeting transcript
        meeting_text = """
        Good morning everyone. Let's start the Q1 planning meeting.
        First on the agenda, we need to review our quarterly goals.
        John, can you update us on the marketing campaign progress?
        Sarah, please take note that we need the budget report by Friday.
        For our next action item, we should schedule a follow-up meeting.
        Does anyone have questions or concerns?
        Great, let's wrap up. Thanks everyone for attending.
        """
        
        print("🎙️  Creating demo audio file...")
        
        # Initialize TTS engine
        engine = pyttsx3.init()
        
        # Configure voice properties
        engine.setProperty('rate', 150)  # Speed
        engine.setProperty('volume', 0.9)  # Volume
        
        # Save to file
        engine.save_to_file(meeting_text, str(output_path))
        engine.runAndWait()
        
        print(f"✅ Demo audio created: {output_path}")
        print(f"   Duration: ~30 seconds")
        print(f"   You can now upload this file through the UI!")
        
        return output_path

except ImportError:
    # Fallback: Create instructions for manual recording
    def create_demo_audio():
        """Provide instructions for creating demo audio"""
        print("📝 pyttsx3 not installed. Here are your options:\n")
        
        print("Option 1: Install text-to-speech library")
        print("   pip install pyttsx3")
        print("   Then run this script again\n")
        
        print("Option 2: Use online TTS service")
        print("   1. Go to https://ttsmp3.com/")
        print("   2. Paste this text:")
        print("   'Good morning everyone. This is a Q1 planning meeting.")
        print("    We need to review quarterly goals and budget reports.")
        print("    Please schedule a follow-up meeting for next week.'")
        print("   3. Generate and download as MP3 or WAV")
        print("   4. Save as 'demo_meeting.wav'\n")
        
        print("Option 3: Record your own audio")
        print("   1. Use QuickTime Player (macOS) or Voice Recorder")
        print("   2. Record a 30-second sample meeting")
        print("   3. Save as WAV or MP3 format")
        print("   4. Upload through the UI\n")
        
        print("Option 4: Download sample audio")
        print("   Download from: https://www2.cs.uic.edu/~i101/SoundFiles/")
        print("   Any WAV file will work for testing\n")

if __name__ == "__main__":
    create_demo_audio()
