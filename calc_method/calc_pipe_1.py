from .config import calc_constants
from .calculators import strait_fire_calc, explosion_calc, flash_calc, toxi_calc
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
        mass_in_equipment = self.__calculate_pipeline_volume(self.equipment.length_meters,
                                                             self.equipment.diameter_pipeline) * self.substance.density_liquid * self.constants.KG_TO_T
        mass_in_accident = mass_in_equipment * self.equipment.accident_rate + (
                self.equipment.flow * self.equipment.time_out) * self.constants.KG_TO_T

        # Пожар пролива (полный)
        calc = strait_fire_calc.Calculation().get_zone_and_risk_param(
            project_code=self.project_code,
            scenario_number=f'{self.init_num_scenario}',
            equipment_name=self.equipment.name,
            equipment_type=self.equipment.equipment_type,
            model_type=self.equipment.diameter_category,
            substance_type=self.substance.sub_type,
            S_spill=mass_in_accident * self.constants.SPILL,
            molecular_weight=self.substance.molecular_weight,
            boiling_temperature_liquid=self.substance.boiling_temperature_liquid,
            type_accident='full',
            dead_man=0,
            injured_man=self.equipment.expected_casualties,
            volume_equipment=0,
            diametr_pipe=self.equipment.diameter_pipeline,
            lenght_pipe=self.equipment.length_meters * self.constants.M_TO_KM,
            degree_damage=0.5,
            mass_in_accident=mass_in_accident,
            mass_in_factor=mass_in_accident,
            mass_in_equipment=mass_in_equipment)
        result.append(calc)
        self.init_num_scenario += 1

        # Взрыв (полный)

        mass_evaporation = calc_evaporation.Evaporation(volume_equipment=mass_in_equipment,
                                                        degree_filling=1,
                                                        spill_square=mass_in_equipment * self.constants.SPILL,
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
            model_type=self.equipment.diameter_category,
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
            volume_equipment=0,
            diametr_pipe=self.equipment.diameter_pipeline,
            lenght_pipe=self.equipment.length_meters * self.constants.M_TO_KM,
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
            model_type=self.equipment.diameter_category,
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
            volume_equipment=0,
            diametr_pipe=self.equipment.diameter_pipeline,
            lenght_pipe=self.equipment.length_meters * self.constants.M_TO_KM,
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
            model_type=self.equipment.diameter_category,
            substance_type=self.substance.sub_type,
            S_spill=mass_in_accident * self.constants.SPILL * self.constants.PART,
            molecular_weight=self.substance.molecular_weight,
            boiling_temperature_liquid=self.substance.boiling_temperature_liquid,
            type_accident='partial',
            dead_man=0,
            injured_man=1,
            volume_equipment=0,
            diametr_pipe=self.equipment.diameter_pipeline,
            lenght_pipe=self.equipment.length_meters * self.constants.M_TO_KM,
            degree_damage=0.5 * self.constants.PART,
            mass_in_accident=mass_in_accident * self.constants.PART,
            mass_in_factor=mass_in_accident * self.constants.PART,
            mass_in_equipment=mass_in_equipment)

        result.append(calc)
        self.init_num_scenario += 1

        # Вспышка (частичный)
        mass_evaporation = calc_evaporation.Evaporation(volume_equipment=mass_in_equipment,
                                                        degree_filling=1,
                                                        spill_square=mass_in_equipment * self.constants.SPILL * self.constants.PART,
                                                        pressure_equipment=self.equipment.pressure,
                                                        temperature_equipment=self.equipment.temperature,
                                                        density_liquid=self.substance.density_liquid,
                                                        molecular_weight=self.substance.molecular_weight * self.constants.MOLE_TO_KMOLE,
                                                        boiling_temperature_liquid=self.substance.boiling_temperature_liquid,
                                                        heat_evaporation_liquid=self.substance.heat_evaporation_liquid * self.constants.KJ_TO_J,
                                                        adiabatic=self.substance.adiabatic,
                                                        heat_capacity_liquid=self.substance.heat_capacity_liquid * self.constants.KJ_TO_J).calculation()

        calc = flash_calc.Calculation().get_zone_and_risk_param(
            project_code=self.project_code,
            scenario_number=f'{self.init_num_scenario}',
            equipment_name=self.equipment.name,
            equipment_type=self.equipment.equipment_type,
            model_type=self.equipment.diameter_category,
            substance_type=self.substance.sub_type,
            S_spill=mass_in_accident * self.constants.SPILL * self.constants.PART,
            molecular_weight=self.substance.molecular_weight,
            boiling_temperature_liquid=self.substance.boiling_temperature_liquid,
            lower_concentration_limit=self.substance.lower_concentration_limit,
            type_accident='partial',
            dead_man=0,
            injured_man=1,
            volume_equipment=0,
            diametr_pipe=self.equipment.diameter_pipeline,
            lenght_pipe=self.equipment.length_meters * self.constants.M_TO_KM,
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
            model_type=self.equipment.diameter_category,
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
            volume_equipment=0,
            diametr_pipe=self.equipment.diameter_pipeline,
            lenght_pipe=self.equipment.length_meters * self.constants.M_TO_KM,
            degree_damage=0.3 * self.constants.PART,
            mass_in_accident=mass_in_accident * self.constants.PART,
            mass_in_factor=mass_evaporation * self.constants.PART,
            mass_in_equipment=mass_in_equipment)

        result.append(calc)
        self.init_num_scenario += 1

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
