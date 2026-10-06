#!/usr/bin/env python3
"""Bounded original/source tests of NOR setup, teardown, and wait helpers.

Only named external platform boundaries are synthetic. Stock wrapper/helper
instructions and compiled candidate instructions execute in Unicorn; no
physical hardware or flash access occurs.
"""
import argparse
import importlib.util
import json
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
spec = importlib.util.spec_from_file_location(
    "bootverify", ROOT / "g2/components/bootloader/update_core/verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)

ENTRY = {"before": 0x41FF08, "configure": 0x420E8C,
         "delay": 0x4207F4, "after": 0x41FF1E, "wait": 0x4207A2}
PROVIDER = {
    0x4156AC: "copy", 0x4166AA: "activity", 0x416710: "pending",
    0x4176CE: "log", 0x418B56: "runtime_mode", 0x41D1C0: "delay_us",
    0x416378: "notify", 0x4205F4: "poll_status", 0x424BE4: "device_config",
    0x425066: "enable", 0x4250F0: "disable", 0x4251C0: "control",
    0x426808: "power_control", 0x41FADC: "publish_device",
}
v.ENTRIES.update(ENTRY)
HANDLE_SLOT = 0x200270DC
ACTIVITY_SLOT = 0x200270E0
XIP_STATE = 0x200271C5
POWER_STATE = 0x200271C6
MODE_SLOT = 0x200270D4
DEVICE_SLOT = 0x200270D8
DEVICE_POINTER = 0x20006100
DEVICE_TEMPLATE = 0x20000224
STATUS_TEMPLATE = 0x2000023C
HANDLE = 0x20006000
ACTIVITY = 0x20006020


class SetupMachine(v.Machine):
    def __init__(self, source=False, segments=(), symbols=None):
        super().__init__(source, segments, symbols)
        if source:
            aliases = {
                "before": "opencfw_bl_nor_read_before",
                "configure": "opencfw_bl_nor_read_configure",
                "delay": "opencfw_bl_nor_read_delay",
                "after": "opencfw_bl_nor_read_after",
                "wait": "opencfw_bl_mspi_ready_wait",
            }
            for short, symbol in aliases.items():
                self.symbols["opencfw_boot_" + short] = self.symbols[symbol]
        self.fixture = {}
        self.provider_events = []
        self.poll_index = 0

    def code(self, uc, pc, size, user):
        kind = PROVIDER.get(pc)
        if kind is None:
            super().code(uc, pc, size, user)
            return
        r0, r1, r2, r3 = self.args()
        if kind == "copy":
            n = r2
            raw = bytes(uc.mem_read(r1, n))
            uc.mem_write(r0, raw)
            self.provider_events.append([kind, n, raw.hex()])
            self.ret(r0)
        elif kind == "activity":
            value = self.fixture.get("activity_result", 0)
            self.provider_events.append([kind, r0, r1, value])
            self.ret(value)
        elif kind == "pending":
            value = self.fixture.get("pending_result", 0)
            self.provider_events.append([kind, r0, value])
            self.ret(value)
        elif kind == "log":
            sp = uc.reg_read(v.a.UC_ARM_REG_SP)
            line = self.u(sp)
            fmt = self.u(sp + 4)
            self.provider_events.append([kind, r0, r1, r2, r3, line, fmt])
            self.ret(0)
        elif kind == "runtime_mode":
            value = self.fixture.get("runtime_mode", 1)
            self.provider_events.append([kind, value])
            self.ret(value)
        elif kind == "delay_us":
            self.provider_events.append([kind, r0])
            self.ret(0)
        elif kind == "notify":
            self.provider_events.append([kind, r0])
            self.ret(0)
        elif kind == "poll_status":
            sp = uc.reg_read(v.a.UC_ARM_REG_SP)
            length = self.u(sp)
            statuses = self.fixture.get("poll_statuses", [])
            status = statuses[self.poll_index] if self.poll_index < len(statuses) else 0
            bytes_out = self.fixture.get("poll_bytes", [])
            byte = bytes_out[self.poll_index] if self.poll_index < len(bytes_out) else 0
            self.poll_index += 1
            uc.mem_write(r3, bytes([byte & 0xFF]) * max(1, length))
            self.provider_events.append([kind, r0, r1, r2, length, status, byte])
            self.ret(status)
        elif kind in ("disable", "enable"):
            status = self.fixture.get(kind + "_status", 0)
            self.provider_events.append([kind, r0, status])
            self.ret(status)
        elif kind == "device_config":
            raw = bytes(uc.mem_read(r1, 24))
            status = self.fixture.get("device_config_status", 0)
            self.provider_events.append([kind, r0, raw.hex(), status])
            self.ret(status)
        elif kind == "control":
            status = self.fixture.get("control_status_" + str(r1), 0)
            if r1 == 0x10:
                value = uc.mem_read(r2, 6)[5]
            else:
                value = uc.mem_read(r2, 1)[0]
            self.provider_events.append([kind, r0, r1, value, status])
            self.ret(status)
        elif kind == "power_control":
            status = self.fixture.get("power_control_status", 0)
            self.provider_events.append([kind, r0, r1, r2, status])
            self.ret(status)
        elif kind == "publish_device":
            self.provider_events.append([kind, r0, r1])
            self.ret(0)

    def setup(self, fixture):
        self.fixture = fixture
        self.provider_events = []
        self.poll_index = 0
        self.w(HANDLE_SLOT, HANDLE)
        self.w(ACTIVITY_SLOT, ACTIVITY)
        self.w(DEVICE_SLOT, DEVICE_POINTER)
        self.w(DEVICE_POINTER, 0x1234ABCD)
        self.w(MODE_SLOT, fixture.get("mode_slot", 0))
        self.cpu.mem_write(XIP_STATE, bytes([fixture.get("xip_state", 0)]))
        self.cpu.mem_write(POWER_STATE, bytes([fixture.get("power_state", 0)]))
        template = bytes(range(24))
        self.cpu.mem_write(DEVICE_TEMPLATE, template)
        self.cpu.mem_write(STATUS_TEMPLATE, b"\x00" * 8)

    def invoke(self, name, args, fixture):
        self.setup(fixture)
        result = self.run(name, args)
        result["providers"] = self.provider_events
        result["xip_state"] = self.cpu.mem_read(XIP_STATE, 1)[0]
        result["power_state"] = self.cpu.mem_read(POWER_STATE, 1)[0]
        result["status_template"] = bytes(self.cpu.mem_read(STATUS_TEMPLATE, 8)).hex()
        return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--elf", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    _, segments, symbols = v.elf.elf_info(args.elf)
    cases, trace = [], {}
    fixtures = {
        "before": [({}, []), ({"activity_result": 1}, []),
                   ({"activity_result": 1, "xip_state": 1}, [])],
        "after": [({}, []), ({"power_state": 1}, []),
                  ({"xip_state": 1, "pending_result": 1}, [])],
        "configure": [({}, []), ({"disable_status": 9}, []),
                      ({"device_config_status": 7}, []),
                      ({"enable_status": 4}, []),
                      ({"control_status_24": 3}, [])],
        "delay": [({}, []), ({"poll_statuses": [0, 0], "poll_bytes": [1, 0]}, [])],
        "wait": [({"poll_bytes": [0]}, [0]),
                 ({"poll_bytes": [1, 0]}, [2]),
                 ({"poll_statuses": [9, 0], "poll_bytes": [0, 0]}, [0]),
                 ({"poll_bytes": [1] * 200 + [0], "runtime_mode": 2}, [1])],
    }
    for name, rows in fixtures.items():
        for fixture, callargs in rows:
            machines = [SetupMachine(), SetupMachine(True, segments, symbols)]
            results = [m.invoke(name, callargs, fixture) for m in machines]
            keys = ["providers", "xip_state", "power_state", "status_template"]
            left = {k: results[0][k] for k in keys}
            right = {k: results[1][k] for k in keys}
            assert left == right, (name, fixture, callargs, left, right)
            trace.update(machines[0].trace)
            cases.append({"function": name, "arguments": callargs,
                          "fixture": fixture, "observed": left})
    used = {int(pc, 0) + i for pc, raw in trace.items()
            for i in range(len(bytes.fromhex(raw)))}
    out = {
        "status": "PASS", "cases": len(cases),
        "original_sha256": v.SHA, "elf_sha256": v.sha(args.elf),
        "source_sha256": {p.name: v.sha(p) for p in HERE.iterdir()
                           if p.suffix in [".c", ".h", ".ld", ".py"]},
        "distinct_original_instruction_bytes": len(used),
        "original_trace": trace, "comparisons": cases,
        "limits": [
            "HAL, RTOS state, delay, copy and log edges are injected at exact local call targets; their internals are not tested here.",
            "The delay helper forwards 5 or 1000 unchanged to 0x41D1C0. Units are not established by this comparison.",
            "The wait tests cover immediate-ready, busy-then-ready, provider error, and 200-pass-to-secondary-loop cases; a 500-retry exhaustion case is not included.",
            "No physical power, MSPI, scheduler, NOR, or logging behavior is exercised.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in
                      ("status", "cases", "distinct_original_instruction_bytes")},
                     indent=2))


if __name__ == "__main__":
    main()
