# -----------------------------------------------------------
# Класс предназначен для расчета ущерба
# Методические рекомендации по проведению количественного анализа риска аварий на конденсатопроводах и продуктопроводах
# Руководство по безопасности от 17.02.2023
# (C) 2024 Kuznetsov Konstantin, Kazan , Russian Federation
# email kuznetsovkm@yandex.ru
# -----------------------------------------------------------
# import matplotlib.pyplot as plt

# Социально-экономический ущерб
SPK1 = 2000_000  # страховая выплата по договору обязательного страхования гражданской ответственности ФЗ-225, руб
SPK2 = 1000_000  # единовременная страховая выплата в случае гибели работника на производстве ФЗ-125, руб
SPK3 = 10 * 12 * 10000  # десять годовых заработков при гибели работника, руб
SPOG1 = 25000  # страховые выплаты по договору обязательного страхования, руб
SPOG2 = 4000  # социальное пособие на погребение, руб
SZHIZ = 0  # 1500_000 стоимость среднестатистической жизни человека, руб
SB = 300_000  # средний размер пособия по временной нетрудоспособности, руб
SIP = 21769  # средний размер пенсии одному лицу, ставшему инвалидом, руб
SM = 300_000  # средний размер расходов, связанных с повреждением здоровья одного пострадавшего, руб
PART_DIRECT_DAMAGE = 0.2  # доля ущерба от прямого ущерба на часть повреждений
K_DESTROY = 1.85  # коэффициент на монтаж/ демонтаж
# Ущерб воздух
K_YEAR_INDEX = 1.32  # См. Постановление Правительства РФ от 17 апреля 2024 г. N 492 "О применении в 2024 году ставок...
BASE_SUB_COST = 108  # См. Постановление Правительства РФ от 13.09.2016 № 913  «О ставках платы за негативное воздействие...
KSR = 25  # коэффициент к ставкам платы за выброс соответствующего i-го загрязняющего вещества за массу выбросов
KOT = 1  # дополнительный коэффициент к ставкам платы в отношении территорий и объектов, находящихся под особой охраной в соответствии с федеральными законами
# Ущерб почва
CZ = 1.5  # степень загрязнения почвы
KR = 1  # показатель в зависимости от глубины загрязнения
KISX = 1.6  # показатель в зависимости от кат.земель и целевого назначения
TX = 500  # руб/м2(расценка для исчисления размера вреда

PART_ECOL=0.25


class Damage:
    def __init__(self, dead_man: int, injured_man: int, volume_equipment: int, diametr_pipe: int, lenght_pipe: float,
                 degree_damage: float, m_out_spill: float, m_in_spill: float, S_spill: int):
        '''
        dead_man - погибшие люди, чел
        injured_man - пострадавшие люди, чел
        volume_equipment - объем емкостного оборудования суммарный который пострадал, м3
        diametr_pipe - диаметр трубопровода средний, мм
        lenght_pipe - длина трубопровода суммарный который пострадал, км (поврежденная часть требующая замены)
        degree_damage - степень повреждения, (0...1)
        m_out_spill - испарилось вещества, т
        m_in_spill - сгорело в проливе, т
        S_spill - площадь пролива, м2
        '''
        self.dead_man = dead_man
        self.injured_man = injured_man
        self.volume_equipment = volume_equipment
        self.diametr_pipe = diametr_pipe
        self.lenght_pipe = lenght_pipe
        self.degree_damage = degree_damage
        self.m_out_spill = m_out_spill
        self.m_in_spill = m_in_spill
        self.S_spill = S_spill

    def socio_economic_damage(self):
        '''Социально-экономический ущерб'''
        dead_damage = (SPK1 + SPK2 + SPK3 + SPOG1 + SPOG2) * self.dead_man + SZHIZ  # ущерб по погибшим
        injured_damage = (SB + SIP + SM) * self.injured_man  # ущерб по пострадавшим
        se_damage = dead_damage + injured_damage
        return se_damage

    def direct_damage(self):
        '''Прямой ущерб'''
        destroyed = (self.__approx_equipment_cost(self.volume_equipment) + self.__approx_pipeline_cost(
            self.diametr_pipe) * self.lenght_pipe) * self.degree_damage * K_DESTROY  # уничтожено
        injuries = PART_DIRECT_DAMAGE * destroyed * (1 - self.degree_damage) * K_DESTROY

        return destroyed + injuries

    def damage_to_localization(self):
        'Затраты на локализацию и ликвидацию'
        return 0.1 * self.direct_damage()

    def environmental_damage(self):
        '''Экологический ущерб'''
        ecolog_damage = (
            self.__damage_air(), self.__damage_air_fire(), self.__damage_earth())
        return (ecolog_damage, sum(ecolog_damage))

    def sum_damage(self):
        socio = self.socio_economic_damage()
        direct = self.direct_damage()
        localization = self.damage_to_localization()
        ecolog = self.environmental_damage()[1]*PART_ECOL
        indirect = 0.259 * direct
        sum_ = direct + localization + socio + ecolog + indirect
        res = [round(i / pow(10, 6), 3) for i in (direct, localization, socio, ecolog, indirect, sum_)]
        return res

    def __damage_air(self):
        """
        Ущерб атмосферному воздуху при испарении углеводородов

        При расчете ущерба от загрязнения воздуха при расчете ущерба
        принимались следующие коэффициенты:
        Загрязняющее вещество - Углеводороды С1-С5
        Норматив платы, руб./т (Мсрi) - 108
        Коэффициент за 2024 г. (Нплi) - 1,32
        Коэффициент Кср - 25 (ПРИКАЗ Минприроды) от 9 января 2017 г. N 3

        """
        tax_1_tonn = BASE_SUB_COST * KOT * K_YEAR_INDEX * KSR

        return int(self.m_out_spill * tax_1_tonn)

    def __damage_air_fire(self):
        """
        Ущерб атмосферному воздуху при горении нефти

        ____________________________________________________
        Ущерб от загрязнения атмосферного воздуха
        при сгорании 1 тонны нефти:
        ____________________________________________________
        Загрязняющее вещество - Оксид углерода (СО)* (0,798т)
        Норматив платы, руб./т (Мсрi) - 1.6
        ____________________________________________________
        Загрязняющее вещество - Оксиды азота (NОx)* (0,066т)
        Норматив платы, руб./т (Мсрi) - 138,8
        ____________________________________________________
        Загрязняющее вещество - Оксиды серы (SO2)** (0,26т)
        Норматив платы, руб./т (Мсрi) - 45,4
        ____________________________________________________
        Загрязняющее вещество - Сероводород (H2S)* (0,001т)
        Норматив платы, руб./т (Мсрi) - 686,2
        ____________________________________________________
        Загрязняющее вещество - Сажа (С)** (1.615т)
        Норматив платы, руб./т (Мсрi) - 109,5
        ____________________________________________________
        Загрязняющее вещество - Синильная кислота (НСN)* (0,01т)
        Норматив платы, руб./т (Мсрi) - 547,4
        ____________________________________________________
        Загрязняющее вещество - Формальдегид (HCHO)* (0,01т)
        Норматив платы, руб./т (Мсрi) - 1823,6
        ____________________________________________________
        Загрязняющее вещество - Органич. к-ты (на СН3СООН)* (0,14т)
        Норматив платы, руб./т (Мсрi) - 93,5

        Коэффициент за 2021 г. (Нплi) - 1,08
        Коэффициент Кср - 25 (ПРИКАЗ Минприроды от 9 января 2017 г. N 3)
        """

        tax_CO = 1.6 * K_YEAR_INDEX * KSR * 0.798
        tax_NOx = 138.8 * K_YEAR_INDEX * KSR * 0.066
        tax_SO2 = 45.4 * K_YEAR_INDEX * KSR * 0.26
        tax_H2S = 686.2 * K_YEAR_INDEX * KSR * 0.001
        tax_C = 109.5 * K_YEAR_INDEX * KSR * 1.615
        tax_HCN = 547.4 * K_YEAR_INDEX * KSR * 0.01
        tax_HCHO = 1823.6 * K_YEAR_INDEX * KSR * 0.01
        tax_CH3COOH = 93.5 * K_YEAR_INDEX * KSR * 0.14

        tax_1_tonn = tax_CO + tax_NOx + tax_SO2 + tax_H2S + tax_C + tax_HCN + tax_HCHO + tax_CH3COOH

        return int(self.m_in_spill * tax_1_tonn)

    def __damage_earth(self):
        """
        Ущерб от загрязнения 1 м2 нефтью
        """

        tax_1m2 = CZ * KR * KISX * TX

        return int(self.S_spill * tax_1m2)

    def __approx_equipment_cost(self, volume: int):
        # данные апроксимировал с http://rezervuarstroy.ru/page/prajs-listy.html
        # стоимость указана на монтаж 1 нового резервуара
        if volume == 0:
            return 0
        else:
            return 7E-07 * pow(volume, 3) - 0.1867 * pow(volume, 2) + 2583.1 * volume + 257377

    def __approx_pipeline_cost(self, diametr: int):
        # данные апроксимировал с http://www.ozti.org/upload/iblock/637/COSTS.pdf
        # стоимость указана на прокладку 1 км трубопровода
        if diametr == 0:
            return 0
        else:
            return 10511 * diametr + 536156


if __name__ == '__main__':
    damage = Damage(dead_man=1, injured_man=1, volume_equipment=500, diametr_pipe=114, lenght_pipe=2.589,
                    degree_damage=1, m_out_spill=0.58, m_in_spill=3.69, S_spill=258).sum_damage()

    # index = ['Соц.-эконом. ущерб', 'Прямой ущерб', 'Затраты на ЛЛА', 'Эколог. ущерб']
    # index = ['а', 'б', 'в', 'г']
    # values = [damage[0], damage[1], damage[2], damage[3]]
    # plt.bar(index, values)
    # plt.ylabel('Ущерб, млн.руб (по видам)')
    # plt.show()
