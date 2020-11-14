from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from speedmeter import SpeedMeter
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
import RPi.GPIO as GPIO

# define the pins connected to L293D 
_MOTORPIN1 = 13
_MOTORPIN2 = 11
_ENABLEPIN = 15
_MINSPEED = 0
_MAXSPEED = 100
motorStatus = False

    
class Motor():
    def __init__(self, speed=0):
        GPIO.cleanup()
        GPIO.setmode(GPIO.BOARD)   
        GPIO.setup(_MOTORPIN1,GPIO.OUT)   # set pins to OUTPUT mode
        GPIO.setup(_MOTORPIN2,GPIO.OUT)
        GPIO.setup(_ENABLEPIN,GPIO.OUT)
        self.__p = GPIO.PWM(_ENABLEPIN,1000) # creat PWM and set Frequency to 1KHz        self.__on = False
        self.speed = speed
        self.__p.start(self.speed)
        self.__on = False
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
        print(x)
        self.__speed = x

    def turn(self):
        if self.__on:
            GPIO.output(_MOTORPIN1,GPIO.HIGH)  # motoRPin1 output HIHG level
            GPIO.output(_MOTORPIN2,GPIO.LOW)   # motoRPin2 output LOW level
            if self.speed > 0:
                print ('Turn Forward...%s' % (self.speed))
                self.__p.start(self.speed)
        else:
            GPIO.output(_MOTORPIN1,GPIO.LOW)
            GPIO.output(_MOTORPIN2,GPIO.LOW)
            print ('Motor Stop...')


class MotorController(FloatLayout, Motor):
    def __init__(self, **kwargs):
        super(MotorController, self).__init__(**kwargs)
        battery = self.ids.battery
        battery.value = 99
        battery.value = 100
        self.clockRunning = True
        self.power =True
        #self.speed = 10
        #print(self.speed)
        
        Clock.schedule_interval(self.tick, 0.5)
        print("motor controller instantiated")

    def tick(self, *args, **kwargs):
        battery = self.ids.battery
        battery.progress_color = (0, 1, 0, 1)
        speed_value = self.ids.speed_value

        if speed_value.value > 0:
            self.__on = True
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
        self.turn()


class motor_controller(App):
    def build(self):
        return MotorController()

    def set_speed(self):
        speed_value = self.root.ids.speed_value
        #print(speed_value.value)
        MotorController.speed = speed_value.value


# run the app
if __name__ == '__main__':
    #motor = Motor()
    motor_controller().run()

