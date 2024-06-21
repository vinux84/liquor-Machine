from phew import access_point, connect_to_wifi, is_connected_to_wifi, dns, server
from phew.template import render_template
import json
import machine
import os
import utime
import _thread


AP_NAME = "DrinkBot"
AP_DOMAIN = "drinkbot.io"
AP_TEMPLATE_PATH = "ap_templates"
APP_TEMPLATE_PATH = "app_templates"
WIFI_FILE = "wifi.json"
IP_ADDRESS = "ip.json"
DRINKS = "drink.json"
WIFI_MAX_ATTEMPTS = 3


drink_one = machine.Pin(28, machine.Pin.IN, machine.Pin.PULL_DOWN)
drink_two = machine.Pin(27, machine.Pin.IN, machine.Pin.PULL_DOWN)
drink_three = machine.Pin(7, machine.Pin.IN, machine.Pin.PULL_DOWN)  # need to assign this a pin, 7 is placeholder
drink_four = machine.Pin(7, machine.Pin.IN, machine.Pin.PULL_DOWN)  # need to assign this a pin, 7 is placeholder

ir_sensor = machine.Pin(21, machine.Pin.IN, machine.Pin.PULL_DOWN)

limit_switch_top = machine.Pin(16, machine.Pin.IN, machine.Pin.PULL_UP) 
limit_switch_bottom = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)

server_motor_down = machine.Pin(26, machine.Pin.OUT)
server_motor_up = machine.Pin(22, machine.Pin.OUT)

spout = machine.PWM(machine.Pin(12))
spout.freq(50)

drink_one_pump_a = machine.Pin(18, machine.Pin.OUT)
drink_one_pump_b = machine.Pin(19, machine.Pin.OUT)

drink_two_pump_a = machine.Pin(17, machine.Pin.OUT) 
drink_two_pump_b = machine.Pin(7, machine.Pin.OUT) # need to assign this a pin, 7 is placeholder

drink_three_pump_a = machine.Pin(7, machine.Pin.OUT) # need to assign this a pin, 7 is placeholder
drink_three_pump_b = machine.Pin(7, machine.Pin.OUT) # need to assign this a pin, 7 is placeholder

drink_four_pump_a = machine.Pin(7, machine.Pin.OUT) # need to assign this a pin, 7 is placeholder
drink_four_pump_b = machine.Pin(7, machine.Pin.OUT) # need to assign this a pin, 7 is placeholder

drink_one_button = False
drink_two_button = False
drink_three_button = False
drink_four_button = False


def spout_down(): 
    spout.duty_u16(4700)
    utime.sleep(2)
    spout.deinit()
    
def spout_up(): 
    spout.duty_u16(1300)
    utime.sleep(2)
    spout.deinit()

def pump_on(pump_a, pump_b):
    pump_a.value(1)
    pump_b.value(0)

def pump_off(pump_a, pump_b):
    pump_a.value(0)
    pump_b.value(0)

def server_stop():
    server_motor_down.value(0)
    server_motor_up.value(0)

def server_up():
    server_motor_down.value(0)
    server_motor_up.value(1)

def server_down():
    server_motor_down.value(1)
    server_motor_up.value(0)

def dispense_drink(type_drink, drink_duration):                         # code to run the actual machine
    if type_drink == 'one':
        pump_on(drink_one_pump_a, drink_one_pump_b)
        utime.sleep(drink_duration)              
        pump_off(drink_one_pump_a, drink_one_pump_b)
    elif type_drink == 'two':
        pump_on(drink_two_pump_a, drink_two_pump_b)
        utime.sleep(drink_duration)              
        pump_off(drink_two_pump_a, drink_two_pump_b)
    elif type_drink == 'three':
        pump_on(drink_three_pump_a, drink_three_pump_b)
        utime.sleep(drink_duration)              
        pump_off(drink_three_pump_a, drink_three_pump_b)
    elif type_drink == 'four':
        pump_on(drink_four_pump_a, drink_four_pump_b)
        utime.sleep(drink_duration)              
        pump_off(drink_four_pump_a, drink_four_pump_b)

def main_dispense(type_drink, drink_duration):
    if ir_sensor.value() == 0:
        if limit_switch_top.value() == 0:
            utime.sleep(1) 
            server_down()
            d = 1
            u = 1
            while d > 0:
                if limit_switch_bottom.value() == 0:
                    server_stop()
                    d -= 1
                    utime.sleep(1)
                    spout_down()
                    utime.sleep(1)
                    dispense_drink(type_drink, drink_duration)  
                    utime.sleep(4)              
                    spout_up()
                    utime.sleep(1)
                    server_up()
                    while u > 0:
                        if limit_switch_top.value() == 0:
                            server_stop()
                            u -= 1
                                           
def reset():
    pump_off(drink_one_pump_a, drink_one_pump_b)
    pump_off(drink_two_pump_a, drink_two_pump_b)
    pump_off(drink_three_pump_a, drink_three_pump_b)
    pump_off(drink_four_pump_a, drink_four_pump_b)
    server_stop()
    spout_up()
    if limit_switch_top.value() == 1:
        server_up()
        u = 1
        while u > 0:
            if limit_switch_top.value() == 0:
                server_stop()
                u -= 1
                
                
reset()                                           # Home machine to default positions

def find_time(ounces):
        one_second = 1 # let's say 1 second dispenses 1 ounce, until this is tested, this needs to be finished, once pumps are hooked up
        time = ounces / one_second
        return time
        
def quantity_calculator(quantity):
    find_ounces = quantity.rsplit()
    if len(find_ounces[0]) == 3:
        if find_ounces[0][1] == '.':
            ounces = float(find_ounces[0])
            time = find_time(ounces)
            return time
    else: 
        ounces = int(find_ounces[0])
        time = find_time(ounces)
        return time
    
def update_json(key, value):                        # Update drinks in json file, when drinks are edited
    with open(DRINKS, 'r') as f:
        drink_db = json.load(f)
        drink_db[key]=value
    with open(DRINKS, 'w') as f:
        f.write(json.dumps(drink_db))

def get_drink_amount(drink_num):
    with open(DRINKS) as f:
        drink_db = json.load(f)
        drink_amount = drink_db[f'drink_{drink_num}_amount']
        drink_duration = quantity_calculator(drink_amount)
        return drink_duration

def button_handler_one(pin):
    global drink_one_button
    drink_one.irq(handler=None)
    utime.sleep_ms(250)
    drink_one.irq(trigger=machine.Pin.IRQ_RISING, handler=button_handler_one)
    if not drink_one_button:
        drink_one_button = True
        type_drink = 'one'
        one_drink_amount = get_drink_amount(type_drink)
        main_dispense(type_drink, one_drink_amount)
        drink_one_button = False

def button_handler_two(pin):
    global drink_two_button
    drink_two.irq(handler=None)
    utime.sleep_ms(250)
    drink_two.irq(trigger=machine.Pin.IRQ_RISING, handler=button_handler_two)
    if not drink_two_button:
        drink_two_button = True
        type_drink = 'two'
        two_drink_amount = get_drink_amount(type_drink)
        main_dispense(type_drink, two_drink_amount)
        drink_two_button = False
        
def button_handler_three(pin):
    global drink_three_button
    drink_three.irq(handler=None)
    utime.sleep_ms(250)
    drink_three.irq(trigger=machine.Pin.IRQ_RISING, handler=button_handler_three)
    if not drink_three_button:
        drink_three_button = True
        type_drink = 'three'
        three_drink_amount = get_drink_amount(type_drink)
        main_dispense(type_drink, three_drink_amount)
        drink_three_button = False

def button_handler_four(pin):
    global drink_four_button
    drink_four.irq(handler=None)
    utime.sleep_ms(250)
    drink_four.irq(trigger=machine.Pin.IRQ_RISING, handler=button_handler_four)
    if not drink_four_button:
        drink_four_button = True
        type_drink = 'four'
        four_drink_amount = get_drink_amount(type_drink)
        main_dispense(type_drink, four_drink_amount)
        drink_four_button = False

drink_one.irq(trigger=machine.Pin.IRQ_RISING, handler=button_handler_one)
drink_two.irq(trigger=machine.Pin.IRQ_RISING, handler=button_handler_two)
drink_three.irq(trigger=machine.Pin.IRQ_RISING, handler=button_handler_three)
drink_four.irq(trigger=machine.Pin.IRQ_RISING, handler=button_handler_four)

def machine_reset():
    utime.sleep(1)
    print("Resetting...")
    machine.reset()


def setup_mode():                                                             # setup mode to grab users wifi credentials
    print("Entering setup mode...")
    
    def ap_index(request):
        if request.headers.get("host").lower() != AP_DOMAIN.lower():
            return render_template(f"{AP_TEMPLATE_PATH}/redirect.html", domain = AP_DOMAIN.lower())

        return render_template(f"{AP_TEMPLATE_PATH}/index.html")

    def ap_configure(request):
        print("Saving wifi credentials...")

        with open(WIFI_FILE, "w") as f:
            json.dump(request.form, f)
            f.close()
                                                                               # Reboot from new thread after we have responded to the user.
        _thread.start_new_thread(machine_reset, ())
        return render_template(f"{AP_TEMPLATE_PATH}/configured.html", ssid = request.form["ssid"])
        
    def ap_catch_all(request):
        if request.headers.get("host") != AP_DOMAIN:
            return render_template(f"{AP_TEMPLATE_PATH}/redirect.html", domain = AP_DOMAIN)

        return "Not found.", 404


    server.add_route("/", handler = ap_index, methods = ["GET"])
    server.add_route("/configure", handler = ap_configure, methods = ["POST"])
    server.set_callback(ap_catch_all)

    ap = access_point(AP_NAME)
    ip = ap.ifconfig()[0]
    dns.run_catchall(ip)


def display_ip():                                                             # displays a page with the IP address (so user can see) no mDNS working for now, then reboots device
    print("Entering display IP mode")
    
    def ap_index(request):
        if request.headers.get("host").lower() != AP_DOMAIN.lower():
            return render_template(f"{AP_TEMPLATE_PATH}/redirect.html", domain = AP_DOMAIN.lower())
        
        with open(IP_ADDRESS) as f:
            ip_address_status = json.load(f)
            ip = ip_address_status["ipa"]
            
        return render_template(f"{AP_TEMPLATE_PATH}/display_index.html", ip_num = ip)
    
    def app_restart(request):
        machine_reset()
        return "OK"
    
    def ap_catch_all(request):
        if request.headers.get("host") != AP_DOMAIN:
            return render_template(f"{AP_TEMPLATE_PATH}/redirect.html", domain = AP_DOMAIN)

        return "Not found.", 404
    
    server.add_route("/", handler = ap_index, methods = ["GET"])
    server.add_route("/reset", handler = app_restart, methods = ["GET"])
    server.set_callback(ap_catch_all)
    
    ap = access_point(AP_NAME)
    ip = ap.ifconfig()[0]
    dns.run_catchall(ip)


def application_mode():                                                     # Starts web server and all its functions
    print("Entering application mode.")
            
    
    def app_index(request):
        save_alert = None
        
        if request.form:                              # checks form.request for update on drinks in json file
            for key, value in request.form.items():
                if value != "":
                    update_json(key, value)
            save_alert = 'on'
        
        with open(DRINKS) as f:                       # load current drink keywords into index.html to display
            drink_db = json.load(f)
            drinkones = drink_db['drink_one_state']
            drinkonen = drink_db['drink_one_name']
            drinkonea = drink_db['drink_one_amount']
            drinktwos = drink_db['drink_two_state']
            drinktwon = drink_db['drink_two_name']
            drinktwoa = drink_db['drink_two_amount']
            drinkthrees = drink_db['drink_three_state']
            drinkthreen = drink_db['drink_three_name']
            drinkthreea = drink_db['drink_three_amount']
            drinkfours = drink_db['drink_four_state']
            drinkfourn = drink_db['drink_four_name']
            drinkfoura = drink_db['drink_four_amount']
                
        return render_template(f"{APP_TEMPLATE_PATH}/index.html", sa=save_alert,
                               drink_one_state=drinkones, drink_one_name=drinkonen, drink_one_amount=drinkonea,
                               drink_two_state=drinktwos, drink_two_name=drinktwon, drink_two_amount=drinktwoa,
                               drink_three_state=drinkthrees, drink_three_name=drinkthreen, drink_three_amount=drinkthreea,
                               drink_four_state=drinkfours, drink_four_name=drinkfourn, drink_four_amount=drinkfoura)
    
    
    def edit_drinks(request):                            # load current drinks to edit page, so drinks can be edited. 
        drink_one_toggle = None
        drink_two_toggle = None
        drink_three_toggle = None
        drink_four_toggle = None
        count_toggle = 0
        
        with open(DRINKS) as f:
            drink_db = json.load(f)
            drinkones = drink_db['drink_one_state']
            if drinkones == 'on':
                drink_one_toggle = 'checked'
            else:
                count_toggle += 1
            drinkonen = drink_db['drink_one_name']
            drinkonea = drink_db['drink_one_amount']
            drinktwos = drink_db['drink_two_state']
            if drinktwos == 'on':
                drink_two_toggle = 'checked'
            else:
                count_toggle += 1
            drinktwon = drink_db['drink_two_name']
            drinktwoa = drink_db['drink_two_amount']
            drinkthrees = drink_db['drink_three_state']
            if drinkthrees == 'on':
                drink_three_toggle = 'checked'
            else:
                count_toggle += 1
            drinkthreen = drink_db['drink_three_name']
            drinkthreea = drink_db['drink_three_amount']
            drinkfours = drink_db['drink_four_state']
            if drinkfours == 'on':
                drink_four_toggle = 'checked'
            else:
                count_toggle += 1
            drinkfourn = drink_db['drink_four_name']
            drinkfoura = drink_db['drink_four_amount']
            
            if count_toggle == 4:
               save_drink_s = 'button'
            else:
                save_drink_s = 'submit'
                
        return render_template(f"{APP_TEMPLATE_PATH}/edit.html", save_drink_status=save_drink_s,
                               drink_one_t=drink_one_toggle, drink_one_state=drinkones, drink_one_name=drinkonen, drink_one_amount=drinkonea,
                               drink_two_t=drink_two_toggle, drink_two_state=drinktwos, drink_two_name=drinktwon, drink_two_amount=drinktwoa,
                               drink_three_t=drink_three_toggle, drink_three_state=drinkthrees, drink_three_name=drinkthreen, drink_three_amount=drinkthreea,
                               drink_four_t=drink_four_toggle, drink_four_state=drinkfours, drink_four_name=drinkfourn, drink_four_amount=drinkfoura)
    
    def drink_one_on(request):                                 
        update_json('drink_one_state', "on")
        return 'OK'
    
    def drink_one_off(request):                                 
        update_json('drink_one_state', "disabled")
        return 'OK'
    
    def drink_one_prime(request):                                 # prime lines
        print("priming drink 1")
        # main_dispense('one', 3)
        return 'OK'
    
    def drink_one(request):
        type_drink = 'one'                                         
        one_drink_amount = get_drink_amount(type_drink)
        # main_dispense(type_drink, one_drink_amount)
        return 'OK'
    
    def drink_two_on(request):                                 
        update_json('drink_two_state', "on")
        return 'OK'
    
    def drink_two_off(request):                                 
        update_json('drink_two_state', "disabled")
        return 'OK'
    
    def drink_two_prime(request):                                      # prime lines
        print("priming drink 2")
        #main_dispense('two', 3)
        return 'OK'
    
    def drink_two(request):                                            # Drink two implementation when pour buttion is pressed for Drink two
        type_drink = 'two'                                         
        two_drink_amount = get_drink_amount(type_drink)
        # main_dispense(type_drink, two_drink_amount)
        return 'OK'
    
    def drink_three_on(request):                                 
        update_json('drink_three_state', "on")
        return 'OK'
    
    def drink_three_off(request):                                 
        update_json('drink_three_state', "disabled")
        return 'OK'
    
    def drink_three_prime(request):                                      # prime lines
        print("priming drink 3")
        #main_dispense('three', 3)
        return 'OK'
    
    def drink_three(request):                                          # Drink three implementation when pour buttion is pressed on Drink three
        type_drink = 'three'                                         
        three_drink_amount = get_drink_amount(type_drink)
        # main_dispense(type_drink, three_drink_amount)
        return 'OK'
    
    def drink_four_on(request):                                 
        update_json('drink_four_state', "on")
        return 'OK'
    
    def drink_four_off(request):                                 
        update_json('drink_four_state', "disabled")
        return 'OK'
    
    def drink_four_prime(request):                                      # prime lines
        print("priming drink 4")
        #main_dispense('four', 3)
        return 'OK'
    
    def drink_four(request):                                           # Drink four implementation when pour buttion is pressed on Drink four
        type_drink = 'four'                                         
        four_drink_amount = get_drink_amount(type_drink)
        # main_dispense(type_drink, four_drink_amount)
        return 'OK'
    
    def app_reset(request):                                             # Resetting DrinkBot settings
        os.remove(WIFI_FILE)
        os.remove(IP_ADDRESS)
        os.remove(DRINKS)
        drink_data = {"drink_one_state": "disabled", "drink_one_name": "Drink 1", "drink_one_amount": "1.5 oz. (Single)",
                      "drink_two_state": "disabled", "drink_two_name": "Drink 2", "drink_two_amount": "1.5 oz. (Single)",
                      "drink_three_state": "disabled", "drink_three_name": "Drink 3", "drink_three_amount": "1.5 oz. (Single)",
                      "drink_four_state": "disabled", "drink_four_name": "Drink 4", "drink_four_amount": "1.5 oz. (Single)"}
        with open(DRINKS, "w") as f:
            json.dump(drink_data, f)
                                                    
        _thread.start_new_thread(machine_reset, ())                      # Reboot from new thread to start the beginning process
        return render_template(f"{APP_TEMPLATE_PATH}/reset.html", access_point_ssid = AP_NAME)

    def app_catch_all(request):
        return "Not found.", 404


    server.add_route("/", handler = app_index, methods = ["GET"])        # All methods for server
    server.add_route("/", handler = app_index, methods = ["POST"])
    
    server.add_route("/drink_one_on", handler = drink_one_on, methods = ["GET"])
    server.add_route("/drink_one_off", handler = drink_one_off, methods = ["GET"])
    server.add_route("/drink_one_prime", handler = drink_one_prime, methods = ["GET"])
    server.add_route("/drink_one", handler = drink_one, methods = ["GET"])
    
    server.add_route("/drink_two_on", handler = drink_two_on, methods = ["GET"])
    server.add_route("/drink_two_off", handler = drink_two_off, methods = ["GET"])
    server.add_route("/drink_two_prime", handler = drink_two_prime, methods = ["GET"])
    server.add_route("/drink_two", handler = drink_two, methods = ["GET"])
    
    server.add_route("/drink_three_on", handler = drink_three_on, methods = ["GET"])
    server.add_route("/drink_three_off", handler = drink_three_off, methods = ["GET"])
    server.add_route("/drink_three_prime", handler = drink_three_prime, methods = ["GET"])
    server.add_route("/drink_three", handler = drink_three, methods = ["GET"])
    
    
    server.add_route("/drink_four_on", handler = drink_four_on, methods = ["GET"])
    server.add_route("/drink_four_off", handler = drink_four_off, methods = ["GET"])
    server.add_route("/drink_four_prime", handler = drink_four_prime, methods = ["GET"])
    server.add_route("/drink_four", handler = drink_four, methods = ["GET"])
    
    server.add_route("/edit", handler = edit_drinks, methods = ["GET"])
    server.add_route("/reset", handler = app_reset, methods = ["GET"])
    server.set_callback(app_catch_all)
    
####################################### Startup process #####################################

try:
    os.stat(IP_ADDRESS)             # if IP address exist
    
    try:
        os.stat(WIFI_FILE)          # if wifi credentials exist
        with open(WIFI_FILE) as f:
            wifi_current_attempt = 1
            wifi_credentials = json.load(f)
            while (wifi_current_attempt < WIFI_MAX_ATTEMPTS):                                            # try to connect up to three times
                ip_address = connect_to_wifi(wifi_credentials["ssid"], wifi_credentials["password"])
                if is_connected_to_wifi():                                                               # confirm wifi connection
                    print(f"Connected to wifi, IP address {ip_address}")
                    break
                else:
                    wifi_current_attempt += 1
        
        with open(IP_ADDRESS) as f:                                           # load json ip address file
            ip_address_status = json.load(f)
            if ip_address_status["ipa"] == ip_address:                        # if IP address hasn't changed, start web server
                application_mode()
            else:
                print("updating IP address in json file")                     # if IP address has changed or updated, update ip address in json file and go to display IP page
                json_ip_Data = {"ipa": ip_address}
                with open(IP_ADDRESS, "w") as f:
                    json.dump(json_ip_Data, f)
                    f.close()
                display_ip()
               
    except Exception:                                             # Either no wifi configuration file found, or something went wrong, got to setup process                                         # so go into setup mode.
        setup_mode()  
             
except:                                                            # if IP address isn't found
    try:
        os.stat(WIFI_FILE)                                         
        with open(WIFI_FILE) as f:                               # File was found, attempt to connect to wifi...
            wifi_current_attempt = 1
            wifi_credentials = json.load(f)
            while (wifi_current_attempt < WIFI_MAX_ATTEMPTS):
                ip_address = connect_to_wifi(wifi_credentials["ssid"], wifi_credentials["password"]) # connect to wifi
                if is_connected_to_wifi():
                    print(f"Connected to wifi, IP address {ip_address}")
                    break
                else:
                    wifi_current_attempt += 1
        print("Saving IP Address to show to user")           # create json file to add IP address in              
        json_ip_Data = {"ipa": ip_address}      
        try:
            with open(IP_ADDRESS, "w") as f:
                json.dump(json_ip_Data, f)
                f.close()
        except:
            print("Error! Could not save file with IP address and restart attempts")
    
        if is_connected_to_wifi():
            display_ip()                                    # turns pico back into a Access point and displays IP address
        else:                                               # Bad configuration, delete the credentials file, reboot                                               
            print("Bad wifi connection!")
            print(wifi_credentials)
            os.remove(WIFI_FILE)
            os.remove(IP_ADDRESS)
            machine_reset()

    except Exception:                                              
        setup_mode()                                        # Either no wifi configuration file found, or something went wrong so go into setup mode.
                                                            
server.run()                                                # Start the web server...
