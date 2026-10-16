import os
import re
import shutil
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


def cleanup_old_ui_mod(ets2_docs_dir: Path):
    old_mod = ets2_docs_dir / "mod" / "dualsense_controls_ui_161.scs"
    if old_mod.exists():
        try:
            old_mod.unlink()
            print(f"[✓] Removed deprecated UI mod: {old_mod.name}")
        except Exception:
            pass


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

    # Expand steering non-linearity range while preserving in-game slider compatibility
    content = re.sub(
        r"\(1\.0\s*\+\s*c_steer_func\s*\*\s*0\.5\)",
        r"(1.0 + c_steer_func * 1.6)",
        content,
    )

    # Clean up any previously injected mouse steering expression
    content = content.replace("(-mouse.rel_position.x?0 * 0.0018) - ", "")

    sii_path.write_text(content, encoding="utf-8")
    print(f"[✓] Profile patched: {sii_path.parent.name}")
    return True


def run_patcher():
    if is_ets2_running():
        print(
            "[!] ETS 2 is currently running. Close the game before patching controls.sii."
        )
        return

    docs = Path(r"C:\Users\demon\Documents\Euro Truck Simulator 2")
    if not docs.exists():
        docs = Path(os.path.expanduser("~")) / "Documents" / "Euro Truck Simulator 2"

    if not docs.exists():
        print("[!] Euro Truck Simulator 2 Documents folder not found.")
        return

    cleanup_old_ui_mod(docs)

    for folder_name in ["profiles", "steam_profiles"]:
        prof_dir = docs / folder_name
        if prof_dir.exists():
            for sii_file in prof_dir.rglob("controls.sii"):
                patch_controls_sii(sii_file)


if __name__ == "__main__":
    run_patcher()
