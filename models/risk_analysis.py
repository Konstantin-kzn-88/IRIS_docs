# models/risk_analysis.py
from dataclasses import dataclass
from typing import List, Optional
import math
from models.calculation_result import CalculationResult
from models.dangerous_object import DangerousObject


@dataclass
class ComponentRiskAnalysis:
    """Класс для анализа рисков по компонентам"""
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
    max_death_frequency: float  # Частота аварии с гибелью, 1/год

    @classmethod
    def calculate_for_component(cls, component: str,
                                results: List[CalculationResult],
                                dangerous_object: Optional[DangerousObject]) -> Optional['ComponentRiskAnalysis']:
        """
        Расчет анализа риска для компонента

        Args:
            component: наименование компонента
            results: список результатов расчета
            dangerous_object: опасный производственный объект

        Returns:
            ComponentRiskAnalysis: результаты анализа для компонента
        """
        # Фильтруем результаты только для данного компонента
        component_results = []
        for r in results:
            if hasattr(r, 'component_enterprise') and r.component_enterprise == component:
                # Если есть компонент предприятия и он совпадает
                component_results.append(r)
            elif hasattr(r, 'equipment_name') and r.equipment_name:
                # Извлекаем компонент из текста в скобках
                import re
                match = re.search(r'\((.*?)\)', r.equipment_name)
                if match and match.group(1) == component:
                    component_results.append(r)

        if not component_results:
            return None

        # Вычисляем максимальные значения
        max_damage = max(r.total_damage for r in component_results)
        max_eco_damage = max(r.environmental_damage for r in component_results)
        max_casualties = max(r.casualties for r in component_results)
        max_injured = max(r.injured for r in component_results)

        # Рассчитываем коллективные риски (сумма по всем сценариям)
        collective_death_risk = sum(r.casualty_risk for r in component_results)
        collective_injury_risk = sum(r.injury_risk for r in component_results)

        # Получаем количество сотрудников из ОПО
        employee_count = dangerous_object.employee_count if dangerous_object else 1

        # Рассчитываем индивидуальные риски
        individual_death_risk = collective_death_risk / employee_count
        individual_injury_risk = collective_injury_risk / employee_count

        # Рассчитываем уровни риска
        risk_level_ppm = individual_death_risk * pow(10, 6)  # Перевод в ppm

        # Расчет уровня риска в дБR
        if risk_level_ppm > 0:
            risk_level_dbr = 10 * math.log10(risk_level_ppm / 195)
        else:
            risk_level_dbr = float('-inf')

        # Находим максимальную частоту среди сценариев с погибшими
        death_scenarios = [r for r in component_results if r.casualties >= 1]
        max_death_frequency = max((r.probability for r in death_scenarios), default=0)

        return cls(
            component_name=component,
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