# models/substance/substance_model.py

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


class Substance:
    def __init__(
        self,
        id=None,
        name="",
        kind=0,
        formula="",
        composition=None,
        physical=None,
        explosion=None,
        toxicity=None,
        reactivity="",
        odor="",
        corrosiveness="",
        precautions="",
        impact="",
        protection="",
        neutralization_methods="",
        first_aid="",
    ):
        # -------- Общие поля --------
        self.id = id
        self.name = name
        self.kind = kind
        self.formula = formula

        # -------- Состав --------
        self.composition = composition if composition is not None else {
            "components": [],
            "notes": ""
        }

        # -------- Физические свойства --------
        self.physical = physical if physical is not None else {
            "molar_mass_kg_per_mol": None,
            "density_liquid_kg_per_m3": None,
            "density_gas_kg_per_m3": None,
            "evaporation_heat_J_per_kg": None,
            "boiling_point_C": None,
        }

        # -------- Взрывоопасность --------
        self.explosion = explosion if explosion is not None else {
            "flash_point_C": None,
            "lel_percent": None,
            "autoignition_temp_C": None,
            "energy_reserve_factor": None,         # 1 или 2
            "expansion_degree": None,              # 4 или 7
            "heat_of_combustion_kJ_per_kg": None,
            "burning_rate_kg_per_s_m2": None,
        }

        # -------- Токсическая опасность --------
        self.toxicity = toxicity if toxicity is not None else {
            "hazard_class": None,
            "pdk_mg_per_m3": None,
            "lethal_tox_dose_mg_min_per_L": None,
            "threshold_tox_dose_mg_min_per_L": None,
        }

        # -------- Прочие свойства/описания --------
        self.reactivity = reactivity
        self.odor = odor
        self.corrosiveness = corrosiveness
        self.precautions = precautions
        self.impact = impact
        self.protection = protection
        self.neutralization_methods = neutralization_methods
        self.first_aid = first_aid
