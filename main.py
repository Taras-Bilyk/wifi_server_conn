from machine import Pin # type: ignore (це технічний коментар щоб PyCherm не сварився)
import network # type: ignore (це технічний коментар щоб PyCherm не сварився)
import _thread
import socket
import time

wifi_ssid = "SSID" # ВАШЕ ІМЯ ВАЙФАЯ
wifi_pwd = "PSSWORD" # ВАШ ПАРОЛЬ ВІД ВАЙФАЯ
ip_of_computer = '192.168.0.XXXX' # айпі адреса сервера (НЕ ЛОКАЛХОСТ)
port = 14888 # порт можна назначити будь який, головне НА СЕРВЕРІ також змініть порт на ТАКИЙ САМИЙ

#====== pins for diagnostics =======
green_led_if_connected_wifi = Pin(12, Pin.OUT)
red_led_if_not_connected_wifi = Pin(14, Pin.OUT)
green_led_if_connected_server = Pin(26, Pin.OUT)
red_led_if_not_connected_server = Pin(33, Pin.OUT)
green_led_if_connected_wifi.value(0)
red_led_if_not_connected_wifi.value(0)
green_led_if_connected_server.value(0)
red_led_if_not_connected_server.value(0)

#====== pins for project (you can edit it for your needs) =======
white_led = Pin(2, Pin.OUT)
white_led.value(0)

#===== wifi connecting =====
wifi_module = network.WLAN(network.STA_IF)
wifi_module.active(True)
wifi_module.connect(wifi_ssid, wifi_pwd)
#===== internal vars =====
connected_to_server = 0
s = None

def is_wifi_connected_led():
    global wifi_module
    if wifi_module.isconnected():
        red_led_if_not_connected_wifi.value(0)
        green_led_if_connected_wifi.value(1)
    else:
        red_led_if_not_connected_wifi.value(1)
        green_led_if_connected_wifi.value(0)
def connection_to_server():
    global connected_to_server, s
    if connected_to_server == 0:
        try:
            if s:
                s.close()
            s = socket.socket()
            s.connect((ip_of_computer, port))
            green_led_if_connected_server.value(1)
            red_led_if_not_connected_server.value(0)
            connected_to_server = 1
        except:
            green_led_if_connected_server.value(0)
            red_led_if_not_connected_server.value(1)
            connected_to_server = 0
            if s:
                s.close()
            s = None
def ping_sending():
    global s
    global connected_to_server
    try:
        s.send(b'ping')
    except:
        connected_to_server = 0
        if s != None:
            s.close()
        green_led_if_connected_server.value(0)
        red_led_if_not_connected_server.value(1)
        s = None
def receive_message_from_server():
    global connected_to_server, s
    while 1:
        if connected_to_server == 1:
            try:
                message_from_server_in_bites = s.recv(1024)
                if not message_from_server_in_bites:
                    connected_to_server = 0
                    s.close()
                    s = None
                    green_led_if_connected_server.value(0)
                    red_led_if_not_connected_server.value(1)
                    continue
                message_from_server = message_from_server_in_bites.decode()
                commands = message_from_server.strip().split('\n')
                for command in commands:

                #===== actions =====
                # ставите перевірку "if command == 'EXAMPLE_COMMAND':" і ця умова покаже TRUE якщо прийде ця стрічка (каоманда) від сервера
          
          
                    if command == 'on_white':
                        white_led.value(1)
                    if command == 'off_white':
                        white_led.value(0)
                
                
                #==================
            except:
                connected_to_server = 0
                if s:
                    s.close()
                s = None
                green_led_if_connected_server.value(0)
                red_led_if_not_connected_server.value(1)
    time.sleep(0.1)
_thread.start_new_thread(receive_message_from_server, ())
def main():
    is_wifi_connected_led() # wifi connection
    connection_to_server() # connection to server
    ping_sending()
    time.sleep(0.5)
while 1:
    main()



