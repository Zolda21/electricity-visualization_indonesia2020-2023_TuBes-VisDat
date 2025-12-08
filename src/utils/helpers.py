# src/utils/helpers.py

import json
from pathlib import Path
from functools import lru_cache

# ---------------------------------------------------------------------
# Path Utilities
# ---------------------------------------------------------------------

def get_project_root() -> Path:
    """Mengembalikan path ke root project.
    
    Catatan: Path(__file__).resolve().parents[2] mengasumsikan file ini
    berada di src/utils/helpers.py.
    """
    return Path(__file__).resolve().parents[2]


def data_path(*parts) -> Path:
    """Shortcut menuju folder /data/..."""
    return get_project_root() / "data" / Path(*parts)


def notebook_path(*parts) -> Path:
    """Shortcut menuju folder /notebooks/..."""
    return get_project_root() / "notebooks" / Path(*parts)


def src_path(*parts) -> Path:
    """Shortcut menuju /src/..."""
    return get_project_root() / "src" / Path(*parts)


def assets_path(*parts) -> Path:
    """Shortcut menuju /streamlit_app/assets/... untuk GeoJSON, dsb."""
    return get_project_root() / "streamlit_app" / "assets" / Path(*parts)


# ---------------------------------------------------------------------
# File Utilities
# ---------------------------------------------------------------------

def ensure_file_exists(path: Path):
    """Raise error kalau file tidak ada."""
    if not path.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {path}")


def read_json(path: Path):
    """Read JSON sederhana."""
    ensure_file_exists(path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data):
    """Write JSON sederhana."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# ---------------------------------------------------------------------
# Caching
# ---------------------------------------------------------------------

@lru_cache(maxsize=16)
def cache_dataframe_loader(func_id: str, path: str):
    """
    Cache hasil loading dataframe berdasarkan string id + path.
    
    Catatan:
    - dataframe-nya harus dibungkus oleh fungsi pemanggil.
    - path dipaksa string supaya hashable.
    """
    # Mengembalikan tuple unik untuk caching key.
    return (func_id, Path(path).stat().st_mtime) # Menggunakan modified time untuk deteksi perubahan file


# ---------------------------------------------------------------------
# Logging ringan
# ---------------------------------------------------------------------

def log(msg: str):
    """Logging sederhana ke console."""
    print(f"[INFO] {msg}")


def warn(msg: str):
    """Warning sederhana."""
    print(f"[WARNING] {msg}")


def error(msg: str):
    """Error sederhana."""
    print(f"[ERROR] {msg}")