import machine
import utime

# declare pins here
on_off_button = machine.Pin(10, machine.Pin.IN, machine.Pin.PULL_DOWN) # Pin 10 is just a placeholder. TBD on pin



pressed_button = False

def drink_two():
    pass

def drink_one():
    pass

def drink(drink_number):
    pass

def spout_down():
    pass

def spout_up():
    pass 

def pour(action, drink):
    pass
    # this will control the spout up or down
    # after down can you input variable drink

def limit_switch():
    pass 

def server_up():
    pass

def server_down():
    pass

def server(action, limit_Switch):
    pass 
    # this will control the cup server motor through action input
    # as well as detect limit swtiches to stop the motor. This can be done through threading or anycio 
    # this will have input variables that will determine up or down

def button_handler(pin):
    global pressed_button
    on_off_button.irq(handler=None)
    utime.sleep_ms(250)
    on_off_button.irq(trigger=machine.Pin.IRQ_RISING, handler=button_handler)
    if not pressed_button:
        # main logic
        pressed_button = True
    else:
        pressed_button = False

on_off_button.irq(trigger=machine.Pin.IRQ_RISING, handler=button_handler)