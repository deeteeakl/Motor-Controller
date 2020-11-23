from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from speedmeter import SpeedMeter
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
import sys

if sys.platform.startswith('linux'):
    import RPi.GPIO as GPIO

# define the pins connected to L293D
_MOTORPIN1 = 13
_MOTORPIN2 = 11
_ENABLEPIN = 15
_MINSPEED = 0
_MAXSPEED = 100


class Motor():
    def __init__(self, speed=0):
        if sys.platform.startswith('linux'):
            GPIO.cleanup()
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(_MOTORPIN1, GPIO.OUT)   # set pins to OUTPUT mode
            GPIO.setup(_MOTORPIN2, GPIO.OUT)
            GPIO.setup(_ENABLEPIN, GPIO.OUT)
            # creat PWM and set Frequency to 1KHz        self.__on = False
            self.__p = GPIO.PWM(_ENABLEPIN, 1000)
        self.__on = False
        self.speed = speed
        self.forward = True
        #print("motor instantiated")

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
        if x > _MAXSPEED:
            x = _MAXSPEED
        self.__speed = x
        if sys.platform.startswith('linux'):
            if self.__on:
                # motoRPin1 output HIHG level
                GPIO.output(_MOTORPIN1, GPIO.HIGH)
                # motoRPin2 output LOW level
                GPIO.output(_MOTORPIN2, GPIO.LOW)
                if self.speed > 0:
                    print('Turn Forward...%s' % (self.speed))
                    self.__p.start(self.speed)
            else:
                GPIO.output(_MOTORPIN1, GPIO.LOW)
                GPIO.output(_MOTORPIN2, GPIO.LOW)
                print('Motor Stop...')


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
        speed_value = self.ids.speed_value
        power_button = self.ids.power_button

        if speed_value.value > 0:
            self.__on = True
            new_battery_value = battery.value - int(0.02 * speed_value.value)
            if new_battery_value < battery.min:
                battery.value = battery.min
            else:
                battery.value = new_battery_value

            if (battery.value <= battery.min or power_button.active == False) and speed_value.value > speed_value.min:
                speed_value.value = speed_value.value * 0.9 - 5
                if speed_value.value <= speed_value.min:
                    speed_value.value = speed_value.min
                    speed_value.disabled = True

        if power_button.active == False and battery.value < 100:
            new_battery_value = battery.value + 1
            if new_battery_value < battery.max:
                battery.value = new_battery_value
            else:
                battery.value = battery.max


class motor_controller(App):
    def __init__(self, motor, **kwargs):
        super(motor_controller, self).__init__(**kwargs)
        self.motor = motor

    def build(self):
        return MotorController()

    def set_speed(self):
        speed_value = self.root.ids.speed_value
        self.motor.speed = speed_value.value

    def power_button(self, instance, value):
        speed_value = self.root.ids.speed_value
        self.motor.power = value
        speed_value.disabled = not value

        # print(self.motor.power)

    def change_direction(self):
        direction = self.root.ids.direction
        self.motor.forward = not self.motor.forward
        print(self.motor.forward)
        if self.motor.forward:
            direction.background_down = "reverse.jpeg"
            direction.background_normal: "forward.jpeg"
        else:
            direction.background_down = "forward.jpeg"
            direction.background_normal: "reverse.jpeg"


# run the app
if __name__ == '__main__':
    motor = Motor()
    motor_controller(motor).run()
