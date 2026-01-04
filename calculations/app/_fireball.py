# -----------------------------------------------------------
# Класс предназначен для расчета "огненного шара"
#
# Приказ МЧС № 404 от 10.07.2009
# (C) 2022 Kuznetsov Konstantin, Kazan , Russian Federation
# email kuznetsovkm@yandex.ru
# -----------------------------------------------------------

import math
from calculations.app._probit import Probit
from calculations.app._found_nearest_value import get_nearest_value


class Fireball:

    def fireball_point(self, mass: float, ef: float, radius: float) -> tuple:

        """
        :@param mass: масса огненного шара, кг
        :@param ef: ср.поверхностная плотность теплового излучения, кВт/м2 (например ef = 450)
        :@param radius: расстояние от геометрического центра шара, м (например radius = 20)

        :@return: tuple: q_term: интенсивность теплового излучения, кВт/м2
                         d_term: доза теплового излучения, кДж/м2
        :@raise проверка функции на введенные нулевые значения
        """
        # Проверки
        if 0 in (mass, ef, radius):
            raise ValueError(f'Фукнция не может принимать нулевые параметры')

        D_eff = 5.33 * pow(mass, 0.327)
        H_eff = D_eff / 2
        t_s = 0.92 * pow(mass, 0.303)

        Fq = (H_eff / D_eff + 0.5) / (4 * ((((H_eff / D_eff + 0.5) ** 2) +
                                            ((radius / D_eff) ** 2)) ** 1.5))

        tay = math.exp(-7 * (10 ** (-4) * (((radius ** 2 + H_eff ** 2) ** (1 / 2)) - D_eff / 2)))

        q_ball = round(ef * Fq * tay, 2)
        d_term = round(q_ball * t_s, 2)

        res = (q_ball, d_term)

        return res

    def fireball_array(self, mass: float, ef: float) -> tuple:

        """
        :@param mass: масса огненного шара, кг
        :@param ef: ср.поверхностная плотность теплового излучения, кВт/м2 (например ef = 450)

        :@return tuple: (radius, q_term, d_term, probit, probability): кортеж списков параметров
        :@raise проверка функции на введенные нулевые значения
        """

        radius_arr = []
        q_term_arr = []
        d_term_arr = []
        probit_arr = []
        probability_arr = []

        # максимальная интенсивность теплового излучения
        radius = 1
        q_term = self.fireball_point(mass, ef, radius)[0]
        t_s = 0.92 * (mass ** 0.303)

        # просчитаем значения пока интенсивность теплового излучения больше 1.2 кВт/м2
        while q_term > 1.2:
            res = self.fireball_point(mass, ef, radius)
            q_term = res[0]
            d_term = res[1]
            probit = Probit().probit_fireball(t_s, q_term)
            probability = Probit().probability(probit)
            # append
            radius_arr.append(radius)
            q_term_arr.append(q_term)
            d_term_arr.append(d_term)
            probit_arr.append(probit)
            probability_arr.append(probability)
            radius += 0.5

        result = (radius_arr, q_term_arr, d_term_arr, probit_arr, probability_arr)

        return result

    def termal_class_zone(self, mass: float, ef: float) -> list:
        """
        :@param mass: масса огненного шара, кг
        :@param ef: ср.поверхностная плотность теплового излучения, кВт/м2 (например ef = 450)

        :@return: : list: [radius_CZA]: список отсортированных зон
        """

        res_list = self.fireball_array(mass, ef)

        # Calculate classified_zone_array
        classified_zone_array = [600, 320, 220, 120]  # CZA
        radius_CZA = []
        d_term_array = res_list[2]
        radius_array = res_list[0]

        for CZA in classified_zone_array:
            ind = d_term_array.index(get_nearest_value(d_term_array, CZA))
            radius_CZA.append(radius_array[ind])
        return radius_CZA


if __name__ == '__main__':
    # ev_class = Fireball()
    # mass = 2.54 * (10 ** 5)
    # ef = 450
    #
    # print(ev_class.termal_class_zone(mass, ef))

    # ГОСТ 12.3.047-98 прил.Д
    ev_class = Fireball()
    mass = 2000
    ef = 450
    radius = 100
    print(ev_class.fireball_point(mass, ef, radius)) #(по ГОСТ q_ball=12.9)
