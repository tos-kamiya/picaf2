import importlib.metadata

# Version setup
__version__: str = "0.0.0-unknown"
if __package__:
    try:
        __version__ = importlib.metadata.version(__package__)
    except (importlib.metadata.PackageNotFoundError, ValueError):
        pass
