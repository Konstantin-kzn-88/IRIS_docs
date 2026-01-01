# -----------------------------------------------------------
# Класс предназначен для расчета взрыва ТВС
#
# CП 12.13130-2009
# (C) 2022 Kuznetsov Konstantin, Kazan , Russian Federation
# email kuznetsovkm@yandex.ru
# -----------------------------------------------------------

from calculations.app._probit import Probit
from calculations.app._found_nearest_value import get_nearest_value


class Explosion:

    def burn_rate(self, class_substance: int, view_space: int, mass: float) -> float:  # скорость горения
        """
        :@param class_substance: класс взрывоопасности вещества (1-4)
        :@param view_space: класс окружающего пространства (1-4)
        :@param mass: масса испарившегося вещества, кг

        :@return: : float: v_burn_rate

        :@raise проверка функции на введенные нулевые значения
        """
        # Проверки
        if 0 in (class_substance, view_space, mass):
            raise ValueError(f'Фукнция не может принимать нулевые параметры')

        class_substance = int(class_substance)
        view_space = int(view_space)

        tmp = ((500, 500, 300, 200),
               (500, 300, 200, 150),
               (300, 200, 150, 43 * pow(mass, 1 / 6)),
               (200, 150, 43 * pow(mass, 1 / 6), 26 * pow(mass, 1 / 6)))

        v_burn_rate = tmp[class_substance - 1][view_space - 1] if view_space >= 1 and view_space <= 4 else min(tmp)
        return v_burn_rate

    def explosion_point(self, class_substance: int, view_space: int, mass: float,
                        heat_of_combustion: float, sigma: int, energy_level: int, radius: float) -> tuple:

        """
        :@param class_substance: класс взрывоопасности вещества (1-4)
        :@param view_space: класс окружающего пространства (1-4)
        :@param mass: масса испарившегося вещества, кг
        :@param heat_of_combustion: теплота сгорания, кДж/кг (например heat_of_combustion = 46000)
        :@param sigma: тип смеси  (4- парогазовая, 7 - газовая)
        :@param energy_level: тип ТВС  (1- легкая, 2 - тяжелая)
        :@param radius: расстояние от геометрического центра взрыва, м (например radius = 20)

        :@return: : list: delta_p: избыточное давление ВУВ, кПа
                         impulse: импульс, Па*с

        :@raise проверка функции на введенные нулевые значения
        """

        # Проверки
        if 0 in (class_substance, view_space, mass, heat_of_combustion, sigma, energy_level, radius):
            raise ValueError(f'Фукнция не может принимать нулевые параметры')

        class_substance = int(class_substance)
        view_space = int(view_space)

        v_burn_rate = self.burn_rate(class_substance, view_space, mass)

        E = mass * heat_of_combustion * energy_level * 1000

        if E < 1:
            E = 0.1 * heat_of_combustion * energy_level * 1000

        Rx = radius / ((E / 101300) ** (1 / 3))
        if Rx > 0.34:
            Rx = radius / ((E / 101300) ** (1 / 3))
        elif Rx <= 0.34:
            Rx = 0.34

        delta_p = ((v_burn_rate / 340) ** 2) * \
                  (((sigma - 1) / sigma) * ((0.83 / Rx) - 0.14 / (Rx ** 2))) * 101.3

        impulse = (v_burn_rate / 340) * ((sigma - 1) / sigma) * \
                  (1 - 0.4 * (v_burn_rate / 340) * ((sigma - 1) / sigma)) * \
                  (0.06 / Rx + 0.01 / (Rx ** 2) - 0.0025 / (Rx ** 3)) * \
                  (101325 ** (2 / 3)) * (E ** (1 / 3)) / 340

        delta_p = round(delta_p, 2)
        impulse = round(impulse, 2)

        res = (delta_p, impulse)

        return res

    def explosion_array(self, class_substance: int, view_space: int, mass: float,
                        heat_of_combustion: float, sigma: int, energy_level: int) -> tuple:

        """
        :@param class_substance: класс взрывоопасности вещества (1-4)
        :@param view_space: класс окружающего пространства (1-4)
        :@param mass: масса испарившегося вещества, кг
        :@param heat_of_combustion: теплота сгорания, кДж/кг (например heat_of_combustion = 46000)
        :@param sigma: тип смеси  (4- парогазовая, 7 - газовая)
        :@param energy_level: тип ТВС  (1- легкая, 2 - тяжелая)

        :@return: : list: [radius, delta_p_arr, impulse_arr, probit, probability]: список списков параметров
        """

        radius_arr = []
        delta_p_arr = []
        impulse_arr = []
        probit_arr = []
        probability_arr = []

        # максимальная избыточное давление
        radius = 0.1
        delta_p = self.explosion_point(class_substance, view_space,
                                       mass, heat_of_combustion, sigma,
                                       energy_level, radius)[0]

        # просчитаем значения пока взрыв больше 2.9 кПА
        while delta_p > 1.9:
            res = self.explosion_point(class_substance, view_space,
                                       mass, heat_of_combustion, sigma,
                                       energy_level, radius)
            delta_p = res[0]
            impulse = res[1]
            probit = round(Probit().probit_explosion(delta_p, impulse), 3)
            probability = round(Probit().probability(probit), 3)
            # append
            radius_arr.append(radius)
            delta_p_arr.append(delta_p)
            impulse_arr.append(impulse)
            probit_arr.append(probit)
            probability_arr.append(probability)
            radius += 0.5

        result = (radius_arr, delta_p_arr, impulse_arr, probit_arr, probability_arr)

        return result

    def explosion_class_zone(self, class_substance: int, view_space: int, mass: float,
                             heat_of_combustion: float, sigma: int, energy_level: int) -> list:
        """
        :@param class_substance: класс взрывоопасности вещества (1-4)
        :@param view_space: класс окружающего пространства (1-4)
        :@param mass: масса испарившегося вещества, кг
        :@param heat_of_combustion: теплота сгорания, кДж/кг (например heat_of_combustion = 46000)
        :@param sigma: тип смеси  (4- парогазовая, 7 - газовая)
        :@param energy_level: тип ТВС  (1- легкая, 2 - тяжелая)

        :@return: : list: [radius_CZA]: список отсортированных зон
        """

        res_list = self.explosion_array(class_substance, view_space,
                                        mass, heat_of_combustion, sigma,
                                        energy_level)

        # Calculate classified_zone_array
        classified_zone_array = [100, 70, 28, 14, 5, 3.5]  # CZA
        radius_CZA = []
        delta_p_array = res_list[1]
        radius_array = res_list[0]

        for CZA in classified_zone_array:
            if len(delta_p_array) == 0:
                radius_CZA.append(0)
            elif CZA > delta_p_array[0]:
                radius_CZA.append(0)
            else:
                ind = delta_p_array.index(get_nearest_value(delta_p_array, CZA))
                radius_CZA.append(radius_array[ind])
        return radius_CZA


if __name__ == '__main__':
    ev_class = Explosion()
    class_substance = 3
    view_space = 2
    mass = 1980
    heat_of_combustion = 44000
    sigma = 7
    energy_level = 2

    print(ev_class.explosion_class_zone(class_substance, view_space,
                                        mass, heat_of_combustion, sigma,
                                        energy_level))
