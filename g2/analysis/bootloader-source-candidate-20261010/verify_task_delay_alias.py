#!/usr/bin/env python3
"""Run the locked delay body suite through the M55 C alias and provider."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OLD = ROOT / "g2/analysis/bootloader-completion-2026-10-06/inventory-worker/task-delay-native"
PROVIDER = ROOT / "g2/components/bootloader/thread_creation/task_delay_native/task_delay.c"
ALIAS = ROOT / "g2/components/bootloader/source_candidate_20261010/task_delay_alias.c"
PYTHON = Path("/Users/kalani/.local/share/opencfw/venv/bin/python")
IMAGE = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
BODY_SHA = "8a3050543e3c959ae1b5ef53792a3aa9a192000c0c82567df806bc1cdc7e51be"


def main():
    assert PROVIDER.read_bytes() == (OLD / "task_delay.c").read_bytes()
    image = IMAGE.read_bytes()
    assert hashlib.sha256(image).hexdigest() == "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"
    body_hash = hashlib.sha256(image[0x6378:0x639a]).hexdigest()
    assert body_hash == BODY_SHA, body_hash
    with tempfile.TemporaryDirectory(prefix="bootloader-delay-alias-") as temporary:
        p = Path(temporary)
        objects = [p / "provider.o", p / "alias.o"]
        for src, obj in zip([PROVIDER, ALIAS], objects):
            subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                            "-mfpu=fpv5-sp-d16", "-mfloat-abi=softfp", "-fshort-enums",
                            "-ffreestanding", "-fno-builtin", "-ffunction-sections",
                            "-fdata-sections", "-std=c11", "-O2", "-fwrapv", "-DNDEBUG",
                            "-c", str(src), "-o", str(obj)], check=True)
        elf = p / "delay.elf"
        subprocess.run(["arm-none-eabi-ld", "-T", str(OLD / "module.ld"),
                        "-u", "opencfw_bl_task_delay", "-o", str(elf),
                        *(str(obj) for obj in objects)], check=True)
        script = (OLD / "verify.py").read_text()
        old_root = "N=Path(__file__).resolve().parent;R=next(p for p in N.parents if (p/'AGENTS.md').exists());"
        assert old_root in script
        script = script.replace(old_root, f"N=Path({str(p)!r});R=Path({str(ROOT)!r});")
        old_entry = "sy['opencfw_cmsis_delay' if f['entry']=='cmsis' else 'opencfw_kernel_delay']"
        assert old_entry in script
        script = script.replace(old_entry, "sy['opencfw_bl_task_delay' if f['entry']=='cmsis' else 'opencfw_kernel_delay']")
        old_reg = "u.reg_write(a.UC_ARM_REG_R0,f['ticks']);u.reg_write(a.UC_ARM_REG_SP,SP);"
        assert old_reg in script
        script = script.replace(old_reg, "u.reg_write(a.UC_ARM_REG_R0,f['ticks']);u.reg_write(a.UC_ARM_REG_R3,0xabcdef00 ^ f['ticks']);u.reg_write(a.UC_ARM_REG_SP,SP);")
        old_return = "'return':u.reg_read(a.UC_ARM_REG_R0) if f['entry']=='cmsis' else None,'terminal':terminal"
        assert old_return in script
        script = script.replace(old_return, "'return':u.reg_read(a.UC_ARM_REG_R0) if f['entry']=='cmsis' else None,'r1':u.reg_read(a.UC_ARM_REG_R1) if f['entry']=='cmsis' else None,'terminal':terminal")
        old_source = "hashlib.sha256((N/'task_delay.c').read_bytes()).hexdigest()"
        assert old_source in script
        script = script.replace(old_source, f"hashlib.sha256(Path({str(PROVIDER)!r}).read_bytes()).hexdigest()")
        copied = p / "verify.py"
        copied.write_text(script)
        result = subprocess.run([str(PYTHON), str(copied), "--elf", str(elf)],
                                check=True, capture_output=True, text=True)
        comparison = json.loads((p / "comparison.json").read_text())
        assert comparison["status"] == "PASS_TASK_DELAY_BODIES_WITH_SCHEDULER_CONTRACTS"
        assert comparison["cases"] == 270
        summary = {"status": "PASS", "cases": comparison["cases"],
                   "original_body_sha256": body_hash,
                   "selected_provider_sha256": hashlib.sha256(PROVIDER.read_bytes()).hexdigest(),
                   "alias_source_sha256": hashlib.sha256(ALIAS.read_bytes()).hexdigest(),
                   "source_elf_sha256": hashlib.sha256(elf.read_bytes()).hexdigest(),
                   "coverage": comparison["bodies"], "comparisons": comparison["comparisons"],
                   "limits": "Public CMSIS R1 register checked in addition to legacy suite fields; scheduler children are controlled contracts and hardware timing is unverified."}
        Path(__file__).with_name("task-delay-alias-comparison.json").write_text(json.dumps(summary, indent=2)+"\n")
        print(result.stdout.strip())
        print("original_body_sha256", body_hash)
        print("source_elf_sha256", hashlib.sha256(elf.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
