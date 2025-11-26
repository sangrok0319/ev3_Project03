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

sub_motor = Motor(Port.D)

robot = DriveBase(left_motor, right_motor, 55.5 , 104)

left_cs = ColorSensor(Port.S1)
right_cs = ColorSensor(Port.S4)
middle_cs = ColorSensor(Port.S3)

ultra_ss = UltrasonicSensor(Port.S2)

# =============================================================

kp = 0.7 # 가중치
N,E,S,W = 1,2,3,4

left_reflection = left_cs.reflection()
right_reflection = right_cs.reflection()

is_dis = 0

class Q:
    def __init__(self):
        self.inven = []

def move_block(speed = 100):
    global is_grap_block, is_dis

    while True:
        left_reflection = left_cs.reflection()
        right_reflection = right_cs.reflection()

        dis = ultra_ss.distance()
        print(dis)

        if dis < 35 and not(is_grap_block):
            is_dis += 1
            if is_dis > 2:
                is_dis = 0
                robot.stop()
                grab_object()
                turn_min((now_dir+2)%4)
                break
        
        if right_reflection < 30 or left_reflection < 30:
            robot.stop()
            break
        else:
            error = left_reflection - right_reflection
            turn_rate = kp * error
            robot.drive(speed, turn_rate)
            wait(10)

    robot.drive(speed, 0)
    wait(50000/speed)
    robot.stop()

def turn_min(target):
    global now_dir

    deff = (target - now_dir) % 4
    angle = [0, 90, 180, -90][deff]
    robot.turn(angle)
    now_dir = target

    robot.drive(100, 0)
    wait(250)
    robot.stop()


def manhattan_load(st, gl, now_dir):
    dx,dy = gl[0] - st[0], gl[1] - st[1]

    print(dx, dy)

    if dx != 0:
        taget_dir = S if dx > 0 else N
        now_dir = turn_min(now_dir, taget_dir)
        step = abs(dx)

        for _ in range(step):
            move_block()
            dx += 1 if taget_dir == S else -1

    print(dx, dy)

    if dy != 0:
        taget_dir = E if dy > 0 else W
        now_dir = turn_min(now_dir, taget_dir)
        step = abs(dy)

        for _ in range(step):
            move_block()
            dy += 1 if taget_dir == E else -1

def at_color(color_loc, arrive = False):
    global now_dir

    loc = [S, W] if arrive else [N, E]
    turn_min(loc[1])

    if color_loc == "G":
        for _ in range(2):
            move_block()
    elif color_loc == "R":
        move_block()
        turn_min(loc[0])
        move_block()
        turn_min(loc[1])
        move_block()
    else:
        move_block()
        turn_min(loc[0])
        for _ in range(2):
            move_block()
        turn_min(loc[1])
        move_block()

def grab_object():
    global block_color, is_grap_block
    ev3.speaker.beep()
    sub_motor.run_until_stalled(200, then = Stop.COAST, duty_limit = 50)
    
    bc = middle_cs.color()
    print(bc)

    if bc == None:
        print("None")

    elif bc != Color.RED:
        block_color = "B"
        is_grap_block = True


    elif bc == Color.RED:
        block_color = "R"
        is_grap_block = True


def release_object():
    global is_grap_block

    ev3.speaker.beep()

    sub_motor.run_until_stalled(-300, then = Stop.COAST, duty_limit = 50)
    is_grap_block = False

#-----------------------------------------------------------

ev3.speaker.beep()

st = (0,0)
gl = (1,2)

is_grap_block = False
now_dir = E

block_color = "G"

while True:
    if any(ev3.buttons.pressed()):
        break

release_object()

at_color("G")

if is_grap_block:
    at_color(block_color, True)
    release_object()