#!/usr/bin/env python3
"""Platform context-enable alias versus locked stock and selected source."""
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
ALIAS = ROOT / "g2/components/bootloader/source_candidate_20261010/context_enable_alias.c"
SOURCE = BASE / "context_instance.c"
BUFFER = 0x20008000


class Machine(v.Machine):
    cq_status = 0

    def code(self, uc, pc, size, user):
        if pc == 0x42c3e2:
            args = [uc.reg_read(v.a.UC_ARM_REG_R0), uc.reg_read(v.a.UC_ARM_REG_R1),
                    uc.reg_read(v.a.UC_ARM_REG_R2)]
            self.events.append(["cq-initialize", *args, self.cq_status])
            uc.reg_write(v.a.UC_ARM_REG_R0, self.cq_status)
            uc.reg_write(v.a.UC_ARM_REG_PC, uc.reg_read(v.a.UC_ARM_REG_LR))
            return
        super().code(uc, pc, size, user)


def main():
    assert hashlib.sha256(v.v.BLOB.read_bytes()).hexdigest() == v.v.LOCKED_SHA
    with tempfile.TemporaryDirectory(prefix="bootloader-context-enable-alias-") as tmp:
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
                        str(Path(__file__).with_name("context-enable-alias-module.ld")),
                        *(str(obj) for obj in objects), "-o", str(elf)],
                       check=True, capture_output=True)
        _, segs, syms = v.v.elf.elf_info(elf)
        for name, (address, _, _) in v.CALLS.items():
            syms.setdefault(name, address | 1)
        v.ENTRIES["enable"] = ("opencfw_boot_context_enable", 0x42c538)
        stock, source = Machine(False, segs, syms), Machine(True, segs, syms)
        source.symbols["opencfw_boot_context_enable"] = syms["opencfw_bl_context_enable"]
        cases = []
        for module, interface, buffer, words, poll, cq_status, match in itertools.product(
                [0, 4, 7], [0, 1, 2], [0, BUFFER], [2, 16], [0, 4], [0, 7], [0, 1]):
            handle = v.POOL + module * v.STRIDE
            observed = []
            for m in [stock, source]:
                m.reset()
                m.cpu.mem_write(handle, struct.pack("<II", 0x01123456, module))
                m.cpu.mem_write(handle + 8, bytes([interface]))
                m.cpu.mem_write(handle + 12, struct.pack("<II", buffer, words))
                selected = int(interface != 0)
                register = (selected << 1) if match else ((1 - selected) << 1)
                m.cpu.mem_write(v.v.IRQ + module * 0x1000 + 0x11c,
                                struct.pack("<I", register))
                m.lower_status = poll
                m.cq_status = cq_status
                result = m.call("enable", [handle])
                observed.append(m.observation(result))
            assert observed[0] == observed[1], (module, interface, buffer, words, poll, cq_status, match)
            cases.append({"module": module, "interface": interface,
                          "buffer": buffer, "words": words, "poll": poll,
                          "cq_status": cq_status, "match": match,
                          "result": observed[0]["status"], "events": observed[0]["events"]})
        trace = {hex(pc): raw for pc, raw in stock.trace.items()}
        used = {int(pc, 16) + i for pc, raw in trace.items()
                for i in range(len(bytes.fromhex(raw)))}
        report = {"status": "PASS", "cases": len(cases),
                  "original_sha256": v.v.LOCKED_SHA,
                  "source_elf_sha256": hashlib.sha256(elf.read_bytes()).hexdigest(),
                  "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                  "alias_sha256": hashlib.sha256(ALIAS.read_bytes()).hexdigest(),
                  "stock_entry": "0x42c539", "distinct_original_trace_bytes": len(used),
                  "comparisons": cases,
                  "limits": ["Platform-finish passes one transfer-handle pointer and consumes R0 status; the matrix covers matching and rejected interfaces, with and without queue storage.",
                             "CQ initialization and status polling are controlled cuts. Context/MMIO state is synthetic; no physical IOM, DMA or scheduling behavior is proved.",
                             "Compatible M4 behavior execution is compared; M55 archive compilation and direct relocation are checked separately."]}
        Path(__file__).with_name("context-enable-alias-comparison.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({key: report[key] for key in ["status", "cases", "distinct_original_trace_bytes"]}))


if __name__ == "__main__":
    main()
