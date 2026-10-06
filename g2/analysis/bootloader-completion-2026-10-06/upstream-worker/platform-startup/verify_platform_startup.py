#!/usr/bin/env python3
"""Compare stock 0x41f846 with the source provider after true scatter init."""
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
    "startup_integrated_v", COMPONENTS / "main_init/verify_startup_integrated.py"
)
iv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(iv)
v = iv.v

# Let the original 0x41f846 execute; the source ELF binds the same call to the
# separately compiled source function instead of a fixed-address trampoline.
iv.mainv.PROVIDERS.remove(0x41F846)

class PlatformMachine(iv.IntegratedMachine):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cpu.mem_map(0x40010000, 0x1000)
        self.mmio_writes = []
        self.cpu.hook_add(UC_HOOK_MEM_WRITE, self.on_write, begin=0x40010000,
                          end=0x40010403)

    def on_write(self, uc, access, address, size, value, user):
        self.mmio_writes.append([hex(address), size, value & 0xffffffff])


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def invoke_configure(machine, argument):
    machine.finished = False
    machine.cpu.reg_write(v.a.UC_ARM_REG_R0, argument)
    machine.cpu.reg_write(v.a.UC_ARM_REG_SP, v.SP)
    machine.cpu.reg_write(v.a.UC_ARM_REG_LR, v.STOP | 1)
    entry = (machine.symbols["opencfw_boot_platform_configure"] & ~1
             if machine.source else 0x41F846)
    machine.cpu.emu_start(entry | 1, v.STOP + 2, count=100000)
    assert machine.finished, (machine.source, hex(argument),
                              hex(machine.cpu.reg_read(v.a.UC_ARM_REG_PC)))
    return machine.cpu.reg_read(v.a.UC_ARM_REG_R0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--elf", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    assert v.sha(v.BLOB) == v.SHA
    blob = v.BLOB.read_bytes()
    _, segments, symbols = v.elf.elf_info(args.elf)

    cases, trace = [], {}
    for mode_result in (0, 7):
        machines = [PlatformMachine(), PlatformMachine(True, segments, symbols)]
        for machine in machines:
            machine.mode_result = mode_result
            machine.slot_target = 0x2003F001
            machine.w(iv.SLOT, iv.SLOT_SENTINEL)
            for address, length in iv.INIT_REGIONS:
                machine.cpu.mem_write(address, b"\xcc" * length)
            machine.cpu.reg_write(v.a.UC_ARM_REG_R9, 0)
            iv.seed_source_inputs(machine, blob)

        results = [machine.run("system_entry", []) for machine in machines]
        assert all(machine.slot_injected for machine in machines)
        assert machines[0].post_scatter_regions == machines[1].post_scatter_regions
        rows = machines[0].post_scatter_regions[0x20000000]
        assert struct.unpack_from("<7I", rows, 0x454) == (0, 0, 0, 0, 0, 0, 0)
        assert struct.unpack_from("<7I", rows, 0x470) == (
            1, 0, 0x433D98, 0x200003F4, 0x20000424, 0, 0
        )
        assert struct.unpack_from("<7I", rows, 0x48C) == (
            2, 0, 0x433DA8, 0x20000404, 0x20000434, 0, 0
        )
        assert struct.unpack_from("<7I", rows, 0x4A8) == (
            3, 0, 0x433DB8, 0x20000414, 0x20000444, 0, 0
        )
        assert machines[0].u(0x200004F0) == 0x200001E8
        assert machines[1].u(0x200004F0) == 0x200001E8
        assert machines[0].u(0x200001E8) == 0x00001000
        assert machines[1].u(0x200001E8) == 0x00001000

        event_lists = [result["events"] for result in results]
        # 0x41f846 is no longer a synthetic event; both executions run its
        # implementation and must continue through the same downstream cuts.
        expected = iv.mainv.expected_events(mode_result, 0x2003F001)
        expected = [event for event in expected if event[0] != "0x41f846"]
        assert event_lists[0] == event_lists[1] == expected

        for machine in machines:
            assert machine.u(0x20000488) == 1
            assert machine.u(0x200004F0) == 0x200001E8
            assert machine.u(0x40010038) == 5, (machine.source, machine.mmio_writes,
                                                  hex(machine.u(0x40010038)))
            assert machine.u(0x40010030) == 5, (machine.source, machine.mmio_writes,
                                                  hex(machine.u(0x40010030)))
            assert machine.u(0x40010400) == 0  # update latch is closed
        assert machines[0].mmio_writes == machines[1].mmio_writes
        assert machines[0].mmio_writes == [
            ["0x40010400", 4, 115], ["0x40010038", 4, 5],
            ["0x40010400", 4, 0], ["0x40010400", 4, 115],
            ["0x40010030", 4, 5], ["0x40010400", 4, 0],
        ]
        assert machines[0].cpu.reg_read(v.a.UC_ARM_REG_PRIMASK) == 0
        assert machines[1].cpu.reg_read(v.a.UC_ARM_REG_PRIMASK) == 0

        direct_cases = []
        for selector in (0, 1, 2, 3, 4, 0x101):
            machines[0].mmio_writes.clear()
            machines[1].mmio_writes.clear()
            returns = [invoke_configure(machine, selector) for machine in machines]
            assert returns[0] == returns[1], (selector, returns)
            assert machines[0].mmio_writes == machines[1].mmio_writes, (
                selector, machines[0].mmio_writes, machines[1].mmio_writes
            )
            assert bytes(machines[0].cpu.mem_read(0x20000454, 0x70)) == bytes(
                machines[1].cpu.mem_read(0x20000454, 0x70)
            )
            assert bytes(machines[0].cpu.mem_read(0x40010000, 0x404)) == bytes(
                machines[1].cpu.mem_read(0x40010000, 0x404)
            )
            assert machines[0].cpu.reg_read(v.a.UC_ARM_REG_PRIMASK) == 0
            assert machines[1].cpu.reg_read(v.a.UC_ARM_REG_PRIMASK) == 0
            if machines[1].source:
                cut_counter = symbols["opencfw_test_accepted_power_object_calls"]
                assert machines[1].u(cut_counter) == 0
            direct_cases.append({
                "argument": hex(selector), "return": hex(returns[0]),
                "register_writes": list(machines[0].mmio_writes),
                "source_accepted_object_cut_calls": 0,
            })

        trace.update(machines[0].trace)
        cases.append({
            "mode_status": mode_result,
            "scatter_row_table_address": "0x20000454",
            "row1_before_call": [hex(x) for x in struct.unpack_from("<7I", rows, 0x470)],
            "row1_after_call": [hex(machines[0].u(0x20000470 + i * 4))
                                 for i in range(7)],
            "scatter_descriptor_pointer": "0x200001e8",
            "power_object_argument": "NULL",
            "power_apply_status": 2,
            "power_apply_accepted_object_cut_calls": 0,
            "register_writes": machines[0].mmio_writes,
            "direct_selector_cases": direct_cases,
            "downstream_main_events": event_lists[0],
        })

    used = {
        int(pc, 0) + offset
        for pc, raw in trace.items()
        for offset in range(len(bytes.fromhex(raw)))
    }
    init_array = blob[0x433440 - v.BASE:0x433460 - v.BASE]
    rows = [struct.unpack_from("<II", init_array, offset)
            for offset in range(0, len(init_array), 8)]
    files = [COMPONENTS / "platform_startup/platform_startup.c",
             COMPONENTS / "platform_startup/platform_startup.h",
             COMPONENTS / "platform_control/runtime.c",
             COMPONENTS / "clock_manager/clock_class_providers.c",
             COMPONENTS / "main_init/main_init.c",
             COMPONENTS / "startup/initialize.c",
             COMPONENTS / "startup/record_dispatch.c",
             COMPONENTS / "startup/record_adapters.S",
             COMPONENTS / "startup/system_entry.c",
             HERE / "verify_platform_startup.py", HERE / "platform_startup.ld",
             HERE / "provider_cuts.c"]
    report = {
        "status": "PASS",
        "cases": len(cases),
        "distinct_original_trace_bytes": len(used),
        "original_sha256": v.SHA,
        "elf_sha256": digest(args.elf),
        "source_sha256": {str(path.relative_to(ROOT)): digest(path) for path in files},
        "source_machine_exec_ranges": [
            [hex(lo), hex(hi)] for lo, hi in machines[1].exec_ranges
        ],
        "comparisons": cases,
        "scalar_config_table": {
            "address": "0x433d98", "words": [12, 14, 5, 5,
                                                   42, 44, 4, 4,
                                                   73, 69, 5, 5],
            "sha256": hashlib.sha256(
                struct.pack("<12I", 12, 14, 5, 5, 42, 44, 4, 4, 73, 69, 5, 5)
            ).hexdigest(),
            "compiled_source_address": hex(symbols["opencfw_boot_platform_config_table"]),
        },
        "original_trace": trace,
        "constructor_array": {
            "address": "0x433440", "bytes": len(init_array),
            "sha256": hashlib.sha256(init_array).hexdigest(),
            "entries": [[hex(function), hex(order)] for function, order in rows],
            "interpretation": "Four function-pointer/order records consumed by 0x41f9f8; they are distinct from the 0x20000454 scatter-initialized platform rows.",
        },
        "limits": [
            "The exact authenticated compressed scatter inputs initialize the source and stock RAM profile; those compressed bytes are fixtures, not rebuilt firmware source.",
            "Only selector 1 is reached by main and compared. The provider implements selector truncation/invalid behavior from instructions, but this startup-level fixture does not exhaust all four selectors.",
            "The authentic selector-1 row has a null power object; stock 0x422ba8 returns 2 and 0x41f846 ignores that status after performing both register updates and setting row flag +0x18.",
            "The accepted-object continuation is a guarded test cut and is proven unreachable for the authentic scatter state; no accepted-object power setup is claimed.",
            "MMIO is synthetic mapped memory. The compile profile is Cortex-M4 for Unicorn compatibility, not IAR or hardware validation.",
            "The nearby 0x41f9f8 constructor runner's indirect callbacks and 0x41fa50 service chain remain separate cuts; neither produces the platform row table in the observed scatter output.",
            "This bounded source provider does not establish whole-image source completeness or byte identity.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({key: report[key] for key in
                      ("status", "cases", "distinct_original_trace_bytes")}, indent=2))


if __name__ == "__main__":
    main()
