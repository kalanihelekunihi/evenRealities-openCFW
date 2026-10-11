#!/usr/bin/env python3
"""Platform instance-configure alias versus locked stock and selected source."""
import hashlib
import importlib.util
import itertools
import json
import struct
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "g2/components/bootloader/initializer_callbacks"
spec = importlib.util.spec_from_file_location("claim_verify", BASE / "verify_context_claim.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
ALIAS = ROOT / "g2/components/bootloader/source_candidate_20261010/context_configure_alias.c"
SOURCE = BASE / "context_instance.c"
CFG = 0x20004000
BUFFER = 0x20008000


class Machine(v.Machine):
    def code(self, uc, pc, size, user):
        if pc == 0x42c26a:
            args = [uc.reg_read(v.a.UC_ARM_REG_R0), uc.reg_read(v.a.UC_ARM_REG_R1)]
            self.events.append(["clock-config", *args])
            uc.reg_write(v.a.UC_ARM_REG_R0, 0x12345678)
            uc.reg_write(v.a.UC_ARM_REG_R1, 0)
            uc.reg_write(v.a.UC_ARM_REG_PC, uc.reg_read(v.a.UC_ARM_REG_LR))
            return
        super().code(uc, pc, size, user)


def main():
    assert hashlib.sha256(v.v.BLOB.read_bytes()).hexdigest() == v.v.LOCKED_SHA
    with tempfile.TemporaryDirectory(prefix="bootloader-context-configure-alias-") as tmp:
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
                        str(Path(__file__).with_name("context-configure-alias-module.ld")),
                        *(str(obj) for obj in objects), "-o", str(elf)],
                       check=True, capture_output=True)
        _, segs, syms = v.v.elf.elf_info(elf)
        for name, (address, _, _) in v.CALLS.items():
            syms.setdefault(name, address | 1)
        v.ENTRIES["configure"] = ("opencfw_boot_context_configure", 0x42cc34)
        stock, source = Machine(False, segs, syms), Machine(True, segs, syms)
        source.symbols["opencfw_boot_context_configure"] = syms["opencfw_bl_instance_configure"]
        cases = []
        for module, interface, hz, mode, buffer, words in itertools.product(
                [0, 4, 7], [0, 1, 2], [0, 100000, 400000, 1000000, 48000001],
                [0, 3, 4], [0, BUFFER], [0, 32]):
            handle = v.POOL + module * v.STRIDE
            observed = []
            for m in [stock, source]:
                m.reset()
                m.cpu.mem_write(handle, struct.pack("<II", 0x01123456, module))
                m.cpu.mem_write(CFG, struct.pack("<5I", interface, hz, mode, buffer, words))
                result = m.call("configure", [handle, CFG])
                observed.append(m.observation(result))
            assert observed[0] == observed[1], (module, interface, hz, mode, buffer, words)
            cases.append({"module": module, "interface": interface, "hz": hz,
                          "mode": mode, "buffer": buffer, "words": words,
                          "result": observed[0]["status"],
                          "events": observed[0]["events"]})
        trace = {hex(pc): raw for pc, raw in stock.trace.items()}
        used = {int(pc, 16) + i for pc, raw in trace.items()
                for i in range(len(bytes.fromhex(raw)))}
        report = {"status": "PASS", "cases": len(cases),
                  "original_sha256": v.v.LOCKED_SHA,
                  "source_elf_sha256": hashlib.sha256(elf.read_bytes()).hexdigest(),
                  "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                  "alias_sha256": hashlib.sha256(ALIAS.read_bytes()).hexdigest(),
                  "stock_entry": "0x42cc35", "distinct_original_trace_bytes": len(used),
                  "comparisons": cases,
                  "limits": ["Platform-finish passes transfer and instance-config pointers as two ARM32 words; actual table rows are outside this standalone matrix.",
                             "Clock-config child is a controlled cut. Full context pool and modeled MMIO agree, but physical clock/IOM behavior is not established."]}
        Path(__file__).with_name("context-configure-alias-comparison.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({key: report[key] for key in ["status", "cases", "distinct_original_trace_bytes"]}))


if __name__ == "__main__":
    main()
