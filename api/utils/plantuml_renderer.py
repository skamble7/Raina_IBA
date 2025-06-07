import subprocess
import os
import uuid

PLANTUML_JAR_PATH = os.path.abspath("tools/plantuml-1.2025.3")  # Adjust if needed
OUTPUT_DIR = os.path.abspath("output/diagrams")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def render_plantuml_to_png(code: str, name_hint: str) -> str:
    temp_id = str(uuid.uuid4())
    filename = f"{name_hint}_{temp_id}.puml"
    puml_path = os.path.join(OUTPUT_DIR, filename)

    with open(puml_path, "w", encoding="utf-8") as f:
        f.write(code)

    try:
        subprocess.run(
            ["java", "-jar", PLANTUML_JAR_PATH, "-tpng", puml_path],
            check=True,
            cwd=OUTPUT_DIR
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"PlantUML failed: {e}")

    # PlantUML outputs a .png with the same basename
    png_path = os.path.splitext(puml_path)[0] + ".png"
    return png_path
