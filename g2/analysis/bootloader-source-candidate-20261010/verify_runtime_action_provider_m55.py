#!/usr/bin/env python3
"""Re-run the authenticated 260-case runtime family suite at M55/O2 settings."""
import hashlib
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OLD = ROOT / "g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-initialize/runtime-action-416200"
PROVIDER = ROOT / "g2/components/bootloader/thread_creation/thread_termination.c"
BASE = ROOT / "g2/build/bootloader-completion/startup-pcm22-handler17-integrated/687b0a4e3ce6aef856d19738977a8285033a36110c629d73b0b3cc7306da187d/candidate17-integrated.elf"
PYTHON = Path("/Users/kalani/.local/share/opencfw/venv/bin/python")


def main():
    assert PROVIDER.read_bytes() == (OLD / "runtime_action.c").read_bytes()
    with tempfile.TemporaryDirectory(prefix="bootloader-selected-runtime-") as tmp:
        p = Path(tmp)
        obj, addon = p / "runtime.o", p / "addon.elf"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                        "-mfpu=fpv5-sp-d16", "-mfloat-abi=softfp", "-fshort-enums",
                        "-ffreestanding", "-fno-builtin", "-ffunction-sections",
                        "-fdata-sections", "-std=c11", "-O2", "-fwrapv", "-DNDEBUG",
                        "-c", str(PROVIDER), "-o", str(obj)], check=True)
        subprocess.run(["arm-none-eabi-ld", "--gc-sections", "-T", str(OLD / "module.ld"),
                        "--just-symbols=" + str(BASE), "-o", str(addon), str(obj)], check=True)
        script = (OLD / "verify.py").read_text()
        expression = "ROOT=Path(__file__).resolve().parents[6];HERE=Path(__file__).parent"
        assert expression in script
        script = script.replace(expression, f"ROOT=Path({str(ROOT)!r});HERE=Path({str(p)!r})")
        copied = p / "verify.py"
        copied.write_text(script)
        result = subprocess.run([str(PYTHON), str(copied), "--addon", str(addon)],
                                check=True, capture_output=True, text=True)
        print(result.stdout.strip())
        comparison = p / "comparison.json"
        assert comparison.is_file()
        print("selected_provider_sha256", hashlib.sha256(PROVIDER.read_bytes()).hexdigest())
        print("m55_addon_sha256", hashlib.sha256(addon.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
