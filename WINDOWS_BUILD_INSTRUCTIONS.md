# Инструкция по сборке APK на Windows

## Ответы на ваши вопросы:

### 1. Программа выдаёт имя автомобиля и его данные?
**ДА**. Программа полностью реализована для декодирования VIN:

- **Файл**: `vin_decoder.py`
- **Функция**: `decode(vin)` - возвращает словарь с данными:
  - Make (марка)
  - Model (модель) 
  - ModelYear (год)
  - Manufacturer (производитель)
  - VehicleType (тип кузова)
  - PlantCountry (страна производства)
  - **FormattedName** - форматированное название вида "Nissan Silvia S15 (2002)"

- **Функция**: `get_vehicle_info_for_website(vin)` - возвращает данные, готовые для интеграции с сайтом

### 2. Что осталось сделать для сборки APK?

**Проблема**: Buildozer (инструмент для сборки APK из Python) работает только на **Linux/macOS**, а не на Windows.

**На Windows есть два варианта:**

#### Вариант A: Использовать WSL (Windows Subsystem for Linux)
1. Установить WSL Ubuntu:
   ```powershell
   wsl --install
   ```
2. Перезагрузить компьютер
3. Открыть Ubuntu и установить зависимости:
   ```bash
   sudo apt update
   sudo apt install -y python3-pip python3-kivy build-essential git ffmpeg libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev
   pip3 install buildozer
   ```
4. Скопировать проект в WSL:
   ```bash
   cp /mnt/c/Users/Itami01/OneDrive/Desktop/TunningManualOBD ~/vinreader
   cd ~/vinreader
   ```
5. Собрать APK:
   ```bash
   buildozer android debug
   ```

#### Вариант B: Использовать онлайн-сервисы
- **GitHub Actions** - можно настроить автоматическую сборку в облаке
- **Replit** - онлайн IDE с поддержкой Buildozer
- **Google Colab** - можно запустить сборку в облаке

### 3. Почему buildozer не работает на Windows?

Buildozer требует:
- Android SDK
- Android NDK
- Java JDK
- Linux-специфичные инструменты (autoconf, automake, libtool и др.)

Эти инструменты не работают на Windows напрямую.

## Альтернативный подход: Использовать BeeWare

BeeWare (Briefcase) может работать на Windows для сборки Android приложений:

```bash
pip install briefcase
briefcase create android
briefcase build android
```

Однако для OBD/Bluetooth функциональности всё равно может потребоваться дополнительная настройка.

## Текущее состояние проекта

✅ **Реализовано:**
- OBD-II подключение через Bluetooth с автоматическим PIN (1234)
- Чтение VIN с автомобиля
- Декодирование VIN через NHTSA API
- Формирование структурированного названия автомобиля
- Material Design UI (KivyMD)
- Android разрешения для Bluetooth

❌ **Ограничения:**
- Библиотека `python-obd` предназначена для desktop систем
- На Android потребуется адаптация Bluetooth подключения через pyjnius
- Сборка APK возможна только на Linux/macOS или через WSL

## Рекомендация

Для быстрого результата рекомендую:
1. Использовать WSL Ubuntu для сборки APK
2. Или настроить GitHub Actions для автоматической сборки в облаке
3. После сборки протестировать на реальном Android устройстве с OBD-II адаптером

Хотите, чтобы я помог настроить WSL или GitHub Actions для сборки?
