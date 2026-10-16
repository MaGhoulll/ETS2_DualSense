import time
import math
import sys
import truck_telemetry
from pydualsense import pydualsense, TriggerModes, PlayerID

SHOW_LIVE_DEBUG = True


def clamp(val, min_val, max_val):
    return max(min_val, min(val, max_val))


def _recursive_lookup(obj, target_key: str):
    if isinstance(obj, dict):
        if target_key in obj and obj[target_key] is not None:
            return obj[target_key]
        for v in obj.values():
            if isinstance(v, (dict, list, tuple)):
                res = _recursive_lookup(v, target_key)
                if res is not None:
                    return res
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            if isinstance(item, (dict, list, tuple)):
                res = _recursive_lookup(item, target_key)
                if res is not None:
                    return res
    return None


def safe_float(
    data: dict, keys: list, sub_axis: str = None, default: float = 0.0
) -> float:
    for k in keys:
        val = _recursive_lookup(data, k)
        if val is not None:
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                return float(val)
            elif isinstance(val, dict):
                if (
                    sub_axis
                    and sub_axis in val
                    and isinstance(val[sub_axis], (int, float))
                ):
                    return float(val[sub_axis])
                for axis in ("y", "z", "x", "value"):
                    if axis in val and isinstance(val[axis], (int, float)):
                        return float(val[axis])
            elif isinstance(val, (list, tuple)) and len(val) > 0:
                if isinstance(val[0], (int, float)):
                    return float(val[0])
    return default


def safe_bool(data: dict, keys: list, default: bool = False) -> bool:
    for k in keys:
        val = _recursive_lookup(data, k)
        if val is not None:
            if isinstance(val, (bool, int)):
                return bool(val)
    return default


def safe_list(data: dict, keys: list) -> list:
    for k in keys:
        val = _recursive_lookup(data, k)
        if isinstance(val, (list, tuple)) and len(val) >= 2:
            return list(val)
    return []


def main():
    print("===================================================================")
    print("  ETS 2 (v1.61) DualSense Core v4.3 (Spatial Stereo & Triggers)    ")
    print("===================================================================")

    ds = pydualsense()
    try:
        ds.init()
        print("[+] DualSense controller initialized.")
    except Exception as e:
        print(f"[!] DualSense connection error: {e}")
        sys.exit(1)

    print("[*] Waiting for Euro Truck Simulator 2 telemetry...")
    while True:
        try:
            truck_telemetry.init()
            print("[+] Telemetry connected! Haptics and Adaptive Triggers active.")
            break
        except Exception:
            time.sleep(2.0)

    prev_gear = 0
    shift_jolt_timer = 0
    shift_intensity = 0
    post_shift_cooldown = 0

    engine_was_on = False
    crank_timer = 0

    collision_timer = 0
    collision_side = 0.0
    prev_wear_chassis = None
    prev_wear_cabin = None
    prev_wear_wheels = None

    lugging_envelope = 0.0
    launch_wave_phase = 0.0
    prev_susp_deflection = None

    last_mic_led = None
    last_player_led = None
    last_rgb = (0, 0, 0)
    debug_counter = 0

    try:
        while True:
            try:
                data = truck_telemetry.get_data()
            except Exception:
                time.sleep(0.5)
                continue

            if not data:
                time.sleep(0.05)
                continue

            paused = safe_bool(data, ["paused"], False)
            if paused:
                ds.setLeftMotor(0)
                ds.setRightMotor(0)
                ds.triggerL.setMode(TriggerModes.Off)
                ds.triggerR.setMode(TriggerModes.Off)
                time.sleep(0.05)
                continue

            # 1. Telemetry reading
            speed_ms = abs(safe_float(data, ["speed"], default=0.0))
            speed_kmh = speed_ms * 3.6
            rpm = safe_float(data, ["engineRpm", "rpm"], default=0.0)
            max_rpm = safe_float(data, ["engineRpmMax", "maxRpm"], default=2400.0)
            if max_rpm <= 100.0:
                max_rpm = 2400.0
            rpm_ratio = clamp(rpm / max_rpm, 0.0, 1.0)

            gear = int(
                safe_float(
                    data, ["gear", "displayedGear", "gearDashboard"], default=0.0
                )
            )
            engine_on = safe_bool(
                data, ["engineEnabled", "electricEnabled"], False
            ) or (rpm > 150.0)

            throttle = safe_float(
                data, ["gameThrottle", "userThrottle", "throttle"], default=0.0
            )
            brake = safe_float(data, ["gameBrake", "userBrake", "brake"], default=0.0)
            park_brake = safe_bool(data, ["parkBrake"], False)
            retarder = int(
                safe_float(
                    data, ["retarderBrake", "retarder", "retarderStep"], default=0.0
                )
            )
            air_warn = safe_bool(
                data, ["airPressureWarning", "airPressureEmergency"], False
            )

            blinker_l = safe_bool(data, ["blinkerLeftOn", "blinkerLeftActive"], False)
            blinker_r = safe_bool(data, ["blinkerRightOn", "blinkerRightActive"], False)
            high_beam = safe_bool(data, ["lightHighBeam", "lightsBeamHigh"], False)

            fuel = safe_float(data, ["fuel", "amount"], default=100.0)
            fuel_cap = safe_float(data, ["fuelCapacity", "capacity"], default=600.0)
            if fuel_cap <= 1.0:
                fuel_cap = 600.0
            fuel_ratio = clamp(fuel / fuel_cap, 0.0, 1.0)

            accel_lat_signed = safe_float(
                data,
                ["linearAcceleration", "acceleration", "linAccel"],
                sub_axis="x",
                default=0.0,
            )
            accel_lat = abs(accel_lat_signed)
            accel_vert = abs(
                safe_float(
                    data,
                    ["linearAcceleration", "acceleration", "linAccel"],
                    sub_axis="y",
                    default=0.0,
                )
            )
            accel_long = safe_float(
                data,
                ["linearAcceleration", "acceleration", "linAccel"],
                sub_axis="z",
                default=0.0,
            )
            roll_accel = safe_float(
                data,
                ["angularAcceleration", "angAccel", "cabinAngularAcceleration"],
                sub_axis="z",
                default=0.0,
            )

            # 2. Spatial stereo wheel & road surface analysis
            left_road_rumble = 0.0
            right_road_rumble = 0.0

            wheel_substances = safe_list(data, ["wheelSubstance", "substance"])
            if len(wheel_substances) >= 2 and speed_kmh > 8.0:
                sub_fl = (
                    int(wheel_substances[0])
                    if isinstance(wheel_substances[0], (int, float))
                    else 0
                )
                sub_fr = (
                    int(wheel_substances[1])
                    if isinstance(wheel_substances[1], (int, float))
                    else 0
                )
                spd_mult = clamp(speed_kmh / 70.0, 0.25, 1.2)
                strip_pulse = 1.0 if (int(time.perf_counter() * 28) % 2 == 0) else 0.35
                if sub_fl > 1:
                    left_road_rumble += 85.0 * spd_mult * strip_pulse
                if sub_fr > 1:
                    right_road_rumble += 85.0 * spd_mult * strip_pulse

            susp_defl = safe_list(data, ["wheelSuspDeflection", "suspDeflection"])
            if len(susp_defl) >= 2:
                if prev_susp_deflection is not None and len(prev_susp_deflection) >= 2:
                    delta_left = abs(
                        float(susp_defl[0]) - float(prev_susp_deflection[0])
                    )
                    delta_right = abs(
                        float(susp_defl[1]) - float(prev_susp_deflection[1])
                    )
                    if delta_left > 0.0045:
                        left_road_rumble += clamp(
                            (delta_left - 0.004) * 9500.0, 0.0, 175.0
                        )
                    if delta_right > 0.0045:
                        right_road_rumble += clamp(
                            (delta_right - 0.004) * 9500.0, 0.0, 175.0
                        )
                prev_susp_deflection = susp_defl

            if accel_vert > 1.35 or accel_lat > 1.4:
                base_bump = clamp(
                    (
                        (max(0.0, accel_vert - 1.3) * 24.0)
                        + (max(0.0, accel_lat - 1.3) * 22.0)
                    ),
                    0.0,
                    165.0,
                )
                stereo_pan = clamp(
                    (accel_lat_signed * 0.35) + (roll_accel * 0.25), -1.0, 1.0
                )
                left_weight = clamp(1.0 - max(0.0, stereo_pan), 0.25, 1.0)
                right_weight = clamp(1.0 + min(0.0, stereo_pan), 0.25, 1.0)
                left_road_rumble = max(left_road_rumble, base_bump * left_weight)
                right_road_rumble = max(right_road_rumble, base_bump * right_weight)

            # 3. Directional collision detection
            wear_chassis = safe_float(data, ["wearChassis"], default=0.0)
            wear_cabin = safe_float(data, ["wearCabin"], default=0.0)
            wear_wheels = safe_float(data, ["wearWheels"], default=0.0)

            damage_delta = 0.0
            if prev_wear_chassis is not None:
                damage_delta = max(
                    wear_chassis - prev_wear_chassis,
                    wear_cabin - prev_wear_cabin,
                    wear_wheels - prev_wear_wheels,
                )
            prev_wear_chassis = wear_chassis
            prev_wear_cabin = wear_cabin
            prev_wear_wheels = wear_wheels

            if damage_delta > 0.0002 or abs(accel_long) > 9.5 or accel_lat > 7.5:
                impact_power = clamp(
                    max(damage_delta * 8000.0, (abs(accel_long) + accel_lat) / 14.0),
                    0.4,
                    1.0,
                )
                collision_timer = max(collision_timer, int(6 + impact_power * 10))
                collision_side = clamp(accel_lat_signed / 5.0, -1.0, 1.0)

            # 4. Smooth engine lugging envelope
            if gear != prev_gear:
                if gear != 0:
                    shift_jolt_timer = 3
                    shift_intensity = 155 if throttle > 0.45 else 95
                    post_shift_cooldown = 150
                else:
                    shift_jolt_timer = 2
                    shift_intensity = 55
                prev_gear = gear

            if post_shift_cooldown > 0:
                post_shift_cooldown -= 1

            raw_lugging_cond = (
                engine_on
                and post_shift_cooldown == 0
                and gear >= 3
                and throttle > 0.68
                and speed_kmh > 10.0
                and rpm < 1120.0
                and accel_long < 0.25
            )

            if raw_lugging_cond:
                strain_depth = clamp((1120.0 - rpm) / 320.0, 0.25, 1.0)
                lugging_envelope = min(strain_depth, lugging_envelope + 0.012)
            else:
                lugging_envelope = max(0.0, lugging_envelope - 0.025)

            if SHOW_LIVE_DEBUG:
                debug_counter += 1
                if debug_counter >= 40:
                    debug_counter = 0
                    sys.stdout.write(
                        f"\r[v4.3] Spd:{speed_kmh:5.1f} km/h | RPM:{rpm:4.0f} | Gear:{gear:2d} | "
                        f"Strain:{lugging_envelope*100:3.0f}% | Road L/R:{left_road_rumble:3.0f}/{right_road_rumble:3.0f}   "
                    )
                    sys.stdout.flush()

            # 5. Adaptive Trigger R2 (Throttle)
            if not engine_on:
                ds.triggerR.setMode(TriggerModes.Off)
            elif rpm_ratio > 0.89:
                ds.triggerR.setMode(TriggerModes.Pulse_A)
                ds.triggerR.setForce(0, 36)
                ds.triggerR.setForce(1, 120)
                ds.triggerR.setForce(2, 115)
            elif lugging_envelope > 0.15:
                if lugging_envelope < 0.35:
                    ds.triggerR.setMode(TriggerModes.Rigid)
                    ds.triggerR.setForce(0, 30)
                    ds.triggerR.setForce(1, int(25 + lugging_envelope * 95))
                else:
                    ds.triggerR.setMode(TriggerModes.Pulse_A)
                    freq = int(clamp(12 + (rpm / 120.0), 12, 20))
                    amp = int(clamp(30 + (lugging_envelope * 65), 30, 95))
                    ds.triggerR.setForce(0, freq)
                    ds.triggerR.setForce(1, amp)
                    ds.triggerR.setForce(2, 65)
            else:
                ds.triggerR.setMode(TriggerModes.Rigid)
                light_res = int(clamp(12 + (rpm_ratio * 20), 12, 32))
                ds.triggerR.setForce(0, 35)
                ds.triggerR.setForce(1, light_res)

            # 6. Adaptive Trigger L2 (Brake)
            if air_warn:
                ds.triggerL.setMode(TriggerModes.Rigid)
                ds.triggerL.setForce(0, 140)
                ds.triggerL.setForce(1, 225)
            elif brake > 0.58 and speed_kmh > 18.0:
                ds.triggerL.setMode(TriggerModes.Pulse_A)
                freq = int(clamp(14 + (speed_kmh * 0.22), 14, 30))
                amp = int(clamp(115 + (brake * 95), 115, 210))
                ds.triggerL.setForce(0, freq)
                ds.triggerL.setForce(1, amp)
                ds.triggerL.setForce(2, 45)
            else:
                ds.triggerL.setMode(TriggerModes.Rigid)
                spd_factor = clamp(speed_kmh / 110.0, 0.0, 1.0)
                light_brake = int(clamp(16 + (spd_factor * 28), 16, 44))
                ds.triggerL.setForce(0, 30)
                ds.triggerL.setForce(1, light_brake)

            # 7. Spatial Stereo Haptic Motors
            left_m = 0.0
            right_m = 0.0

            if engine_on and not engine_was_on:
                crank_timer = 10
            engine_was_on = engine_on

            if collision_timer > 0:
                left_weight = clamp(1.0 - max(0.0, collision_side * 0.7), 0.3, 1.0)
                right_weight = clamp(1.0 + min(0.0, collision_side * 0.7), 0.3, 1.0)
                left_m = 250.0 * left_weight
                right_m = 250.0 * right_weight
                collision_timer -= 1
            elif crank_timer > 0:
                left_m = 160.0 if crank_timer % 2 == 0 else 40.0
                right_m = 105.0
                crank_timer -= 1
            else:
                if (
                    engine_on
                    and gear != 0
                    and throttle > 0.15
                    and 0.2 < speed_kmh < 22.0
                ):
                    wave_speed = 0.12 + (speed_kmh * 0.022)
                    launch_wave_phase += wave_speed
                    speed_env = math.sin(clamp(speed_kmh / 22.0, 0.0, 1.0) * math.pi)
                    wave_amp = 34.0 * speed_env * clamp(throttle + 0.3, 0.4, 1.0)
                    pan = (math.sin(launch_wave_phase) + 1.0) * 0.5
                    left_m += wave_amp * (1.0 - pan * 0.7)
                    right_m += wave_amp * (0.3 + pan * 0.7)
                elif engine_on and speed_kmh <= 0.2:
                    left_m += 4.0

                if lugging_envelope > 0.05:
                    lug_vib = lugging_envelope * 24.0
                    left_m += lug_vib
                    right_m += lug_vib * 0.45

                if shift_jolt_timer > 0:
                    left_m += shift_intensity * 0.8
                    right_m += shift_intensity
                    shift_jolt_timer -= 1

                left_m += left_road_rumble
                right_m += right_road_rumble

                if brake > 0.55 and speed_kmh > 15.0:
                    brake_vib = clamp((brake - 0.50) * speed_kmh * 1.25, 0.0, 115.0)
                    left_m += brake_vib
                    right_m += brake_vib * 0.85

            ds.setLeftMotor(int(clamp(left_m, 0, 255)))
            ds.setRightMotor(int(clamp(right_m, 0, 255)))

            # 8. LEDs & Lightbar
            if collision_timer > 0:
                target_rgb = (255, 0, 0)
            elif blinker_l or blinker_r:
                target_rgb = (
                    (255, 165, 0) if (blinker_l and blinker_r) else (0, 255, 30)
                )
            elif park_brake:
                target_rgb = (220, 0, 0)
            elif high_beam:
                target_rgb = (180, 220, 255)
            elif retarder > 0:
                target_rgb = (0, 140, 255)
            elif engine_on:
                target_rgb = (20, 50, 95)
            else:
                target_rgb = (0, 0, 0)

            if target_rgb != last_rgb:
                ds.light.setColorI(*target_rgb)
                last_rgb = target_rgb

            if fuel_ratio > 0.75:
                target_pled = PlayerID.PLAYER_4
            elif fuel_ratio > 0.50:
                target_pled = PlayerID.PLAYER_3
            elif fuel_ratio > 0.25:
                target_pled = PlayerID.PLAYER_2
            else:
                target_pled = PlayerID.PLAYER_1

            if target_pled != last_player_led:
                ds.light.setPlayerID(target_pled)
                last_player_led = target_pled

            target_mic = bool(fuel_ratio < 0.15 or air_warn)
            if target_mic != last_mic_led:
                ds.audio.setMicrophoneLED(target_mic)
                last_mic_led = target_mic

            time.sleep(0.010)

    except KeyboardInterrupt:
        print("\n[*] Stopping service...")
    finally:
        ds.setLeftMotor(0)
        ds.setRightMotor(0)
        ds.triggerL.setMode(TriggerModes.Off)
        ds.triggerR.setMode(TriggerModes.Off)
        ds.light.setColorI(0, 0, 255)
        ds.close()
        print("[✓] DualSense disconnected.")


if __name__ == "__main__":
    main()
