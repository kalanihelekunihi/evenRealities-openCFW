#!/usr/bin/env python3
"""Differential execution of the bootloader timer port and its leaf helpers."""
import argparse
import hashlib
import importlib.util
import json
import struct
from pathlib import Path

from unicorn import (Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS,
                     UC_HOOK_CODE, UC_HOOK_MEM_READ)
from unicorn import arm_const as a

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
BLOB = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
BLOB_SHA = "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"
BASE = 0x410000
STOP = 0x08000000
STIMER_BASE = 0x40008800
STTMR = STIMER_BASE + 4
SCMPR0 = STIMER_BASE + 0x20
GATE = 0x40008900
COMPARE_SHADOW = 0x200001c8
TIMER_START = 0x20027120
TIMER_INTERVAL = 0x20027124
TIMER_MAX = 0x20027128
TIMER_READY = 0x200271bf
NVIC_ISER = 0xe000e100
NVIC_IPR = 0xe000e400

STOCK = {
    "configure": 0x41b6fa,
    "gate": 0x41f4ac,
    "priority": 0x41b64c,
    "irq_enable": 0x41b614,
    "clock_config": 0x41f358,
    "read_counter": 0x41f424,
    "compare_set": 0x41f440,
}
SOURCE = {
    "configure": "opencfw_bl_port_timer_configure",
    "gate": "opencfw_bl_port_timer_gate_enable",
    "priority": "opencfw_bl_port_timer_irq_priority",
    "irq_enable": "opencfw_bl_port_timer_irq_enable",
    "clock_config": "opencfw_bl_port_timer_clock_configure",
    "read_counter": "opencfw_bl_port_timer_read_counter",
    "compare_set": "opencfw_bl_port_timer_compare_set",
}
STOCK_CLOCK_REQUEST = 0x4222f0
STOCK_CLOCK_RELEASE = 0x422364

spec = importlib.util.spec_from_file_location(
    "elf_reader", ROOT / "g2/components/bootloader/update_core/elf_reader.py")
elf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(elf)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Machine:
    def __init__(self, source=False, segments=(), symbols=None):
        self.cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        # Select the M-class architecture before mapping memory. This enables
        # the v8-M instructions used by the Cortex-M55-targeted source build.
        self.cpu.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
        self.source = source
        self.finished = False
        self.trace = {}
        self.events = []
        self.counter_next = 0
        self.counter_step = 0
        self.counter_reads = []
        self.clock_entries = {}
        self.cpu.mem_map(BASE, 0x25000)
        self.cpu.mem_write(BASE, BLOB.read_bytes())
        self.cpu.mem_map(0x20000000, 0x40000)
        self.cpu.mem_map(0x40008000, 0x2000)
        self.cpu.mem_map(0xe000e000, 0x2000)
        self.cpu.mem_map(STOP, 0x10000)
        if source:
            self.cpu.mem_map(0x10000, 0x10000)
            for seg in segments:
                self.cpu.mem_write(seg["address"], seg["data"])
            self.symbols = symbols
            self.clock_entries = {
                symbols["clock_request"] & ~1: "request",
                symbols["clock_release"] & ~1: "release",
            }
        else:
            self.symbols = {}
            self.clock_entries = {STOCK_CLOCK_REQUEST: "request",
                                  STOCK_CLOCK_RELEASE: "release"}
        self.cpu.hook_add(UC_HOOK_CODE, self.code)
        self.cpu.hook_add(UC_HOOK_MEM_READ, self.read_memory)

    def code(self, uc, pc, size, _):
        if pc == STOP:
            self.finished = True
            uc.emu_stop()
            return
        if pc in self.clock_entries:
            self.events.append([self.clock_entries[pc],
                                uc.reg_read(a.UC_ARM_REG_R0) & 0xff,
                                uc.reg_read(a.UC_ARM_REG_R1) & 0xff])
            uc.reg_write(a.UC_ARM_REG_R0, 0)
            uc.reg_write(a.UC_ARM_REG_PC, uc.reg_read(a.UC_ARM_REG_LR))
            return
        if not self.source:
            self.trace[pc] = bytes(uc.mem_read(pc, size))

    def read_memory(self, uc, access, address, size, value, _):
        if address == STTMR and self.counter_step:
            uc.mem_write(STTMR, struct.pack("<I", self.counter_next & 0xffffffff))
            self.counter_reads.append(self.counter_next)
            self.counter_next = (self.counter_next + self.counter_step) & 0xffffffff

    def write32(self, address, value):
        self.cpu.mem_write(address, struct.pack("<I", value & 0xffffffff))

    def u32(self, address):
        return struct.unpack("<I", self.cpu.mem_read(address, 4))[0]

    def setup(self, case):
        self.cpu.mem_write(0x20000000, b"\0" * 0x40000)
        self.cpu.mem_write(0x40008000, b"\xa5" * 0x2000)
        self.cpu.mem_write(0xe000e000, b"\x5a" * 0x2000)
        self.write32(STIMER_BASE, case.get("stcfg", 0))
        self.write32(STTMR, case.get("counter_start", 100))
        self.write32(GATE, case.get("gate_initial", 0x80000000))
        self.write32(COMPARE_SHADOW, case.get("compare_shadow", 0x70000000))
        for index in range(1, 8):
            self.write32(COMPARE_SHADOW + index * 4, 0x71000000 + index)
        self.write32(TIMER_START, 0x11111111)
        self.write32(TIMER_INTERVAL, 0x22222222)
        self.write32(TIMER_MAX, 0x33333333)
        self.cpu.mem_write(TIMER_READY, b"\0")
        self.counter_next = case.get("counter_start", 100)
        self.counter_step = case.get("counter_step", 0)
        self.cpu.reg_write(a.UC_ARM_REG_PRIMASK, case.get("primask", 0))
        self.events = []
        self.trace = {}
        self.counter_reads = []
        self.finished = False

    def result(self, compare_r0=True):
        result = {
            "primask": self.cpu.reg_read(a.UC_ARM_REG_PRIMASK),
            "timer_registers": bytes(self.cpu.mem_read(STIMER_BASE, 0x108)).hex(),
            "clock_gate_register": self.u32(GATE),
            "nvic_iser": bytes(self.cpu.mem_read(NVIC_ISER, 8)).hex(),
            "nvic_priority": bytes(self.cpu.mem_read(NVIC_IPR, 0x100)).hex(),
            "software_compare": bytes(self.cpu.mem_read(COMPARE_SHADOW, 0x20)).hex(),
            "timer_globals": bytes(self.cpu.mem_read(TIMER_START, 8)).hex() +
                              bytes(self.cpu.mem_read(TIMER_MAX, 4)).hex() +
                              bytes(self.cpu.mem_read(TIMER_READY, 1)).hex(),
            "clock_events": self.events,
        }
        if compare_r0:
            result["r0"] = self.cpu.reg_read(a.UC_ARM_REG_R0)
        return result

    def run(self, name, args, case):
        self.setup(case)
        entry = (self.symbols[SOURCE[name]] & ~1) if self.source else STOCK[name]
        regs = (a.UC_ARM_REG_R0, a.UC_ARM_REG_R1,
                a.UC_ARM_REG_R2, a.UC_ARM_REG_R3)
        for reg, value in zip(regs, args + [0] * (4 - len(args))):
            self.cpu.reg_write(reg, value & 0xffffffff)
        if name == "configure":
            self.cpu.reg_write(a.UC_ARM_REG_R3,
                               case.get("incoming_r3", 0xdecafbad))
        self.cpu.reg_write(a.UC_ARM_REG_SP, 0x2002f000)
        self.cpu.reg_write(a.UC_ARM_REG_LR, STOP | 1)
        try:
            self.cpu.emu_start(entry | 1, STOP + 2, count=1_000_000)
        except Exception:
            print("emulation fault", {"source": self.source, "function": name,
                                      "pc": hex(self.cpu.reg_read(a.UC_ARM_REG_PC)),
                                      "instruction": bytes(self.cpu.mem_read(
                                          self.cpu.reg_read(a.UC_ARM_REG_PC) & ~1, 4)).hex()})
            raise
        assert self.finished, (self.source, name,
                               hex(self.cpu.reg_read(a.UC_ARM_REG_PC)))
        return self.result(name not in ("gate", "priority", "irq_enable"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--elf", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    assert sha(BLOB) == BLOB_SHA
    _, segments, symbols = elf.elf_info(args.elf)
    machines = [Machine(), Machine(True, segments, symbols)]
    cases = []

    def check(name, params, fixture):
        pair = [Machine(), Machine(True, segments, symbols)]
        observed = [m.run(name, params, fixture) for m in pair]
        if observed[0] != observed[1]:
            differences = {}
            for key in observed[0]:
                if observed[0][key] == observed[1][key]:
                    continue
                if isinstance(observed[0][key], str):
                    left = bytes.fromhex(observed[0][key])
                    right = bytes.fromhex(observed[1][key])
                    differences[key] = [(i, left[i], right[i])
                                        for i in range(min(len(left), len(right)))
                                        if left[i] != right[i]][:20]
                else:
                    differences[key] = [observed[0][key], observed[1][key]]
            raise AssertionError({"name": name, "params": params,
                                 "fixture": fixture, "differences": differences,
                                 "counter_reads": [pair[0].counter_reads,
                                                   pair[1].counter_reads]})
        cases.append({"function": name, "arguments": params,
                      "fixture": fixture, "result": observed[0]})
        return observed[0]

    for old in [0, 3, 0x40000003, 0x80000006, 0xc0000003]:
        check("configure", [], {"stcfg": old, "counter_start": 100,
                                 "counter_step": 1, "compare_shadow": 105,
                                 "primask": old & 1,
                                 "incoming_r3": 0xdecafbad})
    for irq, priority in [(32, 0xff), (0, 0x12), (31, 7), (0xffff, 3)]:
        check("priority", [irq, priority], {})
    for irq in [32, 0, 31, 0xffff, 0x8000]:
        check("irq_enable", [irq], {})
    for bits, initial in [(1, 0), (0x20, 0x80000000)]:
        check("gate", [bits], {"gate_initial": initial})
    for old, value in [(0, 0x80000000), (3, 0x80000000),
                       (0x40000003, 0x80000000),
                       (0xc0000003, 0x103),
                       (0x80000006, 0x103), (1, 2), (1, 3)]:
        check("clock_config", [value], {"stcfg": old})
    for step in [0, 1]:
        check("read_counter", [], {"counter_start": 0xfffffffd,
                                    "counter_step": step,
                                    "primask": step})
    check("compare_set", [0, 32], {"counter_start": 100,
                                   "counter_step": 1,
                                   "compare_shadow": 105, "primask": 1})
    check("compare_set", [0, 4], {"counter_start": 100,
                                  "counter_step": 2,
                                  "compare_shadow": 0x70000000})
    check("compare_set", [8, 32], {"counter_start": 100,
                                   "counter_step": 1})

    trace = {}
    for case in cases:
        if case["function"] == "configure":
            pair = [Machine(), Machine(True, segments, symbols)]
            # Re-run only to retain instruction bytes for the main startup path.
            pair[0].run(case["function"], case["arguments"], case["fixture"])
            trace.update(pair[0].trace)
        elif case["function"] in ("clock_config", "compare_set", "read_counter",
                                    "gate", "priority", "irq_enable"):
            pair = [Machine(), Machine(True, segments, symbols)]
            pair[0].run(case["function"], case["arguments"], case["fixture"])
            trace.update(pair[0].trace)

    used = {pc + i for pc, raw in trace.items() for i in range(len(raw))}
    result = {
        "status": "PASS", "cases": len(cases),
        "original_instruction_bytes_reached": len(used),
        "original_image_sha256": BLOB_SHA,
        "source_elf_sha256": sha(args.elf),
        "stock_functions": {
            "configure": {"range": ["0x0041b6fa", "0x0041b752"],
                          "sha256": "45d59465eb1e3b5b6c35c50b7bdc8b64052c86835518e99277c436b8121b8e57"},
            "gate": {"range": ["0x0041f4ac", "0x0041f4b6"],
                     "sha256": "fd98de39e7062501b0d1ff5b9727543177dc3a975d72c80aa12b15453f5f1c9e"},
            "priority": {"range": ["0x0041b64c", "0x0041b670"],
                         "sha256": "48c42138aaa1f347dd54ae3b05570b8b552cf266e44b5981e53db10cbf902656"},
            "irq_enable": {"range": ["0x0041b614", "0x0041b630"],
                           "sha256": "9b50323b56bddfc5e17d7c93f9b410ce9bf05381c0b341d059c1c1e204dfd312"},
            "clock_config": {"range": ["0x0041f358", "0x0041f3f0"],
                             "sha256": "7b90306b1c748074d0661931e2634ee43ebd19e3fec9de470997284b667ec524"},
            "read_counter": {"range": ["0x0041f424", "0x0041f440"],
                             "sha256": "1efeb995ea5a225c5ed153869ff9d741e5ea4ded8a472fc0496946d90202d661"},
            "compare_set": {"range": ["0x0041f440", "0x0041f4ac"],
                            "sha256": "577b2162b8036a9e741c380c3d4c6909af8311395d7e6f00bd983f3a26a89db9"},
        },
        "source_sha256": {
            "port_timer.c": sha(ROOT / "g2/components/bootloader/port_timer/port_timer.c"),
            "port_timer.h": sha(ROOT / "g2/components/bootloader/port_timer/port_timer.h"),
            "clock_provider_stubs.c": sha(HERE / "clock_provider_stubs.c"),
        },
        "trace": {hex(pc): raw.hex() for pc, raw in sorted(trace.items())},
        "comparisons": cases,
        "limits": [
            "STTMR reads are a deterministic synthetic counter model, not wall time or physical STIMER behavior.",
            "clock_request/clock_release are intercepted at the actual stock call boundary and matched to source test stubs; their clock-tree implementations are not reconstructed here.",
            "NVIC, STIMER, global state, and the 0x40008900 OR target are ordinary synthetic memory; no interrupt delivery, clock stability, compare event, or silicon side effect is modeled.",
            "No frequency or milliseconds meaning is assigned to the raw interval value 32; clock selection and counter-delta semantics require external clock configuration and runtime measurements.",
        ],
    }
    image_bytes = BLOB.read_bytes()
    for function in result["stock_functions"].values():
        start = int(function["range"][0], 16)
        end = int(function["range"][1], 16)
        body = image_bytes[start - BASE:end - BASE]
        assert hashlib.sha256(body).hexdigest() == function["sha256"], function
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in
                      ("status", "cases", "original_instruction_bytes_reached")}))


if __name__ == "__main__":
    main()
