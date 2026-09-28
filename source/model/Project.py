from pathlib import Path
import sys

def get_project_path() -> Path:
    result = Path.cwd() 
    if sys.platform == "win32":
        result = result / 'PlamodelReleaseDate'
    return result
        
def get_cache_path() -> Path:
    return get_project_path() / 'cache'
