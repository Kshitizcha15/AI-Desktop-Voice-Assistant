import sys
import os

# Add the project root to the path so we can import from speech/ and core/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from speech.text_to_speech import speak
from speech.speech_to_text import listen
from core.command_parser import parse_command
from core.plugin_loader import load_plugins
from ai.llm import ask_llm
from core.memory import ConversationMemory
from services.weather import get_weather
from services.ollama_manager import ensure_ollama_running

import subprocess
import psutil
import webbrowser

memory = ConversationMemory()

plugin_commands = {}
load_plugins(plugin_commands)


def handle_open_app(app_name):
    """
    Opens a macOS application by name using the 'open' command.
    Works for anything in /Applications — Chrome, Calculator, VS Code, etc.
    """
    try:
        subprocess.run(["open", "-a", app_name], check=True)
        return f"Opening {app_name}."
    except subprocess.CalledProcessError:
        return f"I couldn't find an app called {app_name}. Please check the name and try again."


def handle_system_status():
    """
    Reads real CPU, RAM, and battery info using psutil and
    formats it into a sentence natural to speak out loud.
    """
    cpu_percent = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    ram_percent = ram.percent

    response = f"CPU usage is at {cpu_percent} percent, and RAM usage is at {ram_percent} percent."

    battery = psutil.sensors_battery()
    if battery is not None:
        battery_percent = round(battery.percent)
        charging_status = "charging" if battery.power_plugged else "not charging"
        response += f" Battery is at {battery_percent} percent and {charging_status}."

    return response


def handle_web_search(query):
    """
    Opens the default web browser with a Google search for the given query.
    """
    if not query:
        return "I didn't catch what you wanted to search for."

    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.open(search_url)
    return f"Searching the web for {query}."


def handle_weather(city):
    return get_weather(city)


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
    elif command_name == "weather":
        return handle_weather(extra_data)
    elif command_name == "exit":
        return "__EXIT__"  # special signal, handled in the main loop below
    elif command_name in plugin_commands:
        return plugin_commands[command_name](extra_data)
    else:
        # "unknown" commands fall through to the LLM —
        # extra_data holds the original spoken text in this case
        reply = ask_llm(extra_data, memory.get())
        memory.add("user", extra_data)
        memory.add("assistant", reply)
        return reply


WAKE_PHRASE = "hello friday"


def _stop_requested(stop_event):
    return stop_event is not None and stop_event.is_set()


def _publish(message_callback, speaker, message):
    if message_callback:
        message_callback(speaker, str(message))


def _reply_to_command(heard_text, message_callback=None, speak_response=True):
    """Route one spoken command and speak its response."""
    _publish(message_callback, "You", heard_text)
    command_name, extra_data = parse_command(heard_text)
    response = route_command(command_name, extra_data)

    if response == "__EXIT__":
        response = "Going back to sleep. Say hello Friday when you need me."
        _publish(message_callback, "Friday", response)
        if speak_response:
            speak(response)
        return False

    _publish(message_callback, "Friday", response)
    if speak_response:
        speak(response)
    return True


def process_command(command, status_callback=None, message_callback=None):
    """Run one typed command from the desktop interface."""
    ensure_ollama_running(status_callback=status_callback)
    # Typed requests stay in the visual chat interface. Voice mode speaks replies.
    return _reply_to_command(command, message_callback=message_callback, speak_response=False)


def run_assistant(stop_event=None, status_callback=None, message_callback=None):
    """
    Waits for the wake phrase, then handles commands until asked to sleep.
    It keeps running until the desktop app's Stop button is pressed.
    """
    ensure_ollama_running(status_callback=status_callback)
    speak("Friday is ready. Say hello Friday to wake me.")

    while not _stop_requested(stop_event):
        # Idle mode: ignore everything except the wake phrase.
        heard_text = listen(timeout=3, phrase_time_limit=5, calibrate=False)

        if heard_text is None:
            continue

        normalized_text = heard_text.lower().strip()
        if WAKE_PHRASE not in normalized_text:
            continue

        # A command can follow the wake phrase, e.g. "Hello Friday, weather in Mumbai".
        command_after_wake = normalized_text.split(WAKE_PHRASE, 1)[1].strip(" ,.!?")
        if command_after_wake:
            speak("Yes?")
            if not _reply_to_command(command_after_wake, message_callback):
                continue
        else:
            speak("Yes? How can I help?")

        # Active mode: answer commands until the user asks Friday to sleep.
        while not _stop_requested(stop_event):
            command_text = listen(timeout=5, phrase_time_limit=12, calibrate=False)
            if command_text is None:
                continue

            if not _reply_to_command(command_text, message_callback):
                break

    speak("Friday has stopped.")


if __name__ == "__main__":
    run_assistant()
