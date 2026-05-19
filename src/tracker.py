import json
from datetime import datetime
from pathlib import Path


TRACKING_PATH = Path("logs/pipeline_tracking.json")


def init_tracking():
    TRACKING_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not TRACKING_PATH.exists() or TRACKING_PATH.stat().st_size == 0:
        data = {
            "project": "Proyecto Big Data Inmobiliario Premium Europeo",
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "pipeline_runs": []
        }

        with open(TRACKING_PATH, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)


def log_step(phase, source, input_rows, output_rows, discarded_rows, reason, details=None):
    init_tracking()

    with open(TRACKING_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    step = {
        "timestamp": datetime.now().isoformat(),
        "phase": phase,
        "source": source,
        "input_rows": int(input_rows) if input_rows is not None else None,
        "output_rows": int(output_rows) if output_rows is not None else None,
        "discarded_rows": int(discarded_rows) if discarded_rows is not None else None,
        "reason": reason,
        "details": details or {}
    }

    data["pipeline_runs"].append(step)

    with open(TRACKING_PATH, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print(f"[TRACKING] {phase} - {source}: {input_rows} -> {output_rows}")
