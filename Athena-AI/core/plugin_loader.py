import os
import importlib.util

PLUGIN_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "plugins")

def load_plugins(router_registry):
    """
    Scans the plugins/ folder, imports each .py file, and calls its
    register(router_registry) function if one exists.
    router_registry is a dict mapping command_name -> handler_function,
    which plugins add their own entries into.
    """
    if not os.path.isdir(PLUGIN_DIR):
        print(f"[PluginLoader] No plugins folder found at {PLUGIN_DIR}")
        return

    for filename in os.listdir(PLUGIN_DIR):
        if not filename.endswith(".py") or filename.startswith("_"):
            continue

        plugin_path = os.path.join(PLUGIN_DIR, filename)
        module_name = filename[:-3]  # strip ".py"

        try:
            spec = importlib.util.spec_from_file_location(module_name, plugin_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if hasattr(module, "register"):
                module.register(router_registry)
                print(f"[PluginLoader] Loaded plugin: {module_name}")
            else:
                print(f"[PluginLoader] Skipped {module_name} (no register() function)")
        except Exception as e:
            print(f"[PluginLoader] Failed to load {module_name}: {e}")