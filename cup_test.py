import machine
import os
import utime

server_motor_down = machine.Pin(16, machine.Pin.OUT)
server_motor_up = machine.Pin(17, machine.Pin.OUT)

def server_stop():
    server_motor_down.value(0)
    server_motor_up.value(0)

def server_up():
    server_motor_down.value(0)
    server_motor_up.value(1)

def server_down():
    server_motor_down.value(1)
    server_motor_up.value(0)

def down(time):
    server_down()
    utime.sleep(time)
    server_stop()

def up(time):
    server_up()
    utime.sleep(time)
    server_stop()


up(.25)
#utime.sleep(.50)
#down(.25)
