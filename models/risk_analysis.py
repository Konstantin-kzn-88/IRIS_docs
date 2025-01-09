# models/risk_analysis.py
from dataclasses import dataclass
from typing import List
from models.calculation_result import CalculationResult
from models.dangerous_object import DangerousObject
import math


@dataclass
class ComponentRiskAnalysis:
    """Анализ риска для компонента предприятия"""
    component_name: str  # Наименование компонента
    max_damage: float  # Максимальный ущерб, млн.руб
    max_eco_damage: float  # Максимальный экологический ущерб, млн.руб
    max_casualties: int  # Максимальное количество погибших
    max_injured: int  # Максимальное количество пострадавших
    collective_death_risk: float  # Коллективный риск гибели, чел/год
    collective_injury_risk: float  # Коллективный риск ранения, чел/год
    individual_death_risk: float  # Индивидуальный риск гибели, чел/год
    individual_injury_risk: float  # Индивидуальный риск ранения, чел/год
    risk_level_ppm: float  # Уровень риска, ppm
    risk_level_dbr: float  # Уровень риска, дБR
    max_death_frequency: float  # Частота аварии с гибелью не менее одного человека, 1/год

    @classmethod
    def calculate_for_component(cls, component_name: str,
                                results: List[CalculationResult],
                                dangerous_object: DangerousObject) -> 'ComponentRiskAnalysis':
        """
        Расчет анализа риска для компонента предприятия

        Args:
            component_name: Наименование компонента
            results: Список результатов расчета для данного компонента
            dangerous_object: Опасный производственный объект

        Returns:
            ComponentRiskAnalysis: Результат анализа риска
        """
        # Фильтруем результаты по компоненту
        component_results = [r for r in results if hasattr(r, 'component_enterprise')
                             and r.component_enterprise == component_name]

        if not component_results:
            return None

        # Расчет максимальных значений
        max_damage = max(r.total_damage for r in component_results)
        max_eco_damage = max(r.environmental_damage for r in component_results)
        max_casualties = max(r.casualties for r in component_results)
        max_injured = max(r.injured for r in component_results)

        # Расчет коллективных рисков
        collective_death_risk = sum(r.casualty_risk for r in component_results)
        collective_injury_risk = sum(r.injury_risk for r in component_results)

        # Расчет индивидуальных рисков
        employee_count = dangerous_object.employee_count if dangerous_object else 100
        individual_death_risk = collective_death_risk / employee_count
        individual_injury_risk = collective_injury_risk / employee_count

        # Расчет уровней риска
        risk_level_ppm = individual_death_risk * pow(10, 6)
        try:
            risk_level_dbr = 10 * math.log10(risk_level_ppm / 195)
        except (ValueError, ZeroDivisionError):
            risk_level_dbr = float('-inf')

        # Расчет максимальной частоты
        death_scenarios = [r for r in component_results if r.casualties >= 1]
        max_death_frequency = max((r.probability for r in death_scenarios), default=0)

        return cls(
            component_name=component_name,
            max_damage=max_damage,
            max_eco_damage=max_eco_damage,
            max_casualties=max_casualties,
            max_injured=max_injured,
            collective_death_risk=collective_death_risk,
            collective_injury_risk=collective_injury_risk,
            individual_death_risk=individual_death_risk,
            individual_injury_risk=individual_injury_risk,
            risk_level_ppm=risk_level_ppm,
            risk_level_dbr=risk_level_dbr,
            max_death_frequency=max_death_frequency
        )