# ------------------------------------------------------------------------------------
# Модуль работы с испарение веществ.
# @version: 1.0
# @date: 2024-08-29
# ------------------------------------------------------------------------------------
# volume_equipment - объем, м3
# degree_filling - степень заполения, доли единицы
# spill_square - площадь пролива м2
# pressure_equipment - давление, МПа
# temperature_equipment -температура, градусов Цельсия
# density_liquid - плотность, кг/м3
# molecular_weight - мол.масса, кг/моль
# boiling_temperature_liquid - температура кипения, градусов Цельсия (чем больше температура кипения, тем меньше мгновенно испаряется)
# heat_evaporation_liquid - теплота испарения, Дж/кг (чем больше теплота, тем меньше мгновенно испаряется, пропан 356000, аммиак 1371000, ацетон 538000)
# adiabatic = 1.01  - показатель адиабаты
# heat_capacity_liquid - теплоемкость жидкости, Дж/кг/град (чем меньше теплоемкость, тем меньше мгновенно испаряется, бензин 2050, нефть 1670, пропан 2800)

# ------------------------------------------------------------------------------------
# @author: Kuznetsov Konstantin, kuznetsov@yandex.ru
# (C) 2024
# ------------------------------------------------------------------------------------

import math

DENSITY_SURFACE = 2200  # плотность бетона, кг/м3
THERMAL_CONDUCTIVITY_SURFACE = 1.42  # теплопроводность бетона, Вт/(м·град)
HEAT_CAPACITY_SURFACE = 770  # теплоёмкость бетона, Дж/(кг·K)
TEMPERATURE_SURFACE = 30  # температура, градусов Цельсия (чем больше температура поверности, тем больше кипит)
R = 8.314  # газовая постоянная
C_TO_K = 273.15  # перевод к град.Кельвин
TIME_EVAPORATION = 3600  # время испарения, с
P_ATM = 101.325  # давление атмосферное, МПа

class Evaporation:
    def __init__(self, volume_equipment: float, degree_filling: float, spill_square: float,
                 pressure_equipment: float, temperature_equipment: int, density_liquid: int,
                 molecular_weight: float, boiling_temperature_liquid: int, heat_evaporation_liquid: int,
                 adiabatic: float, heat_capacity_liquid: int):

        self.volume_equipment= volume_equipment
        self.degree_filling = degree_filling
        self.spill_square = spill_square

        self.pressure_equipment= pressure_equipment
        self.temperature_equipment = temperature_equipment
        self.density_liquid = density_liquid

        self.molecular_weight= molecular_weight
        self.boiling_temperature_liquid = boiling_temperature_liquid
        self.heat_evaporation_liquid = heat_evaporation_liquid

        self.adiabatic = adiabatic
        self.heat_capacity_liquid = heat_capacity_liquid

    def report(self):
        print('1. Объем парогазовой фазы в блоке, м3:')
        volume_gas = self.volume_equipment * (1 - self.degree_filling)
        print(volume_gas)

        print('2. Масса жидкости в блоке, кг:')
        mass_liguid = self.volume_equipment * self.degree_filling * self.density_liquid
        print(mass_liguid)

        print('3. Масса ПГФ, имеющаяся непосредственно в блоке, кг:')
        mass_gas = self.molecular_weight * volume_gas * self.pressure_equipment * pow(10, 6) / (
                    R * (self.temperature_equipment + C_TO_K))
        print(mass_gas)

        print(
            '4.Масса вещества, переходящая в парогазовую фазу при мгновенном вскипании перегретой жидкости блока (аппарата), кг:')
        fraction = 1 - math.exp(-self.heat_capacity_liquid * (((self.temperature_equipment + C_TO_K) - (
                self.boiling_temperature_liquid + C_TO_K) + math.fabs(
            (self.temperature_equipment + C_TO_K) - (self.boiling_temperature_liquid + C_TO_K))) / self.heat_evaporation_liquid))
        mass_instantly_boiling = fraction * mass_liguid
        print(mass_instantly_boiling)

        print('5. Масса вещества в проливе после мгновенного вскипания жидкости, кг:')
        mass_liguid_after_instantly_boiling = mass_liguid - mass_instantly_boiling
        print(mass_liguid_after_instantly_boiling)

        print('6. Давление насыщенного пара при расчетной температуре, кПа:')
        steam_pressure = P_ATM * math.exp((self.heat_evaporation_liquid * self.molecular_weight / R) * (
                (1 / (self.boiling_temperature_liquid + C_TO_K)) - (1 / (self.temperature_equipment + C_TO_K))))
        print(steam_pressure)

        print('7. Масса испарившегося в-ва от теплопритока поверхности, кг и время кипения, с:')

        if TEMPERATURE_SURFACE > self.boiling_temperature_liquid:
            time_boiling = ((TEMPERATURE_SURFACE - self.boiling_temperature_liquid + math.fabs(
                TEMPERATURE_SURFACE - self.boiling_temperature_liquid)) / (2 * self.heat_evaporation_liquid / 1000)) * pow(
                THERMAL_CONDUCTIVITY_SURFACE * HEAT_CAPACITY_SURFACE * DENSITY_SURFACE / math.pi, 1 / 2) * 1 / (
                                   pow(self.molecular_weight, 1 / 2) * pow(10, -6) * 9.93 * steam_pressure)
            print(time_boiling)
            mass_surface_heat_intake = min(self.__mass_boiling(time_boiling),
                                           mass_liguid_after_instantly_boiling)
            mass_surface_heat_intake = mass_liguid_after_instantly_boiling if mass_surface_heat_intake < 0 else mass_surface_heat_intake
            print(mass_surface_heat_intake)
        else:
            mass_surface_heat_intake = min(
                pow(10, -6) * (steam_pressure) * math.sqrt(self.molecular_weight * 1000) * 3600 * self.spill_square,
                mass_liguid_after_instantly_boiling)
            print(0)
            print(mass_surface_heat_intake)

        print('8. Масса вещества оставшегося в проливе после испарения от теплопритока поверхности, кг:')
        mass_end = mass_liguid_after_instantly_boiling - mass_surface_heat_intake
        print(mass_end)

        print('9. Масса вещества перешедшее в газообразное состояние, кг:')
        mass_gas_end = mass_gas + mass_instantly_boiling + mass_surface_heat_intake
        print(mass_gas_end)

    def calculation(self):
        '''
        Функция определения сколько испарилось газа
        '''
        # print('1. Объем парогазовой фазы в блоке, м3:')
        volume_gas = self.volume_equipment * (1 - self.degree_filling)

        # print('2. Масса жидкости в блоке, кг:')
        mass_liguid = self.volume_equipment * self.degree_filling * self.density_liquid

        # print('3. Масса ПГФ, имеющаяся непосредственно в блоке, кг:')
        mass_gas = self.molecular_weight * volume_gas * self.pressure_equipment * pow(10, 6) / (
                    R * (self.temperature_equipment + C_TO_K))
        # print('4.Масса вещества, переходящая в парогазовую фазу при мгновенном вскипании перегретой жидкости блока (аппарата), кг:')
        fraction = 1 - math.exp(-self.heat_capacity_liquid * (((self.temperature_equipment + C_TO_K) - (
                self.boiling_temperature_liquid + C_TO_K) + math.fabs(
            (self.temperature_equipment + C_TO_K) - (self.boiling_temperature_liquid + C_TO_K))) / self.heat_evaporation_liquid))
        mass_instantly_boiling = fraction * mass_liguid

        # print('5. Масса вещества в проливе после мгновенного вскипания жидкости, кг:')
        mass_liguid_after_instantly_boiling = mass_liguid - mass_instantly_boiling
        # print(mass_liguid_after_instantly_boiling)

        # print('6. Давление насыщенного пара при расчетной температуре, кПа:')
        steam_pressure = P_ATM * math.exp((self.heat_evaporation_liquid * self.molecular_weight / R) * (
                (1 / (self.boiling_temperature_liquid + C_TO_K)) - (1 / (self.temperature_equipment + C_TO_K))))

        # print('steam_pressure ',steam_pressure)
        # print('7. Масса испарившегося в-ва от теплопритока поверхности, кг и время кипения, с:')

        if TEMPERATURE_SURFACE > self.boiling_temperature_liquid:
            time_boiling = ((TEMPERATURE_SURFACE - self.boiling_temperature_liquid + math.fabs(
                TEMPERATURE_SURFACE - self.boiling_temperature_liquid)) / (2 * self.heat_evaporation_liquid / 1000)) * pow(
                THERMAL_CONDUCTIVITY_SURFACE * HEAT_CAPACITY_SURFACE * DENSITY_SURFACE / math.pi, 1 / 2) * 1 / (
                                   pow(self.molecular_weight, 1 / 2) * pow(10, -6) * 9.93 * steam_pressure)
            mass_surface_heat_intake = min(self.__mass_boiling(time_boiling),
                                           mass_liguid_after_instantly_boiling)
            mass_surface_heat_intake = mass_liguid_after_instantly_boiling if mass_surface_heat_intake < 0 else mass_surface_heat_intake
        else:
            mass_surface_heat_intake = min(
                pow(10, -6) * (steam_pressure) * math.sqrt(self.molecular_weight * 1000) * 3600 * self.spill_square,
                mass_liguid_after_instantly_boiling)

        # print('8. Масса вещества оставшегося в проливе после испарения от теплопритока поверхности, кг:')
        mass_end = mass_liguid_after_instantly_boiling - mass_surface_heat_intake

        # print('9. Масса вещества перешедшее в газообразное состояние, кг:')
        mass_gas_end = mass_gas + mass_instantly_boiling + mass_surface_heat_intake
        return mass_gas_end

    def __mass_boiling(self, time_boiling: int):
        '''
        Ф-ция определения количества испарившейся жидкости при кипении и последующем испарении при захолаживании жидкости

        :param boiling_temperature_liquid: температура кипения, градусов Цельсия
        :param spill_square: площадь пролива, м2
        :param time_boiling: время кипения, с
        :return:
        '''
        sum_g_50 = 0.0001 * pow(self.boiling_temperature_liquid, 3) + 0.0067 * pow(self.boiling_temperature_liquid, 2) - \
                   3.4616 * self.boiling_temperature_liquid + 163.37  # интерполяция табл.2 прил.2 ОПВБ
        return sum_g_50 * (self.spill_square / 50) * (time_boiling / 180)  # ф-ла табл.2 прил.2 ОПВБ


if __name__ == '__main__':
    Evaporation(volume_equipment=3000, degree_filling=0.75, spill_square=3000,
                 pressure_equipment=0.07, temperature_equipment=20, density_liquid=750,
                 molecular_weight=0.1, boiling_temperature_liquid=35, heat_evaporation_liquid=295000,
                 adiabatic=1.23, heat_capacity_liquid=2100).report()

    print(Evaporation(volume_equipment=200, degree_filling=0.8, spill_square=500,
                 pressure_equipment=0.3, temperature_equipment=45, density_liquid=840,
                 molecular_weight=0.03, boiling_temperature_liquid=150, heat_evaporation_liquid=356000,
                 adiabatic=1.02, heat_capacity_liquid=1200).calculation())







