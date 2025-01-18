from .config import calc_constants
from .calculators import strait_fire_calc, explosion_calc, flash_calc, no_factors_calc, toxi_calc
from .math_ import calc_evaporation


class Calc:
    def __init__(self, project_code, init_num_scenario, substance, equipment, dangerous_object):
        self.project_code = project_code
        self.init_num_scenario = init_num_scenario
        self.substance = substance
        self.equipment = equipment
        self.dangerous_object = dangerous_object
        # Инициализация констант
        self.constants = calc_constants.CalculationConstants()

    def result(self):
        result = []

        # Оперделение массы вещества в оборудовании и аварии
        mass_in_equipment = self.equipment.volume * self.equipment.degree_filling * self.substance.density_liquid * self.constants.KG_TO_T
        mass_in_accident = mass_in_equipment

        # Пожар пролива (полный)
        calc = strait_fire_calc.Calculation().get_zone_and_risk_param(
            project_code=self.project_code,
            scenario_number=f'{self.init_num_scenario}',
            equipment_name=self.equipment.name,
            equipment_type=self.equipment.equipment_type,
            model_type=self.equipment.tank_type,
            substance_type=self.substance.sub_type,
            S_spill=self.equipment.spill_square,
            molecular_weight=self.substance.molecular_weight,
            boiling_temperature_liquid=self.substance.boiling_temperature_liquid,
            type_accident='full',
            dead_man=0,
            injured_man=self.equipment.expected_casualties,
            volume_equipment=self.equipment.volume,
            diametr_pipe=0,
            lenght_pipe=0,
            degree_damage=0.5,
            mass_in_accident=mass_in_accident,
            mass_in_factor=mass_in_accident,
            mass_in_equipment=mass_in_equipment)
        result.append(calc)
        self.init_num_scenario += 1


        # Взрыв (полный)

        mass_evaporation = calc_evaporation.Evaporation(volume_equipment=mass_in_equipment,
                                                        degree_filling=self.equipment.degree_filling,
                                                        spill_square=self.equipment.spill_square,
                                                        pressure_equipment=self.equipment.pressure,
                                                        temperature_equipment=self.equipment.temperature,
                                                        density_liquid=self.substance.density_liquid,
                                                        molecular_weight=self.substance.molecular_weight * self.constants.MOLE_TO_KMOLE,
                                                        boiling_temperature_liquid=self.substance.boiling_temperature_liquid,
                                                        heat_evaporation_liquid=self.substance.heat_evaporation_liquid*self.constants.KJ_TO_J,
                                                        adiabatic=self.substance.adiabatic,
                                                        heat_capacity_liquid=self.substance.heat_capacity_liquid*self.constants.KJ_TO_J).calculation()


        calc = explosion_calc.Calculation().get_zone_and_risk_param(
            project_code=self.project_code,
            scenario_number=f'{self.init_num_scenario}',
            equipment_name=self.equipment.name,
            equipment_type=self.equipment.equipment_type,
            model_type=self.equipment.tank_type,
            substance_type=self.substance.sub_type,
            S_spill=self.equipment.spill_square,
            class_substance=self.substance.class_substance,
            view_space=self.dangerous_object.view_space,
            heat_of_combustion=self.substance.heat_of_combustion,
            sigma=self.substance.sigma,
            energy_level=self.substance.energy_level,
            type_accident='full',
            dead_man=self.equipment.expected_casualties,
            injured_man=0,
            volume_equipment=self.equipment.volume,
            diametr_pipe=0,
            lenght_pipe=0,
            degree_damage=0.6,
            mass_in_accident=mass_in_accident,
            mass_in_factor=mass_evaporation,
            mass_in_equipment=mass_in_equipment)
        result.append(calc)
        self.init_num_scenario += 1

        # Токси жидкость (полный)
        calc = toxi_calc.Calculation().get_zone_and_risk_param(
            project_code=self.project_code,
            scenario_number=f'{self.init_num_scenario}',
            equipment_name=self.equipment.name,
            equipment_type=self.equipment.equipment_type,
            model_type=self.equipment.tank_type,
            substance_type=self.substance.sub_type,
            S_spill=self.equipment.spill_square,
            gas_temperature=self.equipment.temperature,
            gas_weight=0,  # первичного облака нет
            gas_flow=mass_evaporation / self.constants.TIME_EVAPORATION,
            molecular_weight=self.substance.molecular_weight,
            threshold_dose=self.substance.threshold_toxic_dose,
            lethal_dose=self.substance.lethal_toxic_dose,
            type_accident='full',
            dead_man=0,
            injured_man=1,
            volume_equipment=self.equipment.volume,
            diametr_pipe=0,
            lenght_pipe=0,
            degree_damage=0.3,
            mass_in_accident=mass_in_accident,
            mass_in_factor=mass_evaporation,
            mass_in_equipment=mass_in_equipment)
        result.append(calc)
        self.init_num_scenario += 1

        # Пожар пролива (частичный)
        calc = strait_fire_calc.Calculation().get_zone_and_risk_param(
            project_code=self.project_code,
            scenario_number=f'{self.init_num_scenario}',
            equipment_name=self.equipment.name,
            equipment_type=self.equipment.equipment_type,
            model_type=self.equipment.tank_type,
            substance_type=self.substance.sub_type,
            S_spill=self.equipment.spill_square * self.constants.PART,
            molecular_weight=self.substance.molecular_weight,
            boiling_temperature_liquid=self.substance.boiling_temperature_liquid,
            type_accident='partial',
            dead_man=0,
            injured_man=1,
            volume_equipment=self.equipment.volume,
            diametr_pipe=0,
            lenght_pipe=0,
            degree_damage=0.5 * self.constants.PART,
            mass_in_accident=mass_in_accident * self.constants.PART,
            mass_in_factor=mass_in_accident * self.constants.PART,
            mass_in_equipment=mass_in_equipment)

        result.append(calc)
        self.init_num_scenario += 1

        # Вспышка (частичный)
        mass_evaporation = calc_evaporation.Evaporation(volume_equipment=mass_in_equipment,
                                                        degree_filling=self.equipment.degree_filling,
                                                        spill_square=self.equipment.spill_square,
                                                        pressure_equipment=self.equipment.pressure,
                                                        temperature_equipment=self.equipment.temperature,
                                                        density_liquid=self.substance.density_liquid,
                                                        molecular_weight=self.substance.molecular_weight * self.constants.MOLE_TO_KMOLE,
                                                        boiling_temperature_liquid=self.substance.boiling_temperature_liquid,
                                                        heat_evaporation_liquid=self.substance.heat_evaporation_liquid*self.constants.KJ_TO_J,
                                                        adiabatic=self.substance.adiabatic,
                                                        heat_capacity_liquid=self.substance.heat_capacity_liquid*self.constants.KJ_TO_J).calculation()

        calc = flash_calc.Calculation().get_zone_and_risk_param(
            project_code=self.project_code,
            scenario_number=f'{self.init_num_scenario}',
            equipment_name=self.equipment.name,
            equipment_type=self.equipment.equipment_type,
            model_type=self.equipment.tank_type,
            substance_type=self.substance.sub_type,
            S_spill=self.equipment.spill_square * self.constants.PART,
            molecular_weight=self.substance.molecular_weight,
            boiling_temperature_liquid=self.substance.boiling_temperature_liquid,
            lower_concentration_limit=self.substance.lower_concentration_limit,
            type_accident='partial',
            dead_man=0,
            injured_man=1,
            volume_equipment=self.equipment.volume,
            diametr_pipe=0,
            lenght_pipe=0,
            degree_damage=0.6 * self.constants.PART,
            mass_in_accident=mass_in_accident * self.constants.PART,
            mass_in_factor=mass_evaporation,
            mass_in_equipment=mass_in_equipment)

        result.append(calc)
        self.init_num_scenario += 1

        # Токси (частичный)
        calc = toxi_calc.Calculation().get_zone_and_risk_param(
            project_code=self.project_code,
            scenario_number=f'{self.init_num_scenario}',
            equipment_name=self.equipment.name,
            equipment_type=self.equipment.equipment_type,
            model_type=self.equipment.tank_type,
            substance_type=self.substance.sub_type,
            S_spill=self.equipment.spill_square * self.constants.PART,
            gas_temperature=self.equipment.temperature,
            gas_weight=0,  # первичного облака нет
            gas_flow=(mass_evaporation / self.constants.TIME_EVAPORATION) * self.constants.PART,
            molecular_weight=self.substance.molecular_weight,
            threshold_dose=self.substance.threshold_toxic_dose,
            lethal_dose=self.substance.lethal_toxic_dose,
            type_accident='partial',
            dead_man=0,
            injured_man=0,
            volume_equipment=self.equipment.volume,
            diametr_pipe=0,
            lenght_pipe=0,
            degree_damage=0.6 * self.constants.PART,
            mass_in_accident=mass_in_accident * self.constants.PART,
            mass_in_factor=mass_evaporation,
            mass_in_equipment=mass_in_equipment)

        result.append(calc)
        self.init_num_scenario += 1

        return (result, self.init_num_scenario)

