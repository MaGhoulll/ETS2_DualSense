# ETS 2 PS5 DualSense Telemetry & Haptics Suite (v1.61)

This software provides a telemetry-driven haptic feedback and adaptive trigger profile for Euro Truck Simulator 2 (version 1.61+), designed specifically for the PlayStation 5 DualSense controller on PC. It reads real-time physics data from the game memory via the SCS Telemetry SDK and communicates directly with the controller over the HID protocol without requiring paid third-party wrappers.

* [English Documentation](#english-documentation)
* [Документация на русском языке](#документация-на-русском-языке)

---

<a name="english-documentation"></a>
## English Documentation

### Acknowledgments
This project relies on the following open-source libraries and plugins:
* **[RenCloud/scs-sdk-plugin](https://github.com/RenCloud/scs-sdk-plugin)** — Native C++ telemetry plugin that exports live vehicle and world physics from Euro Truck Simulator 2 to Windows shared memory (`Local\SCSTelemetry`).
* **[libusb/hidapi](https://github.com/libusb/hidapi)** — Low-level cross-platform library used for direct USB and Bluetooth HID communication with the DualSense controller.
* **[flok/pydualsense](https://github.com/flok/pydualsense)** — Python interface for controlling DualSense trigger registers, haptic motors, and LEDs.
* **[truck-telemetry](https://pypi.org/project/truck-telemetry/)** — Python shared memory reader for the SCS Telemetry SDK.

---

### Features

* **Engine & Drivetrain Simulation:**
  * **Engine Cranking:** Rhythmic starter motor pulses when turning the ignition on.
  * **Rolling Torque Launch Wave:** Smooth sinusoidal vibration wave shifting between the left and right motors during initial acceleration from a standstill (0.2 to 22 km/h), scaling in frequency with vehicle speed.
  * **Progressive Engine Lugging (R2 Trigger & Chassis):** Smooth envelope filter that detects genuine drivetrain strain (high gear, high throttle, low RPM, and low acceleration on steep inclines). Includes a 1.5-second post-shift grace period to prevent false activation during normal gear changes.
  * **Redline Warning (R2 Trigger):** High-frequency vibration on the accelerator trigger when engine RPM exceeds 89% of its limit.
  * **Gear Shift Jolt:** Crisp, load-dependent mechanical pulse every time a gear is engaged.
* **Braking & Pneumatic Physics:**
  * **Speed-Dependent Brake Resistance (L2 Trigger):** Light, comfortable baseline resistance during normal braking that progressively stiffens as truck speed increases.
  * **ABS & Heavy Braking Pulsation (L2 Trigger):** Active pulsing feedback on the left trigger combined with chassis pitch vibration when braking above 58% at speeds over 18 km/h.
  * **Low Air Pressure Lockup:** High rigid resistance at the end of the L2 trigger travel when the brake air pressure warning is active.
* **Spatial Stereo Road Feedback (Left / Right Separation):**
  * **Directional Surface Detection:** Reads individual front-left and front-right wheel telemetry (`wheelSubstance` and `wheelSuspDeflection`). Driving onto gravel, grass, curbs, or rumble strips with the right wheels vibrates strictly the right side of the controller (and vice versa for the left side).
  * **Chassis Roll & Lateral Impacts:** Potholes, bridge joints, and collisions are panned across the left and right motors based on lateral acceleration and cabin roll vectors.
* **Profile Configuration Patcher (`controls.sii`):**
  * Automatically backs up and patches the local ETS 2 profile (`controls.sii`) to set optimal deadzones (`2%`), separate trigger axes, and an expanded steering non-linearity curve (`1.0 + c_steer_func * 1.6`) that remains fully compatible with in-game sliders.
* **Status Indicators:**
  * **Lightbar Telemetry:**
    * Blinking Green: Left or right turn signal active.
    * Blinking Orange: Hazard lights active.
    * Solid Red: Parking brake engaged (flashes bright red on collision).
    * Ice White: High beam headlights active.
    * Cyan: Retarder engaged.
    * Dim Dark Blue: Normal driving with engine running.
  * **Player LED Fuel Gauge:** The bottom LEDs indicate current fuel tank level in 25% steps (`PLAYER_4` down to `PLAYER_1`).
  * **Microphone LED Master Warning:** Illuminates when fuel drops below 15% or when brake air pressure is critically low.

---

### Prerequisites & Required Files

1. **Python 3.10 or newer** installed on your system (ensure *"Add Python to PATH"* was checked during installation).
2. **`scs-telemetry.dll`**: Download the latest release from **[RenCloud/scs-sdk-plugin Releases](https://github.com/RenCloud/scs-sdk-plugin/releases)**.
3. **`hidapi.dll`**: Download `hidapi-win.zip` from **[libusb/hidapi Releases](https://github.com/libusb/hidapi/releases)** and extract `hidapi.dll` from the `x64` folder.

---

### Installation

1. Download or clone this repository into a dedicated folder (for example, `C:\ETS2_DualSense\`).
2. Place the extracted **`hidapi.dll`** (from the `x64` archive folder) directly into the root of this script folder (`C:\ETS2_DualSense\hidapi.dll`), next to `dualsense_ets2.py`.
3. Navigate to your Euro Truck Simulator 2 installation directory:
   `...\Steam\steamapps\common\Euro Truck Simulator 2\bin\win_x64\`
4. Create a folder named **`plugins`** inside `win_x64` (if it does not already exist) and place **`scs-telemetry.dll`** inside it:
   `...\Euro Truck Simulator 2\bin\win_x64\plugins\scs-telemetry.dll`

---

### Steam & In-Game Configuration (Important)

To allow direct access to the DualSense adaptive trigger registers and prevent input conflicts, complete these steps once:

1. **Disable Steam Input:**
   * Open your Steam Library, right-click **Euro Truck Simulator 2** -> **Properties** -> **Controller**.
   * Select **"Disable Steam Input"** from the dropdown menu.
   * Close any background controller remappers (such as DS4Windows or DualSenseX).
2. **Disable Steam Cloud for Profile Configuration Patching:**
   * Launch ETS 2. On the profile selection screen, select your profile, click **Edit Profile**, and uncheck **Use Steam Cloud**. This ensures your `controls.sii` file is stored locally in `Documents\Euro Truck Simulator 2\profiles\`.
3. **Bind Primary Axes in ETS 2:**
   * Go to **Options** -> **Controls**.
   * At the top device selector, choose **`Keyboard + Wireless Controller`**.
   * Assign **Steering Axis** (Left Stick X), **Acceleration Axis** (R2), and **Brake Axis** (L2).
   * Check the yellow input bars under Acceleration and Brake: if the bar is full when the trigger is released, set the axis mode to **Inverted** or **Inverted and Centered**.
   * Exit the game so ETS 2 saves the clean `controls.sii` file.

#### DirectInput Button Reference Table
When Steam Input is disabled, Euro Truck Simulator 2 addresses the DualSense via DirectInput (`Button 0` – `Button 13`):

| In-Game Label | DualSense Button | In-Game Label | DualSense Button |
| :--- | :--- | :--- | :--- |
| **Button 0** | Square | **Button 7** | R2 Trigger (Digital) |
| **Button 1** | Cross | **Button 8** | Create (Share) |
| **Button 2** | Circle | **Button 9** | Options |
| **Button 3** | Triangle | **Button 10** | L3 (Left Stick Click) |
| **Button 4** | L1 Bumper | **Button 11** | R3 (Right Stick Click) |
| **Button 5** | R1 Bumper | **Button 12** | PS Button |
| **Button 6** | L2 Trigger (Digital) | **Button 13** | Touchpad Click |

---

### How to Use

1. Connect your DualSense controller via USB or Bluetooth.
2. Run **`start_ets2_dualsense.bat`** (keep the game closed prior to running the batch file so `config_patcher.py` can update `controls.sii`).
3. During execution, the batch launcher will:
   * Install required Python packages (`pydualsense`, `truck-telemetry`, `psutil`).
   * Patch `controls.sii` in your Documents folder.
   * Locate `eurotrucks2.exe` automatically (or ask for the path once and save it to `ets2_path.cfg`) and launch the game.
   * Attach to `Local\SCSTelemetry`.
4. When the game starts, confirm the **"Advanced SDK features detected"** dialog by clicking **OK**.
5. To stop the service after exiting the game, press `Ctrl + C` in the console window or close the window.

---
---

<a name="документация-на-русском-языке"></a>
## Документация на русском языке

Данное приложение обеспечивает полную поддержку контроллера PlayStation 5 DualSense в игре Euro Truck Simulator 2 (версия 1.61 и новее) на ПК. Скрипт считывает телеметрию физики из оперативной памяти игры в реальном времени и управляет адаптивными триггерами, пространственной стерео-вибрацией и светодиодами напрямую через протокол HID без использования платного стороннего ПО.

### Используемые компоненты
Работа проекта основана на следующих открытых библиотеках:
* **[RenCloud/scs-sdk-plugin](https://github.com/RenCloud/scs-sdk-plugin)** — Нативный C++ плагин для выгрузки телеметрии из движка ETS 2 в разделяемую память Windows (`Local\SCSTelemetry`).
* **[libusb/hidapi](https://github.com/libusb/hidapi)** — Библиотека для прямой низкоуровневой связи с контроллером DualSense по USB и Bluetooth.
* **[flok/pydualsense](https://github.com/flok/pydualsense)** — Python-библиотека для управления регистрами триггеров, моторов и подсветки DualSense.
* **[truck-telemetry](https://pypi.org/project/truck-telemetry/)** — Модуль чтения разделяемой памяти SCS Telemetry SDK.

---

### Реализованные функции

* **Симуляция двигателя и трансмиссии:**
  * **Запуск стартера:** Ритмичные импульсы моторов при повороте ключа зажигания и пуске дизеля.
  * **Переливающаяся волна при старте с места:** Плавная синусоидальная волна вибрации, перетекающая между левым и правым мотором при трогании с места под газом (от 0.2 до 22 км/ч). Частота перелива растет пропорционально набору скорости и плавно затухает при выходе на крейсерский ход.
  * **Плавная нагрузка «Двигатель внатяг» (Курок R2 и кузов):** Огибающий фильтр (Envelope Filter), определяющий реальную тяжесть хода (крутой подъем, высокая передача, газ > 68%, низкие обороты < 1120 RPM и отсутствие ускорения). Включает 1.5-секундную задержку после переключения КПП для исключения ложных срабатываний. Сопротивление и пульсация на курке R2 плавно нарастают по мере нагрузки и мягко стихают, когда тягачу становится легче.
  * **Отсечка оборотов (Курок R2):** Предупреждающая высокочастотная вибрация в верхней части хода педали газа при превышении 89% максимальных оборотов.
  * **Переключение передач:** Короткий механический толчок при смене ступени КПП, сила которого зависит от текущего нажатия на педаль газа.
* **Тормозная система и пневматика:**
  * **Динамическое усилие на тормозе (Курок L2):** Мягкий и комфортный ход курка при плавных притормаживаниях, прогрессивно тяжелеющий с ростом скорости тягача.
  * **Срабатывание ABS и экстренное торможение (Курок L2):** При нажатии тормоза свыше 58% на скорости более 18 км/ч включается отдача ABS на курке L2 и вибрация шасси от клевка кабины.
  * **Падение давления воздуха:** Блокировка курка L2 жестким упором при срабатывании аварийного датчика давления в тормозной системе.
* **Пространственная стерео-физика дороги (Разделение Лево / Право):**
  * **Поколесный анализ покрытия и подвески:** Скрипт считывает данные переднего левого и переднего правого колеса (`wheelSubstance` и `wheelSuspDeflection`). При наезде правыми колесами на виброразметку, гравийную обочину, траву или бордюр вибрирует **строго правая сторона** геймпада (при наезде левыми колесами — строго левая).
  * **Крен кабины и направленные столкновения:** Кочки, стыки мостов и аварии распределяются между левым и правым мотором по вектору бокового ускорения и углу крена кабины.
* **Автоматический патчер профиля (`controls.sii`):**
  * Создает резервную копию и настраивает оптимальные мертвые зоны (`2%`), раздельные оси курков и расширенную формулу нелинейности руля (`1.0 + c_steer_func * 1.6`), которая полностью совместима с внутриигровыми ползунками настроек.
* **Светодиодная индикация:**
  * **Световая панель (Lightbar):**
    * Мигающий зеленый: Поворотники.
    * Мигающий оранжевый: Аварийная сигнализация.
    * Красный: Стояночный тормоз (при ДТП — яркая красная вспышка).
    * Бело-голубой: Дальний свет фар.
    * Голубой: Активен ретардер.
    * Спокойный темно-синий: Штатная работа двигателя.
  * **Индикатор топлива (Player LEDs):** Нижние белые светодиоды отображают остаток топлива в баке с шагом 25%.
  * **Светодиод микрофона (Mute LED):** Загорается при критическом остатке топлива (< 15%) или падении давления воздуха в ресиверах.

---

### Необходимые компоненты

1. Установленный **Python 3.10 или новее** (при установке отметьте галочку *"Add Python to PATH"*).
2. **`scs-telemetry.dll`**: Скачайте актуальный релиз из репозитория **[RenCloud/scs-sdk-plugin Releases](https://github.com/RenCloud/scs-sdk-plugin/releases)**.
3. **`hidapi.dll`**: Скачайте архив `hidapi-win.zip` из репозитория **[libusb/hidapi Releases](https://github.com/libusb/hidapi/releases)** и извлеките файл `hidapi.dll` из папки `x64`.

---

### Установка

1. Скачайте файлы данного репозитория в отдельную папку (например, `C:\ETS2_DualSense\`).
2. Поместите файл **`hidapi.dll`** (из папки `x64` скачанного архива) прямо в папку со скриптами (`C:\ETS2_DualSense\hidapi.dll`), рядом с файлом `dualsense_ets2.py`.
3. Перейдите в директорию установленной игры Euro Truck Simulator 2:
   `...\Steam\steamapps\common\Euro Truck Simulator 2\bin\win_x64\`
4. Создайте внутри `win_x64` папку **`plugins`** (если она отсутствует) и поместите в неё файл **`scs-telemetry.dll`**:
   `...\Euro Truck Simulator 2\bin\win_x64\plugins\scs-telemetry.dll`

---

### Настройка Steam и игры перед первым запуском

Для прямого управления регистрами адаптивных триггеров необходимо исключить перехват контроллера со стороны Steam:

1. **Отключите систему ввода Steam (Steam Input):**
   * Откройте Библиотеку Steam, нажмите правой кнопкой мыши по **Euro Truck Simulator 2** -> **Свойства** -> **Контроллер**.
   * В выпадающем списке выберите **«Отключить систему ввода Steam»** (Disable Steam Input).
   * Полностью закройте сторонние эмуляторы геймпадов (DS4Windows, DualSenseX и др.).
2. **Локальное сохранение профиля (`controls.sii`):**
   * Запустите ETS 2. В меню выбора профиля нажмите **«Изменить профиль»** и снимите галочку **«Использовать Steam Cloud»**, чтобы файл настроек управления `controls.sii` сохранялся локально в папке `Documents\Euro Truck Simulator 2\profiles\`.
3. **Назначение осей в игре:**
   * Перейдите в **Настройки** -> **Устройства**.
   * В верхнем списке выберите **`Клавиатура + Wireless Controller`**.
   * Назначьте **Ось рулевого управления** (левый стик), **Ось педали газа** (курок R2) и **Ось педали тормоза** (курок L2).
   * Проверьте желтые индикаторы нажатия под осями газа и тормоза: если при отпущенных курках полоска заполнена, переключите режим оси на **«Инвертированный»** или **«Инвертированный и центрированный»**.
   * Выйдите из игры для сохранения чистого файла `controls.sii`.

#### Таблица соответствия кнопок DirectInput в меню ETS 2
При отключенном Steam Input игра обращается к DualSense через протокол DirectInput (`Кнопка 0` – `Кнопка 13`):

| Обозначение в игре | Кнопка на DualSense | Обозначение в игре | Кнопка на DualSense |
| :--- | :--- | :--- | :--- |
| **Кнопка 0** | Квадрат (Square) | **Кнопка 7** | Курок R2 (Кнопка) |
| **Кнопка 1** | Крест (Cross) | **Кнопка 8** | Кнопка Create (Share) |
| **Кнопка 2** | Круг (Circle) | **Кнопка 9** | Кнопка Options |
| **Кнопка 3** | Треугольник (Triangle) | **Кнопка 10** | Нажатие левого стика (L3) |
| **Кнопка 4** | Бампер L1 | **Кнопка 11** | Нажатие правого стика (R3) |
| **Кнопка 5** | Бампер R1 | **Кнопка 12** | Кнопка PlayStation (PS) |
| **Кнопка 6** | Курок L2 (Кнопка) | **Кнопка 13** | Нажатие Тачпада |

---

### Запуск и использование

1. Подключите контроллер DualSense к ПК (по USB или Bluetooth).
2. Запустите файл **`start_ets2_dualsense.bat`** (рекомендуется запускать при закрытой игре, чтобы скрипт пропатчил `controls.sii` и сам запустил ETS 2).
3. Скрипт автоматически:
   * Проверит и установит библиотеки Python (`pydualsense`, `truck-telemetry`, `psutil`).
   * Обновит параметры `controls.sii`.
   * Найдет путь к `eurotrucks2.exe` (при нестандартном расположении запросит путь один раз и сохранит его в файл `ets2_path.cfg`) и запустит игру.
   * Подключится к каналу памяти `Local\SCSTelemetry`.
4. При входе в игру подтвердите системное уведомление **«Запрос на использование расширенных функций SDK»**, нажав **ОК**.
5. Для закрытия приложения после завершения игры нажмите `Ctrl + C` в окне консоли или закройте окно — триггеры и моторы автоматически сбросятся в исходное состояние.

---

### Support the Project / Поддержать проект

If you find this project useful, you can support the author on Boosty:
Если проект оказался вам полезен и вы хотите поддержать автора:

* **[Support on Boosty / Поддержать на Boosty](https://boosty.to/maghoul/donate/)**

---

### License
This project is licensed for personal, non-commercial use. You are free to use, modify, and share the code with proper attribution to the original authors and dependencies.