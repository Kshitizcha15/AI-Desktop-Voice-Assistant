# import pyttsx3

# # Initialize the engine once, reuse it everywhere.
# # Creating a new engine per call is a common bug that causes audio glitches.
# _engine = pyttsx3.init()
# _engine.setProperty('rate', 175)   # words per minute, 175 is a natural pace
# _engine.setProperty('volume', 1.0)

# def speak(text):
#     """
#     Converts text to speech and plays it out loud.
#     This is the ONLY function other modules should call —
#     keep the pyttsx3 details contained here.
#     """
#     print(f"[Assistant]: {text}")  # also print, so you can debug without sound
#     _engine.say(text)
#     _engine.runAndWait()

# if __name__ == "__main__":
#     # Quick manual test — run this file directly to check TTS works
#     speak("Hello, this is your assistant speaking.If you can hear this, text to speech is working.")
    





# import pyttsx3

# # Create the speech engine once and reuse it.
# engine = pyttsx3.init()

# # Voice settings
# engine.setProperty("rate", 175)   # Speech speed
# engine.setProperty("volume", 1.0) # Volume: 0.0 to 1.0


# def speak(text):
#     """Speak the assistant's response aloud."""
#     text = str(text).strip()

#     if not text:
#         return

#     print(f"[Assistant]: {text}")  # Keeps text visible for debugging
#     engine.say(text)
#     engine.runAndWait()


# if __name__ == "__main__":
#     speak(
#         "Hello, this is your assistant speaking. "
#         "If you can hear this, text to speech is working."
#     )



import subprocess


def speak(text):
    """Speak text aloud using the macOS built-in speech engine."""
    text = str(text).strip()

    if not text:
        return

    print(f"[Assistant]: {text}")

    try:
        subprocess.run(
            ["say", "-r", "175", text],
            check=True
        )
    except subprocess.CalledProcessError as error:
        print(f"Text-to-speech error: {error}")


if __name__ == "__main__":
    speak("Hello! Friday here. I'm online and ready to assist you. How can I help you today?")