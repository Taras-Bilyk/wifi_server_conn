from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
import threading
import socket
import time

class serverApp(App):
    def build(self):
        Window.bind(on_key_down=self.on_white_led_from_key)
        Window.bind(on_key_up=self.off_white_led_from_key)

        #==== interface ====
        self.main_layout = FloatLayout()
        self.label_with_ip_of_connected_device = Label(text = 'server listening...',
                                                        color = (1, 1, 1, 1),
                                                        font_size=20,
                                                        size_hint=(.3, .1),
                                                        pos_hint={'x': 0, 'y': .9})
        self.disconnected_label = Label(text = '!!! disconnected ... !!!',
                                                        color = (1, 0, 0, 1),
                                                        font_size=20,
                                                        size_hint=(.3, .1),
                                                        pos_hint={'x': 0, 'y': 0})
        self.button = Button(background_color = (.2, .2, .2, 1),
                             size_hint=(.5, .5),
                            pos_hint={'x': .5, 'y': 0},
                            on_press = self.on_white_led,
                            on_release = self.off_white_led)
        self.main_layout.add_widget(self.label_with_ip_of_connected_device)
        self.main_layout.add_widget(self.button)
        #==========================

        self.host = '0.0.0.0' # має бути саме '0.0.0.0' !!!
        self.port = 14888 # порт можна назначити будь який, головне на клієнті також змініть порт на такий самий
        self.is_server_listening = 0
        self.listen_process = threading.Thread(target = self.listen)
        self.listen_process.daemon = True
        self.listen_process.start()
        self.get_data_from_client = threading.Thread(target = self.listen_connected_device)
        self.get_data_from_client.daemon = True
        self.get_data_from_client.start()
        return self.main_layout

    def listen(self):
        while 1:
            if self.is_server_listening == 0:
                self.label_with_ip_of_connected_device.text = 'server listening...'
                self.s = socket.socket()
                self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.s.bind((self.host, self.port))
                self.s.listen(1)
                self.conn, self.addr = self.s.accept()
                self.conn.settimeout(10)
                self.label_with_ip_of_connected_device.text = str(self.addr)
                self.is_server_listening = 1
                self.get_data_from_client = threading.Thread(target=self.listen_connected_device)
                self.get_data_from_client.daemon = True
                self.get_data_from_client.start()
            time.sleep(0.5)
    def send_message_to_connected_device(self, data):
        if self.is_server_listening == 1:
            self.conn.send((str(data)+'\n').encode())
    def listen_connected_device(self):
        while 1:
            if self.is_server_listening == 1:
                try:
                    self.data_from_client_in_bites = self.conn.recv(1024)
                    if not self.data_from_client_in_bites:
                        self.label_with_ip_of_connected_device.text = 'server listening...'
                        self.is_server_listening = 0
                        try:
                            self.conn.close()
                        except:
                            pass
                        self.conn = None
                        self.addr = None
                        continue
                    self.data_from_connected_device = self.data_from_client_in_bites.decode()
                    self.label_with_ip_of_connected_device.text = str(self.addr)
                    self.is_server_listening = 1
                except socket.timeout:
                    self.label_with_ip_of_connected_device.text = 'server listening...'
                    self.is_server_listening = 0
                    try:
                        self.conn.close()
                    except:
                        pass
                    self.conn = None
                    self.addr = None
                except:
                    pass
            time.sleep(0.5)
#================================= send commands to client =========================
# use self.send_message_to_connected_device('EXAMPLE_COMMAND') to send something to client


    def on_white_led(self, instance):
        self.send_message_to_connected_device('on_white')
    def off_white_led(self, instance):
        self.send_message_to_connected_device('off_white')
    
    def on_white_led_from_key(self, window, key, scancode, codepoint, modifier):
        self.send_message_to_connected_device('on_white')
    def off_white_led_from_key(self, window, key, scancode):
        self.send_message_to_connected_device('off_white')



#====================================================================================

serverApp().run()






