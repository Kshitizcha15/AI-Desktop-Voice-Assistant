import pyttsx3

# Initialize the engine once, reuse it everywhere.
# Creating a new engine per call is a common bug that causes audio glitches.
_engine = pyttsx3.init()
_engine.setProperty('rate', 175)   # words per minute, 175 is a natural pace
_engine.setProperty('volume', 1.0)

def speak(text):
    """
    Converts text to speech and plays it out loud.
    This is the ONLY function other modules should call —
    keep the pyttsx3 details contained here.
    """
    print(f"[Assistant]: {text}")  # also print, so you can debug without sound
    _engine.say(text)
    _engine.runAndWait()

if __name__ == "__main__":
    # Quick manual test — run this file directly to check TTS works
    speak("Hello, this is your assistant speaking.If you can hear this, text to speech is working.")
    