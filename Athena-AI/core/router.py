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