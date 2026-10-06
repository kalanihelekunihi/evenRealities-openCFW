#!/usr/bin/env python3
"""Compare stock 0x420254 setup with its source using synthetic HAL cuts."""
import argparse
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
spec = importlib.util.spec_from_file_location(
    "bootv", ROOT / "g2/components/bootloader/update_core/verify.py"
)
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
v.ENTRIES["nor_mspi_init"] = 0x420254
v.ENTRIES["mspi_handle_init"] = 0x424a5a

STOP = 0x08000000
SLOT = 0x20026fd0
HANDLE_SLOT = 0x200270dc
CURRENT_DEVICE = 0x200270d8
STATE_BASE = 0x2001caa0
STATE_STRIDE = 0x8d0
DEVICE_DEFAULT = 0x20000224
DEVICE_MODE_DEFAULT = 0x2000020c

PROVIDERS = {
    0x426808, 0x424af0, 0x424be4, 0x425066, 0x42516c,
    0x41ff34, 0x41fadc, 0x41d90e, 0x426506, 0x426450,
    0x41fdde, 0x41fdc0, 0x41b8e0, 0x4176ce,
}


class MspiInitMachine(v.Machine):
    def __init__(self, *args, stage_status=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.stage_status = stage_status or {}
        self.events = []
        self.w(CURRENT_DEVICE, 0xc0ffee01)
        self.w(HANDLE_SLOT, 0)
        self.cpu.mem_write(SLOT, b"\0" * 16)
        self.cpu.mem_write(DEVICE_DEFAULT, bytes(range(32)))
        self.cpu.mem_write(DEVICE_MODE_DEFAULT, bytes(range(32, 64)))
        self.cpu.mem_write(0x20007000, bytes(reversed(range(32))))

    def cstr(self, address):
        data = bytearray()
        while len(data) < 512:
            byte = self.cpu.mem_read(address + len(data), 1)[0]
            if byte == 0:
                return data.decode("ascii")
            data.append(byte)
        raise AssertionError(("unterminated string", hex(address)))

    def ret_status(self, pc, default=0):
        return self.stage_status.get(pc, default)

    def code(self, uc, pc, size, user):
        if pc not in PROVIDERS:
            super().code(uc, pc, size, user)
            return
        r0, r1, r2, r3 = self.args()
        if pc == 0x426808:
            self.events.append(["power_control", r0, r1, r2])
            self.ret(self.ret_status(pc))
        elif pc == 0x424af0:
            raw = bytes(uc.mem_read(r1, 12))
            self.events.append(["base_configure", r0, raw.hex()])
            self.ret(self.ret_status(pc))
        elif pc == 0x424be4:
            self.events.append([
                "device_configure", r0, r1,
                bytes(uc.mem_read(r1, 16)).hex(),
            ])
            self.ret(self.ret_status(pc))
        elif pc == 0x425066:
            self.events.append(["enable", r0])
            self.ret(self.ret_status(pc))
        elif pc == 0x42516c:
            self.events.append(["deinitialize", r0])
            self.ret()
        elif pc == 0x41ff34:
            self.events.append(["control_latency", r0])
            self.ret()
        elif pc == 0x41fadc:
            self.events.append(["publish_mode", r0, r1])
            self.ret()
        elif pc == 0x41d90e:
            uc.mem_write(r1, (0x12345678).to_bytes(4, "little"))
            self.events.append(["read_register_id", r0])
            self.ret()
        elif pc == 0x426506:
            self.events.append(["interrupt_clear", r0, r1])
            self.ret(self.ret_status(pc))
        elif pc == 0x426450:
            self.events.append(["interrupt_enable", r0, r1])
            self.ret(self.ret_status(pc))
        elif pc == 0x41fdde:
            self.events.append(["interrupt_priority", r0, r1])
            self.ret()
        elif pc == 0x41fdc0:
            self.events.append(["interrupt_unmask", r0])
            self.ret()
        elif pc == 0x41b8e0:
            self.events.append(["irq_guard_initialize"])
            self.ret()
        elif pc == 0x4176ce:
            sp = uc.reg_read(v.a.UC_ARM_REG_SP)
            line = self.u(sp)
            fmt = self.cstr(self.u(sp + 4))
            self.events.append([
                "log", r0, self.cstr(r1), self.cstr(r2), self.cstr(r3),
                line, fmt,
            ])
            self.ret()

    def fixture_setup(self, *, module=1, device_config=0,
                      busy=False, initialized=False):
        if busy:
            self.cpu.mem_write(SLOT + 0x0c, b"\x01")
        if initialized:
            self.w(STATE_BASE + module * STATE_STRIDE,
                   0x01000000)
        return [module, device_config, CURRENT_DEVICE, 0]

    def observe(self, result, module):
        state_address = STATE_BASE + module * STATE_STRIDE
        result["events"] = self.events
        result["current_device"] = self.u(CURRENT_DEVICE)
        result["handle"] = self.u(HANDLE_SLOT)
        result["record"] = bytes(self.cpu.mem_read(SLOT, 16)).hex()
        result["mspi_state"] = bytes(
            self.cpu.mem_read(state_address, STATE_STRIDE)
        ).hex()
        return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--elf", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    assert v.sha(v.BLOB) == v.SHA
    _, segments, symbols = v.elf.elf_info(args.elf)
    cases, trace = [], {}
    runs = [
        ("default-device-success", {}, {}),
        ("custom-device-success", {}, {"device_config": 0x20007000}),
        ("occupied-device-slot", {}, {"busy": True}),
        ("already-initialized-module", {}, {"initialized": True}),
        ("module-out-of-range", {}, {"module": 4}),
        ("power-control-failure", {0x426808: 7}, {}),
        ("base-configure-failure", {0x424af0: 5}, {}),
        ("device-configure-failure", {0x424be4: 6}, {}),
        ("enable-failure", {0x425066: 9}, {}),
        ("interrupt-clear-failure", {0x426506: 7}, {}),
        ("interrupt-enable-failure", {0x426450: 7}, {}),
    ]
    for name, stage_status, fixture in runs:
        pair = [
            MspiInitMachine(stage_status=stage_status),
            MspiInitMachine(True, segments, symbols,
                            stage_status=stage_status),
        ]
        params = [m.fixture_setup(**fixture) for m in pair]
        results = [m.run("nor_mspi_init", p) for m, p in zip(pair, params)]
        observed = [m.observe(r, fixture.get("module", 1))
                    for m, r in zip(pair, results)]
        # update_core's common flash/hash fields are identical by construction;
        # compare the meaningful status, provider sequence, and affected RAM.
        for key in ["return", "events", "current_device", "handle",
                    "record", "mspi_state"]:
            assert observed[0][key] == observed[1][key], (
                name, key, observed[0][key], observed[1][key]
            )
        trace.update(pair[0].trace)
        cases.append({
            "name": name,
            "stage_status": {hex(k): value for k, value in stage_status.items()},
            "fixture": {key: (hex(value) if isinstance(value, int) else value)
                        for key, value in fixture.items()},
            "return": observed[0]["return"],
            "events": observed[0]["events"],
            "current_device": hex(observed[0]["current_device"]),
            "handle": hex(observed[0]["handle"]),
            "record": observed[0]["record"],
            "mspi_state_sha256": __import__("hashlib").sha256(
                bytes.fromhex(observed[0]["mspi_state"])).hexdigest(),
        })

    # The parent initializer supplies a fixed non-null handle slot. Exercise
    # the constructor's null-output case directly as well.
    for handle_out in (0, 0x20007020):
        pair = [MspiInitMachine(),
                MspiInitMachine(True, segments, symbols)]
        for machine in pair:
            machine.w(0x20007020, 0xaabbccdd)
        results = [m.run("mspi_handle_init", [1, handle_out]) for m in pair]
        observed = []
        for machine, result in zip(pair, results):
            state = bytes(machine.cpu.mem_read(STATE_BASE + STATE_STRIDE,
                                               STATE_STRIDE))
            observed.append((result["return"], machine.u(0x20007020),
                             state.hex()))
        assert observed[0] == observed[1], (handle_out, observed)
        trace.update(pair[0].trace)
        cases.append({
            "name": "handle-constructor-null-output" if handle_out == 0
                    else "handle-constructor-direct-success",
            "stage_status": {},
            "fixture": {"handle_out": hex(handle_out)},
            "return": observed[0][0],
            "events": [],
            "current_device": hex(0xc0ffee01),
            "handle": hex(observed[0][1]),
            "record": bytes(pair[0].cpu.mem_read(SLOT, 16)).hex(),
            "mspi_state_sha256": __import__("hashlib").sha256(
                bytes.fromhex(observed[0][2])).hexdigest(),
        })

    used = {int(pc, 0) + i for pc, raw in trace.items()
            for i in range(len(bytes.fromhex(raw)))}
    sources = [p for p in HERE.iterdir()
               if p.suffix in {".c", ".h", ".ld", ".py"}
               or p.name == "Makefile"]
    report = {
        "status": "PASS",
        "cases": len(cases),
        "comparisons": cases,
        "distinct_original_instruction_bytes": len(used),
        "original_trace": trace,
        "original_sha256": v.SHA,
        "elf_sha256": v.sha(args.elf),
        "source_sha256": {p.name: v.sha(p) for p in sources},
        "limits": [
            "Original 0x420254 and 0x424a5a instructions execute; HAL, MMIO/control, interrupt-priority, IRQ guard, and logging providers are synthetic exact-address cuts.",
            "The 12-byte base-config structure is passed to a synthetic configure provider; its fields and target TCB address are inspected, but the TCB is not DMA-accessed.",
            "The C source implements the fixed module-state constructor at 0x424a5a using synthetic RAM at the firmware's fixed state address; no hardware register writes are claimed.",
            "Only the listed success and failure paths are compared; no physical MSPI device, clock, interrupts, or flash are exercised.",
            "This slice is not a bootable image and does not claim full-source completion or byte-identical rebuild.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in
                      ("status", "cases", "distinct_original_instruction_bytes")}))


if __name__ == "__main__":
    main()
