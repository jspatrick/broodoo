#!/home/pi/brew_temp/venv/bin/python

import sys, traceback, time, os, glob, subprocess, re, datetime
try:
    import RPi.GPIO as GPIO
except ImportError:
    print("Error importing GPIO!")
    
import brew

print subprocess.call(['modprobe',  'w1-gpio'])
subprocess.call(['modprobe',  'w1-gpio'])

#LED Setup
RED_LED = 23
GREEN_LED = 18
BLUE_LED = 21
BUTTON = 22

GPIO.setmode(GPIO.BCM)
GPIO.setup(GREEN_LED, GPIO.OUT)
GPIO.setup(RED_LED, GPIO.OUT)
GPIO.setup(BLUE_LED, GPIO.OUT)
GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

#Temp device setup
BASE_DEVICE_DIR = '/sys/bus/w1/devices/'
DEVICE_FOLDER = glob.glob(BASE_DEVICE_DIR + '28-*')[0]
DEVICE_FILE = os.path.join(DEVICE_FOLDER + '/w1_slave')

GOOD_TEMP_RANGE = (70, 80)



TIME_FMT = "%d/%m/%y %H:%M:%S"

def read_temp_raw():
    try:
        f = open(DEVICE_FILE, 'r')
        lines = f.readlines()
    finally:
        f.close()
    return lines

def test_leds():
    GPIO.output(RED_LED, True)
    GPIO.output(GREEN_LED, True)
    GPIO.output(BLUE_LED, True)    

    
def read_temp(farenheit=True):
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(.1)
        lines = read_temp_raw()
    matches = re.search(".*t=([0-9]+)", lines[1])
    
    temp = float(matches.group(1)) / 1000
    if farenheit:
        temp = (temp*(9.0/5))+32
    return temp

def activate_single_led(led_to_activate, is_active=True):
    all_leds = [RED_LED, GREEN_LED, BLUE_LED]
    for led in all_leds:
        if (led == led_to_activate):
            GPIO.output(led, is_active)
        else:
            GPIO.output(led, False)
            
def activate_correct_led(temp):
    active_led = None

    #set the active LED and blinks/second
    if (temp < GOOD_TEMP_RANGE[0]):
        active_led = BLUE_LED        
    elif (temp > GOOD_TEMP_RANGE[1]):        
        active_led = RED_LED
    else:
        active_led = GREEN_LED

    is_on = True
    activate_single_led(active_led, is_on)

    
g_brew = None
g_brew_file = None
g_brew_name = "JP's IPA"
g_username = 'john'
g_last_time_recorded = datetime.datetime.now()
def get_filepath():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    homedir = os.environ['HOME']
    return os.path.join(homedir, "%s_templog.csv")
    
def main_loop():
    global g_brew
    global g_brew_file
    global g_last_time_recorded
    
    if not g_brew:
        try:
            g_brew = brew.Brew(g_username, g_brew_name)
        except:
            g_brew = None
            print("Cannot update temp")
    if not g_brew_file:
        g_brew_file = open(get_filepath(), "w")
    temp = read_temp()
    activate_correct_led(temp)
    print temp

    now = datetime.datetime.now()
    now_str = now.strftime(TIME_FMT)
    elapsed = (now - g_last_time_recorded).total_seconds()
    if elapsed < 5:
        time.sleep(1)
    else:
        if g_brew:
            try:
                g_brew.update_temp(temp)
            except:
                print "Cannot update temp on web"
        if g_brew_file:
            g_brew_file.write("%.1f degrees f,%s\n" %(temp, now_str))
        g_last_time_recorded = now

def button_press(channel):
    print "Pressed"
    global g_brew
    if g_brew:
        g_brew.create_event("button pressed")
        
    for led in [BLUE_LED, GREEN_LED, RED_LED]:
        GPIO.output(led, False)
    time.sleep(1)
    

GPIO.add_event_detect(BUTTON, GPIO.RISING, callback=button_press, bouncetime=300)

def main(args):
    try:
        while True:
            main_loop()
            
    except KeyboardInterrupt:
        print "\nCtrl-c detected"        
    finally:
        GPIO.cleanup()
        if g_brew_file:
            g_brew_file.close()    

if __name__ == "__main__":
    print "Running!"
    result = 0
    try:
        main(sys.argv)        
    except:
        print("Error detected!")
        result=2
        traceback.print_exc()

    sys.exit(result)
