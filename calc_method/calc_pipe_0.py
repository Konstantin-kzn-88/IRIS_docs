from models.calculation_result import CalculationResult


class Calc:
    def __init__(self, project_code, init_num_scenario, substance, equipment):
        self.project_code = project_code
        self.init_num_scenario = init_num_scenario
        self.substance = substance
        self.equipment = equipment

    def get_zone(self):
        result = []

        for _ in range(6):
            # Создаем запись расчета
            calculation = CalculationResult(
                id=None,
                project_code=self.project_code,
                scenario_number=f'{self.init_num_scenario}',  # С1
                equipment_name=self.equipment.name,
                equipment_type=self.equipment.equipment_type,
                substance_type=self.substance.sub_type,
                q_10_5=0.0,
                q_7_0=0.0,
                q_4_2=0.0,
                q_1_4=0.0,
                p_53=0.0,
                p_28=0.0,
                p_12=0.0,
                p_5=0.0,
                p_2=0.0,
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
                casualties=0,
                injured=0,
                direct_losses=0.0,
                liquidation_costs=0.0,
                social_losses=0.0,
                indirect_damage=0.0,
                environmental_damage=0.0,
                total_damage=0.0,
                casualty_risk=0.0,
                injury_risk=0.0,
                expected_damage=0.0,
                probability=1.0e-6,  # Добавляем новое поле
                mass_risk=1e-6,
                mass_in_accident=1,
                mass_in_factor=1,
                mass_in_equipment=1  # Добавляем начальное значение вероятности
            )
            result.append(calculation)
            self.init_num_scenario += 1
        # Возвращаем список сценариев result и номер последнего сценария
        return (result, self.init_num_scenario)
