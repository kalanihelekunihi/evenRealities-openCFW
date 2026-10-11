#!/usr/bin/env python3
"""Power-guard callback alias against locked stock and selected source."""
import importlib.util
import itertools
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "g2/components/bootloader/platform_control"
spec = importlib.util.spec_from_file_location("power_verify", BASE / "verify_power_domains.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
ALIAS = ROOT / "g2/components/bootloader/source_candidate_20261010/power_callback_alias.c"
SOURCE = BASE / "power_domains.c"
VALUE = 0x20032000


class Machine(v.v.Machine):
    def code(self, uc, pc, size, user):
        if pc == 0x08002400:
            id_value, enabled, pointer, _ = self.args()
            self.events.append(["callback", id_value, enabled, self.u(pointer)])
            self.ret(7)
            return
        super().code(uc, pc, size, user)


def main():
    assert v.v.sha(v.v.BLOB) == v.v.SHA
    with tempfile.TemporaryDirectory(prefix="bootloader-power-callback-alias-") as tmp:
        p = Path(tmp)
        objects = [p / "alias.o", p / "source.o"]
        for source, obj in zip([ALIAS, SOURCE], objects):
            subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                            "-mthumb", "-mfloat-abi=soft", "-ffreestanding",
                            "-fno-builtin", "-std=c11", "-O2", "-fwrapv",
                            "-ffunction-sections", "-fdata-sections", "-c", str(source),
                            "-o", str(obj)], check=True)
        elf = p / "source.elf"
        subprocess.run(["arm-none-eabi-ld", "--gc-sections", "-T",
                        str(Path(__file__).with_name("power-callback-alias-module.ld")),
                        *(str(obj) for obj in objects), "-o", str(elf)],
                       check=True, capture_output=True)
        _, segs, syms = v.v.elf.elf_info(elf)
        v.v.ENTRIES["power_control"] = 0x41cd1a
        cases, trace = [], {}
        for callback, id_value, enabled, value in itertools.product(
                [False, True], [0, 1, 5, 255, 256, 0x1234],
                [0, 1, 255, 256, 0x1234], [0, 0x80, 0x12345678]):
            pair = [Machine(), Machine(True, segs, dict(syms))]
            pair[1].symbols["opencfw_boot_power_control"] = syms["opencfw_boot_power_control"]
            observed = []
            for m in pair:
                m.w(0x20026e3c, 0x08002401 if callback else 0)
                m.w(VALUE, value)
                result = m.run("power_control", [id_value, enabled, VALUE])
                observed.append({"return": result["return"], "events": result["events"],
                                 "value": m.u(VALUE)})
            assert observed[0] == observed[1], (callback, id_value, enabled, value, observed)
            trace.update(pair[0].trace)
            cases.append({"callback": callback, "id": id_value, "enabled": enabled,
                          "value": value, "observed": observed[0]})
        used = {int(pc, 0) + i for pc, raw in trace.items()
                for i in range(len(bytes.fromhex(raw)))}
        report = {"status": "PASS", "cases": len(cases),
                  "original_sha256": v.v.SHA, "source_elf_sha256": v.v.sha(elf),
                  "source_sha256": v.v.sha(SOURCE), "alias_sha256": v.v.sha(ALIAS),
                  "stock_entry": "0x41cd1b", "distinct_original_trace_bytes": len(used),
                  "comparisons": cases,
                  "limits": ["The guard callers use ID 5 and enabled 0/1 with a word pointer; broader byte-truncation behavior is compared.",
                             "Registered callback body is a controlled cut. No physical power-domain transition or hardware callback semantics are established.",
                             "Compatible M4 source executes in Unicorn; M55 archive compilation and direct relocation are checked separately."]}
        Path(__file__).with_name("power-callback-alias-comparison.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({key: report[key] for key in ["status", "cases", "distinct_original_trace_bytes"]}))


if __name__ == "__main__":
    main()
