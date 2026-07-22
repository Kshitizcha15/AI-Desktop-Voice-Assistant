import re


def _calculate(expression):
    """
    Safely evaluates a simple math expression like "5 plus 3" or "10 * 2".
    Only allows numbers and basic operators — never uses raw eval() on
    arbitrary text, since that's a security risk.
    """
    expression = expression.lower()
    expression = expression.replace("calculate", "")  # strip the trigger word
    expression = expression.replace("plus", "+").replace("minus", "-")
    expression = expression.replace("times", "*").replace("divided by", "/")

    if not re.match(r'^[\d\s\+\-\*/\.\(\)]+$', expression):
        return None

    try:
        return eval(expression, {"__builtins__": {}}, {})
    except Exception:
        return None


def handle_calculate(query):
    result = _calculate(query)
    if result is None:
        return "I couldn't calculate that. Try something like '5 plus 3'."
    return f"The answer is {result}."


def register(router_registry):
    """
    Called by the plugin loader. Registers this plugin's command
    into the shared router registry dict.
    """
    router_registry["calculate"] = handle_calculate