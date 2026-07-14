from pathlib import Path

def get_project_path() -> Path:
    return Path.cwd() / 'PlamodelReleaseDate'

def get_cache_path() -> Path:
    return get_project_path() / 'cache'
