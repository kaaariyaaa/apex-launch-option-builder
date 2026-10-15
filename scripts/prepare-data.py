from pathlib import Path

root = Path(__file__).resolve().parents[1]
target = root / "public/data/registrations.json"
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text("[]\n", encoding="utf-8")
print(f"Prepared an empty option registry → {target.relative_to(root)}")
