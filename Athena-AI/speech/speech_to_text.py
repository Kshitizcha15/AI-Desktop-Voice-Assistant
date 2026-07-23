import speech_recognition as sr

recognizer = sr.Recognizer()


def listen(timeout=5, phrase_time_limit=8, calibrate=False):
    """
    Listens to the microphone once, converts speech to text, and returns it.
    Returns None if nothing was understood (silence, unclear audio, etc.)
    so callers can handle that case instead of crashing.
    """
    with sr.Microphone() as source:
        if calibrate:
            print("[Listening] Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print("[Listening] Speak now...")
        try:
            audio = recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit,
            )
        except sr.WaitTimeoutError:
            return None

    try:
        text = recognizer.recognize_google(audio)
        print(f"[Heard]: {text}")
        return text
    except sr.UnknownValueError:
        print("[Listening] Could not understand audio.")
        return None
    except sr.RequestError as e:
        print(f"[Listening] Speech recognition service error: {e}")
        return None


if __name__ == "__main__":
    if result := listen():
        print(f"You said: {result}")
    else:
        print("Nothing recognized. Try again.")
