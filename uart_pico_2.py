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

def button_handler_one(pin):
    global button_one_presses
    drink_one_b.irq(handler=None)
    button_one_presses +=1
    print("handling 1")
    utime.sleep_ms(375)
    drink_one_b.irq(trigger=machine.Pin.IRQ_RISING, handler=button_handler_one)
    
def button_handler_two(pin):
    global button_two_presses
    drink_two_b.irq(handler=None)
    button_two_presses +=1
    print("handling 2")
    utime.sleep_ms(375)
    drink_two_b.irq(trigger=machine.Pin.IRQ_RISING, handler=button_handler_two)
    
def button_handler_three(pin):
    global button_three_presses
    drink_three_b.irq(handler=None)
    button_three_presses +=1
    print("handling 3")
    utime.sleep_ms(375)
    drink_three_b.irq(trigger=machine.Pin.IRQ_RISING, handler=button_handler_three)
    
def button_handler_four(pin):
    global button_four_presses
    drink_four_b.irq(handler=None)
    button_four_presses +=1
    print("handling 4")
    utime.sleep_ms(375)
    drink_four_b.irq(trigger=machine.Pin.IRQ_RISING, handler=button_handler_four)
    
    
drink_one_b.irq(trigger=machine.Pin.IRQ_RISING, handler=button_handler_one)
drink_two_b.irq(trigger=machine.Pin.IRQ_RISING, handler=button_handler_two)
drink_three_b.irq(trigger=machine.Pin.IRQ_RISING, handler=button_handler_three)
drink_four_b.irq(trigger=machine.Pin.IRQ_RISING, handler=button_handler_four)


while True:
    if button_one_presses == button_guard:
        print("drink 1")
        uart.write('1')
        button_one_presses = 0
    elif button_one_presses >= button_guard + 1:
        button_one_presses = 1
    elif button_two_presses == button_guard:
        print("drink 2")
        uart.write('2')
        button_two_presses = 0
    elif button_two_presses >= button_guard + 1:
        button_two_presses = 1
    elif button_three_presses == button_guard:
        print("drink 3")
        uart.write('3')
        button_three_presses = 0
    elif button_three_presses >= button_guard + 1:
        button_three_presses = 1
    elif button_four_presses == button_guard:
        print("drink 4")
        uart.write('4')
        button_four_presses = 0
    elif button_four_presses >= button_guard + 1:
        button_four_presses = 1
