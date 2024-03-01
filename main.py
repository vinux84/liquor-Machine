import machine
import utime
import _thread

# declare pins here
drink_one = machine.Pin(10, machine.Pin.IN, machine.Pin.PULL_DOWN) # Pin 10 is just a placeholder. TBD on pin
drink_two = machine.Pin(10, machine.Pin.IN, machine.Pin.PULL_DOWN) # Pin 10 is just a placeholder. TBD on pin

ir_sensor = machine.Pin(10, machine.Pin.IN, machine.Pin.PULL_DOWN) # Pin 10 is just a placeholder. TBD on pin

limit_switch_top = machine.Pin(10, machine.Pin.IN, machine.Pin.PULL_DOWN) # Pin 10 is just a placeholder. TBD on pin
limit_switch_bottom = machine.Pin(10, machine.Pin.IN, machine.Pin.PULL_DOWN) # Pin 10 is just a placeholder. TBD on pin

server_motor_one = machine.Pin(10, machine.Pin.OUT) # Pin 10 is just a placeholder. TBD on pin
server_motor_two = machine.Pin(10, machine.Pin.OUT) # Pin 10 is just a placeholder. TBD on pin

spout_servo = machine.PWM(machine.Pin(15)) # Pin 15 is just a placeholder. Need PWM pin, TBD on pin / this is a servo motor
spout_servo.freq(50) # need to research, or look sat original whiskey code 

drink_one_pump = machine.Pin(10, machine.Pin.OUT) # Pin 10 is just a placeholder. TBD on pin
drink_two_pump = machine.Pin(10, machine.Pin.OUT) # Pin 10 is just a placeholder. TBD on pin


drink_one_button = False
drink_two_button = False 

global top_limit_switch
top_limit_switch = True 

global bottom_limit_switch
bottom_limit_switch = False 

    

def dispense_drink(type_drink):
    if type_drink == 'one':
        pump_on(drink_one_pump)
        utime.sleep(3)              # this is how long the liquid should pour out
        pump_off(drink_one_pump)
    elif type_drink == 'two':
        pump_on(drink_two_pump)
        utime.sleep(3)              # this is how long the liquid should pour out
        pump_off(drink_two_pump)
       

def spout_down(): 
    spout_servo.duty_u16(12500) # psuedo duty numbers
    spout_servo.deinit


def spout_up(): 
    spout_servo.duty_u16(2500) # psuedo duty numbers
    spout_servo.deinit


def pump_off(pump_number):
    pump_number.value(0)
    pump_number.value(0)


def pump_on(pump_number):
    pump_number.value(0)
    pump_number.value(1)


def server_stop():
    server_motor_one.value(0)
    server_motor_two.value(0)


def server_up():
    server_motor_one.value(0)
    server_motor_two.value(1)


def server_down():
    server_motor_one.value(1)
    server_motor_two.value(0)


def limit_switch_thread():
    global top_limit_switch
    global bottom_limit_switch
    while True:
        if limit_switch_bottom.value() == 1: # if limit_switch is off == 0, it will always check if it is 1 (on)
            bottom_limit_switch = True
        elif limit_switch_top.value() == 0:
            top_limit_switch = False
        elif limit_switch_bottom.value() == 0: 
            bottom_limit_switch = False
        elif limit_switch_top.value() == 1:
            top_limit_switch = True


def main(type_drink):  
    _thread.start_new_thread(limit_switch_thread, ())                   # starting another thread to detect limit switch                                                       # this will control the cup server motor and know what drink to dispense with type_drink
    if ir_sensor.value() == 1:                                              # does this need a true/false variable
        if top_limit_switch == True:                                            # as well as detect limit swtiches to stop the motor. This can be done through threading or anycio 
            utime.sleep(1) 
            server_down()
            while True:
                if bottom_limit_switch == True:
                    server_stop()
                    utime.sleep(1)
                    spout_down()
                    utime.sleep(1)
                    dispense_drink(type_drink)
                    utime.sleep(4)              # wait for drips  to stop
                    spout_up()
                    utime.sleep(1)
                    server_up()
                    while True:
                        if top_limit_switch == True:
                            server_stop()
                            exit() # break or exit. find proper way to end program to restart 

    else:
        print("Please place cup on holder")                 # debug print        


def button_handler_one(pin):
    global drink_one_button
    drink_one.irq(handler=None)
    utime.sleep_ms(250)
    drink_one.irq(trigger=machine.Pin.IRQ_RISING, handler=button_handler_one)
    if not drink_one_button:
        drink_one_button = True
        type_drink = 'one'
        main(type_drink)
    else:
        drink_one_button = False


def button_handler_two(pin):
    global drink_two_button
    drink_two.irq(handler=None)
    utime.sleep_ms(250)
    drink_two.irq(trigger=machine.Pin.IRQ_RISING, handler=button_handler_two)
    if not drink_two_button:
        drink_two_button = True
        type_drink = 'two'
        main(type_drink)
    else:
        drink_two_button = False


drink_one.irq(trigger=machine.Pin.IRQ_RISING, handler=button_handler_one)
drink_two.irq(trigger=machine.Pin.IRQ_RISING, handler=button_handler_two)