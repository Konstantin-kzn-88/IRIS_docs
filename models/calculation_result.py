# models/calculation_result.py
from dataclasses import dataclass
from typing import Optional, Dict, Any
from .equipment import EquipmentType
from .substance import SubstanceType


@dataclass
class CalculationResult:
    """Доменная модель результатов расчетов"""
    id: Optional[int]
    project_code: str
    scenario_number: int
    equipment_name: str
    equipment_type: EquipmentType
    substance_type: SubstanceType

    # Тепловое излучение (кВт/м2)
    q_10_5: Optional[float]  # 10.5 кВт/м2
    q_7_0: Optional[float]  # 7.0 кВт/м2
    q_4_2: Optional[float]  # 4.2 кВт/м2
    q_1_4: Optional[float]  # 1.4 кВт/м2

    # Избыточное давление (кПа)
    p_53: Optional[float]  # 53 кПа
    p_28: Optional[float]  # 28 кПа
    p_12: Optional[float]  # 12 кПа
    p_5: Optional[float]  # 5 кПа
    p_2: Optional[float]  # 2 кПа

    # Параметры вспышки и пожара
    l_f: Optional[float]  # Длина факела
    d_f: Optional[float]  # Диаметр факела
    r_nkpr: Optional[float]  # Радиус НКПР
    r_flash: Optional[float]  # Радиус вспышки
    l_pt: Optional[float]  # Глубина токсичного поражения
    p_pt: Optional[float]  # Ширина токсичного поражения

    # Тротиловый эквивалент (кг)
    q_600: Optional[float]  # 600 кПа
    q_320: Optional[float]  # 320 кПа
    q_220: Optional[float]  # 220 кПа
    q_120: Optional[float]  # 120 кПа

    # Площадь и последствия
    s_spill: Optional[float]  # Площадь пролива
    casualties: int  # Количество погибших
    injured: int  # Количество пострадавших

    # Ущерб (млн.руб)
    direct_losses: float  # Прямые потери
    liquidation_costs: float  # Затраты на ликвидацию
    social_losses: float  # Социальные потери
    indirect_damage: float  # Косвенный ущерб
    environmental_damage: float  # Экологический ущерб
    total_damage: float  # Суммарный ущерб

    # Риски
    casualty_risk: float  # Количественный риск погибших (чел/год)
    injury_risk: float  # Количественный риск пострадавших (чел/год)
    expected_damage: float  # Математическое ожидание ущерба (млн.руб/год)

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для БД"""
        return {
            'id': self.id,
            'project_code': self.project_code,
            'scenario_number': self.scenario_number,
            'equipment_name': self.equipment_name,
            'equipment_type': self.equipment_type.value,
            'substance_type': int(self.substance_type),
            'q_10_5': self.q_10_5,
            'q_7_0': self.q_7_0,
            'q_4_2': self.q_4_2,
            'q_1_4': self.q_1_4,
            'p_53': self.p_53,
            'p_28': self.p_28,
            'p_12': self.p_12,
            'p_5': self.p_5,
            'p_2': self.p_2,
            'l_f': self.l_f,
            'd_f': self.d_f,
            'r_nkpr': self.r_nkpr,
            'r_flash': self.r_flash,
            'l_pt': self.l_pt,
            'p_pt': self.p_pt,
            'q_600': self.q_600,
            'q_320': self.q_320,
            'q_220': self.q_220,
            'q_120': self.q_120,
            's_spill': self.s_spill,
            'casualties': self.casualties,
            'injured': self.injured,
            'direct_losses': self.direct_losses,
            'liquidation_costs': self.liquidation_costs,
            'social_losses': self.social_losses,
            'indirect_damage': self.indirect_damage,
            'environmental_damage': self.environmental_damage,
            'total_damage': self.total_damage,
            'casualty_risk': self.casualty_risk,
            'injury_risk': self.injury_risk,
            'expected_damage': self.expected_damage
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CalculationResult':
        """Создание объекта из словаря"""
        return cls(
            id=data.get('id'),
            project_code=data['project_code'],
            scenario_number=data['scenario_number'],
            equipment_name=data['equipment_name'],
            equipment_type=EquipmentType(data['equipment_type']),
            substance_type=SubstanceType(data['substance_type']),
            q_10_5=data.get('q_10_5'),
            q_7_0=data.get('q_7_0'),
            q_4_2=data.get('q_4_2'),
            q_1_4=data.get('q_1_4'),
            p_53=data.get('p_53'),
            p_28=data.get('p_28'),
            p_12=data.get('p_12'),
            p_5=data.get('p_5'),
            p_2=data.get('p_2'),
            l_f=data.get('l_f'),
            d_f=data.get('d_f'),
            r_nkpr=data.get('r_nkpr'),
            r_flash=data.get('r_flash'),
            l_pt=data.get('l_pt'),
            p_pt=data.get('p_pt'),
            q_600=data.get('q_600'),
            q_320=data.get('q_320'),
            q_220=data.get('q_220'),
            q_120=data.get('q_120'),
            s_spill=data.get('s_spill'),
            casualties=data['casualties'],
            injured=data['injured'],
            direct_losses=data['direct_losses'],
            liquidation_costs=data['liquidation_costs'],
            social_losses=data['social_losses'],
            indirect_damage=data['indirect_damage'],
            environmental_damage=data['environmental_damage'],
            total_damage=data['total_damage'],
            casualty_risk=data['casualty_risk'],
            injury_risk=data['injury_risk'],
            expected_damage=data['expected_damage']
        )

    def to_display_dict(self) -> Dict[str, str]:
        """Получение словаря для отображения в UI"""
        return {
            'Номер сценария': str(self.scenario_number),
            'Наименование оборудования': self.equipment_name,
            'Тип оборудования': EquipmentType.get_display_name(self.equipment_type),
            'Тип вещества': SubstanceType.get_display_name(self.substance_type),

            'Тепловое излучение 10.5 кВт/м2': f"{self.q_10_5:.2f}" if self.q_10_5 is not None else "-",
            'Тепловое излучение 7.0 кВт/м2': f"{self.q_7_0:.2f}" if self.q_7_0 is not None else "-",
            'Тепловое излучение 4.2 кВт/м2': f"{self.q_4_2:.2f}" if self.q_4_2 is not None else "-",
            'Тепловое излучение 1.4 кВт/м2': f"{self.q_1_4:.2f}" if self.q_1_4 is not None else "-",

            'Избыточное давление 53 кПа': f"{self.p_53:.2f}" if self.p_53 is not None else "-",
            'Избыточное давление 28 кПа': f"{self.p_28:.2f}" if self.p_28 is not None else "-",
            'Избыточное давление 12 кПа': f"{self.p_12:.2f}" if self.p_12 is not None else "-",
            'Избыточное давление 5 кПа': f"{self.p_5:.2f}" if self.p_5 is not None else "-",
            'Избыточное давление 2 кПа': f"{self.p_2:.2f}" if self.p_2 is not None else "-",

            'Длина факела': f"{self.l_f:.2f}" if self.l_f is not None else "-",
            'Диаметр факела': f"{self.d_f:.2f}" if self.d_f is not None else "-",
            'Радиус НКПР': f"{self.r_nkpr:.2f}" if self.r_nkpr is not None else "-",
            'Радиус вспышки': f"{self.r_flash:.2f}" if self.r_flash is not None else "-",
            'Глубина поражения': f"{self.l_pt:.2f}" if self.l_pt is not None else "-",
            'Ширина поражения': f"{self.p_pt:.2f}" if self.p_pt is not None else "-",

            'ТНТ 600 кПа': f"{self.q_600:.2f}" if self.q_600 is not None else "-",
            'ТНТ 320 кПа': f"{self.q_320:.2f}" if self.q_320 is not None else "-",
            'ТНТ 220 кПа': f"{self.q_220:.2f}" if self.q_220 is not None else "-",
            'ТНТ 120 кПа': f"{self.q_120:.2f}" if self.q_120 is not None else "-",

            'Площадь пролива': f"{self.s_spill:.2f}" if self.s_spill is not None else "-",
            'Количество погибших': str(self.casualties),
            'Количество пострадавших': str(self.injured),

            'Прямые потери': f"{self.direct_losses:.2f}",
            'Затраты на ликвидацию': f"{self.liquidation_costs:.2f}",
            'Социальные потери': f"{self.social_losses:.2f}",
            'Косвенный ущерб': f"{self.indirect_damage:.2f}",
            'Экологический ущерб': f"{self.environmental_damage:.2f}",
            'Суммарный ущерб': f"{self.total_damage:.2f}",

            'Риск гибели': f"{self.casualty_risk:.2e}",
            'Риск травмирования': f"{self.injury_risk:.2e}",
            'Ожидаемый ущерб': f"{self.expected_damage:.2f}"
        }

    def validate(self) -> None:
        """Валидация объекта"""
        if not self.project_code:
            raise ValueError("Код проекта не может быть пустым")

        if self.scenario_number <= 0:
            raise ValueError("Номер сценария должен быть положительным")

        if not self.equipment_name:
            raise ValueError("Наименование оборудования не может быть пустым")

        if self.casualties < 0:
            raise ValueError("Количество погибших не может быть отрицательным")

        if self.injured < 0:
            raise ValueError("Количество пострадавших не может быть отрицательным")

        if any(value < 0 for value in [
            self.direct_losses, self.liquidation_costs,
            self.social_losses, self.indirect_damage,
            self.environmental_damage, self.total_damage
        ]):
            raise ValueError("Значения ущерба не могут быть отрицательными")

        if any(value < 0 for value in [
            self.casualty_risk, self.injury_risk,
            self.expected_damage
        ]):
            raise ValueError("Значения риска не могут быть отрицательными")

    def __post_init__(self):
        """Валидация после инициализации"""
        self.validate()