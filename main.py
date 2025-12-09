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

def move_block(n = 1,speed = 230):
    global is_grap_block, is_dis, now_x, now_y, grid

    for i in range(n):

        while True:
            left_reflection = left_cs.reflection()
            right_reflection = right_cs.reflection()

            dis = ultra_ss.distance()

            if dis < 37 and not(is_grap_block):
                is_dis += 1
                if is_dis > 2:
                    is_dis = 0
                    robot.stop()

                    if not is_in_color:
                        dx, dy = directions[now_dir-1]
                        now_x, now_y = now_x + dx, now_y + dy
                        grid[now_x][now_y] = 0

                        # for w in grid:
                        #     print(w)

                    grab_object()
                    turn_min((now_dir+2)%4)
                    return
            
            if right_reflection < 21 or left_reflection < 21:
                print(left_reflection, right_reflection)

                if not is_in_color:
                    dx, dy = directions[now_dir-1]
                    now_x, now_y = now_x + dx, now_y + dy
                    grid[now_x][now_y] = 0

                    # for w in grid:
                    #     print(w)

                break
            else:
                error = left_reflection - right_reflection
                turn_rate = kp * error
                robot.drive(speed, turn_rate)
                wait(10)

        robot.drive(speed, 0)
        wait(50000/(speed*0.9))

        if i != n-1:
            left_reflection = left_cs.reflection()
            right_reflection = right_cs.reflection()

            error = left_reflection - right_reflection
            while abs(error) > 13:
                turn_rate = kp * error
                robot.drive(speed, turn_rate)
                wait(5)

                left_reflection = left_cs.reflection()
                right_reflection = right_cs.reflection()

                error = left_reflection - right_reflection

def turn_min(target):
    global now_dir, angle_lst

    deff = (target - now_dir) % 4
    angle = angle_lst[deff]
    robot.turn(angle)
    now_dir = target

    # 회전 보정
    left_reflection = left_cs.reflection()
    right_reflection = right_cs.reflection()

    error = left_reflection - right_reflection

    while abs(error) > 13:
        turn_rate = kp * error
        robot.drive(0, turn_rate)
        wait(10)

        left_reflection = left_cs.reflection()
        right_reflection = right_cs.reflection()

        error = left_reflection - right_reflection

def at_color(color_loc, arrive = False):
    global is_in_color

    """
    Docstring for at_color
    :param arrive: false면 색에서 출발
    """
    global now_dir

    loc = [S, W] if arrive else [N, E]
    turn_min(loc[1])

    is_in_color = True

    if color_loc == "G":
        move_block(2)
    elif color_loc == "R":
        move_block()
        turn_min(loc[0])
        move_block()
        turn_min(loc[1])
        move_block()
    else:
        move_block()
        turn_min(loc[0])
        move_block(2)
        turn_min(loc[1])
        move_block()
    
    is_in_color = False
    
    if arrive:
        robot.stop()

def grab_object():
    global block_color, is_grap_block
    ev3.speaker.beep()
    sub_motor.run_until_stalled(500, then = Stop.COAST, duty_limit = 50)
    
    bc = middle_cs.color()

    print(bc)
    if bc == None:
        block_color = "G"
        is_grap_block = True

    elif bc != Color.RED:
        block_color = "B"
        is_grap_block = True

    elif bc == Color.RED:
        block_color = "R"
        is_grap_block = True


def release_object(is_b = False):
    global is_grap_block, block_count

    robot.stop()
    ev3.speaker.beep()

    sub_motor.run_until_stalled(-500, then = Stop.COAST, duty_limit = 50)
    is_grap_block = False

    block_count += 1

    if is_b:
        # robot.drive(100, 0)
        # wait(1250)
        robot.drive(-200, 0)
        wait(800)

        turn_min(E)

def check_block():
    i = 0
    global clear_loc

    if clear_loc != 0:
        turn_min(E)
        move_block(clear_loc - 1 - now_y)
        turn_min(S)
    else:
        turn_min(E)

    turn_min(now_dir)
    while i < len(block_distance):
        dis = ultra_ss.distance()
        print("dis :",dis)

        if block_distance[i][0] < dis < block_distance[i][1]:
            is_clear[clear_loc] += 1
            if is_clear[clear_loc] >= 2:
                clear_loc+= 1

            break
        else:
            if not(i == 0 and is_clear[clear_loc] == 1):
                is_clear[clear_loc] += 1
            i += 1

            if is_clear[clear_loc] >= 2:
                clear_loc+= 1
    else:
        return
    
    move_block(i+1)

    if not is_grap_block:
        robot.drive(-150,0)
        wait(1250)
        turn_min((now_dir+2)%4)

    manhattan_load((now_x, now_y),(0,0))

def manhattan_load(st, gl):
    dx,dy = gl[0] - st[0], gl[1] - st[1]

    if dx != 0:
        taget_dir = S if dx > 0 else N
        turn_min(taget_dir)

        move_block(abs(dx))

    if dy != 0:
        taget_dir = E if dy > 0 else W
        turn_min(taget_dir)

        move_block(abs(dy))

#-----------------------------------------------------------

robot.settings(
    straight_speed=210,        # 직진 속도 (mm/s)
    straight_acceleration=400,
    turn_rate=500,             # 회전 속도 (deg/s) ← turn() 속도는 이것으로 결정됨
    turn_acceleration=300
)

directions = [
        [-1, 0],
        [0, 1],
        [1, 0],
        [0, -1]
    ]

grid = [
    [0,1,1,2],
    [1,1,1,2],
    [1,1,1,2]
]

N,E,S,W = 1,2,3,4
angle_lst = [0, 96, 185, -99]

now_x, now_y = (0,0)
now_dir = E

block_count = -1
block_color = "G"

kp = 1.7 # 가중치

is_dis = 0
is_grap_block = False

is_clear = [0, 0, 0, 0] #1 2 3 , 5 9, 6 10, 7 11
clear_loc = 0

is_in_color = True

block_distance = [[200,390],
                  [390,780]]

#--------------------------------------------------------

ev3.speaker.beep()

while True:
    if any(ev3.buttons.pressed()):
        break

# while True:
#     dis = ultra_ss.distance()
#     print(dis)

release_object()

at_color(block_color)
robot.stop()

ev3.speaker.beep()

while True:
    if is_grap_block:
        turn_min(W)
        at_color(block_color, True)
        release_object(True)

        if sum(is_clear) >= 8 or block_count == 4:
            move_block()
            turn_min(N)

            if block_color == 'R':
                move_block()
            else:
                move_block(2)
            turn_min(W)
            move_block()

            turn_min(E)
            break

        else:
            at_color(block_color)

    if sum(is_clear) >= 8:
        manhattan_load((now_x, now_y),(0,0))
        at_color('G', True)
        break
    
    check_block()
    print("while end")


print('main end==================================')

def check_bonus():

    i = 0
    global clear_loc, now_y, angle_lst

    dis = ultra_ss.distance()
    print("dis :",dis)

    if block_distance[i][0] < dis < block_distance[i][1]:
        robot.straight(440)

        grab_object()

        robot.straight(-440)

        angle_lst = [0, 112, 185, -90]

        turn_min(W)
    else:
        robot.straight(400)
        turn_min(S)

        dis = ultra_ss.distance()
        robot.straight(dis + 40)

        grab_object()
        robot.straight(-dis - 40)

        angle_lst = [0, 98, 180, -90]

        turn_min(W)
        
        now_y +=1

    move_block()
    turn_min(W)
    
    manhattan_load((now_x,now_y),(0,0))
    at_color(block_color,True)

is_clear = [0,0,0]
clear_loc = 0
angle_lst = [0, 90, 180, -90]

at_color('G')
move_block(2)

check_bonus()

robot.stop()