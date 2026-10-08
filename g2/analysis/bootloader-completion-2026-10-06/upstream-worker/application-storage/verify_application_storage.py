#!/usr/bin/env python3
"""Call locked descriptor callbacks through stock/source startup state."""
import argparse
import hashlib
import importlib.util
import json
import struct
from pathlib import Path
from unicorn import UC_HOOK_MEM_WRITE

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
COMPONENTS = ROOT / "g2/components/bootloader"
spec = importlib.util.spec_from_file_location(
    "platform_startup_v",
    ROOT / "g2/analysis/bootloader-completion-2026-10-06/upstream-worker/platform-startup/verify_platform_startup.py",
)
pv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pv)
v = pv.v

DESCRIPTOR_POINTER = 0x200004F0
DESCRIPTOR_FIELDS = {"read": 0x18, "program": 0x1C, "erase_validate": 0x20}
RANGE_CACHE = 0x200270C8
RANGE_REGISTER = 0x40020014
ROM_ENTRY = 0x0200FF20
ROM_DATA = 0x20010000
LIMITS = [0x100000, 0x200000, 0x300000, 0x400000]


class StorageMachine(pv.PlatformMachine):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cpu.mem_map(0x000FF000, 0x1000)
        self.cpu.mem_map(0x40014000, 0x1000)
        self.cpu.mem_map(0x40020000, 0x1000)
        self.cpu.mem_map(0x0200F000, 0x1000)
        self.range_provider_calls = []
        self.rom_calls = []
        self.storage_mmio_writes = []
        self.rom_status = 0
        self.cpu.hook_add(UC_HOOK_MEM_WRITE, self.storage_write,
                          begin=0x40014000, end=0x40014027)

    def storage_write(self, uc, access, address, size, value, user):
        self.storage_mmio_writes.append([hex(address), size, value & 0xFFFFFFFF])

    def code(self, uc, pc, size, user):
        if pc == 0x41D792:
            r0, r1, _, _ = self.args()
            assert r0 == 1, (hex(pc), self.args())
            mode = (self.u(RANGE_REGISTER) >> 2) & 3
            table_word = struct.unpack("<H", uc.mem_read(0x43401C + 2 * mode, 2))[0]
            bound = table_word << 10
            self.w(r1 + 0x2C, bound)
            self.range_provider_calls.append({"mode": mode, "bound": bound})
            self.ret(0)
            return
        if pc == ROM_ENTRY:
            r0, r1, r2, r3 = self.args()
            words = self.u(uc.reg_read(v.a.UC_ARM_REG_SP))
            assert words <= 0x4000
            self.rom_calls.append({
                "key": hex(r0), "operation": r1, "source": hex(r2),
                "word_offset": hex(r3), "word_count": words,
                "source_bytes": bytes(uc.mem_read(r2, words * 4)).hex()
                if words else "",
                "status": hex(self.rom_status),
            })
            self.ret(self.rom_status)
            return
        super().code(uc, pc, size, user)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def call_descriptor_callback(machine, field, arguments):
    descriptor = machine.u(DESCRIPTOR_POINTER)
    callback = machine.u(descriptor + DESCRIPTOR_FIELDS[field])
    assert callback == {
        "read": 0x430A9D,
        "program": 0x430AC5,
        "erase_validate": 0x430AED,
    }[field], (field, hex(callback))
    machine.events.clear()
    machine.mmio_writes.clear()
    machine.storage_mmio_writes.clear()
    machine.range_provider_calls.clear()
    machine.rom_calls.clear()
    machine.w(RANGE_CACHE, 0)
    machine.w(RANGE_REGISTER, arguments.pop("mode", 0) << 2)
    machine.w(0x200271A7, 0)  # gate power-control callback in source MRAM guard
    machine.rom_status = arguments.pop("rom_status", 0)
    if "source_bytes" in arguments:
        raw = bytes.fromhex(arguments.pop("source_bytes"))
        machine.cpu.mem_write(ROM_DATA, raw)
    if "read_bytes" in arguments:
        raw = bytes.fromhex(arguments.pop("read_bytes"))
        read_address = arguments.pop("read_address")
        machine.cpu.mem_write(read_address, raw)
    if "read_zero_size" in arguments:
        read_address = arguments.pop("read_address")
        machine.cpu.mem_write(read_address,
                              b"\0" * arguments.pop("read_zero_size"))
    if "argument" in arguments:
        values = [arguments.pop("argument")]
    else:
        values = [arguments.pop(name) for name in ("arg0", "arg1", "arg2")]
    machine.finished = False
    for register, value in zip((v.a.UC_ARM_REG_R0, v.a.UC_ARM_REG_R1,
                                v.a.UC_ARM_REG_R2), values):
        machine.cpu.reg_write(register, value)
    machine.cpu.reg_write(v.a.UC_ARM_REG_R3, 0)
    machine.cpu.reg_write(v.a.UC_ARM_REG_SP, v.SP)
    machine.cpu.reg_write(v.a.UC_ARM_REG_LR, v.STOP | 1)
    entry = (callback & ~1)
    machine.cpu.emu_start(entry | 1, v.STOP + 2, count=2_000_000)
    assert machine.finished, (machine.source, field,
                              hex(machine.cpu.reg_read(v.a.UC_ARM_REG_PC)))
    return {
        "return": hex(machine.cpu.reg_read(v.a.UC_ARM_REG_R0)),
        "range_limit_after": hex(machine.u(RANGE_CACHE)),
        "range_provider_calls": list(machine.range_provider_calls),
        "rom_calls": list(machine.rom_calls),
        "mram_cleanup_writes": list(machine.storage_mmio_writes),
        "primask": machine.cpu.reg_read(v.a.UC_ARM_REG_PRIMASK),
        "read_destination": bytes(machine.cpu.mem_read(0x20010000, 16)).hex(),
        "power_control_cut_calls": machine.u(
            machine.symbols["opencfw_test_power_control_calls"]
            if machine.source else 0xFFFFFFFF
        ) if machine.source else 0,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--elf", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    assert v.sha(v.BLOB) == v.SHA
    blob = v.BLOB.read_bytes()
    _, segments, symbols = v.elf.elf_info(args.elf)
    for entry in ("opencfw_boot_storage_read", "opencfw_boot_storage_program",
                  "opencfw_boot_storage_erase_validate"):
        assert symbols[entry] & ~1 in (0x430A9C, 0x430AC4, 0x430AEC)

    cases, trace = [], {}
    startup_pair = [StorageMachine(), StorageMachine(True, segments, symbols)]
    for machine in startup_pair:
        machine.mode_result = 0
        machine.slot_target = 0x2003F001
        machine.w(pv.iv.SLOT, pv.iv.SLOT_SENTINEL)
        for address, length in pv.iv.INIT_REGIONS:
            machine.cpu.mem_write(address, b"\xcc" * length)
        machine.cpu.reg_write(v.a.UC_ARM_REG_R9, 0)
        pv.iv.seed_source_inputs(machine, blob)
    startup_results = [machine.run("system_entry", []) for machine in startup_pair]
    assert startup_results[0]["events"] == startup_results[1]["events"]
    assert startup_pair[0].post_scatter_regions == startup_pair[1].post_scatter_regions
    descriptor = startup_pair[0].u(DESCRIPTOR_POINTER)
    assert descriptor == startup_pair[1].u(DESCRIPTOR_POINTER) == 0x200001E8
    descriptor_bytes = [bytes(machine.cpu.mem_read(descriptor, 64)).hex()
                        for machine in startup_pair]
    assert descriptor_bytes[0] == descriptor_bytes[1]
    callbacks = [
        [hex(startup_pair[0].u(descriptor + offset)) for offset in (0x18, 0x1C, 0x20)],
        [hex(startup_pair[1].u(descriptor + offset)) for offset in (0x18, 0x1C, 0x20)],
    ]
    assert callbacks[0] == callbacks[1] == ["0x430a9d", "0x430ac5", "0x430aed"]
    trace.update(startup_pair[0].trace)

    def check(name, field, fixture):
        results = [call_descriptor_callback(machine, field, dict(fixture))
                   for machine in startup_pair]
        original_limit_cut = results[0].pop("range_provider_calls")
        source_limit_reads = results[1].pop("range_provider_calls")
        assert source_limit_reads == [], (name, fixture, source_limit_reads)
        assert results[0] == results[1], (name, fixture, results)
        trace.update(startup_pair[0].trace)
        if startup_pair[1].source:
            assert startup_pair[1].u(symbols["opencfw_test_power_control_calls"]) == 0
            assert startup_pair[1].u(
                symbols["opencfw_test_accepted_power_object_calls"]
            ) == 0
        cases.append({"case": name, "callback": field,
                      "fixture": fixture,
                      "original_range_helper_cut": original_limit_cut,
                      "result": results[0]})

    for mode, limit in enumerate(LIMITS):
        check(f"erase-below-minimum-mode-{mode}", "erase_validate",
              {"argument": 0x3FFC, "mode": mode})
        check(f"erase-minimum-address-mode-{mode}", "erase_validate",
              {"argument": 0x4000, "mode": mode})

    check("read-final-16-bytes-under-limit", "read", {
        "arg0": 0x20010000, "arg1": 0x00004010, "arg2": 16,
        "mode": 0, "read_address": 0x4010,
        "read_bytes": bytes(range(16)).hex(),
    })
    check("read-below-minimum-address", "read", {
        "arg0": 0x20010000, "arg1": 0x00003FFF, "arg2": 16, "mode": 0,
    })
    check("read-16k-below-mode-size-limit", "read", {
        "arg0": 0x20010000, "arg1": 0x00005000, "arg2": 0x4000,
        "mode": 0, "read_address": 0x5000, "read_zero_size": 0x4000,
    })
    check("read-mode-size-limit", "read", {
        "arg0": 0x20010000, "arg1": 0x00005000, "arg2": LIMITS[2],
        "mode": 2,
    })
    check("read-zero-length", "read", {
        "arg0": 0x20010000, "arg1": 0x00005000, "arg2": 0, "mode": 0,
    })

    check("program-valid-rom-success", "program", {
        "arg0": 0x00004000, "arg1": ROM_DATA, "arg2": 16,
        "mode": 3, "rom_status": 0,
        "source_bytes": bytes(range(16)).hex(),
    })
    check("program-valid-rom-error-ignored", "program", {
        "arg0": 0x00004000, "arg1": ROM_DATA, "arg2": 16,
        "mode": 3, "rom_status": 0xFFFFFFFF,
        "source_bytes": bytes(range(16)).hex(),
    })
    check("program-size-limit", "program", {
        "arg0": 0x00004000, "arg1": ROM_DATA, "arg2": LIMITS[3], "mode": 3,
    })
    check("program-misaligned-destination", "program", {
        "arg0": 0x00004002, "arg1": ROM_DATA, "arg2": 16, "mode": 3,
    })
    check("program-below-minimum-address", "program", {
        "arg0": 0x00003FFF, "arg1": ROM_DATA, "arg2": 16, "mode": 3,
    })
    check("program-address-high", "program", {
        "arg0": 0xFFFFFFF8, "arg1": ROM_DATA, "arg2": 16, "mode": 3,
    })

    used = {
        int(pc, 0) + offset
        for pc, raw in trace.items()
        for offset in range(len(bytes.fromhex(raw)))
    }
    files = [
        COMPONENTS / "application_storage/storage_callbacks.c",
        COMPONENTS / "application_storage/storage_callbacks.h",
        COMPONENTS / "application_storage/storage_callback_veneers.S",
        COMPONENTS / "platform_control/control.c",
        COMPONENTS / "platform_control/power_guards.c",
        COMPONENTS / "platform_control/mram_rom_bridge.c",
        COMPONENTS / "platform_control/critical_save.S",
        COMPONENTS / "platform_startup/platform_startup.c",
        COMPONENTS / "platform_control/runtime.c",
        COMPONENTS / "clock_manager/clock_class_providers.c",
        HERE / "test_cuts.c", HERE / "application_storage.ld",
        HERE / "verify_application_storage.py",
    ]
    report = {
        "status": "PASS",
        "cases": len(cases),
        "distinct_original_trace_bytes": len(used),
        "original_sha256": v.SHA,
        "elf_sha256": sha(args.elf),
        "source_sha256": {str(path.relative_to(ROOT)): sha(path) for path in files},
        "scatter_descriptor": {
            "address": hex(descriptor), "raw_64_bytes": descriptor_bytes[0],
            "callback_fields": {name: callbacks[0][index]
                                 for index, name in enumerate(DESCRIPTOR_FIELDS)},
        },
        "callback_source_addresses": {
            "read": hex(symbols["opencfw_boot_storage_read"] & ~1),
            "program": hex(symbols["opencfw_boot_storage_program"] & ~1),
            "erase_validate": hex(symbols["opencfw_boot_storage_erase_validate"] & ~1),
        },
        "range_limit_bytes_by_mode": [hex(value) for value in LIMITS],
        "comparisons": cases,
        "limits": [
            "The callback pointers are read from the exact descriptor published by startup scatter at 0x200001e8; the source ELF replaces the three callback entry addresses with four-byte C-source veneers.",
            "For original execution only, 0x41d792 is cut at the single output field consumed by 0x430a60: stack+0x2c receives the value selected by synthetic 0x40020014 bits[3:2] and the locked halfword table 0x43401c. Its unrelated power-status construction and repeated delay calls are not modeled. Source derives the same selected field directly and maintains cache 0x200270c8.",
            "The public/control source is executed through 0x42e4f4/0x42e4a0 and stock 0x42e8a4; only the external ROM service 0x0200ff20 is stubbed with controlled status. Its register cleanup executes on both sides. No physical MRAM programming is claimed.",
            "The descriptor +0x20 callback only validates a 4-byte range and returns 0 or -1; it performs no erase operation.",
            "The raw range helper computes 32-bit `address + size - 1` but does not consume it; it accepts when the original address is at least 0x4000 and size is strictly below the cached mode-selected limit. Tests cover both independent comparisons, zero-size behavior, and program-word alignment rejection.",
            "ROM guard-enabled power control is set to zero in the fixture; no hardware acknowledgement, delay timing, flash coherence, cache behavior, or device write is modeled.",
            "This focused callback/profile comparison is not a full source rebuild or byte-identity result.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({key: report[key] for key in
                      ("status", "cases", "distinct_original_trace_bytes")}, indent=2))


if __name__ == "__main__":
    main()
