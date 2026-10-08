#!/usr/bin/env python3
"""Original/source comparison for the MSPI CQ pause and DMA continuation."""
import argparse
import hashlib
import importlib.util
import json
import struct
from pathlib import Path
from unicorn import UC_HOOK_MEM_WRITE

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
spec = importlib.util.spec_from_file_location(
    "bootverify", ROOT / "g2/components/bootloader/update_core/verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
ENTRY = 0x4240AA
v.ENTRIES["pause_dma"] = ENTRY
STATE = 0x20006000
DESC = 0x20010000
MMIO = 0x40060000


class Machine(v.Machine):
    def __init__(self, source=False, segments=(), symbols=None, fixture=None):
        super().__init__(source, segments, symbols)
        self.fixture = fixture or {}
        self.cpu.mem_map(MMIO, 0x4000)
        self.delay_count = 0
        self.clock_calls = []
        self.pause_steps = []
        self.trace = {}
        if source:
            self.symbols["opencfw_boot_pause_dma"] = \
                self.symbols["opencfw_provider_4240aa"]
            self.cpu.mem_write(0x41b8ec,
                v.BLOB.read_bytes()[0x41b8ec-v.BASE:0x41b8f4-v.BASE])
            self.exec_ranges.append((0x41b8ec, 0x41b8f4))
        self.cpu.hook_add(UC_HOOK_MEM_WRITE, self.trace_mmio,
                          begin=MMIO, end=MMIO+0x3fff)

    def trace_mmio(self, uc, access, address, size, value, _):
        pass

    def put32(self, address, value):
        self.cpu.mem_write(address, struct.pack("<I", value & 0xffffffff))

    def u32(self, address):
        return struct.unpack("<I", self.cpu.mem_read(address, 4))[0]

    def code(self, uc, pc, size, user):
        if not self.source and pc in (0x423fb8, 0x423fe6, 0x423ff0,
                                       0x423ffa, 0x423fd8, 0x424020):
            module = self.u32(STATE+4)
            addr = MMIO + module*0x1000 + 0x2a0
            self.pause_steps.append([hex(pc), module, hex(self.u32(addr)),
                                     self.args()[:2]])
        if pc == 0x41D1C0:
            self.delay_count += 1
            ready_at = self.fixture.get("clear_busy_after")
            status_at = self.fixture.get("status_ready_after")
            module_base = MMIO + self.fixture.get("module", 0) * 0x1000
            if ready_at == self.delay_count:
                self.put32(module_base + 0x2a0,
                           self.u32(module_base + 0x2a0) & ~1)
            if status_at == self.delay_count:
                self.put32(module_base + 0x104,
                           self.u32(module_base + 0x104) & ~1)
            self.ret(0)
            return
        if pc == 0x4222F0:
            clock, user = self.args()[:2]
            status = self.fixture.get("clock_status", 0)
            self.clock_calls.append([clock, user, status])
            self.ret(status)
            return
        super().code(uc, pc, size, user)

    def setup(self, fixture):
        module = fixture.get("module", 0)
        state = bytearray(0x8d0)
        struct.pack_into("<II", state, 0, 0x01BEBEBE, module)
        struct.pack_into("<I", state, 0x24, 0xa5a5a5a5)
        struct.pack_into("<I", state, 0x840, fixture.get("prior", 0))
        struct.pack_into("<I", state, 0x83c, 0xabababab)
        struct.pack_into("<I", state, 0x848, fixture.get("ring", 4))
        struct.pack_into("<I", state, 0x850, fixture.get("index", 0))
        struct.pack_into("<I", state, 0x854, DESC)
        self.cpu.mem_write(STATE, bytes(state))
        descriptors = bytearray(0x200)
        # Set every ring slot to a distinct four-word DMA descriptor.
        for slot in range(8):
            struct.pack_into("<4I", descriptors, slot * 0x18,
                             0x10000000+slot, 0x20000000+slot,
                             0x30000000+slot, 0x40000000+slot)
        self.cpu.mem_write(DESC, bytes(descriptors))
        mbase = MMIO + module * 0x1000
        self.cpu.mem_write(mbase, bytes(0x1000))
        self.put32(mbase+0x2a0, fixture.get("control", 0))
        self.put32(mbase+0x2ac, fixture.get("control_aux", 0))
        self.put32(mbase+0x2b8, fixture.get("status_aux", 0))
        self.put32(mbase+0x104, fixture.get("dma_status", 0))
        self.cpu.reg_write(v.a.UC_ARM_REG_PRIMASK, fixture.get("primask", 0))

    def run(self, name, args):
        self.finished = False
        self.events = []
        entry = ((self.symbols["opencfw_boot_pause_dma"] & ~1)
                 if self.source else ENTRY)
        for reg, value in zip([v.a.UC_ARM_REG_R0, v.a.UC_ARM_REG_R1,
                               v.a.UC_ARM_REG_R2, v.a.UC_ARM_REG_R3],
                              args+[0]*4):
            self.cpu.reg_write(reg, value)
        self.cpu.reg_write(v.a.UC_ARM_REG_SP, v.SP)
        self.cpu.reg_write(v.a.UC_ARM_REG_LR, v.STOP|1)
        self.cpu.emu_start(entry|1, v.STOP+2, count=30000000)
        assert self.finished, (self.source, hex(self.cpu.reg_read(v.a.UC_ARM_REG_PC)),
                               self.delay_count)
        return {"return": self.cpu.reg_read(v.a.UC_ARM_REG_R0),
                "state": bytes(self.cpu.mem_read(STATE, 0x8d0)),
                "mmio": bytes(self.cpu.mem_read(MMIO, 0x4000)),
                "descriptor": bytes(self.cpu.mem_read(DESC, 0x200)),
                "primask": self.cpu.reg_read(v.a.UC_ARM_REG_PRIMASK),
                "delay_calls": self.delay_count,
                "clock_calls": self.clock_calls}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--elf", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    assert v.sha(v.BLOB) == v.SHA
    _, segments, symbols = v.elf.elf_info(args.elf)
    fixtures = [
        {"prior": 1, "increment": 7, "primask": 1},
        {"prior": 0, "increment": 9, "primask": 0, "dma_status": 0},
        {"prior": 0, "increment": 1, "control": 1,
         "control_aux": 8, "status_aux": 0x80, "dma_status": 0,
         "index": 1, "ring": 4},
        {"prior": 0, "increment": 1, "control": 1,
         "clear_busy_after": 1, "dma_status": 1,
         "status_ready_after": 2, "index": 3, "ring": 4,
         "module": 2, "clock_status": 0},
        {"prior": 0, "increment": 3, "control": 1,
         "control_aux": 8, "status_aux": 0, "module": 1},
        {"prior": 0, "increment": 3, "control": 0,
         "dma_status": 0, "clock_status": 9, "index": 3, "ring": 4},
        {"prior": 0, "increment": 3, "control": 0,
         "dma_status": 0, "clock_status": 0, "index": 0xffffffff,
         "ring": 0},
    ]
    details, trace = [], {}
    for fixture in fixtures:
        increment = fixture.pop("increment")
        machines = [Machine(fixture=fixture),
                    Machine(True, segments, dict(symbols), fixture)]
        for machine in machines:
            machine.setup(fixture)
        pair = [machine.run("pause_dma", [STATE, increment])
                for machine in machines]
        a, b = pair
        for key in a:
            if isinstance(a[key], bytes):
                if a[key] != b[key]:
                    differences = []
                    for offset in range(0, len(a[key]), 4):
                        left = int.from_bytes(a[key][offset:offset+4], "little")
                        right = int.from_bytes(b[key][offset:offset+4], "little")
                        if left != right:
                            differences.append([hex(offset), hex(left), hex(right)])
                    raise AssertionError((fixture, key, differences[:50],
                        [(m.delay_count, m.clock_calls) for m in machines],
                        machines[0].pause_steps,
                        {k: k in machines[0].trace for k in
                         ["0x4240aa", "0x4240d0", "0x4240d2", "0x423fb8", "0x42403e"]},
                        list(machines[0].trace)[-40:]))
            else:
                assert a[key] == b[key], (fixture, key, a[key], b[key])
        trace.update(machines[0].trace)
        details.append({"fixture": fixture, "return": a["return"],
                        "delay_calls": a["delay_calls"],
                        "clock_calls": a["clock_calls"],
                        "state_sha256": hashlib.sha256(a["state"]).hexdigest(),
                        "mmio_sha256": hashlib.sha256(a["mmio"]).hexdigest()})
    used = {int(pc, 0)+i for pc, raw in trace.items()
            for i in range(len(bytes.fromhex(raw)))}
    stock_spans = {
        "scheduler_entry": (0x4240aa, 0x4240d1),
        "scheduler_pause_continuation": (0x4240d2, 0x42410d),
        "scheduler_dma_continuation": (0x42410e, 0x42411f),
        "cq_pause_poll": (0x423fb8, 0x42403d),
        "dma_program": (0x42403e, 0x4240a9),
        "status_check": (0x41d246, 0x41d289),
    }
    blob = v.BLOB.read_bytes()
    source_files = [HERE / "verify_pause_dma.py", HERE / "Makefile",
                    HERE / "module.ld",
                    ROOT / "g2/components/bootloader/nor_mspi_queue/mspi_pause_dma.c",
                    ROOT / "g2/components/bootloader/nor_mspi_queue/mspi_pause_dma.h",
                    ROOT / "g2/components/bootloader/nor_mspi_init/status_poll.c"]
    out = {"status": "PASS", "cases": len(details),
           "distinct_original_instruction_bytes": len(used),
           "original_sha256": v.SHA,
           "stock_ranges": {name: [hex(span[0]), hex(span[1])]
                            for name, span in stock_spans.items()},
           "stock_range_sha256": {name: hashlib.sha256(
               blob[start-v.BASE:end-v.BASE+1]).hexdigest()
               for name, (start, end) in stock_spans.items()},
           "source_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(
               path.read_bytes()).hexdigest() for path in source_files},
           "source_elf_sha256": v.sha(args.elf), "cases_detail": details,
           "original_trace": trace,
           "limits": ["MMIO is synthetic; delay callback can evolve modeled peripheral status.",
                      "No elapsed-time, hardware CQ, DMA completion, or flash effect is asserted."]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2)+"\n")
    print(json.dumps({k: out[k] for k in ("status", "cases",
                                           "distinct_original_instruction_bytes")}, indent=2))


if __name__ == "__main__":
    main()
