import json
from pathlib import Path
import re

# ===============================
# CONFIG
# ===============================
INPUT_GEOJSON = Path("data/raw/indonesia_provinces.geojson")
OUTPUT_GEOJSON = Path("data/raw/indonesia_provinces_std.geojson")


# ===============================
# HELPER FUNCTION
# ===============================
def standardize_province_name(name: str) -> str:
    """
    Convert province name to standard format:
    - UPPERCASE
    - Remove spaces, dots, special characters
    - Example:
      'NUSA TENGGARA BARAT' -> 'NUSATENGGARABARAT'
      'DI. ACEH'           -> 'DIACEH'
    """
    if not isinstance(name, str):
        return None

    name = name.upper()
    name = re.sub(r"[^A-Z]", "", name)
    return name


# ===============================
# MAIN PROCESS
# ===============================
def normalize_geojson():
    # Load GeoJSON
    with open(INPUT_GEOJSON, "r", encoding="utf-8") as f:
        geojson = json.load(f)

    features = geojson.get("features", [])
    print(f"📍 Loaded GeoJSON: {len(features)} features")

    missing = []

    for feature in features:
        props = feature.get("properties", {})

        raw_name = props.get("Propinsi")

        if raw_name is None:
            missing.append(feature.get("id"))
            props["Province_std"] = None
        else:
            props["Province_std"] = standardize_province_name(raw_name)

        feature["properties"] = props

    # Save new GeoJSON
    OUTPUT_GEOJSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_GEOJSON, "w", encoding="utf-8") as f:
        json.dump(
            geojson,
            f,
            ensure_ascii=False,
            indent=2 
        )

    print("✅ GeoJSON normalization completed")
    print(f"💾 Saved to: {OUTPUT_GEOJSON}")

    if missing:
        print(f"⚠️  Missing 'Propinsi' in {len(missing)} features: {missing}")
    else:
        print("✅ All features have 'Propinsi' field")


# ===============================
# RUN
# ===============================
if __name__ == "__main__":
    normalize_geojson()
