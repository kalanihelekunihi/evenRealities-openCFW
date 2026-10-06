#!/usr/bin/env python3
"""Stock/source Unicorn differential for am_hal_cmdq_init's sparse ABI."""
import argparse
import hashlib
import importlib.util
import json
import struct
from pathlib import Path

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as a

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
BASE = 0x410000
STATE_BASE = 0x200262F0
STATE_SIZE = 12 * 0x2C
PERIPH_BASE = 0x40050000
PERIPH_SIZE = 0x14000
CONFIG = 0x20005000
OUT_SLOT = 0x20005020
BUFFER = 0x20007000
STOP = 0x08000000
STOCK_ENTRY = 0x427794
STOCK_SHA = "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"
BLOB = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"

spec = importlib.util.spec_from_file_location(
    "elf_reader", ROOT / "g2/components/bootloader/update_core/elf_reader.py")
elf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(elf)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Machine:
    def __init__(self, source=False, segments=(), symbols=None):
        self.cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        self.source = source
        self.finished = False
        self.trace = {}
        self.cpu.mem_map(BASE, 0x25000)
        self.cpu.mem_write(BASE, BLOB.read_bytes())
        self.cpu.mem_map(0x20000000, 0x40000)
        self.cpu.mem_map(PERIPH_BASE, PERIPH_SIZE)
        self.cpu.mem_map(STOP, 0x10000)
        if source:
            for seg in segments:
                lo = seg["address"] & ~0xfff
                hi = (seg["address"] + seg["memory_size"] + 0xfff) & ~0xfff
                self.cpu.mem_map(lo, hi - lo)
                self.cpu.mem_write(seg["address"], seg["data"])
            self.entry = symbols["opencfw_bl_cmdq_init"] & ~1
        else:
            self.entry = STOCK_ENTRY
        self.cpu.hook_add(UC_HOOK_CODE, self.code)

    def code(self, uc, pc, size, _):
        if pc == STOP:
            self.finished = True
            uc.emu_stop()
        elif not self.source:
            self.trace[pc] = bytes(uc.mem_read(pc, size))

    def w(self, address, value):
        self.cpu.mem_write(address, struct.pack("<I", value & 0xffffffff))

    def u(self, address):
        return struct.unpack("<I", self.cpu.mem_read(address, 4))[0]

    def setup(self, case):
        state = bytearray(((i * 29 + 7) ^ 0x93) & 0xff for i in range(STATE_SIZE))
        # The raw UBFX checks bit 24 (not the top/sign bit).
        flags = int.from_bytes(state[0:4], "little") & 0xfeffffff
        if case.get("initialized"):
            flags |= 0x01000000
        state[0:4] = flags.to_bytes(4, "little")
        self.cpu.mem_write(STATE_BASE, bytes(state))
        self.cpu.mem_write(PERIPH_BASE, b"\xa5" * PERIPH_SIZE)
        for index, value in enumerate(case.get("presets", [])):
            self.w(PERIPH_BASE + index * 4, value)
        self.cpu.mem_write(CONFIG, b"\0" * 12)
        if not case.get("null_config"):
            self.w(CONFIG, case.get("size", 8))
            self.w(CONFIG + 4, case.get("buffer", BUFFER))
            self.cpu.mem_write(CONFIG + 8, bytes([case.get("option", 1)]))
        self.w(OUT_SLOT, 0xDEADBEEF)

    def invoke(self, case):
        self.setup(case)
        interface = case.get("interface", 8)
        config = 0 if case.get("null_config") else CONFIG
        out = 0 if case.get("null_output") else OUT_SLOT
        for reg, value in zip((a.UC_ARM_REG_R0, a.UC_ARM_REG_R1, a.UC_ARM_REG_R2),
                              (interface, config, out)):
            self.cpu.reg_write(reg, value)
        self.cpu.reg_write(a.UC_ARM_REG_SP, 0x2002f000)
        self.cpu.reg_write(a.UC_ARM_REG_LR, STOP | 1)
        self.cpu.emu_start(self.entry | 1, STOP + 2, count=200000)
        assert self.finished, (self.source, hex(self.cpu.reg_read(a.UC_ARM_REG_PC)))
        return {
            "return": self.cpu.reg_read(a.UC_ARM_REG_R0),
            "state": bytes(self.cpu.mem_read(STATE_BASE, STATE_SIZE)).hex(),
            "peripherals": bytes(self.cpu.mem_read(PERIPH_BASE, PERIPH_SIZE)).hex(),
            "out": self.u(OUT_SLOT),
        }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--elf", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    assert sha(BLOB) == STOCK_SHA
    _, segments, symbols = elf.elf_info(args.elf)
    cases = [
        {"interface": 12}, {"interface": 255}, {"null_config": True},
        {"interface": 8, "buffer": 0}, {"interface": 8, "size": 1},
        {"interface": 8, "null_output": True}, {"interface": 8, "initialized": True},
    ]
    for interface in range(12):
        cases.append({"interface": interface, "size": 2 + interface,
                      "buffer": BUFFER + interface * 0x100,
                      "option": interface & 1})

    comparisons = []
    raw_trace = {}
    for case in cases:
        pair = [Machine(), Machine(True, segments, symbols)]
        result = [m.invoke(case) for m in pair]
        assert result[0] == result[1], {"case": case, "stock": result[0], "source": result[1]}
        raw_trace.update(pair[0].trace)
        comparisons.append({"case": case, "result": result[0]})

    traced = sorted({pc + i for pc, raw in raw_trace.items() for i in range(len(raw))})
    source_files = [p for p in HERE.iterdir() if p.is_file() and p.suffix in {".c", ".h", ".py", ".ld"}]
    output = {
        "status": "PASS",
        "cases": len(comparisons),
        "covered_stock_instruction_bytes": len(traced),
        "stock_range": ["0x00427794", "0x00427878"],
        "stock_function_sha256": "ad7e3d6257b791855a8cd7fe90389313dfb9496262724777900d6a4193c09b52",
        "stock_image_sha256": STOCK_SHA,
        "elf_sha256": sha(args.elf),
        "source_sha256": {p.name: sha(p) for p in source_files},
        "traced_stock_bytes": {hex(pc): raw.hex() for pc, raw in sorted(raw_trace.items())},
        "comparisons": comparisons,
        "layout": {
            "state_table_base": "0x200262f0", "state_stride": "0x2c",
            "interface_ops_base": "0x00430880", "interface_ops_stride": "0x28",
            "state_offsets_accessed": ["0x00", "0x04", "0x08", "0x0c", "0x10", "0x14", "0x18", "0x1c", "0x20", "0x24"],
            "ops_offsets_accessed": ["0x00", "0x04", "0x08", "0x0c", "0x10", "0x14"],
        },
        "limits": [
            "Synthetic peripheral RAM contains the locked firmware's exact ops pointer/mask table but does not model actual MSPI side effects, clocking, DMA, or timing.",
            "The modeled state is only the sparse layout this function reads/writes; no complete SDK CMDQ state type is asserted.",
            "This is original/source behavioral equivalence, not a byte-identical compiler build or complete bootloader image.",
        ],
    }
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({k: output[k] for k in ("status", "cases", "covered_stock_instruction_bytes")}))


if __name__ == "__main__":
    main()
