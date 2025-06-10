import importlib, sys

for mod in ("cli", "workflow", "orchestrator"):
    module = importlib.import_module(mod)
    sys.modules[__name__ + f".{mod}"] = module
    setattr(sys.modules[__name__], mod, module)
