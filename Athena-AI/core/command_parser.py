def parse_command(text):
    """
    Takes raw text from speech-to-text and decides which action to trigger.
    Returns a tuple: (command_name, extra_data)
    command_name is a string the router uses to pick a handler.
    extra_data holds any extra info that handler might need (e.g. app name).
    Returns ("unknown", text) if nothing matches, so callers can decide
    what to do with unrecognized input instead of crashing.
    """
    if not text:
        return ("unknown", None)

    text = text.lower().strip()

    # --- Open app ---
    if "open" in text:
        # crude extraction: whatever comes after "open "
        app_name = text.split("open", 1)[1].strip()
        return ("open_app", app_name)

    # --- System status ---
    if "cpu" in text or "battery" in text or "system status" in text or "ram" in text:
        return ("system_status", None)

    # --- Web search ---
    if "search" in text or "google" in text:
        # crude extraction: whatever comes after "search" or "google"
        for keyword in ["search for", "search", "google"]:
            if keyword in text:
                query = text.split(keyword, 1)[1].strip()
                return ("web_search", query)

    # --- Calculator ---
    if "calculate" in text or "plus" in text or "minus" in text or "times" in text:
        return ("calculate", text)

    # --- Weather ---
    if "weather" in text:
        # crude extraction: whatever comes after "weather in/for/of", or bare "weather"
        for keyword in ["weather in", "weather for", "weather of", "weather"]:
            if keyword in text:
                city = text.split(keyword, 1)[1].strip()
                # strip any leftover leading preposition the keyword match missed
                for leftover in ["in ", "for ", "of "]:
                    if city.startswith(leftover):
                        city = city[len(leftover):].strip()
                return ("weather", city)

    # --- Exit ---
    if "exit" in text or "quit" in text or "goodbye" in text:
        return ("exit", None)

    # --- Nothing matched ---
    return ("unknown", text)


if __name__ == "__main__":
    # Quick manual test — no mic needed, just typed strings
    test_inputs = [
        "open chrome",
        "what's my cpu usage",
        "search for python tutorials",
        "google best pizza recipe",
        "calculate 5 plus 3",
        "weather of London",
        "weather in Mumbai",
        "goodbye",
        "asdkjfh nonsense",
    ]
    for t in test_inputs:
        print(f"Input: {t!r} -> {parse_command(t)}")