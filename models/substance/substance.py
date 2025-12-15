"""
substance.py

Базовый класс "Вещество" для программы анализа промышленного риска.
Код написан максимально просто (без dataclass), с комментариями и примером запуска.

Идея структуры:
- Простые поля (name, formula, odor...) — строки/числа.
- Сложные разделы (physical, explosion, toxicity) — словари фиксированной структуры.
- Для будущей SQLite: можно хранить JSON этих словарей или разносить по таблицам.
"""

from typing import Any, Dict, Optional


class Substance:
    """
    Substance (Вещество) — базовая структура данных для анализа.

    Поля сгруппированы по смыслу:
    - Общие
    - Состав
    - Физические свойства
    - Взрывоопасность
    - Токсическая опасность
    - И прочие описательные разделы
    """

    # Профессиональные названия категорий (вместо "вид 0/1/2...")
    # Можно расширять/переименовывать без изменения остального кода.
    KIND_LABELS = {
        0: "Легковоспламеняющаяся жидкость (ЛВЖ)",
        1: "ЛВЖ (токсичная)",
        2: "Горючий газ",
        3: "Горючий газ (токсичный)",
        4: "Сжиженный горючий газ",
        5: "Сжиженный горючий газ (токсичный)",
        6: "Токсичная жидкость (практически неиспаряемая)",
        7: "Токсичный газ",
        8: "Сжиженный токсичный газ",
    }

    def __init__(
        self,
        name: str,
        kind: int,
        formula: str = "",
        composition: Optional[Dict[str, Any]] = None,
        physical: Optional[Dict[str, Any]] = None,
        explosion: Optional[Dict[str, Any]] = None,
        toxicity: Optional[Dict[str, Any]] = None,
        reactivity: str = "",
        odor: str = "",
        corrosiveness: str = "",
        precautions: str = "",
        impact: str = "",
        protection: str = "",
        neutralization_methods: str = "",
        first_aid: str = "",
        id: Optional[int] = None,

    ):
        # -------- Общие поля --------
        self.id = id
        self.name = name            # Наименование вещества (строка)
        self.kind = kind            # Вид (целое число, см. KIND_LABELS)
        self.formula = formula      # Химическая формула (строка)

        # -------- Состав --------
        # composition — словарь состава, например:
        # {"components": [{"name": "метанол", "mass_fraction": 0.7}, ...], "notes": "..."}
        self.composition = composition if composition is not None else {
            "components": [],  # список компонентов
            "notes": ""        # примечания
        }

        # -------- Физические свойства --------
        # Единицы указаны в ключах/значениях комментариями.
        self.physical = physical if physical is not None else {
            "molar_mass_kg_per_mol": None,          # молекулярная масса [кг/моль]
            "density_liquid_kg_per_m3": None,       # плотность жидкой фазы [кг/м3]
            "density_gas_kg_per_m3": None,          # плотность газовой фазы [кг/м3]
            "evaporation_heat_J_per_kg": None,      # удельная теплота испарения [Дж/кг]
            "boiling_point_C": None,                # температура кипения [°C]
        }

        # -------- Взрывоопасность --------
        # Важно: некоторые поля принимают ограниченные значения.
        self.explosion = explosion if explosion is not None else {
            "flash_point_C": None,                  # температура вспышки [°C]
            "lel_percent": None,                    # нижний концентрационный предел [об.%] (если у вас так принято)
            "autoignition_temp_C": None,            # температура самовоспламенения [°C]
            "energy_reserve_factor": None,          # коэффициент энергозапаса: 1 или 2 (лёгкий/тяжёлый газ)
            "expansion_degree": None,               # степень расширения продуктов сгорания: 4 или 7 (пары/газы)
            "heat_of_combustion_kJ_per_kg": None,   # теплота сгорания [кДж/кг]
            "burning_rate_kg_per_s_m2": None,       # удельная скорость выгорания [кг/(с*м2)]
        }

        # -------- Токсическая опасность --------
        self.toxicity = toxicity if toxicity is not None else {
            "hazard_class": None,                   # класс опасности (например 1..4)
            "pdk_mg_per_m3": None,                  # ПДК [мг/м3]
            "lethal_tox_dose_mg_min_per_L": None,    # летальная токсодоза [мг*мин/л]
            "threshold_tox_dose_mg_min_per_L": None, # пороговая токсодоза [мг*мин/л]
        }

        # -------- Прочие свойства/описания --------
        self.reactivity = reactivity                    # реакционная способность (текст)
        self.odor = odor                                # запах (текст)
        self.corrosiveness = corrosiveness              # коррозионная активность (текст)
        self.precautions = precautions                  # меры предосторожности (текст)
        self.impact = impact                            # воздействие на людей/среду (текст)
        self.protection = protection                    # средства защиты (текст)
        self.neutralization_methods = neutralization_methods  # перевод в безвредное состояние (текст)
        self.first_aid = first_aid                      # первая помощь (текст)

        # Минимальная валидация, чтобы не хранить заведомо неправильные значения
        self._validate()

    def _validate(self) -> None:
        """Простая проверка ключевых ограничений (без сложной логики)."""

        # Проверяем, что вид известен (если надо — можно разрешить неизвестные)
        if self.kind not in self.KIND_LABELS:
            raise ValueError(f"Неизвестный kind={self.kind}. Допустимые: {list(self.KIND_LABELS.keys())}")

        # Проверяем допустимые значения некоторых полей взрывоопасности, если они заданы
        erf = self.explosion.get("energy_reserve_factor")
        if erf is not None and erf not in (1, 2):
            raise ValueError("energy_reserve_factor должен быть 1 или 2 (если задан).")

        exp_deg = self.explosion.get("expansion_degree")
        if exp_deg is not None and exp_deg not in (4, 7):
            raise ValueError("expansion_degree должен быть 4 или 7 (если задан).")

    def kind_name(self) -> str:
        """Человекочитаемое название вида вещества."""
        return self.KIND_LABELS.get(self.kind, f"Неизвестный вид ({self.kind})")

    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразовать объект в словарь (удобно для JSON/SQLite).
        """
        return {
            "id": self.id,
            "name": self.name,
            "kind": self.kind,
            "formula": self.formula,
            "composition": self.composition,
            "physical": self.physical,
            "explosion": self.explosion,
            "toxicity": self.toxicity,
            "reactivity": self.reactivity,
            "odor": self.odor,
            "corrosiveness": self.corrosiveness,
            "precautions": self.precautions,
            "impact": self.impact,
            "protection": self.protection,
            "neutralization_methods": self.neutralization_methods,
            "first_aid": self.first_aid,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Substance":
        """
        Создать объект Substance из словаря (например, после чтения из SQLite/JSON).
        """
        return Substance(
            id=data.get("id"),
            name=data.get("name", ""),
            kind=data.get("kind", 0),
            formula=data.get("formula", ""),
            composition=data.get("composition"),
            physical=data.get("physical"),
            explosion=data.get("explosion"),
            toxicity=data.get("toxicity"),
            reactivity=data.get("reactivity", ""),
            odor=data.get("odor", ""),
            corrosiveness=data.get("corrosiveness", ""),
            precautions=data.get("precautions", ""),
            impact=data.get("impact", ""),
            protection=data.get("protection", ""),
            neutralization_methods=data.get("neutralization_methods", ""),
            first_aid=data.get("first_aid", ""),
        )

    def __str__(self) -> str:
        """Короткое представление для печати."""
        return f"Substance(name='{self.name}', kind={self.kind} -> {self.kind_name()}, formula='{self.formula}')"


def main() -> None:
    """
    Пример запуска модуля.
    Здесь создаём вещество, заполняем некоторые свойства и печатаем.
    """

    # Пример: бензин (условно)
    s = Substance(
        name="Бензин (условно)",
        kind=0,  # ЛВЖ
        formula="Смешанная (углеводороды)",
        odor="Характерный бензиновый запах",
        precautions="Исключить источники зажигания; обеспечить вентиляцию; заземление при перекачке.",
        first_aid="Вывести на свежий воздух; при попадании на кожу — промыть водой с мылом; при симптомах — медпомощь."
    )

    # Заполняем физические свойства (примерные/учебные значения)
    s.physical["density_liquid_kg_per_m3"] = 740.0        # [кг/м3]
    s.physical["boiling_point_C"] = 35.0                 # [°C] (для фракций может быть диапазон)
    s.physical["evaporation_heat_J_per_kg"] = 3.5e5      # [Дж/кг] условно

    # Заполняем взрывоопасность (пример)
    s.explosion["flash_point_C"] = -40.0                 # [°C]
    s.explosion["lel_percent"] = 1.4                     # [об.%]
    s.explosion["autoignition_temp_C"] = 280.0           # [°C]
    s.explosion["expansion_degree"] = 4                  # пары
    s.explosion["heat_of_combustion_kJ_per_kg"] = 44000  # [кДж/кг]

    # Заполняем токсичность (пример)
    s.toxicity["hazard_class"] = 3
    s.toxicity["pdk_mg_per_m3"] = 300.0

    # Печать
    print(s)
    print("\n--- В виде словаря (для SQLite/JSON) ---")
    data = s.to_dict()
    for k, v in data.items():
        print(f"{k}: {v}")

    # Демонстрация восстановления из словаря
    print("\n--- Восстановление из словаря ---")
    s2 = Substance.from_dict(data)
    print(s2)


if __name__ == "__main__":
    main()
