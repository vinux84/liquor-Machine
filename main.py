import machine
import utime
import _thread

drink_one = machine.Pin(26, machine.Pin.IN, machine.Pin.PULL_DOWN)
drink_two = machine.Pin(27, machine.Pin.IN, machine.Pin.PULL_DOWN)

ir_sensor = machine.Pin(22, machine.Pin.IN, machine.Pin.PULL_DOWN)

limit_switch_top = machine.Pin(16, machine.Pin.IN, machine.Pin.PULL_UP) 
limit_switch_bottom = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)

server_motor_one = machine.Pin(19, machine.Pin.OUT)
server_motor_two = machine.Pin(18, machine.Pin.OUT)

spout = machine.PWM(machine.Pin(12))
spout.freq(50)

drink_one_pump_a = machine.Pin(4, machine.Pin.OUT)
drink_one_pump_b = machine.Pin(5, machine.Pin.OUT)

drink_two_pump_a = machine.Pin(6, machine.Pin.OUT) 
drink_two_pump_b = machine.Pin(7, machine.Pin.OUT) 

drink_one_button = False
drink_two_button = False 

global top_limit_switch
top_limit_switch = True 

global bottom_limit_switch
bottom_limit_switch = False 

    
def dispense_drink(type_drink):
    if type_drink == 'one':
        pump_on(drink_one_pump_a, drink_one_pump_b)
        utime.sleep(2.5)              
        pump_off(drink_one_pump_a, drink_one_pump_b)
    elif type_drink == 'two':
        pump_on(drink_two_pump_a, drink_two_pump_b)
        utime.sleep(3)              
        pump_off(drink_two_pump_a, drink_two_pump_b)
       
def spout_down(): 
    spout.duty_u16(6000)
    utime.sleep(2)
    spout.deinit()

def spout_up(): 
    spout.duty_u16(2500)
    utime.sleep(2)
    spout.deinit()

def pump_on(pump_a, pump_b):
    pump_a.value(1)
    pump_b.value(0)
    
def pump_off(pump_a, pump_b):
    pump_a.value(0)
    pump_b.value(0)

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
        if limit_switch_top.value() == 0:
            top_limit_switch = True
            bottom_limit_switch = False
        elif limit_switch_bottom.value() == 0:
            bottom_limit_switch = True
            top_limit_switch = False 

def main(type_drink):
    if ir_sensor.value() == 0:
        _thread.start_new_thread(limit_switch_thread, ()) 
        if top_limit_switch == True:
            utime.sleep(1) 
            server_down()
            while True:
                if bottom_limit_switch == True:
                    server_stop()
                    utime.sleep(1)
                    spout_down()
                    utime.sleep(1)
                    dispense_drink(type_drink)
                    utime.sleep(4)              
                    spout_up()
                    utime.sleep(1)
                    server_up()
                    while True:
                        if top_limit_switch == True:
                            server_stop()
                            machine.reset()        
                
def reset():
    pump_off(drink_one_pump_a, drink_one_pump_b)
    pump_off(drink_two_pump_a, drink_two_pump_b)
    server_stop()
    spout_up()
    if limit_switch_top.value() == 1:
        server_up()
        while True:
            if limit_switch_top.value() == 0:
                server_stop()
                break
                
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

reset() 

drink_one.irq(trigger=machine.Pin.IRQ_RISING, handler=button_handler_one)
drink_two.irq(trigger=machine.Pin.IRQ_RISING, handler=button_handler_two)


