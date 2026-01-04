# -----------------------------------------------------------
# Класс предназначен для расчета "вспышки"
#
# Приказ МЧС № 404 от 10.07.2009
# (C) 2022 Kuznetsov Konstantin, Kazan , Russian Federation
# email kuznetsovkm@yandex.ru
# -----------------------------------------------------------

class LCLP:

    def lower_concentration_limit(self, mass: float, mol_mass: float, t_boiling: float,
                                  lower_concentration: float) -> list:
        """
        Расчет зон НКПР и пожара-вспышки для паров ЛВЖ

        Parametrs:
        :@param масса паров ЛВЖ и ГГ, кг;
        :@param mol_mass - молекулярная масса, кг/кмоль
        :@param t_boiling - температура кипения, град.С
        :@param lower_concentration - нижний концентрационный предел, % об.;

        Return:
        :@return radius (float)
        """
        # Проверки
        if 0 in (mass, mol_mass, lower_concentration):
            raise ValueError(f'Фукнция не может принимать нулевые параметры')

        vapour_density = mol_mass / (22.413 * (1 + 0.00367 * t_boiling))
        # print(vapour_density)
        R_LCLP = round(7.8 * ((mass / (vapour_density * lower_concentration)) ** 0.33), 2)
        R_f = round((R_LCLP * 1.2), 2)

        return [R_LCLP, R_f]


if __name__ == '__main__':
    ev_class = LCLP()
    mass = 9.81
    mol_mass = 90
    t_boiling = 60
    lower_concentration = 2.9

    print(ev_class.lower_concentration_limit(mass, mol_mass, t_boiling, lower_concentration))
