try:
    from importlib.metadata import version

    __version__ = version("learn-lock")
except Exception:
    __version__ = "0.1.6"
