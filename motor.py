from kivymd.app import MDApp
from kivymd.uix.gridlayout import MDGridLayout
from speedmeter import SpeedMeter
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock


class Motor():
    def __init__(self):
        self.__on = False
        self.__speed = 0

    def __repr__(self):
        return "Motor %s, speed %s" % (self.power, self.speed)

    @property
    def power(self):
        if self.__on:
            return "On"
        else:
            return "Off"

    @power.setter
    def power(self, x):
        self.__on = x
        if not self.__on:
            self.__speed = 0

    @property
    def speed(self):
        return self.__speed

    @speed.setter
    def speed(self, x):
        if x > 120:
            x = 120
        if x < -120:
            x = -120
        self.__speed = x


class NoValueSpeedMeter(SpeedMeter):

    def value_str(self, n): return ''


class MotorController(FloatLayout):
    def __init__(self, **kwargs):
        super(MotorController, self).__init__(**kwargs)
        battery = self.ids.battery
        battery.value = 99
        battery.value = 100
        self.clockRunning = True
        Clock.schedule_interval(self.tick, 0.5)

    def tick(self, *args, **kwargs):
        battery = self.ids.battery
        battery.progress_color = (0, 1, 0, 1)
        speed_value = self.ids.speed_value

        if speed_value.value > 0:
            new_battery_value = battery.value - int(0.02 * speed_value.value)
            if new_battery_value < battery.min:
                battery.value = battery.min
            else:
                battery.value = new_battery_value

            if battery.value <= battery.min and speed_value.value > speed_value.min:
                speed_value.value = speed_value.value * 0.9 - 3
                if speed_value.value <= speed_value.min:
                    speed_value.value = speed_value.min
                    speed_value.disabled = True


class motor_controller(MDApp):
    def build(self):
        return MotorController()

    def set_speed(self):
        ids = self.root.ids
        motor.speed = ids.speed_value.value


# run the app
if __name__ == '__main__':
    motor = Motor()
    motor_controller().run()
