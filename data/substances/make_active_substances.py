from pathlib import Path
import json

ACTIVE_DIR = Path("active")
OUTPUT_JSON = Path("substances.json")
INFO_TXT = Path("info.txt")


def make_active_substances():
    files = sorted(ACTIVE_DIR.glob("*.json"))

    data = []
    lines = ["id\tname\tkind"]

    for i, path in enumerate(files, 1):
        with open(path, encoding="utf-8") as f:
            obj = json.load(f)

        obj["id"] = i
        data.append(obj)

        name = obj.get("name", "—")
        kind = obj.get("kind", "—")
        lines.append(f"{i}\t{name}\t{kind}")

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    with open(INFO_TXT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Создано: {OUTPUT_JSON} ({len(data)} веществ)")
    print(f"Создано: {INFO_TXT}")


if __name__ == "__main__":
    make_active_substances()