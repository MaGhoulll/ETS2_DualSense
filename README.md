# ETS 2 DualSense Full Support Suite (v1.61)

[🇷🇺 Русский](#русский) | [🇬🇧 English](#english)

---

<a name="русский"></a>
## 🇷🇺 Полная интеграция контроллера DualSense в Euro Truck Simulator 2 (v1.61)

Автономный набор скриптов и модов для ПК, обеспечивающий прямую работу геймпада **Sony DualSense** (через USB или Bluetooth) с игрой **Euro Truck Simulator 2 (версия 1.61)** без использования стороннего платного софта (вроде DualSenseX или DS4Windows).

### 🚀 Реализованные фишки:
* **Адаптивный курок газа (R2):** Легкая и комфортная педаль в крейсерском режиме, плавно нарастающая пульсация при тяжелой нагрузке в гору («внатяг») и мягкий зуд на отсечке оборотов.
* **Адаптивный курок тормоза (L2):** Пневматическое сопротивление, зависящее от скорости тягача, и срабатывание **ABS** при экстренном торможении.
* **Пространственная стерео-вибрация (Left / Right Stereo Haptics):** 
  * Поколесный анализ дорожного покрытия: наезд на виброразметку, гравий или бордюр левой или правой стороной отдает строго в соответствующую ладонь.
  * Переливающаяся волна крутящего момента при трогании с места.
  * Направленные удары при авариях и столкновениях.
* **Светодиодная индикация:** Подсветка тачпада дублирует поворотники, аварийку, дальний свет, ручник, ретардер и статус двигателя; 5 нижних диодов показывают уровень топлива в баке.

### 📁 Структура файлов проекта:
1. `scs-telemetry.dll` — плагин телеметрии (кладется в папку игры). 
Для работы телеметрии скачайте плагин `scs-telemetry.dll` из официального репозитория [RenCloud/scs-sdk-plugin](https://github.com/RenCloud/scs-sdk-plugin/releases) и поместите его в папку с игрой.
2. `hidapi.dll` — драйвер HID-связи с геймпадом.
**[libusb/hidapi](https://github.com/libusb/hidapi)** — Кроссплатформенная библиотека для низкоуровневой работы с HID-устройствами (DualSense).
3. `requirements.txt` — зависимости Python (`pydualsense`, `truck-telemetry`, `psutil`).
4. `config_patcher.py` — авто-патчер мертвых зон и кривых профиля `controls.sii` + генератор UI-мода.
5. `dualsense_ets2.py` — главное ядро телеметрии, триггеров и стерео-вибрации.
6. `start_ets2_dualsense.bat` — лаунчер в один клик.

### 🛠 Установка и настройка:
1. **Плагин игры:** Скопируйте файл `scs-telemetry.dll` в папку `...\Euro Truck Simulator 2\bin\win_x64\plugins\` (если папки нет — создайте её).
2. **Файлы скрипта:** Положите `hidapi.dll`, `requirements.txt`, `config_patcher.py`, `dualsense_ets2.py` и `start_ets2_dualsense.bat` в общую рабочую папку (например, `C:\ETS2_DualSense`). 
3. **Настройки Steam:** Откройте Библиотеку Steam → ПКМ по ETS 2 → Свойства → Контроллер → Выберите **«Отключить систему ввода Steam»**.
4. **Запуск:** Подключите геймпад и запустите **`start_ets2_dualsense.bat`**.

---

<a name="english"></a>
## 🇬🇧 Full DualSense Controller Integration for Euro Truck Simulator 2 (v1.61)

An autonomous Python & C++ suite for PC that provides native, direct integration of the **Sony DualSense** controller with **Euro Truck Simulator 2 (v1.61)** without requiring paid third-party apps.

### 🚀 Key Features:
* **Adaptive Throttle (R2):** Light, comfortable pedal resistance during cruising, smoothly ramping haptic pulses under heavy uphill loads ("lugging"), and rev-limiter buzz.
* **Adaptive Brake (L2):** Speed-dependent pneumatic pedal resistance and **ABS** feedback during emergency stops.
* **Spatial Stereo Haptics:** 
  * Wheel-by-wheel road surface analysis: rumble strips, gravel, or curbs felt specifically on the left or right side of the gamepad.
  * Launch torque wave when pulling away from a standstill.
  * Directional crash impacts.
* **LED Telemetry:** Lightbar reflects turn signals, hazard lights, high beams, parking brake, retarder, and engine status; lower LEDs show fuel level.

### 🛠 Installation & Setup:
1. Place `scs-telemetry.dll` into `...\Euro Truck Simulator 2\bin\win_x64\plugins\`.
2. Place `hidapi.dll`, Python scripts, and the `.bat` file into your working directory (e.g., `C:\ETS2_DualSense`).
3. In Steam, right-click ETS 2 → Properties → Controller → Set to **"Disable Steam Input"**.
4. Run **`start_ets2_dualsense.bat`**.