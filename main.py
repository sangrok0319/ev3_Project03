#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile


# This program requires LEGO EV3 MicroPython v2.0 or higher.
# Click "Open user guide" on the EV3 extension tab for more information.


# Create your objects here.
ev3 = EV3Brick()

# =============================================================

left_motor = Motor(Port.A)
right_motor = Motor(Port.B)

robot = DriveBase(left_motor, right_motor, 55.5 , 104)

left_cs = ColorSensor(Port.S1)
right_cs = ColorSensor(Port.S4)


#2칸 전진, for 문을 통해 n칸 전민 알고리즘 만들 수 있음
threshold = 50
kp = 0.5
ev3.speaker.beep()

left_reflection = left_cs.reflection()
right_reflection = right_cs.reflection()

def move(n):
    for _ in range(n):
        while True:
            left_reflection = left_cs.reflection()
            right_reflection = right_cs.reflection()
            
            print(left_reflection, right_reflection)
            if right_reflection < 30 or left_reflection < 30:
                robot.stop()
                break
            else:
                error = left_reflection - right_reflection
                turn_rate = kp * error
                robot.drive(100, turn_rate)
                wait(10)
    
        robot.drive(100, 0)
        wait(500)
        robot.stop()


while True:
    if any(ev3.buttons.pressed()):
        break

move(1)
robot.turn(-90)
ev3.speaker.beep()

move(2)
robot.turn(90)
ev3.speaker.beep()

move(2)
robot.turn(90)
ev3.speaker.beep()

move(2)
robot.turn(-90)
ev3.speaker.beep()

move(1)
ev3.speaker.beep()