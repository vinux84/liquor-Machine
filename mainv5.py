from phew import access_point, connect_to_wifi, is_connected_to_wifi, dns, server
from phew.template import render_template
import json
import machine
import os
import utime
import _thread
import gc
from machine import Timer
import requests
import urequests
import ujson
import network
from machine import I2C, Pin
from machine import Pin, Timer
led_web_status = Pin(2, Pin.OUT)

#
AP_NAME = "DrinkBot"
AP_DOMAIN = "drinkbot.io"
AP_TEMPLATE_PATH = "ap_templates"
APP_TEMPLATE_PATH = "app_templates"
WIFI_FILE = "wifi.json"
IP_ADDRESS = "ip.json"
DRINKS = "drink.json"
WIFI_MAX_ATTEMPTS = 3
previous_time=""

# api_lock = _thread.allocate_lock()


ir_sensor_status=False


headers = {
    "Accept": "application/json",
    "User-Agent": "MicroPython"
}

# API to Get the selected drink details from alexa 
url = "https://5u0fw9o7ke.execute-api.eu-west-2.amazonaws.com/default/getdetailsDrinkBot"

drink_one = machine.Pin(28, machine.Pin.IN, machine.Pin.PULL_DOWN)
drink_two = machine.Pin(27, machine.Pin.IN, machine.Pin.PULL_DOWN)

ir_sensor = machine.Pin(21, machine.Pin.IN, machine.Pin.PULL_DOWN)

limit_switch_top = machine.Pin(16, machine.Pin.IN, machine.Pin.PULL_UP) 
limit_switch_bottom = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)

server_motor_one = machine.Pin(26, machine.Pin.OUT)
server_motor_two = machine.Pin(22, machine.Pin.OUT)

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

global top_limit_switch
top_limit_switch = True 

global bottom_limit_switch
bottom_limit_switch = False 

global thread_running
thread_running = False

button1 = Pin(16, Pin.IN, Pin.PULL_DOWN)
button2 = Pin(17, Pin.IN, Pin.PULL_DOWN)

drinktwo_var=""
drinkone_var=""
drinkthree_var=""
drinkfour_var=""
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

def update_json_api():
    global drinktwo_var
    global drinkone_var
    global drinkthree_var
    global drinkfour_var
    try:
        with open(DRINKS, 'r') as f:
            drink_db = json.load(f)
            drink_one_name = drink_db.get('drink_one_name', 'Unknown')
            drink_two_name = drink_db.get('drink_two_name', 'Unknown')
            drink_three_name = drink_db.get('drink_three_name', 'Unknown')
            drink_four_name = drink_db.get('drink_four_name', 'Unknown')
            print(drink_one_name)

            drinks_list = f"[1.{drink_one_name},2.{drink_two_name},3.{drink_three_name},4.{drink_four_name}]"
            data = json.dumps({"drinks": drinks_list})
            drinktwo_var=drink_two_name
            drinkone_var=drink_one_name
            drinkthree_var=drink_three_name
            drinkfour_var=drink_four_name
            
            
            drink_one_name_up=str(drink_one_name).replace(" ","")
            drink_two_name_up=str(drink_two_name).replace(" ","")
            drink_three_name_up=str(drink_three_name).replace(" ","")
            drink_four_name_up=str(drink_four_name).replace(" ","")
            # Send the drink details to alexa as per the Webpage
            url = "https://5u0fw9o7ke.execute-api.eu-west-2.amazonaws.com/default/drinks"
            print(url)
            
            response = urequests.post(url, headers=headers_alexa, data=data, timeout=5
                                      )  # Set a longer timeout
            print(url)
            if response.status_code == 200:
                alexa_command = response.text
                print(alexa_command)
                print("done")
            else:
                print(f"Error {response.status_code}: {response.text}")

            response.close()

    except Exception as e:
        print(f"An error occurred: {e}")


def application_mode(data_from_sensor):                                                     # Starts web server and all its functions
    print("Entering application mode.")
    global drink_three
    global drink_two
    global drink_one
    global ir_sensor_status
    print(data_from_sensor)
    
    if data_from_sensor=="test":
        
        def dispense_drink(type_drink, drink_duration):                         # code to run the actual machine
            if type_drink == 'one':
                pump_on(drink_one_pump_a, drink_one_pump_b)
                utime.sleep(drink_duration)              
                pump_off(drink_one_pump_a, drink_one_pump_b)
            elif type_drink == 'one_prime':
                pump_on(drink_one_pump_a, drink_one_pump_b)
                utime.sleep(drink_duration)              
                pump_off(drink_one_pump_a, drink_one_pump_b)
            elif type_drink == 'two':
                pump_on(drink_two_pump_a, drink_two_pump_b)
                utime.sleep(drink_duration)              
                pump_off(drink_two_pump_a, drink_two_pump_b)
            elif type_drink == 'two_prime':
                pump_on(drink_two_pump_a, drink_two_pump_b)
                utime.sleep(drink_duration)              
                pump_off(drink_two_pump_a, drink_two_pump_b)
            elif type_drink == 'three':
                pump_on(drink_three_pump_a, drink_three_pump_b)
                utime.sleep(drink_duration)              
                pump_off(drink_three_pump_a, drink_three_pump_b)
            elif type_drink == 'three_prime':
                pump_on(drink_three_pump_a, drink_three_pump_b)
                utime.sleep(drink_duration)              
                pump_off(drink_three_pump_a, drink_three_pump_b)
            elif type_drink == 'four':
                pump_on(drink_four_pump_a, drink_four_pump_b)
                utime.sleep(drink_duration)              
                pump_off(drink_four_pump_a, drink_four_pump_b)
            elif type_drink == 'four_prime':
                pump_on(drink_four_pump_a, drink_four_pump_b)
                utime.sleep(drink_duration)              
                pump_off(drink_four_pump_a, drink_four_pump_b)
           
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
            global thread_running 
            global top_limit_switch
            global bottom_limit_switch
            thread_running = True
            while thread_running:
                gc.collect()
                if limit_switch_top.value() == 0:
                    top_limit_switch = True
                    bottom_limit_switch = False
                elif limit_switch_bottom.value() == 0:
                    bottom_limit_switch = True
                    top_limit_switch = False
                    
        #         utime.sleep(1)
        def main_dispense(type_drink, drink_duration):
            global thread_running
            global  ir_sensor_status
            if ir_sensor_status:
                print("236")
                print(top_limit_switch)
                # Delay before making the next request
                if top_limit_switch == True:
                    utime.sleep(1) 
                    server_down()
                    c = 1
                    n = 1
                    while c > 0:
                        print(bottom_limit_switch)
                        if bottom_limit_switch == True:
                            c -= 1
                            server_stop()
                            utime.sleep(1)
                            spout_down()
                            utime.sleep(1)
                            dispense_drink(type_drink, drink_duration)  
                            utime.sleep(4)              
                            spout_up()
                            utime.sleep(1)
                            server_up()
                            print("herereere")
                            while n > 0:
                                if top_limit_switch == True:
                                    n -= 1
                                    server_stop()
                                    thread_running = False
                    
                        else:
                            break
                else:
                    print("limt switch false")
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
                    
        # reset()                                           # Home machine to default positions
        
        # _thread.start_new_thread(limit_switch_thread, ()) # start new thread before homepage displays
        
        def update_json(key, value):
            led_web_status.on()
            with open(DRINKS, 'r') as f:
                drink_db = json.load(f)
                drink_db[key]=value
                
            with open(DRINKS, 'w') as f:
                f.write(json.dumps(drink_db))
                print(f)
                f.close()
                update_json_api()
                led_web_status.off()  
        def app_index(request):
            save_alert = None
            if request.form:                              # checks form.request for update on drinks in json file
                for key, value in request.form.items():
                    if value != "":
                        update_json(key, value)
                save_alert = 'on'
            
            with open(DRINKS) as f:                       # load current drink keywords into index.html to display
                drink_db = json.load(f)
                drinkonen = drink_db['drink_one_name']
                drinkoned = drink_db['drink_one_duration']
                drinktwon = drink_db['drink_two_name']
                drinktwod = drink_db['drink_two_duration']
                drinkthreen = drink_db['drink_three_name']
                drinkthreed = drink_db['drink_three_duration']
                drinkfourn = drink_db['drink_four_name']
                drinkfourd = drink_db['drink_four_duration']
                f.close()
                    
            return render_template(f"{APP_TEMPLATE_PATH}/index.html", sa=save_alert,
                                   drink_one_name=drinkonen, drink_one_duration=drinkoned,
                                   drink_two_name=drinktwon, drink_two_duration=drinktwod,
                                   drink_three_name=drinkthreen, drink_three_duration=drinkthreed,
                                   drink_four_name=drinkfourn, drink_four_duration=drinkfourd)
        
        
        def edit_drinks(request):                          # load current drinks to edit page, so drinks can be edited. 
            with open(DRINKS) as f:
                
                drink_db = json.load(f)
                drinkonen = drink_db['drink_one_name']
                drinkoned = drink_db['drink_one_duration']
                drinktwon = drink_db['drink_two_name']
                drinktwod = drink_db['drink_two_duration']
                drinkthreen = drink_db['drink_three_name']
                drinkthreed = drink_db['drink_three_duration']
                drinkfourn = drink_db['drink_four_name']
                drinkfourd = drink_db['drink_four_duration']
                f.close()
                
            return render_template(f"{APP_TEMPLATE_PATH}/edit.html",
                                   drink_one_name=drinkonen, drink_one_duration=drinkoned,
                                   drink_two_name=drinktwon, drink_two_duration=drinktwod,
                                   drink_three_name=drinkthreen, drink_three_duration=drinkthreed,
                                   drink_four_name=drinkfourn, drink_four_duration=drinkfourd)
        
        
        
        def drink_one_prime(request):                                 # prime lines
            print("priming drink 1")
            # main_dispense('one_prime', 3)
            return 'OK'
        
        def drink_one(request):                                       # Drink one implementation when pour buttion is pressed for Drink one
            with open(DRINKS) as f:
                drink_db = json.load(f)
                drink_one_duration = drink_db['drink_one_duration']
                f.close()
            print("dispensing drink one")
            print(drink_one_duration)
            main_dispense('one', float(drink_one_duration))
            return 'OK'
        
        def drink_two_prime(request):                                      # prime lines
            print("priming drink 2")
            main_dispense('two_prime', 3)
            return 'OK'
        
        def drink_two(request):                                            # Drink two implementation when pour buttion is pressed for Drink two
            with open(DRINKS) as f:
                drink_db = json.load(f)
                drink_two_duration = drink_db['drink_two_duration']
                f.close()
            print("dispensing drink two")
            main_dispense('two', float(drink_two_duration))
            return 'OK'
        
        def drink_three_prime(request):                                      # prime lines
            print("priming drink 3")
            main_dispense('three_prime', 3)
            return 'OK'
        
        def drink_three(request):                                          # Drink three implementation when pour buttion is pressed on Drink three
            with open(DRINKS) as f:
                drink_db = json.load(f)
                drink_three_duration = drink_db['drink_three_duration']
                f.close()
            print("dispensing drink three")
            main_dispense('three', float(drink_three_duration))
            return 'OK'
        
        def drink_four_prime(request):                                      # prime lines
            print("priming drink 4")
            main_dispense('four_prime', 3)
            return 'OK'
        
        def drink_four(request):                                           # Drink four implementation when pour buttion is pressed on Drink four
            with open(DRINKS) as f:
                drink_db = json.load(f)
                drink_four_duration = drink_db['drink_four_duration']
                f.close()
            print("dispensing drink four")
            main_dispense('four', float(drink_four_duration))
            return 'OK'
        
      
        def app_reset(request):                                             # Resetting DrinkBot settings
            os.remove(WIFI_FILE)
            os.remove(IP_ADDRESS)
            os.remove(DRINKS)
            drink_data = {"drink_one_name": "Drink 1", "drink_one_duration": "1.5",
                          "drink_two_name": "Drink 2", "drink_two_duration": "1.5",
                          "drink_three_name": "Drink 3", "drink_three_duration": "1.5",
                          "drink_four_name": "Drink 4", "drink_four_duration": "1.5"}
            with open(DRINKS, "w") as f:
                json.dump(drink_data, f)
                f.close()
                                                        
            _thread.start_new_thread(machine_reset, ())                      # Reboot from new thread to start the beginning process
            return render_template(f"{APP_TEMPLATE_PATH}/reset.html", access_point_ssid = AP_NAME)

        def app_catch_all(request):
            return "Not found.", 404


        server.add_route("/", handler = app_index, methods = ["GET"])        # All methods for server
        server.add_route("/", handler = app_index, methods = ["POST"])
        server.add_route("/drink_one", handler = drink_one, methods = ["GET"])
        server.add_route("/drink_one_prime", handler = drink_one_prime, methods = ["GET"])
        server.add_route("/drink_two", handler = drink_two, methods = ["GET"])
        server.add_route("/drink_two_prime", handler = drink_one_prime, methods = ["GET"])
        server.add_route("/drink_three", handler = drink_three, methods = ["GET"])
        server.add_route("/drink_three_prime", handler = drink_one_prime, methods = ["GET"])
        server.add_route("/drink_four", handler = drink_four, methods = ["GET"])
        server.add_route("/drink_four_prime", handler = drink_one_prime, methods = ["GET"])
        server.add_route("/edit", handler = edit_drinks, methods = ["GET"])
        server.add_route("/reset", handler = app_reset, methods = ["GET"])
        server.set_callback(app_catch_all)
        
    else:
            if data_from_sensor=="drink_one":
                print("422")
                drink_one("test")
            if data_from_sensor=="drink_two":
                print("425")
                drink_two("test")
            if data_from_sensor=="drink_three":
                print("428")
                drink_three("test")

    ####################################### Startup process #####################################
headers_alexa = {
    'Content-Type': 'application/json',
    'Cache-Control': 'no-cache, no-store, must-revalidate'
}




inc=0      
def second_func(timer):
    global inc
    global previous_time
    global ir_sensor_status
    global drinkone_var
    global drinktwo_var
    global drinkthree_var
    global drinkfour_var
    print("----------------------------------------------------")
    if ir_sensor.value() == 0:
        inc+=1
        if inc==15:
            inc=0
        if button1.value()==0:
            print("======================== Button drink one============================")
            application_mode("drink_one")
            inc=0
            
        if button2.value()==0:
            print("============================Button drink two==========================")
            application_mode("drink_two")
            inc=0
        
        if inc==5:
            
            
            response = urequests.get(url, headers=headers_alexa)
            
            alexa_command = response.text
            response.close()  
                        
                    # Process the command
            if alexa_command and alexa_command != '{"result":"null"}':
                repl = str(alexa_command).split("datetime")
                conv_str_repl = str(repl[1])
                get_time = str(conv_str_repl).replace(":", "").replace("am", "").replace('"', '').replace("}", "").replace("pm","").replace(" ", "")
                print(get_time)
                conv_tim_int=int(get_time)
                if conv_tim_int!=previous_time:
                    print("drink true")
                    previous_time=conv_tim_int
                    repl = str(alexa_command).split("title")
                    again_spl = str(repl[1]).split('"')
                    command_upper = again_spl[2][:-1].strip()
                    
                    command=command_upper.lower()
                    print(command)
                    drinkone_var_upper=drinkone_var.lower()
                    drinktwo_var_upper=drinktwo_var.lower()
                    drinkthree_var_upper=drinkthree_var.lower()
                    drinkfour_var_upper=drinkfour_var.lower()
                    
                    print(drinkone_var_upper)
                    inc=0
                    
                    
                    if command == drinkone_var_upper:
                        print("===============alexa call "+drinkone_var_upper+" =====================")
                        application_mode("drink_one")
                    elif command == drinktwo_var_upper:
                        print("===============alexa call "+drinktwo_var_upper+"=====================")
                        application_mode("drink_two")
                    elif command == drinkthree_var_upper:
                        print("===============alexa call "+drinkthree_var_upper+"=====================")
                        application_mode("drink_three")
                    elif command == drinkfour_var_upper:
                        print("===============alexa call "+drinkfour_var_upper+"=====================")
                        application_mode("drink_four")
                else:
                    print("same as last one ")
            ir_sensor_status=False

        
    

timer = Timer(-1)
timer.init(period=1000, mode=Timer.PERIODIC, callback=second_func)




while True:
    try:
        os.stat(IP_ADDRESS)             # if IP address exist
        print(IP_ADDRESS)
        try:
            os.stat(WIFI_FILE)          # if wifi credentials exist
            with open(WIFI_FILE) as f:
                wifi_current_attempt = 1
                wifi_credentials = json.load(f)
                while (wifi_current_attempt < WIFI_MAX_ATTEMPTS):                                            # try to connect up to three times
                    ip_address = connect_to_wifi(wifi_credentials["ssid"], wifi_credentials["password"])
                    if is_connected_to_wifi():
                        
                        # confirm wifi connection
                        
                        print(f"Connected to wifi, IP address {ip_address}")
                        update_json_api()
                        application_mode("test")
                        
                        break
                    else:
                        wifi_current_attempt += 1
            
            with open(IP_ADDRESS) as f:                                           # load json ip address file
                ip_address_status = json.load(f)
                if ip_address_status["ipa"] == ip_address:                        # if IP address hasn't changed, start web server
                    application_mode("test")
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
            print("except")
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

    server.run()
