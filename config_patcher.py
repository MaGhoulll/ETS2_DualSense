import os
import re
import shutil
import zipfile
from pathlib import Path

try:
    import psutil
except ImportError:
    psutil = None


def is_ets2_running() -> bool:
    if not psutil:
        return False
    for proc in psutil.process_iter(["name"]):
        try:
            if proc.info["name"] and "eurotrucks2" in proc.info["name"].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False


def create_dualsense_ui_mod(ets2_docs_dir: Path):
    mod_dir = ets2_docs_dir / "mod"
    mod_dir.mkdir(parents=True, exist_ok=True)
    mod_zip_path = mod_dir / "dualsense_controls_ui_161.scs"

    manifest_sii = """SiiNunit
{
mod_package : .package_name {
    package_version: "2.5"
    display_name: "DualSense Controller Native UI Labels (1.61)"
    author: "DualSense_Mod_Suite"
    category[]: "ui"
    category[]: "other"
    description_file: "description.txt"
}
}
"""
    description_txt = (
        "Таблица кнопок Sony DualSense для DirectInput (ETS 2 v1.61):\n"
        "Кнопка 0 = [X] Квадрат (Square)\n"
        "Кнопка 1 = [X] Крест (Cross)\n"
        "Кнопка 2 = [O] Круг (Circle)\n"
        "Кнопка 3 = [^] Треугольник (Triangle)\n"
        "Кнопка 4 = Бампер L1\n"
        "Кнопка 5 = Бампер R1\n"
        "Кнопка 6 = Курок L2\n"
        "Кнопка 7 = Курок R2\n"
        "Кнопка 8 = Кнопка Create (Share)\n"
        "Кнопка 9 = Кнопка Options\n"
        "Кнопка 10 = Нажатие левого стика (L3)\n"
        "Кнопка 11 = Нажатие правого стика (R3)\n"
        "Кнопка 12 = Кнопка PS\n"
        "Кнопка 13 = Нажатие Тачпада\n"
        "Кнопка 14 = Кнопка Микрофона (Mute)"
    )

    # Перекрываем все возможные варианты ключей локализации DirectInput в Prism3D 1.50-1.61
    buttons_map = [
        (0, "Квадрат [Square]"),
        (1, "Крест [Cross]"),
        (2, "Круг [Circle]"),
        (3, "Треугольник [Triangle]"),
        (4, "Бампер L1"),
        (5, "Бампер R1"),
        (6, "Курок L2"),
        (7, "Курок R2"),
        (8, "Share [Create]"),
        (9, "Options"),
        (10, "Стик L3"),
        (11, "Стик R3"),
        (12, "Кнопка PS"),
        (13, "Тачпад"),
        (14, "Микрофон [Mute]"),
    ]

    lines = ["SiiNunit", "{", "localization_db : .localization", "{"]
    for idx, label in buttons_map:
        b1 = idx + 1
        for key_pattern in [
            f"inp_joy_b{b1}",
            f"inp_joy_b{idx}",
            f"key_joy_b{b1}",
            f"key_joy_b{idx}",
            f"joy_b{b1}",
            f"joy_b{idx}",
            f"button_{idx}",
            f"button_{b1}",
        ]:
            lines.append(f'    key[]: "{key_pattern}"')
            lines.append(f'    val[]: "DS: {label}"')
    lines.append("}")
    lines.append("}")
    locale_sii = "\n".join(lines)

    with zipfile.ZipFile(mod_zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.sii", manifest_sii)
        zf.writestr("description.txt", description_txt)
        for lang in ["ru_ru", "en_gb", "en_us"]:
            zf.writestr(f"locale/{lang}/local.override.sii", locale_sii)
            zf.writestr(f"locale/{lang}/local_module.dualsense.sii", locale_sii)

    print(f"[✓] Обновлен UI-мод и шпаргалка кнопок: {mod_zip_path.name}")


def patch_controls_sii(sii_path: Path):
    backup_path = sii_path.with_suffix(".sii.clean_backup")
    if not backup_path.exists():
        shutil.copy2(sii_path, backup_path)

    content = sii_path.read_text(encoding="utf-8", errors="ignore")
    if not content.startswith("SiiNunit"):
        return False

    constants_patch = {
        "c_steer_dz": "0.020000",
        "c_throt_dz": "0.020000",
        "c_brake_dz": "0.020000",
        "c_steer_func": "0.750000",
        "c_rsteersens": "0.550000",
        "c_jcombined": "0.000000",
    }

    for const_name, val in constants_patch.items():
        pattern = rf'(config_lines\[\d+\]:\s*"constant\s+{const_name}\s+)[0-9.-]+(")'
        content = re.sub(pattern, rf"\g<1>{val}\g<2>", content)

    content = re.sub(
        r"\(1\.0\s*\+\s*c_steer_func\s*\*\s*0\.5\)",
        r"(1.0 + c_steer_func * 1.6)",
        content,
    )

    content = re.sub(
        r'(config_lines\[\d+\]:\s*"mix\s+steering\s+`dsteering\s*-\s*)',
        r"\g<1>(-mouse.rel_position.x?0 * 0.0018) - ",
        content,
    )
    content = content.replace(
        "(-mouse.rel_position.x?0 * 0.0018) - (-mouse.rel_position.x?0 * 0.0018) - ",
        "(-mouse.rel_position.x?0 * 0.0018) - ",
    )

    sii_path.write_text(content, encoding="utf-8")
    print(f"[✓] Профиль {sii_path.parent.name} оптимизирован.")
    return True


def run_patcher():
    if is_ets2_running():
        print("[!] Игра сейчас запущена. Пропуск патча controls.sii.")
        return

    docs = Path(r"C:\Users\demon\Documents\Euro Truck Simulator 2")
    if not docs.exists():
        docs = Path(os.path.expanduser("~")) / "Documents" / "Euro Truck Simulator 2"

    create_dualsense_ui_mod(docs)

    for folder_name in ["profiles", "steam_profiles"]:
        prof_dir = docs / folder_name
        if prof_dir.exists():
            for sii_file in prof_dir.rglob("controls.sii"):
                patch_controls_sii(sii_file)


if __name__ == "__main__":
    run_patcher()
