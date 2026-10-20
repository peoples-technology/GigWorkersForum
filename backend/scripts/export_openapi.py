import json
import sys
from pathlib import Path

# Add backend to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app


def export_schema():
    schema = app.openapi_schema.to_schema()
    out_path = Path(__file__).parent.parent.parent / "openapi.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)
    print(f"OpenAPI schema successfully written to {out_path}")

if __name__ == "__main__":
    export_schema()
