import importlib
import os

class PluginLoader:
    def __init__(self, plugin_dir="plugins"):
        self.plugin_dir = plugin_dir

    def load_plugins(self):
        plugins = {}
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith(".py"):
                module_name = filename[:-3]
                module = importlib.import_module(f"{self.plugin_dir}.{module_name}")
                plugin_class_name = f"{module_name.title().replace('_', '')}Plugin"
                plugin_class = getattr(module, plugin_class_name, None)
                if plugin_class:
                    plugins[module_name] = plugin_class()
        return plugins
