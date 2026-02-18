from pathlib import Path
import pandas as pd
import json


def make_equipments():
    xlsx_path = Path("equipment_data.xlsx")

    if not xlsx_path.exists():
        print("Файл equipment_data.xlsx не найден!")
        return

    df = pd.read_excel(xlsx_path, sheet_name="Equipment Data")

    # парсим координаты "[0, 0]" → [0.0, 0.0]
    def parse_coord(c):
        if pd.isna(c) or str(c).strip() == "":
            return [0, 0]
        s = str(c).strip()
        if s.startswith("[") and s.endswith("]"):
            s = s[1:-1].strip()
        try:
            parts = [float(x.strip()) for x in s.split(",")]
            return parts[:2] if len(parts) >= 2 else [0, 0]
        except:
            return [0, 0]

    if "coordinates" in df.columns:
        df["coordinates"] = df["coordinates"].apply(parse_coord)

    # перезаписываем id по порядку (как в substances)
    df["id"] = range(1, len(df) + 1)

    data = df.to_dict(orient="records")

    json_path = Path("equipments.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Создано: {json_path} ({len(data)} единиц оборудования)")


if __name__ == "__main__":
    make_equipments()