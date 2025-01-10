import numpy as np
from PySide6.QtWidgets import QVBoxLayout, QWidget
import matplotlib
from matplotlib import pyplot as plt

matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import numpy as np

class FNFGPlotsWidget(QWidget):
    """Виджет для отображения F/N и F/G диаграмм"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        layout = QVBoxLayout(self)

        # Создаем фигуру с тремя графиками
        self.figure, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(12, 5))
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout.addWidget(self.canvas)

        # Настраиваем графики
        self.ax1.set_xlabel('N, Количество погибших')
        self.ax1.set_ylabel('F, Частота возникновения, 1/год')
        self.ax1.set_title('F/N диаграмма')
        self.ax1.grid(True)


        self.ax2.set_xlabel('G, Ущерб, млн.руб.')
        self.ax2.set_ylabel('F, Частота возникновения, 1/год')
        self.ax2.set_title('F/G диаграмма')
        self.ax2.grid(True)

        self.figure.tight_layout()

    def _sum_data_for_fn(self, data: list):
        '''
        Функция вычисления суммирования вероятностей F при которой пострадало не менее N человек
        :param data: данные вида [[3.8e-08, 1],[5.8e-08, 2],[1.1e-08, 1]..]
        :return: данные вида: {1: 0.00018, 2: 0.012, 3: 6.9008e-06, 4: 3.8e-08, 5: 7.29e-05}
        '''
        uniq = set(sorted([i[1] for i in data]))
        result = dict(zip(uniq, [0] * len(uniq)))

        for item_data in data:
            for item_uniq in uniq:
                if item_data[1] >= item_uniq:
                    result[item_uniq] = result[item_uniq] + item_data[0]

        if 0 in result:
            del result[0]  # удалить суммарную вероятность где пострадало 0 человек
        return result

    def _sum_data_for_fg(self, data: list):
        '''
        Функция вычисления суммирования вероятностей F при которой ущерб не менее G млн.руб
        :param data: данные вида [[3.8e-08, 1.2],[5.8e-08, 0.2],[1.1e-08, 12.4]..]
        :return: данные вида: {0.2: 0.00018, 1: 0.012, 3: 6.9008e-06, 5: 3.8e-08, 6.25: 7.29e-05}
        '''
        uniq = np.arange(0, max([i[1] for i in data])+max([i[1] for i in data]) / 7, max([i[1] for i in data]) / 7)

        result = dict(zip(uniq, [0] * len(uniq)))

        for item_data in data:
            for item_uniq in uniq:
                if item_data[1] >= item_uniq:
                    result[item_uniq] = result[item_uniq] + item_data[0]

        del result[0]  # удалить суммарную вероятность где ущерб 0
        return result

    def update_plots(self, results):
        """Обновление графиков на основе результатов расчета"""
        if not results:
            return

        # Очищаем графики
        self.ax1.clear()
        self.ax2.clear()

        # Построение Fn диаграммы
        casualty_data = []
        for result in results:
            if result.casualties > 0:
                casualty_data.append((result.probability, result.casualties))

        sum_data = self._sum_data_for_fn(casualty_data)

        if casualty_data:
            people, probability = list(sum_data.keys()), list(sum_data.values())
            # для сплошных линий
            chart_line_x = []
            chart_line_y = []
            for i in people:
                chart_line_x.extend([i - 1, i, i, i])
                chart_line_y.extend([probability[people.index(i)], probability[people.index(i)], None, None])
            # для пунктирных линий
            chart_dot_line_x = []
            chart_dot_line_y = []
            for i in people:
                if i == people[-1]:
                    chart_dot_line_x.extend([i, i])
                    chart_dot_line_y.extend([probability[people.index(i)], 0])
                    break
                chart_dot_line_x.extend([i, i])
                chart_dot_line_y.extend([probability[people.index(i)], probability[people.index(i) + 1]])
            # Создание графика
            # Построение основной диаграммы
            self.ax1.semilogy(chart_line_x, chart_line_y, color='b', linestyle='-', marker='.')
            self.ax1.semilogy(chart_dot_line_x, chart_dot_line_y, color='b', linestyle='--', marker='.')
            self.ax1.set_xticks(people)
            self.ax1.grid(True)

        # Построение F/G диаграммы
        damage_data = []
        for result in results:
            if result.casualties > 0:
                damage_data.append((result.probability, result.casualties))

        sum_data = self._sum_data_for_fg(damage_data)

        if damage_data:
            damage, probability = list(sum_data.keys()), list(sum_data.values())
            # для сплошных линий
            chart_line_x = []
            chart_line_y = []
            for i in damage:
                if damage[0] == i:
                    chart_line_x.extend([0, i, i, i])
                    chart_line_y.extend([probability[damage.index(i)], probability[damage.index(i)], None, None])
                elif damage[-1] == i:
                    chart_line_x.extend([damage[damage.index(i)-1], damage[damage.index(i)-1], i, i])
                    chart_line_y.extend([probability[damage.index(i)], probability[damage.index(i)], probability[damage.index(i)], probability[damage.index(i)]])
                    break
                else:
                    chart_line_x.extend([damage[damage.index(i) - 1], i, i, i])
                    chart_line_y.extend([probability[damage.index(i)], probability[damage.index(i)], None, None])

            # для пунктирных линий
            chart_dot_line_x = []
            chart_dot_line_y = []
            for i in damage:
                if i == damage[-1]:
                    chart_dot_line_x.extend([i, i])
                    chart_dot_line_y.extend([probability[damage.index(i)], probability[damage.index(i)]])
                    chart_dot_line_x.extend([i, i])
                    chart_dot_line_y.extend([probability[damage.index(i)], 0])
                    break
                chart_dot_line_x.extend([i, i])
                chart_dot_line_y.extend([probability[damage.index(i)], probability[damage.index(i) + 1]])

            # Создание графика
            # Построение основной диаграммы
            self.ax2.semilogy(chart_line_x, chart_line_y, color='r', linestyle='-', marker='.')
            self.ax2.semilogy(chart_dot_line_x, chart_dot_line_y, color='r', linestyle='--', marker='.')
            self.ax2.set_xticks(damage)
            self.ax2.grid(True)


        # Обновляем подписи осей
        self.ax1.set_xlabel('N, Количество погибших')
        self.ax1.set_ylabel('F, Частота возникновения, 1/год')
        self.ax1.set_title('F/N диаграмма')

        self.ax2.set_xlabel('G, Ущерб, млн.руб, млн.руб.')
        self.ax2.set_ylabel('F, Частота возникновения, 1/год')
        self.ax2.set_title('F/G диаграмма')

        self.figure.tight_layout()
        self.canvas.draw()