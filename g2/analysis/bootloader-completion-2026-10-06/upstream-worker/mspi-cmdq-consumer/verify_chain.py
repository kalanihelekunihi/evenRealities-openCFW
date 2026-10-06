#!/usr/bin/env python3
"""End-to-end stock/source execution of enable -> cq_init -> cmdq_init."""
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
BLOB = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
BLOB_SHA = "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"
BASE = 0x410000
STOP = 0x08000000
HANDLE = 0x20010000
HANDLE_SIZE = 0x8d0
OUTER_SLOTS = 0x2001caa0
OUTER_SLOTS_SIZE = 4 * 0x8d0
CMDQ_STATE_BASE = 0x200262f0
CMDQ_STATE_SIZE = 12 * 0x2c
PERIPH_BASE = 0x40050000
PERIPH_SIZE = 0x14000
STOCK_ENTRY = 0x425066
OPS_TABLE_ADDRESS = 0x430880
OPS_TABLE_SIZE = 12 * 0x28

spec = importlib.util.spec_from_file_location(
    "elf_reader", ROOT / "g2/components/bootloader/update_core/elf_reader.py")
elf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(elf)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Machine:
    def __init__(self, source=False, segments=(), symbols=None,
                 include_blob_data=True):
        self.cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        self.source = source
        self.finished = False
        self.trace = {}
        self.cpu.mem_map(BASE, 0x25000)
        if not source or include_blob_data:
            self.cpu.mem_write(BASE, BLOB.read_bytes())
        self.cpu.mem_map(0x20000000, 0x40000)
        self.cpu.mem_map(PERIPH_BASE, PERIPH_SIZE)
        self.cpu.mem_map(STOP, 0x10000)
        if source:
            self.cpu.mem_map(0x10000, 0x10000)
            for seg in segments:
                self.cpu.mem_write(seg["address"], seg["data"])
            self.entry = symbols["opencfw_bl_mspi_enable"] & ~1
        else:
            self.entry = STOCK_ENTRY
        self.cpu.hook_add(UC_HOOK_CODE, self.code)

    def code(self, uc, pc, size, _):
        if pc == STOP:
            self.finished = True
            uc.emu_stop()
        elif not self.source:
            self.trace[pc] = bytes(uc.mem_read(pc, size))

    def write32(self, p, x):
        self.cpu.mem_write(p, struct.pack("<I", x & 0xffffffff))

    def setup(self, case):
        handle = bytearray(((i * 37 + 11) ^ 0xa5) & 0xff for i in range(HANDLE_SIZE))
        prefix = 0x01bebebe
        if case.get("bad_magic"):
            prefix ^= 1
        if case.get("uninitialized"):
            prefix &= ~0x01000000
        if case.get("already_enabled"):
            prefix |= 0x02000000
        handle[0:4] = prefix.to_bytes(4, "little")
        module = case.get("module", 0)
        handle[4:8] = module.to_bytes(4, "little")
        handle[8] = 0 if case.get("unconfigured") else 1
        handle[0x14:0x18] = case.get("queue_size_input", 16).to_bytes(4, "little")
        context = 0 if case.get("no_queue") else case.get("queue_buffer", 0x20023400)
        handle[0x18:0x1c] = context.to_bytes(4, "little")
        self.cpu.mem_write(HANDLE, bytes(handle))

        # Keep every per-interface stock bit-24 init guard clear so each
        # successful fixture exercises the complete CQ initializer path.
        cmdq = bytearray(((i * 29 + 7) ^ 0x93) & 0xff for i in range(CMDQ_STATE_SIZE))
        for row in range(12):
            off = row * 0x2c
            flags = int.from_bytes(cmdq[off:off + 4], "little") & 0xfeffffff
            cmdq[off:off + 4] = flags.to_bytes(4, "little")
        self.cpu.mem_write(CMDQ_STATE_BASE, bytes(cmdq))
        self.cpu.mem_write(PERIPH_BASE, b"\xa5" * PERIPH_SIZE)
        self.cpu.mem_write(OUTER_SLOTS, b"\x3c" * OUTER_SLOTS_SIZE)

    def run(self, case):
        self.setup(case)
        self.cpu.reg_write(a.UC_ARM_REG_R0, 0 if case.get("null_handle") else HANDLE)
        self.cpu.reg_write(a.UC_ARM_REG_SP, 0x2002f000)
        self.cpu.reg_write(a.UC_ARM_REG_LR, STOP | 1)
        self.cpu.emu_start(self.entry | 1, STOP + 2, count=1000000)
        assert self.finished, (self.source, hex(self.cpu.reg_read(a.UC_ARM_REG_PC)))
        return {
            "return": self.cpu.reg_read(a.UC_ARM_REG_R0),
            "handle": bytes(self.cpu.mem_read(HANDLE, HANDLE_SIZE)).hex(),
            "cmdq_state": bytes(self.cpu.mem_read(CMDQ_STATE_BASE, CMDQ_STATE_SIZE)).hex(),
            "outer_slots": bytes(self.cpu.mem_read(OUTER_SLOTS, OUTER_SLOTS_SIZE)).hex(),
            "peripherals": bytes(self.cpu.mem_read(PERIPH_BASE, PERIPH_SIZE)).hex(),
        }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--elf", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--source-table", action="store_true",
                    help="load the source-owned .cmdq_ops segment without using the image table")
    args = ap.parse_args()
    assert sha(BLOB) == BLOB_SHA
    _, segments, symbols = elf.elf_info(args.elf)
    source_table_sha = None
    stock_table_sha = None
    if args.source_table:
        table_segment = next((s for s in segments
                              if s["address"] <= OPS_TABLE_ADDRESS and
                              OPS_TABLE_ADDRESS + OPS_TABLE_SIZE <=
                              s["address"] + len(s["data"])), None)
        assert table_segment is not None, "ELF has no loadable .cmdq_ops source bytes"
        off = OPS_TABLE_ADDRESS - table_segment["address"]
        source_table = table_segment["data"][off:off + OPS_TABLE_SIZE]
        stock_table = BLOB.read_bytes()[OPS_TABLE_ADDRESS - BASE:
                                        OPS_TABLE_ADDRESS - BASE + OPS_TABLE_SIZE]
        assert source_table == stock_table, "compiled .cmdq_ops bytes differ from locked image table"
        source_table_sha = hashlib.sha256(source_table).hexdigest()
        stock_table_sha = hashlib.sha256(stock_table).hexdigest()
    cases = [
        {"null_handle": True}, {"bad_magic": True}, {"uninitialized": True},
        {"unconfigured": True}, {"no_queue": True},
        {"already_enabled": True, "module": 1, "queue_size_input": 24},
    ]
    for module in range(4):
        cases.append({"module": module, "queue_size_input": 16 + module * 2,
                      "queue_buffer": 0x20023400 + module * 0x1000})
    cases += [
        {"module": 2, "already_enabled": True, "queue_size_input": 128,
         "queue_buffer": 0x2003a000},
        {"module": 0, "no_queue": True, "queue_size_input": 0},
    ]

    pairs, comparisons, trace = [Machine(), Machine(True, segments, symbols)], [], {}
    for case in cases:
        # Fresh machines per fixture prevent one case's queue state from
        # changing another's already-initialized result.
        current = [Machine(), Machine(True, segments, symbols,
                                      include_blob_data=not args.source_table)]
        observed = [m.run(case) for m in current]
        assert observed[0] == observed[1], {"case": case, "stock": observed[0], "source": observed[1]}
        trace.update(current[0].trace)
        comparisons.append({"case": case, "result": observed[0]})
    used = {pc + i for pc, raw in trace.items() for i in range(len(raw))}
    tracked = [p for p in HERE.iterdir() if p.is_file() and p.suffix in {".c", ".h", ".py", ".ld"}]
    result = {
        "status": "PASS", "cases": len(comparisons),
        "covered_original_instruction_bytes": len(used),
        "original_image_sha256": BLOB_SHA,
        "source_elf_sha256": sha(args.elf),
        "source_table_mode": args.source_table,
        "source_table": ({"address": hex(OPS_TABLE_ADDRESS), "size_bytes": OPS_TABLE_SIZE,
                          "sha256": source_table_sha,
                          "locked_image_sha256": stock_table_sha,
                          "matches_locked_image_byte_for_byte": True}
                         if args.source_table else None),
        "source_sha256": {p.name: sha(p) for p in tracked},
        "compared_stock_ranges": {
            "enable": ["0x00425066", "0x004250f0"],
            "mspi_cq_init": ["0x00423f28", "0x00423f54"],
            "am_hal_cmdq_init": ["0x00427794", "0x00427878"],
        },
        "original_trace": {hex(pc): raw.hex() for pc, raw in sorted(trace.items())},
        "comparisons": comparisons,
        "limits": [
            "MSPI and CMDQ register addresses from the stock ops table are synthetic RAM; physical clock, DMA, command-queue execution, timing, and flash effects are not modeled.",
            "Only the three named functions execute as stock/source code in this chain; all remaining HAL providers and initialization are outside this profile.",
            "Behavioral agreement does not establish original compiler flags, IAR ABI/library behavior outside this bounded call path, full image layout, or bundle byte identity.",
        ],
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ("status", "cases", "covered_original_instruction_bytes")}))


if __name__ == "__main__":
    main()
