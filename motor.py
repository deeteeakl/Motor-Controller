from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from speedmeter import SpeedMeter
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.properties import NumericProperty

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
    def __init__(self):
        if sys.platform.startswith('linux'):
            print("on linux -- prob should check for gpio")
            GPIO.cleanup()
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(_MOTORPIN1, GPIO.OUT)
            GPIO.setup(_MOTORPIN2, GPIO.OUT)
            GPIO.setup(_ENABLEPIN, GPIO.OUT)
            self.__p = GPIO.PWM(_ENABLEPIN, 1000)
            # initialise to stop
            GPIO.output(_MOTORPIN1, GPIO.LOW)
            GPIO.output(_MOTORPIN2, GPIO.LOW)
        self.__on = False
        self.__speed = 0
        self.__forward = True
        print("motor instantiated")

    def __repr__(self):
        return "Motor %s, speed %s" % (self.power, self.speed)

    @property
    def power(self):
        if self.__on:
            return "On"
        else:
            return "Off"

    @power.setter
    def power(self, pwer):
        self.__on = pwer
        if self.__on:
            if self.__forward:
                GPIO.output(_MOTORPIN1, GPIO.LOW)
                GPIO.output(_MOTORPIN2, GPIO.HIGH)
                print("power up - forward")
            else:
                GPIO.output(_MOTORPIN1, GPIO.HIGH)
                GPIO.output(_MOTORPIN2, GPIO.LOW)
                print("power up - reverse")
        else:
            self.__speed = 0
            print("powered down")

    @property
    def speed(self):
        return self.__speed
    
    @property
    def forward(self):
        return self.__forward
        
    def change_dir(self):
        # Flip direction
        self.__forward = not self.__forward
        print("change direction forward = ",self.__forward)

        if sys.platform.startswith('linux'):
            if self.__forward:
                print('Turn Forwards...%s' % (self.speed))
                GPIO.output(_MOTORPIN1, GPIO.HIGH)
                GPIO.output(_MOTORPIN2, GPIO.LOW)
            else:
                print('Turn Backwards...%s' % (self.speed))
                GPIO.output(_MOTORPIN1, GPIO.LOW)
                GPIO.output(_MOTORPIN2, GPIO.HIGH)
    
    @speed.setter
    def speed(self, spd):
        if spd > _MAXSPEED:
            spd = _MAXSPEED
        self.__speed = spd
        if sys.platform.startswith('linux'):
            if self.__on and self.__speed > 0:
                self.__p.start(self.__speed)
                print("Speed set to ",self.__speed)
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
    angle = NumericProperty(360)
    max_speed = NumericProperty(_MAXSPEED)

    def __init__(self, motor, **kwargs):
        super(motor_controller, self).__init__(**kwargs)
        self.motor = motor
        self.anim = Animation(angle=0, duration=2)
        self.anim += Animation(angle=0, duration=2)
        self.anim.repeat = True

    def build(self):
        return MotorController()

    def set_speed(self):
        speed_value = self.root.ids.speed_value
        self.motor.speed = speed_value.value

    def power_button(self, instance, value):
        speed_value = self.root.ids.speed_value
        self.motor.power = value
        speed_value.disabled = not value
        if value:
            self.anim.start(self)
        else:
            self.anim.cancel(self)

    def change_direction(self):
        direction = self.root.ids.direction
        self.motor.change_dir()
        if self.motor.forward:
            direction.background_down = "reverse.png"
            direction.background_normal = "forward.png"

        else:
            direction.background_down = "forward.png"
            direction.background_normal = "reverse.png"

    def on_angle(self, item, angle):

        if angle == 0:
            item.angle = 360 if self.motor.forward else -360


# run the app
if __name__ == '__main__':
    motor = Motor()
    motor_controller(motor).run()
