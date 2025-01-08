# Модуль мгновенного расхода жидкости и газа при постоянном отверстии
# @version: 1.0
# @date: 2024-08-29
# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------
# @author: Kuznetsov Konstantin, kuznetsov@yandex.ru
# (C) 2024
# ------------------------------------------------------------------------------------
import math

MU = 0.6  # коэф.истечения
Ahol = 0.000314  # м2 (отверстие с диаметром 20 мм)
MPA_TO_PA = pow(10, 6)
G = 9.81



class Outflow:

    def __init__(self, pressure_equipment: float):
        self.pressure_equipment = pressure_equipment

    def outflow_liquid(self, density_liquid: int):
        return MU * density_liquid * Ahol * math.sqrt(2 * (self.pressure_equipment * MPA_TO_PA / density_liquid) + 2 * G)/4 # на 4 поделил для уменьшения

    def outflow_gas(self):
        'Аппроксимация газа при отверстии 20 мм, плотности газа 3 кг/м3'
        return -0.0588 * pow(self.pressure_equipment, 2) + 0.2858 * self.pressure_equipment + 0.0645


if __name__ == '__main__':
    print(Outflow(0.5).outflow_liquid(850))
