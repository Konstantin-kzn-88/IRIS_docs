from typing import Any

from calc_method.math_ import calc_strait_fire, calc_damage
from calc_method.config import calc_constants
from calc_method.tree import failure_set, tree_set
from models.calculation_result import CalculationResult


class Calculation():

    def __init__(self):
        # Инициализация констант
        self.constants = calc_constants.CalculationConstants()

    def get_zone_and_risk_param(self, project_code: str, scenario_number: str, equipment_name: str, equipment_type: Any,
                                model_type: str, substance_type: Any,
                                S_spill: int, molecular_weight: float, boiling_temperature_liquid: float,
                                type_accident: str, dead_man: int, injured_man: int, volume_equipment: int,
                                diametr_pipe: int, lenght_pipe: float, degree_damage: float, mass_in_accident:float,
                                mass_in_factor:float, mass_in_equipment:float):
        """

        :param project_code:                   - код проекта
        :param scenario_number:                - номер сценария
        :param equipment_name:                 - наименование оборудования
        :param equipment_type:                 - тип оборудования
        :param model_type                      - подтип оборудования ("Центробежные герметичные", "Центробежные с уплотнениями", "Поршневые" и т.п.)
        :param substance_type:                 - тип вещества
        :param S_spill:                        - площадь пролива, м2
        :param molecular_weight:               - молекулярная масса, кг/кмоль (например mol_mass = 95.3)
        :param boiling_temperature_liquid:     - температура кипения, град.С (например t_boiling = 68)
        :param type_accident:                  - тип аварии ('full', 'partial')
        :param dead_man:                       - предпологаемое количество погибших
        :param injured_man:                    - предпологаемое количество пострадавших
        :param volume_equipment:               - объем оборудования, м3 (если считаем трубопровод, то 0)
        :param diametr_pipe:                   - диаметр трубопровода, мм (если считаем стационарный, то 0)
        :param lenght_pipe:                    - длина трубопровода, км (если считаем стационарный, то 0)
        :param degree_damage:                  - доля учитываемого ущерба (от 0,01 до 1)
        :return:
        """

        print('in fire module' , volume_equipment)
        # расчитываем зоны (пожар пролива)
        q_10_5, q_7_0, q_4_2, q_1_4 = calc_strait_fire.Strait_fire().termal_class_zone(
            S_spill=S_spill, m_sg=self.constants.M_SG, mol_mass=molecular_weight,
            t_boiling=boiling_temperature_liquid, wind_velocity=self.constants.WIND_VELOCITY)

        # набор дерева событий

        tree = tree_set.equipment_substance_mapping[equipment_type.value][
            substance_type.value]
        # вероятность сценария
        probability = failure_set.equipment_failure_rates[equipment_type.value]['categories'][model_type][type_accident] * \
                      tree[type_accident][0][tree[type_accident][1].index('strait_fire')]

        # Опасного вещества в поражающем факторе
        mass_in_factor = mass_in_factor
        # Количество погибших пострадавших и коллективный риск
        casualties = dead_man
        injured = injured_man
        casualty_risk = casualties * probability  # Коллективный риск гибели
        injury_risk = injured * probability  # Коллективный риск травмы


        # Ущерб
        direct_losses, liquidation_costs, social_losses, indirect_damage, environmental_damage, total_damage = calc_damage.Damage(
            dead_man=casualties, injured_man=injured, volume_equipment=volume_equipment,
            diametr_pipe=diametr_pipe,
            lenght_pipe=lenght_pipe,
            degree_damage=degree_damage, m_out_spill=0, m_in_spill=mass_in_accident,
            S_spill=S_spill).sum_damage()

        expected_damage = total_damage * probability

        calculation = CalculationResult(
            id=None,
            project_code=project_code,
            scenario_number=scenario_number,
            equipment_name=equipment_name,
            equipment_type=equipment_type,
            substance_type=substance_type,
            q_10_5=q_10_5,
            q_7_0=q_7_0,
            q_4_2=q_4_2,
            q_1_4=q_1_4,
            p_53=0,
            p_28=0,
            p_12=0,
            p_5=0,
            p_2=0,
            l_f=0.0,
            d_f=0.0,
            r_nkpr=0.0,
            r_flash=0.0,
            l_pt=0.0,
            p_pt=0.0,
            q_600=0.0,
            q_320=0.0,
            q_220=0.0,
            q_120=0.0,
            s_spill=0.0,
            casualties=casualties,
            injured=injured,
            direct_losses=direct_losses,
            liquidation_costs=liquidation_costs,
            social_losses=social_losses,
            indirect_damage=indirect_damage,
            environmental_damage=environmental_damage,
            total_damage=total_damage,
            casualty_risk=casualty_risk,
            injury_risk=injury_risk,
            expected_damage=expected_damage,
            probability=probability,
            mass_risk=probability * round(mass_in_accident, 2),
            mass_in_accident=round(mass_in_accident, 2),
            mass_in_factor=round(mass_in_factor, 2),
            mass_in_equipment=round(mass_in_equipment, 2)
        )

        return calculation
