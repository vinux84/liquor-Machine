import machine
import os
import utime
from machine import Pin, UART

drink_one_b = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_DOWN) 
drink_two_b = machine.Pin(3, machine.Pin.IN, machine.Pin.PULL_DOWN)
drink_three_b = machine.Pin(6, machine.Pin.IN, machine.Pin.PULL_DOWN)  
drink_four_b = machine.Pin(7, machine.Pin.IN, machine.Pin.PULL_DOWN)

uart = UART(1, baudrate=9600, tx=Pin(4))
uart.init(bits=8, parity=None, stop=2)

button_one_presses = 0
button_two_presses = 0
button_three_presses = 0
button_four_presses = 0

debounce_time_one = 0
debounce_time_two = 0
debounce_time_three = 0
debounce_time_four = 0

button_guard = 1

while True:
    if ((drink_one_b.value() is 1) and (utime.ticks_ms()-debounce_time_one) > 500):
        button_one_presses+=1
        debounce_time_one=utime.ticks_ms()
        if button_one_presses == 1:
            print('button one pressed')
            print("drink 1")
            uart.write('1')
            button_one_presses = 0
    elif ((drink_two_b.value() is 1) and (utime.ticks_ms()-debounce_time_two) > 500):
        button_two_presses+=1
        debounce_time_two=utime.ticks_ms()
        if button_two_presses == 1:
            print('button two pressed')
            print("drink 2")
            uart.write('2')
            button_two_presses = 0
    elif ((drink_three_b.value() is 1) and (utime.ticks_ms()-debounce_time_three) > 500):
        button_three_presses+=1
        debounce_time_three=utime.ticks_ms()
        if button_three_presses == 1:
            print('button three pressed')
            print("drink 3")
            uart.write('3')
            button_three_presses = 0
    elif ((drink_four_b.value() is 1) and (utime.ticks_ms()-debounce_time_four) > 500):
        button_four_presses+=1
        debounce_time_four=utime.ticks_ms()
        if button_four_presses == 1:
            print('button four pressed')
            print("drink 4")
            uart.write('4')
            button_four_presses = 0
