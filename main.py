# ////////////////////////////////////////////////////////////////
# //                     IMPORT STATEMENTS                      //
# ////////////////////////////////////////////////////////////////

import math
import sys
import time

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import *
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.slider import Slider
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from kivy.animation import Animation
from functools import partial
from kivy.config import Config
from kivy.core.window import Window

from pidev.MixPanel import MixPanel
from pidev.kivy import DPEAButton
from pidev.kivy import PauseScreen
from time import sleep
# import RPi.GPIO as GPIO
from pidev.stepper import stepper
from pidev.Cyprus_Commands import Cyprus_Commands_RPi as cyprus
from dpeaDPi.DPiFuncGen import DPiFuncGen
from dpeaDPi.DPiPowerDrive import DPiPowerDrive
from time import sleep

from dpeaDPi.DPiSolenoid import DPiSolenoid

from Objects.robotArm import RobotArm


# ////////////////////////////////////////////////////////////////
# //                      GLOBAL VARIABLES                      //
# //                         CONSTANTS                          //
# ////////////////////////////////////////////////////////////////
START = True
STOP = False
UP = False
DOWN = True
ON = True
OFF = False
YELLOW = .180, 0.188, 0.980, 1
BLUE = 0.917, 0.796, 0.380, 1
CLOCKWISE = 0
COUNTERCLOCKWISE = 1
ARM_SLEEP = 2.5
DEBOUNCE = 0.10

lowerTowerPosition = 60
upperTowerPosition = 76


dpiFuncGen1 = DPiFuncGen()
dpiFuncGen1.setBoardNumber(0) #Square
dpiFuncGen2 = DPiFuncGen()
dpiFuncGen2.setBoardNumber(1) #Circle

dpiPowerDrive = DPiPowerDrive()
dpiPowerDrive.setBoardNumber(0)
dpiPowerDrive2 = DPiPowerDrive()
dpiPowerDrive2.setBoardNumber(0)

if dpiFuncGen1.initialize() != True:
    print("Communication with the DPiFuncGen board failed.")

if dpiPowerDrive.initialize() != True:
    print("Communication with the DPiPowerDrive board failed.")

if dpiFuncGen2.initialize() != True:
    print("Communication with the DPiFuncGen board failed.")

if dpiPowerDrive2.initialize() != True:
    print("Communication with the DPiPowerDrive board failed.")

MIXPANEL_TOKEN = "x"
MIXPANEL = MixPanel("Project Name", MIXPANEL_TOKEN)

dpiFuncGen1.mute(False)
dpiFuncGen2.mute(False)
waveshape = DPiFuncGen.SINE_WAVE

SCREEN_MANAGER = ScreenManager()

# ////////////////////////////////////////////////////////////////
# //            DECLARE APP CLASS AND SCREENMANAGER             //
# //                     LOAD KIVY FILE                         //
# ////////////////////////////////////////////////////////////////
class MainApp(App):
    def build(self):
        SCREEN_MANAGER.add_widget(MainScreen(name='main'))
        SCREEN_MANAGER.add_widget(TrajScreen(name='traj'))
        return SCREEN_MANAGER

    print("class created")


Builder.load_file('main.kv')
Builder.load_file('traj.kv')
Window.clearcolor = (.1, .1, .1, 1)  # (WHITE)


# ////////////////////////////////////////////////////////////////
# //                    SLUSH/HARDWARE SETUP                    //
# ////////////////////////////////////////////////////////////////


volumeOn = False
pneumatic = False
airOn = False


# ////////////////////////////////////////////////////////////////
# //                       MAIN FUNCTIONS                       //
# //             SHOULD INTERACT DIRECTLY WITH HARDWARE         //
# ////////////////////////////////////////////////////////////////

robot = RobotArm()


print('Setting up robot')
if not robot.setup():
    raise Exception("Robot setup failed")


class MainScreen(Screen):
    frequency = 0

    def __init__(self, **kwargs):
        self.frequency = 1
        super(MainScreen, self).__init__(**kwargs)

    def move_to_traj(self):
        self.move(0)
        time.sleep(3)
        SCREEN_MANAGER.transition.direction = "right"
        SCREEN_MANAGER.current = TRAJ_SCREEN_NAME

    def square1282(self):
        global waveshape
        dpiFuncGen1.setFrequency(1282, waveshape)

    def circle952(self):
        global waveshape
        dpiFuncGen2.setFrequency(952, waveshape)

    def update_pneumatic(self):
        global pneumatic
        if not pneumatic:
            dpiPowerDrive.switchDriverOnOrOff(0, pneumatic)
            pneumatic = True
        else:
            dpiPowerDrive.switchDriverOnOrOff(0, pneumatic)
            pneumatic = False

    def toggle_air(self):
        global airOn
        if not airOn:
            dpiPowerDrive2.switchDriverOnOrOff(1, airOn)
            airOn = True
        else:
            dpiPowerDrive2.switchDriverOnOrOff(1, airOn)
            airOn = False

    def update_freq_square(self, freq):
        global waveshape
        self.ids.frequencySquare.text = "Circle Frequency: " + str(freq)
        dpiFuncGen2.setFrequency(freq, waveshape)

    def update_freq_circle(self, freq):
        global waveshape
        self.ids.frequencyCircle.text = "Square Frequency: " + str(freq)
        dpiFuncGen1.setFrequency(freq, waveshape)


    def update_vol(self, vol):
        self.ids.vol.text = "Volume: " + str(vol)
        if volumeOn:
            dpiFuncGen1.setVolume(int(vol))
            dpiFuncGen2.setVolume(int(vol))

    def toggle_volume(self):
        global volumeOn
        if not volumeOn:
            dpiFuncGen1.setVolume(int(self.ids.updateVol.value))
            dpiFuncGen2.setVolume(int(self.ids.updateVol.value))
            volumeOn = True
        else:
            dpiFuncGen1.setVolume(0)
            dpiFuncGen2.setVolume(0)
            volumeOn = False

    def move(self, position):
        robot.processMove(position)
        return None

    def quit(self):
        sleep(1)
        quit()

class TrajScreen(Screen):
    frequency = 0
    # def __init__(self, **kwargs):
    #     self.frequency = 1
    #     super(TrajScreen, self).__init__(**kwargs)
    def toggle_volume(self):
        global volumeOn
        if not volumeOn:
            dpiFuncGen1.setVolume(int(45))
            dpiFuncGen2.setVolume(int(45))
            volumeOn = True
        else:
            dpiFuncGen1.setVolume(0)
            dpiFuncGen2.setVolume(0)
            volumeOn = False
    def move_to_main(self):
        SCREEN_MANAGER.transition.direction = "right"
        SCREEN_MANAGER.current = MAIN_SCREEN_NAME

    def move(self, position):
        if robot.processMove(position) == 1:
            time.sleep(.5)
            dpiPowerDrive2.switchDriverOnOrOff(1, False)
        else:
            time.sleep(2.5)
            dpiPowerDrive2.switchDriverOnOrOff(1, True)

        return None

    def update_pneumatic(self):
        global pneumatic
        if not pneumatic:
            dpiPowerDrive.switchDriverOnOrOff(0, pneumatic)
            pneumatic = True
        else:
            dpiPowerDrive.switchDriverOnOrOff(0, pneumatic)
            pneumatic = False
    def put_sand_on_square(self):
        self.move(0)
        if self.move(3) != 3:
            time.sleep(1.5)
            self.move(1)
            time.sleep(5)
            self.update_pneumatic()
            time.sleep(1)
            self.update_pneumatic()
            time.sleep(1)
            self.update_pneumatic()
            time.sleep(1)
            self.move(0)
            time.sleep(2)
        else:
            time.sleep(4.5)
            self.move(3)
            time.sleep(1.5)
            self.move(1)
            time.sleep(5)
            self.update_pneumatic()
            time.sleep(1)
            self.update_pneumatic()
            time.sleep(1)
            self.update_pneumatic()
            time.sleep(1)
            self.move(0)
            time.sleep(2)
    def put_sand_on_circle(self):
        self.move(0)
        if self.move(3) != 3:
            time.sleep(1.5)
            self.move(2)
            time.sleep(5)
            self.update_pneumatic()
            time.sleep(1)
            self.update_pneumatic()
            time.sleep(1)
            self.update_pneumatic()
            time.sleep(1)
            self.move(0)
            time.sleep(2)
        else:
            time.sleep(4.5)
            self.move(3)
            time.sleep(1.5)
            self.move(2)
            time.sleep(5)
            self.update_pneumatic()
            time.sleep(1)
            self.update_pneumatic()
            time.sleep(1)
            self.update_pneumatic()
            time.sleep(1)
            self.move(0)
            time.sleep(2)
    def circle1(self):
        global waveshape
        dpiFuncGen2.setFrequency(287, waveshape)
    def circle2(self):
        global waveshape
        dpiFuncGen2.setFrequency(553, waveshape)
    def circle3(self):
        global waveshape
        dpiFuncGen2.setFrequency(1009, waveshape)
    def square1(self):
        global waveshape
        dpiFuncGen1.setFrequency(100, waveshape)
    def square2(self):
        global waveshape
        dpiFuncGen1.setFrequency(455, waveshape)
    def square3(self):
        global waveshape
        dpiFuncGen1.setFrequency(722, waveshape)


MAIN_SCREEN_NAME = 'main'
TRAJ_SCREEN_NAME = 'traj'

def send_event(event_name):
    """
    Send an event to MixPanel without properties
    :param event_name: Name of the event
    :return: None
    """
    global MIXPANEL

    MIXPANEL.set_event_name(event_name)
    MIXPANEL.send_event()
    print("mix panel")


# ////////////////////////////////////////////////////////////////
# //                          RUN APP                           //
# ////////////////////////////////////////////////////////////////

if __name__ == "__main__":
    print("done setting up :D")
    MainApp().run()
