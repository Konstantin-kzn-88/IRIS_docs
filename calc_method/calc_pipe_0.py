from models.calculation_result import CalculationResult
from .tree import tree_set, failure_set
from .math_ import calc_evaporation, calc_strait_fire, calc_tvs_explosion, calc_lower_concentration, calc_damage

PART = 0.15  # доля частичной разгерметизации
KG_TO_T = 0.001
SPILL = 20  # пролив на грунт 20м-1
MOLE_TO_KMOLE = 0.001
PART_GAS_IN_EXPLOSION = 0.1  # доля газа во взрыве
T_TO_KG = 1000
M_TO_KM = 0.001


class Calc:
    def __init__(self, project_code, init_num_scenario, substance, equipment, dangerous_object):
        self.project_code = project_code
        self.init_num_scenario = init_num_scenario
        self.substance = substance
        self.equipment = equipment
        self.dangerous_object = dangerous_object

    def get_zone(self):
        result = []

        tree = tree_set.equipment_substance_mapping[str(self.equipment.equipment_type.value)][
            self.substance.sub_type]

        # Создаем нулевые параметры которые будет расчитываться
        # Обнуляем параметры которые будет расчитываться
        q_10_5, q_7_0, q_4_2, q_1_4, \
        p_53, p_28, p_12, p_5, p_3, \
        r_nkpr, r_flash, probability, mass_in_factor, casualties, injured, casualty_risk, injury_risk, \
        direct_losses, liquidation_costs, social_losses, indirect_damage, \
        environmental_damage, total_damage, expected_damage = [0] * 24

        mass_in_equipment = self.__calculate_pipeline_volume(self.equipment.length_meters,
                                                             self.equipment.diameter_pipeline) * self.substance.density_liquid * KG_TO_T
        mass_in_accident = mass_in_equipment*self.equipment.accident_rate + (self.equipment.flow * self.equipment.time_out) * KG_TO_T

        for type_accident in tree['full'][1]:
            if type_accident == 'strait_fire':
                q_10_5, q_7_0, q_4_2, q_1_4 = calc_strait_fire.Strait_fire().termal_class_zone(
                    S_spill=mass_in_accident * SPILL, m_sg=0.06, mol_mass=self.substance.molecular_weight,
                    t_boiling=self.substance.boiling_temperature_liquid, wind_velocity=1)

                # вероятность сценария
                probability = \
                    failure_set.equipment_failure_rates[str(self.equipment.equipment_type.value)]['categories'][
                        self.equipment.diameter_category]['full'] * tree['full'][0][
                        tree['full'][1].index('strait_fire')]

                mass_in_factor = mass_in_accident

                casualties = 0
                injured = self.equipment.expected_casualties

                casualty_risk = casualties * probability  # Коллективный риск гибели
                injury_risk = injured * probability  # Коллективный риск травмы

                direct_losses, liquidation_costs, social_losses, indirect_damage, environmental_damage, total_damage = calc_damage.Damage(
                    dead_man=casualties, injured_man=injured, volume_equipment=0,
                    diametr_pipe=self.equipment.diameter_pipeline,
                    lenght_pipe=self.equipment.length_meters * M_TO_KM,
                    degree_damage=0.5, m_out_spill=0, m_in_spill=mass_in_accident,
                    S_spill=mass_in_accident * SPILL).sum_damage()

                expected_damage = total_damage*probability


            elif type_accident == 'explosion':
                print('explosion', 'p_53', 'p_28', 'p_12', 'p_5', 'p_3')

                # вероятность сценария
                probability = \
                    failure_set.equipment_failure_rates[str(self.equipment.equipment_type.value)]['categories'][
                        self.equipment.diameter_category]['full'] * tree['full'][0][
                        tree['full'][1].index('explosion')]

                mass_in_factor = calc_evaporation.Evaporation(volume_equipment=mass_in_equipment,
                                                              degree_filling=1, spill_square=mass_in_equipment * SPILL,
                                                              pressure_equipment=self.equipment.pressure,
                                                              temperature_equipment=self.equipment.temperature,
                                                              density_liquid=self.substance.density_liquid,
                                                              molecular_weight=self.substance.molecular_weight * MOLE_TO_KMOLE,
                                                              boiling_temperature_liquid=self.substance.boiling_temperature_liquid,
                                                              heat_evaporation_liquid=self.substance.heat_evaporation_liquid,
                                                              adiabatic=self.substance.adiabatic,
                                                              heat_capacity_liquid=self.substance.heat_capacity_liquid).calculation() * KG_TO_T

                p_53, p_28, p_12, p_5, p_3 = calc_tvs_explosion.Explosion().explosion_class_zone(
                    class_substance=self.substance.class_substance, view_space=self.dangerous_object.view_space,
                    mass=mass_in_factor * PART_GAS_IN_EXPLOSION * T_TO_KG,
                    heat_of_combustion=self.substance.heat_of_combustion, sigma=self.substance.sigma,
                    energy_level=self.substance.energy_level)

                casualties = self.equipment.expected_casualties
                injured = 0

                casualty_risk = casualties * probability  # Коллективный риск гибели
                injury_risk = injured * probability  # Коллективный риск травмы

                direct_losses, liquidation_costs, social_losses, indirect_damage, environmental_damage, total_damage = calc_damage.Damage(
                    dead_man=casualties, injured_man=injured, volume_equipment=0,
                    diametr_pipe=self.equipment.diameter_pipeline,
                    lenght_pipe=self.equipment.length_meters * M_TO_KM,
                    degree_damage=0.6, m_out_spill=mass_in_factor, m_in_spill=0,
                    S_spill=mass_in_accident * SPILL).sum_damage()

                expected_damage = total_damage * probability

            elif type_accident == 'no_factors':
                print('no_factors')
                # вероятность сценария
                probability = \
                    failure_set.equipment_failure_rates[str(self.equipment.equipment_type.value)]['categories'][
                        self.equipment.diameter_category]['full'] * tree['full'][0][
                        tree['full'][1].index('no_factors')]

                mass_in_factor = 0
                casualties = 0
                injured = 0

                casualty_risk = casualties * probability  # Коллективный риск гибели
                injury_risk = injured * probability  # Коллективный риск травмы

                direct_losses, liquidation_costs, social_losses, indirect_damage, environmental_damage, total_damage = calc_damage.Damage(
                    dead_man=casualties, injured_man=injured, volume_equipment=0,
                    diametr_pipe=self.equipment.diameter_pipeline,
                    lenght_pipe=self.equipment.length_meters * M_TO_KM,
                    degree_damage=0.4, m_out_spill=0, m_in_spill=0,
                    S_spill=mass_in_accident * SPILL).sum_damage()

                expected_damage = total_damage * probability

            calculation = CalculationResult(
                id=None,
                project_code=self.project_code,
                scenario_number=f'{self.init_num_scenario}',  # С1
                equipment_name=self.equipment.name,
                equipment_type=self.equipment.equipment_type,
                substance_type=self.substance.sub_type,
                q_10_5=q_10_5 or 0,
                q_7_0=q_7_0 or 0,
                q_4_2=q_4_2 or 0,
                q_1_4=q_1_4 or 0,
                p_53=p_53 or 0,
                p_28=p_28 or 0,
                p_12=p_12 or 0,
                p_5=p_5 or 0,
                p_2=p_3 or 0,
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
                casualties=casualties or 0,
                injured=injured or 0,
                direct_losses=direct_losses or 0,
                liquidation_costs=liquidation_costs or 0,
                social_losses=social_losses or 0,
                indirect_damage=indirect_damage or 0,
                environmental_damage=environmental_damage or 0,
                total_damage=total_damage or 0,
                casualty_risk=casualty_risk or 0,
                injury_risk=injury_risk or 0,
                expected_damage=expected_damage or 0,
                probability=probability,  # Добавляем новое поле
                mass_risk=probability * round(mass_in_accident, 2),
                mass_in_accident=round(mass_in_accident, 2),
                mass_in_factor=mass_in_factor,
                mass_in_equipment=round(mass_in_equipment, 2)
            )
            result.append(calculation)
            # Обнуляем параметры которые будет расчитываться
            q_10_5, q_7_0, q_4_2, q_1_4, \
            p_53, p_28, p_12, p_5, p_3, \
            r_nkpr, r_flash, probability, mass_in_factor, casualties, injured, casualty_risk, injury_risk, \
            direct_losses, liquidation_costs, social_losses, indirect_damage, \
            environmental_damage, total_damage, expected_damage = [0] * 24

            self.init_num_scenario += 1
        # Создаем нулевые параметры которые будет расчитываться
        # Обнуляем параметры которые будет расчитываться
        q_10_5, q_7_0, q_4_2, q_1_4, \
        p_53, p_28, p_12, p_5, p_3, \
        r_nkpr, r_flash, probability, mass_in_factor, casualties, injured, casualty_risk, injury_risk, \
        direct_losses, liquidation_costs, social_losses, indirect_damage, \
        environmental_damage, total_damage, expected_damage = [0] * 24

        for type_accident in tree['partial'][1]:
            if type_accident == 'strait_fire':
                q_10_5, q_7_0, q_4_2, q_1_4 = calc_strait_fire.Strait_fire().termal_class_zone(
                    S_spill=round(PART * mass_in_accident, 2) * SPILL, m_sg=0.06,
                    mol_mass=self.substance.molecular_weight,
                    t_boiling=self.substance.boiling_temperature_liquid, wind_velocity=1)
                # вероятность сценария
                probability = \
                    failure_set.equipment_failure_rates[str(self.equipment.equipment_type.value)]['categories'][
                        self.equipment.diameter_category]['partial'] * tree['partial'][0][
                        tree['partial'][1].index('strait_fire')]

                mass_in_factor = round(PART * mass_in_accident, 2)

                casualties = 0
                injured = 1

                casualty_risk = casualties * probability  # Коллективный риск гибели
                injury_risk = injured * probability  # Коллективный риск травмы

                direct_losses, liquidation_costs, social_losses, indirect_damage, environmental_damage, total_damage = calc_damage.Damage(
                    dead_man=casualties, injured_man=injured, volume_equipment=0,
                    diametr_pipe=self.equipment.diameter_pipeline,
                    lenght_pipe=self.equipment.length_meters * M_TO_KM,
                    degree_damage=0.3, m_out_spill=0, m_in_spill=mass_in_factor,
                    S_spill=round(PART * mass_in_accident, 2) * SPILL).sum_damage()

                expected_damage = total_damage * probability

            elif type_accident == 'flash':
                print('flash', 'r_nkpr', 'r_flash')

                # вероятность сценария
                probability = \
                    failure_set.equipment_failure_rates[str(self.equipment.equipment_type.value)]['categories'][
                        self.equipment.diameter_category]['partial'] * tree['partial'][0][
                        tree['partial'][1].index('flash')]

                mass_in_factor = calc_evaporation.Evaporation(volume_equipment=round(PART * mass_in_accident, 2),
                                                              degree_filling=1,
                                                              spill_square=round(PART * mass_in_accident, 2) * SPILL,
                                                              pressure_equipment=self.equipment.pressure,
                                                              temperature_equipment=self.equipment.temperature,
                                                              density_liquid=self.substance.density_liquid,
                                                              molecular_weight=self.substance.molecular_weight * MOLE_TO_KMOLE,
                                                              boiling_temperature_liquid=self.substance.boiling_temperature_liquid,
                                                              heat_evaporation_liquid=self.substance.heat_evaporation_liquid,
                                                              adiabatic=self.substance.adiabatic,
                                                              heat_capacity_liquid=self.substance.heat_capacity_liquid).calculation() * KG_TO_T

                r_nkpr, r_flash = calc_lower_concentration.LCLP().lower_concentration_limit(
                    mass=mass_in_factor * T_TO_KG, molecular_weight=self.substance.molecular_weight,
                    t_boiling=self.substance.boiling_temperature_liquid,
                    lower_concentration=self.substance.lower_concentration_limit)


                casualties = 0
                injured = 1

                casualty_risk = casualties * probability  # Коллективный риск гибели
                injury_risk = injured * probability  # Коллективный риск травмы

                direct_losses, liquidation_costs, social_losses, indirect_damage, environmental_damage, total_damage = calc_damage.Damage(
                    dead_man=casualties, injured_man=injured, volume_equipment=0,
                    diametr_pipe=self.equipment.diameter_pipeline,
                    lenght_pipe=self.equipment.length_meters * M_TO_KM,
                    degree_damage=0.2, m_out_spill=mass_in_factor, m_in_spill=0,
                    S_spill=round(PART * mass_in_accident, 2) * SPILL).sum_damage()

                expected_damage = total_damage * probability


            elif type_accident == 'no_factors':
                print('no_factors')
                # вероятность сценария
                probability = \
                    failure_set.equipment_failure_rates[str(self.equipment.equipment_type.value)]['categories'][
                        self.equipment.diameter_category]['partial'] * tree['partial'][0][
                        tree['partial'][1].index('no_factors')]

                mass_in_factor = 0

                casualties = 0
                injured = 0

                casualty_risk = casualties * probability  # Коллективный риск гибели
                injury_risk = injured * probability  # Коллективный риск травмы

                direct_losses, liquidation_costs, social_losses, indirect_damage, environmental_damage, total_damage = calc_damage.Damage(
                    dead_man=casualties, injured_man=injured, volume_equipment=0,
                    diametr_pipe=self.equipment.diameter_pipeline,
                    lenght_pipe=self.equipment.length_meters * M_TO_KM,
                    degree_damage=0.1, m_out_spill=0, m_in_spill=0,
                    S_spill=round(PART * mass_in_accident, 2) * SPILL).sum_damage()

                expected_damage = total_damage * probability

            calculation = CalculationResult(
                id=None,
                project_code=self.project_code,
                scenario_number=f'{self.init_num_scenario}',  # С1
                equipment_name=self.equipment.name,
                equipment_type=self.equipment.equipment_type,
                substance_type=self.substance.sub_type,
                q_10_5=q_10_5 or 0,
                q_7_0=q_7_0 or 0,
                q_4_2=q_4_2 or 0,
                q_1_4=q_1_4 or 0,
                p_53=0.0,
                p_28=0.0,
                p_12=0.0,
                p_5=0.0,
                p_2=0.0,
                l_f=0.0,
                d_f=0.0,
                r_nkpr=r_nkpr or 0,
                r_flash=r_flash or 0,
                l_pt=0.0,
                p_pt=0.0,
                q_600=0.0,
                q_320=0.0,
                q_220=0.0,
                q_120=0.0,
                s_spill=0.0,
                casualties=casualties or 0,
                injured=injured or 0,
                direct_losses=direct_losses or 0,
                liquidation_costs=liquidation_costs or 0,
                social_losses=social_losses or 0,
                indirect_damage=indirect_damage or 0,
                environmental_damage=environmental_damage or 0,
                total_damage=total_damage or 0,
                casualty_risk=casualty_risk or 0,
                injury_risk=injury_risk or 0,
                expected_damage=expected_damage or 0,
                probability=probability,  # Добавляем новое поле
                mass_risk=probability * round(PART * mass_in_accident, 2),
                mass_in_accident=round(PART * mass_in_accident, 2),
                mass_in_factor=mass_in_factor,
                mass_in_equipment=round(mass_in_equipment, 2)
            )
            result.append(calculation)
            # Обнуляем параметры которые будет расчитываться
            q_10_5, q_7_0, q_4_2, q_1_4, \
            p_53, p_28, p_12, p_5, p_3, \
            r_nkpr, r_flash, probability, mass_in_factor, casualties, injured, casualty_risk, injury_risk, \
            direct_losses, liquidation_costs, social_losses, indirect_damage, \
            environmental_damage, total_damage, expected_damage = [0] * 24

            self.init_num_scenario += 1

        # Возвращаем список сценариев result и номер последнего сценария
        return (result, self.init_num_scenario)

    def __calculate_pipeline_volume(self, length_m: float, diameter_mm: float) -> float:
        """
        Рассчитывает объем цилиндрического трубопровода в кубических метрах

        Args:
            length_m (float): Длина трубопровода в метрах
            diameter_mm (float): Диаметр трубопровода в миллиметрах

        Returns:
            float: Объем трубопровода в кубических метрах

        Raises:
            ValueError: Если длина или диаметр меньше или равны 0
        """
        import math

        # Проверка входных данных
        if length_m <= 0 or diameter_mm <= 0:
            raise ValueError("Длина и диаметр должны быть положительными числами")

        # Переводим диаметр из мм в метры
        diameter_m = diameter_mm / 1000

        # Рассчитываем радиус в метрах
        radius_m = diameter_m / 2

        # Рассчитываем объем по формуле V = π * r² * h
        volume = math.pi * (radius_m ** 2) * length_m

        return volume
