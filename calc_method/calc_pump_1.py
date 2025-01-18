from .config import calc_constants
from .calculators import strait_fire_calc, explosion_calc, flash_calc, no_factors_calc, jet_fire_calc, toxi_calc
from .math_ import calc_evaporation, calc_outflow


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
        mass_in_equipment = self.equipment.volume * self.substance.density_liquid * self.constants.KG_TO_T
        mass_in_accident = mass_in_equipment + (self.equipment.flow * self.equipment.time_out) * self.constants.KG_TO_T

        # Пожар пролива (полный)
        calc = strait_fire_calc.Calculation().get_zone_and_risk_param(
            project_code=self.project_code,
            scenario_number=f'{self.init_num_scenario}',
            equipment_name=self.equipment.name,
            equipment_type=self.equipment.equipment_type,
            model_type=self.equipment.pump_type,
            substance_type=self.substance.sub_type,
            S_spill=mass_in_accident * self.constants.SPILL,
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
                                                        degree_filling=1,
                                                        spill_square=mass_in_accident * self.constants.SPILL,
                                                        pressure_equipment=self.equipment.pressure,
                                                        temperature_equipment=self.equipment.temperature,
                                                        density_liquid=self.substance.density_liquid,
                                                        molecular_weight=self.substance.molecular_weight * self.constants.MOLE_TO_KMOLE,
                                                        boiling_temperature_liquid=self.substance.boiling_temperature_liquid,
                                                        heat_evaporation_liquid=self.substance.heat_evaporation_liquid * self.constants.KJ_TO_J,
                                                        adiabatic=self.substance.adiabatic,
                                                        heat_capacity_liquid=self.substance.heat_capacity_liquid * self.constants.KJ_TO_J).calculation()

        calc = explosion_calc.Calculation().get_zone_and_risk_param(
            project_code=self.project_code,
            scenario_number=f'{self.init_num_scenario}',
            equipment_name=self.equipment.name,
            equipment_type=self.equipment.equipment_type,
            model_type=self.equipment.pump_type,
            substance_type=self.substance.sub_type,
            S_spill=mass_in_accident * self.constants.SPILL,
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
            model_type=self.equipment.pump_type,
            substance_type=self.substance.sub_type,
            S_spill=mass_in_accident * self.constants.SPILL,
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


        # Факел жидкостной (частичный)

        outflow = calc_outflow.Outflow(pressure_equipment=self.equipment.pressure).outflow_liquid(
            density_liquid=self.substance.density_liquid)

        mass_in_accident_part = outflow * self.constants.TIME_OUT_DIVICE

        calc = jet_fire_calc.Calculation().get_zone_and_risk_param(
            project_code=self.project_code,
            scenario_number=f'{self.init_num_scenario}',
            equipment_name=self.equipment.name,
            equipment_type=self.equipment.equipment_type,
            model_type=self.equipment.pump_type,
            substance_type=self.substance.sub_type,
            S_spill=mass_in_accident * self.constants.PART * self.constants.SPILL,
            type_accident='partial',
            dead_man=0,
            injured_man=1,
            volume_equipment=self.equipment.volume,
            diametr_pipe=0,
            lenght_pipe=0,
            degree_damage=0.5 * self.constants.PART,
            mass_in_accident=mass_in_accident_part,
            mass_in_factor=mass_in_accident_part,
            mass_in_equipment=mass_in_equipment)

        result.append(calc)
        self.init_num_scenario += 1

        # Вспышка (частичный)
        calc = flash_calc.Calculation().get_zone_and_risk_param(
            project_code=self.project_code,
            scenario_number=f'{self.init_num_scenario}',
            equipment_name=self.equipment.name,
            equipment_type=self.equipment.equipment_type,
            model_type=self.equipment.pump_type,
            substance_type=self.substance.sub_type,
            S_spill=mass_in_accident * self.constants.PART * self.constants.SPILL,
            molecular_weight=self.substance.molecular_weight,
            boiling_temperature_liquid=self.substance.boiling_temperature_liquid,
            lower_concentration_limit=self.substance.lower_concentration_limit,
            type_accident='partial',
            dead_man=0,
            injured_man=1,
            volume_equipment=self.equipment.volume,
            diametr_pipe=0,
            lenght_pipe=0,
            degree_damage=0.35 * self.constants.PART,
            mass_in_accident=mass_in_accident_part,
            mass_in_factor=mass_in_accident_part,
            mass_in_equipment=mass_in_equipment)

        result.append(calc)
        self.init_num_scenario += 1

        # Токси (частичный)
        calc = toxi_calc.Calculation().get_zone_and_risk_param(
            project_code=self.project_code,
            scenario_number=f'{self.init_num_scenario}',
            equipment_name=self.equipment.name,
            equipment_type=self.equipment.equipment_type,
            model_type=self.equipment.pump_type,
            substance_type=self.substance.sub_type,
            S_spill=mass_in_accident * self.constants.SPILL * self.constants.PART,
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
            degree_damage=0.35 * self.constants.PART,
            mass_in_accident=mass_in_accident_part,
            mass_in_factor=mass_in_accident_part,
            mass_in_equipment=mass_in_equipment)

        result.append(calc)
        self.init_num_scenario += 1

        return (result, self.init_num_scenario)
