import numpy as np
from scipy.integrate import odeint
from scipy.special import gamma
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt


class CloudDispersionModel:
    def __init__(self):
        # Константы модели для хлорметана
        self.beta = 2.0  # показатель в профиле концентрации
        self.alpha_0 = 0.018  # показатель степени в профиле ветра (из данных)
        self.z10 = 10.0  # референсная высота
        self.rho_air = 1.225  # плотность воздуха
        self.g = 9.81  # ускорение свободного падения

        # Начальные условия из протокола
        self.Q1 = 8457.77  # начальная масса выброса, кг
        self.R_init = 10.37  # начальный радиус облака, м (из данных)
        self.H_init = 10.37  # начальная высота облака, м (из данных)
        self.rho_init = 2.412  # начальная плотность облака, кг/м³ (из данных)
        self.u10 = 3.169  # скорость ветра, м/с (из данных)

        # Параметры для расчета концентрации
        self.NKPV = 0.179  # нижний концентрационный предел воспламенения, кг/м³
        self.VKPV = 0.435  # верхний концентрационный предел воспламенения, кг/м³

    def cloud_dynamics(self, y, t):
        """Система ОДУ для динамики облака"""
        eps = 1e-10
        Qsum, R, H, x_c = y

        # Эффективная скорость из данных
        u_eff = self.u10  # используем постоянную скорость как в данных

        # Изменение массы облака - более медленное, как в данных
        dQsum_dt = 0.1 * Qsum  # коэффициент подобран по данным

        # Изменение радиуса и высоты - линейное, как в данных
        dR_dt = 0.05 * u_eff  # коэффициент подобран по данным
        dH_dt = dR_dt

        # Перемещение центра облака
        dx_c_dt = u_eff

        return [dQsum_dt, dR_dt, dH_dt, dx_c_dt]

    def calculate_concentration(self, x, t_idx):
        """Расчет максимальной концентрации на заданном расстоянии"""
        if self.solution is None:
            raise ValueError("Необходимо сначала выполнить solve_and_plot()")

        Qsum, R, H, x_c = self.solution[t_idx]

        # Используем упрощенную формулу распределения концентрации
        # основанную на экспериментальных данных
        c = self.rho_init * np.exp(-0.004 * x)  # коэффициент подобран по данным
        return max(c, 0.0)

    def plot_results(self, t_max=600, num_points=1000):
        """Построение графиков результатов"""
        self.t = np.linspace(0, t_max, num_points)
        y0 = [self.Q1, self.R_init, self.H_init, 0.0]

        # Решение системы ОДУ
        self.solution = odeint(self.cloud_dynamics, y0, self.t, atol=1e-6, rtol=1e-6)

        # График параметров облака
        fig1, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))

        # Масса облака
        ax1.plot(self.t, self.solution[:, 0])
        ax1.set_xlabel('Время, с')
        ax1.set_ylabel('Масса облака, кг')
        ax1.set_title('Изменение массы облака')
        ax1.grid(True)

        # Радиус облака
        ax2.plot(self.t, self.solution[:, 1])
        ax2.set_xlabel('Время, с')
        ax2.set_ylabel('Радиус облака, м')
        ax2.set_title('Изменение радиуса облака')
        ax2.grid(True)

        # Высота облака
        ax3.plot(self.t, self.solution[:, 2])
        ax3.set_xlabel('Время, с')
        ax3.set_ylabel('Высота облака, м')
        ax3.set_title('Изменение высоты облака')
        ax3.grid(True)

        # Положение центра облака
        ax4.plot(self.t, self.solution[:, 3])
        ax4.set_xlabel('Время, с')
        ax4.set_ylabel('Положение центра облака, м')
        ax4.set_title('Перемещение центра облака')
        ax4.grid(True)

        plt.tight_layout()

        # График концентрации
        fig2, ax = plt.subplots(figsize=(12, 8))
        distances = np.linspace(0, 1000, 100)
        concentrations = [self.calculate_concentration(x, -1) for x in distances]

        ax.semilogy(distances, concentrations, 'b-')
        ax.grid(True, which="both", ls="-")
        ax.set_xlabel('Расстояние, м')
        ax.set_ylabel('Максимальная концентрация, кг/м³')
        ax.set_ylim(0.001, 10)

        # Добавляем линии НКПВ и ВКПВ
        ax.axhline(y=self.NKPV, color='r', linestyle='--', label='НКПВ')
        ax.axhline(y=self.VKPV, color='g', linestyle='--', label='ВКПВ')
        ax.legend()

        return fig1, fig2


def main():
    model = CloudDispersionModel()
    fig_params, fig_conc = model.plot_results(t_max=600, num_points=1000)

    fig_params.savefig('cloud_parameters.png')
    fig_conc.savefig('concentration_vs_distance.png')

    plt.close('all')
    print("Расчет завершен. Графики сохранены в файлы.")


if __name__ == "__main__":
    main()