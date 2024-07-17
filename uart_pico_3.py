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

button_guard = 1

while True:
    if drink_one_b.value() == 1:
        utime.sleep_ms(375)
        button_one_presses += 1
        while True:
            if button_one_presses == button_guard:
                print("drink 1")
                uart.write('1')
                button_one_presses = 0
                utime.sleep(5)
                break
            elif button_one_presses >= button_guard + 1:
                button_one_presses = 1
            
    elif drink_two_b.value() == 1:
        utime.sleep_ms(375)
        button_two_presses += 1
        while True:
            if button_two_presses == button_guard:
                print("drink 2")
                uart.write('2')
                button_two_presses = 0
                utime.sleep(5)
                break
            elif button_two_presses >= button_guard + 1:
                button_two_presses = 1
                
    elif drink_three_b.value() == 1:
        utime.sleep_ms(375)
        button_three_presses += 1
        while True:
            if button_three_presses == button_guard:
                print("drink 3")
                uart.write('3')
                button_three_presses = 0
                utime.sleep(5)
                break
            elif button_three_presses >= button_guard + 1:
                button_three_presses = 1
                
    elif drink_four_b.value() == 1:
        utime.sleep_ms(375)
        button_four_presses += 1
        while True:
            if button_four_presses == button_guard:
                print("drink 4")
                uart.write('4')
                button_four_presses = 0
                utime.sleep(5)
                break
            elif button_four_presses >= button_guard + 1:
                button_four_presses = 1 
