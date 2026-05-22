import asyncio
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.storage.jsonstore import JsonStore
import threading

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.card import MDCard
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.toast import toast
from kivymd.uix.dialog import MDDialog

from obd_interface import OBDInterface
from desktop_obd import DesktopOBDInterface
from android_obd import AndroidOBDInterface
from vin_decoder import VINDecoder
from bluetooth_manager import BluetoothManager

Window.size = (400, 700)


class MainScreen(MDScreen):
    """Main screen for VIN reader application."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.obd_interface: OBDInterface = None
        self.vin_decoder = VINDecoder()
        self.bluetooth_manager = BluetoothManager()
        self.devices = []
        self.current_vin = None
        self.current_vehicle_info = None
        self.settings_store = JsonStore('vinreader_settings.json')
        
        # Load settings
        self.pin_code = self.settings_store.get('pin_code', {'value': '1234'})['value']
        self.bluetooth_manager.default_pin = self.pin_code
        
        self.orientation = 'vertical'
        self.padding = dp(20)
        self.spacing = dp(10)
        
        self._build_ui()
    
    def _build_ui(self):
        """Build the user interface."""
        # Title
        title = MDLabel(
            text="VIN Reader",
            halign="center",
            theme_text_color="Primary",
            font_style="H5",
            size_hint_y=None,
            height=dp(60)
        )
        self.add_widget(title)
        
        # Connection Status Card
        self.connection_card = MDCard(
            size_hint_y=None,
            height=dp(100),
            padding=dp(10),
            spacing=dp(10)
        )
        connection_layout = MDBoxLayout(orientation='vertical')
        
        self.connection_status = MDLabel(
            text="Статус: Не подключено",
            halign="center",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(30)
        )
        
        self.device_spinner = Spinner(
            text='Выберите устройство',
            size_hint_y=None,
            height=dp(50),
            values=['Сканирование...']
        )
        self.device_spinner.bind(text=self.on_device_select)
        
        connection_layout.add_widget(self.connection_status)
        connection_layout.add_widget(self.device_spinner)
        self.connection_card.add_widget(connection_layout)
        self.add_widget(self.connection_card)
        
        # Action Buttons
        button_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(60)
        )
        
        self.scan_button = MDRaisedButton(
            text="Сканировать",
            on_release=self.scan_devices,
            size_hint_x=0.33
        )
        
        self.connect_button = MDRaisedButton(
            text="Подключиться",
            on_release=self.connect_to_device,
            size_hint_x=0.33
        )
        
        self.settings_button = MDRaisedButton(
            text="Настройки",
            on_release=self.show_settings,
            size_hint_x=0.33
        )
        
        button_layout.add_widget(self.scan_button)
        button_layout.add_widget(self.connect_button)
        button_layout.add_widget(self.settings_button)
        self.add_widget(button_layout)
        
        # VIN Display Card
        self.vin_card = MDCard(
            size_hint_y=None,
            height=dp(150),
            padding=dp(10),
            spacing=dp(10)
        )
        vin_layout = MDBoxLayout(orientation='vertical')
        
        vin_label = MDLabel(
            text="VIN-код:",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(30)
        )
        
        self.vin_display = MDLabel(
            text="Не считан",
            halign="center",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(40)
        )
        
        self.read_vin_button = MDRaisedButton(
            text="Считать VIN",
            on_release=self.read_vin,
            size_hint_y=None,
            height=dp(50)
        )
        
        vin_layout.add_widget(vin_label)
        vin_layout.add_widget(self.vin_display)
        vin_layout.add_widget(self.read_vin_button)
        self.vin_card.add_widget(vin_layout)
        self.add_widget(self.vin_card)
        
        # Vehicle Info Card
        self.vehicle_card = MDCard(
            size_hint_y=None,
            height=dp(200),
            padding=dp(10),
            spacing=dp(10)
        )
        vehicle_layout = MDBoxLayout(orientation='vertical')
        
        vehicle_label = MDLabel(
            text="Информация об автомобиле:",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(30)
        )
        
        self.vehicle_info_display = MDLabel(
            text="Данные не загружены",
            halign="center",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(150)
        )
        
        vehicle_layout.add_widget(vehicle_label)
        vehicle_layout.add_widget(self.vehicle_info_display)
        self.vehicle_card.add_widget(vehicle_layout)
        self.add_widget(self.vehicle_card)
        
        # Request permissions on startup
        Clock.schedule_once(self.request_permissions, 1)
    
    def request_permissions(self, dt):
        """Request Bluetooth permissions."""
        self.bluetooth_manager.request_permissions()
    
    def scan_devices(self, instance):
        """Scan for Bluetooth devices using threading."""
        self.device_spinner.values = ['Сканирование...']
        self.device_spinner.text = 'Сканирование...'
        self.scan_button.disabled = True
        
        def do_scan():
            try:
                self.devices = self.bluetooth_manager.discover_devices()
                
                def update_ui(dt):
                    if self.devices:
                        device_names = [f"{d['name']} ({d['address']})" for d in self.devices]
                        self.device_spinner.values = device_names
                        self.device_spinner.text = device_names[0]
                        toast(f"Найдено {len(self.devices)} устройств")
                    else:
                        self.device_spinner.values = ['Устройства не найдены']
                        self.device_spinner.text = 'Устройства не найдены'
                        toast("Устройства не найдены")
                    self.scan_button.disabled = False
                
                Clock.schedule_once(update_ui, 0)
                    
            except Exception as e:
                def update_error(dt):
                    self.device_spinner.values = ['Ошибка сканирования']
                    self.device_spinner.text = 'Ошибка сканирования'
                    toast(f"Ошибка: {str(e)}")
                    self.scan_button.disabled = False
                
                Clock.schedule_once(update_error, 0)
        
        # Run in separate thread to avoid blocking UI
        scan_thread = threading.Thread(target=do_scan)
        scan_thread.start()
    
    def on_device_select(self, spinner, text):
        """Handle device selection."""
        pass
    
    def connect_to_device(self, instance):
        """Connect to selected OBD-II device using threading."""
        if not self.devices:
            toast("Сначала выберите устройство")
            return
        
        selected_text = self.device_spinner.text
        if 'Сканирование' in selected_text or 'не найдены' in selected_text.lower():
            toast("Выберите устройство")
            return
        
        self.connect_button.disabled = True
        self.connection_status.text = "Статус: Подключение..."
        
        def do_connect():
            try:
                # Extract device address from selection
                device_address = None
                for device in self.devices:
                    device_text = f"{device['name']} ({device['address']})"
                    if device_text == selected_text:
                        device_address = device['address']
                        break
                
                if not device_address:
                    def error_selection(dt):
                        toast("Ошибка выбора устройства")
                        self.connect_button.disabled = False
                        self.connection_status.text = "Статус: Ошибка"
                    Clock.schedule_once(error_selection, 0)
                    return
                
                # Pair device if needed
                if not self.bluetooth_manager.is_device_paired(device_address):
                    if not self.bluetooth_manager.pair_device(device_address):
                        def error_pairing(dt):
                            toast("Ошибка сопряжения")
                            self.connect_button.disabled = False
                            self.connection_status.text = "Статус: Ошибка сопряжения"
                        Clock.schedule_once(error_pairing, 0)
                        return
                
                # Create appropriate OBD interface based on platform
                try:
                    from android import activity
                    # Android platform
                    self.obd_interface = AndroidOBDInterface(device_address)
                except ImportError:
                    # Desktop platform
                    self.obd_interface = DesktopOBDInterface()
                
                # Connect to OBD
                if self.obd_interface.connect():
                    def success(dt):
                        self.connection_status.text = f"Статус: Подключено к {selected_text}"
                        toast("Подключено успешно")
                    Clock.schedule_once(success, 0)
                else:
                    def error_connect(dt):
                        self.connection_status.text = "Статус: Ошибка подключения"
                        toast("Ошибка подключения OBD")
                        self.connect_button.disabled = False
                    Clock.schedule_once(error_connect, 0)
                    
            except Exception as e:
                def error_general(dt):
                    self.connection_status.text = "Статус: Ошибка"
                    toast(f"Ошибка: {str(e)}")
                    self.connect_button.disabled = False
                Clock.schedule_once(error_general, 0)
        
        # Run in separate thread to avoid blocking UI
        connect_thread = threading.Thread(target=do_connect)
        connect_thread.start()
    
    def read_vin(self, instance):
        """Read VIN from connected device using threading."""
        if not self.obd_interface or not self.obd_interface.is_connected():
            toast("Сначала подключитесь к устройству")
            return
        
        self.read_vin_button.disabled = True
        self.vin_display.text = "Чтение..."
        
        def do_read():
            try:
                vin = self.obd_interface.read_vin()
                
                if vin:
                    def success(dt):
                        self.current_vin = vin
                        self.vin_display.text = vin
                        toast("VIN считан успешно")
                        self.decode_vin()
                    Clock.schedule_once(success, 0)
                else:
                    def error(dt):
                        self.vin_display.text = "Ошибка чтения"
                        toast("Не удалось считать VIN")
                        self.read_vin_button.disabled = False
                    Clock.schedule_once(error, 0)
                    
            except Exception as e:
                def error(dt):
                    self.vin_display.text = "Ошибка"
                    toast(f"Ошибка: {str(e)}")
                    self.read_vin_button.disabled = False
                Clock.schedule_once(error, 0)
        
        # Run in separate thread to avoid blocking UI
        read_thread = threading.Thread(target=do_read)
        read_thread.start()
    
    def show_settings(self, instance):
        """Show settings dialog for PIN configuration."""
        dialog_content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=dp(20),
            size_hint_y=None,
            height=dp(150)
        )
        
        pin_label = MDLabel(
            text="PIN-код Bluetooth:",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(30)
        )
        
        pin_field = MDTextField(
            text=self.pin_code,
            hint_text="Введите PIN-код",
            size_hint_y=None,
            height=dp(50)
        )
        
        dialog_content.add_widget(pin_label)
        dialog_content.add_widget(pin_field)
        
        self.settings_dialog = MDDialog(
            title="Настройки",
            type="custom",
            content_cls=dialog_content,
            buttons=[
                MDFlatButton(
                    text="Отмена",
                    on_release=lambda x: self.settings_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="Сохранить",
                    on_release=lambda x: self.save_pin(pin_field.text)
                )
            ]
        )
        self.settings_dialog.open()
    
    def save_pin(self, new_pin):
        """Save new PIN code."""
        if new_pin and len(new_pin) >= 4:
            self.pin_code = new_pin
            self.bluetooth_manager.default_pin = new_pin
            self.settings_store.put('pin_code', value=new_pin)
            toast("PIN-код сохранен")
            self.settings_dialog.dismiss()
        else:
            toast("PIN-код должен быть не менее 4 символов")
    
    def decode_vin(self):
        """Decode the current VIN."""
        if not self.current_vin:
            return
        
        self.vehicle_info_display.text = "Декодирование..."
        
        def do_decode(dt):
            try:
                vehicle_info = self.vin_decoder.decode(self.current_vin)
                
                if vehicle_info:
                    self.current_vehicle_info = vehicle_info
                    
                    # Format display
                    info_text = f"Марка: {vehicle_info.get('Make', 'N/A')}\n"
                    info_text += f"Модель: {vehicle_info.get('Model', 'N/A')}\n"
                    info_text += f"Год: {vehicle_info.get('ModelYear', 'N/A')}\n"
                    info_text += f"Производитель: {vehicle_info.get('Manufacturer', 'N/A')}\n"
                    info_text += f"Тип: {vehicle_info.get('VehicleType', 'N/A')}\n"
                    info_text += f"Страна: {vehicle_info.get('PlantCountry', 'N/A')}\n\n"
                    info_text += f"Полное название:\n{vehicle_info.get('FormattedName', 'N/A')}"
                    
                    self.vehicle_info_display.text = info_text
                    toast("VIN декодирован")
                else:
                    self.vehicle_info_display.text = "Ошибка декодирования"
                    toast("Не удалось декодировать VIN")
                    
            except Exception as e:
                self.vehicle_info_display.text = "Ошибка"
                toast(f"Ошибка декодирования: {str(e)}")
        
        Clock.schedule_once(do_decode, 0.5)


class VINReaderApp(MDApp):
    """Main application class."""
    
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        
        return MainScreen()
    
    def on_stop(self):
        """Clean up on app exit."""
        # Disconnect OBD if connected
        if hasattr(self.root, 'obd_interface') and self.root.obd_interface:
            self.root.obd_interface.disconnect()


if __name__ == '__main__':
    VINReaderApp().run()
