import sys
import os

# Add the project root to the path so we can import from speech/ and core/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from speech.text_to_speech import speak
from speech.speech_to_text import listen
from core.command_parser import parse_command


def handle_open_app(app_name):
    """
    Placeholder for now — Phase 1 doc calls for pyautogui/subprocess here.
    Keeping this simple until we wire in the real automation module.
    """
    return f"Opening {app_name}. (App-opening not wired up yet — this is a placeholder.)"


def handle_system_status():
    """
    Placeholder for now — Phase 1 doc calls for psutil here.
    """
    return "System status check is not wired up yet. Coming in the next step."


def handle_web_search(query):
    """
    Placeholder for now — Phase 1 doc calls for webbrowser here.
    """
    return f"Searching the web for {query}. (Web search not wired up yet — this is a placeholder.)"


def route_command(command_name, extra_data):
    """
    Takes the parsed command and dispatches to the right handler.
    Returns the text response to be spoken.
    """
    if command_name == "open_app":
        return handle_open_app(extra_data)
    elif command_name == "system_status":
        return handle_system_status()
    elif command_name == "web_search":
        return handle_web_search(extra_data)
    elif command_name == "exit":
        return "__EXIT__"  # special signal, handled in the main loop below
    else:
        return "Sorry, I didn't understand that command."


def run_assistant():
    """
    The main loop: listen -> parse -> route -> speak. Repeats until exit.
    """
    speak("Assistant is ready. What would you like me to do?")

    while True:
        heard_text = listen()

        if heard_text is None:
            speak("I didn't catch that. Could you try again?")
            continue

        command_name, extra_data = parse_command(heard_text)
        response = route_command(command_name, extra_data)

        if response == "__EXIT__":
            speak("Goodbye!")
            break

        speak(response)


if __name__ == "__main__":
    run_assistant()