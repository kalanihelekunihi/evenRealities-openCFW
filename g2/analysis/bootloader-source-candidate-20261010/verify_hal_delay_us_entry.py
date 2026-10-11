#!/usr/bin/env python3
"""Check HAL delay entry against selected authored assembly."""
import hashlib
import importlib.util
import json
import random
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OLD = ROOT / "g2/components/bootloader/platform_startup/verify_delay_math.py"
spec = importlib.util.spec_from_file_location("delay_verify", OLD)
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
ALIAS = ROOT / "g2/components/bootloader/source_candidate_20261010/hal_delay_us_entry.c"
ASM = ROOT / "g2/components/bootloader/platform_startup/delay_math.S"
BODY_SHA = "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"
OUT = Path(__file__).with_name("hal-delay-us-entry-comparison.json")


def main():
    assert v.sha(v.BLOB) == BODY_SHA
    with tempfile.TemporaryDirectory(prefix="bootloader-hal-delay-entry-") as tmp:
        path = Path(tmp)
        objs = [path / "alias.o", path / "delay.o"]
        for src, obj in zip([ALIAS, ASM], objs):
            subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                            "-mthumb", "-mfpu=fpv5-sp-d16", "-mfloat-abi=softfp",
                            "-ffreestanding", "-fno-builtin", "-O2", "-c", str(src),
                            "-o", str(obj)], check=True)
        elf = path / "source.elf"
        subprocess.run(["arm-none-eabi-ld", "-T", str(ASM.with_suffix(".ld")),
                        "-e", "opencfw_hal_delay_us", *(str(o) for o in objs),
                        "-o", str(elf)], check=True)
        _, segments, syms = v.elf.elf_info(elf)
        assert syms["opencfw_hal_delay_us"] != syms["opencfw_boot_delay_us_math"]
        syms["opencfw_boot_delay_us_math"] = syms["opencfw_hal_delay_us"]
        rng = random.Random(0x41d1c0)
        values = [0,1,2,10,15,24,31,32,1000,0xffffff,0x1000001,
                  0x7ffffff,0x8000000,0x80000000,0xffffffff]
        values += [rng.getrandbits(32) for _ in range(24)]
        cases = []
        trace = {}
        for arg in values:
            for mode in [0,8,16,24,0xffffffff]:
                for fpscr in [0x02040000,0x02440000,0x02840000,0x02c40000]:
                    original = v.Machine(False, segments, syms)
                    source = v.Machine(True, segments, syms)
                    a = original.call(arg, mode, fpscr)
                    b = source.call(arg, mode, fpscr)
                    assert a == b, (arg, mode, fpscr, a, b)
                    trace.update(original.trace)
                    cases.append([arg, mode, fpscr, a])
        visited = {int(pc,16)+i for pc, raw in trace.items()
                   for i in range(len(bytes.fromhex(raw)))}
        report = {"status":"PASS", "cases":len(cases),
                  "original_image_sha256":BODY_SHA,
                  "original_body_sha256":hashlib.sha256(v.BLOB.read_bytes()[0x41d1c0-0x410000:0x41d210-0x410000]).hexdigest(),
                  "source_elf_sha256":v.sha(elf),
                  "alias_sha256":v.sha(ALIAS), "assembly_sha256":v.sha(ASM),
                  "distinct_original_trace_bytes":len(visited),
                  "comparisons":cases,
                  "limits":["Resident ROM Thumb 0x41 is an intercepted callback; timing and ROM internals are not validated.",
                            "Original and source run under Unicorn Cortex-M33 with FPU; physical M55 behavior remains unmeasured."]}
        OUT.write_text(json.dumps(report, indent=2)+"\n")
        print(json.dumps({k:report[k] for k in ["status","cases","distinct_original_trace_bytes"]}))


if __name__ == "__main__":
    main()
