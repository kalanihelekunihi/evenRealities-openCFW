#!/usr/bin/env python3
"""Run official scatter records into source startup and bounded main init."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
spec = importlib.util.spec_from_file_location("main_init_v", HERE / "verify_main_init.py")
mainv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mainv)
startup = mainv.startup
v = mainv.v
v.ENTRIES.update(system_entry=0x43297C, init_records_run=0x43299C,
                 vector_base_init=0x432910)

SLOT = 0x200004F4
SLOT_SENTINEL = 0xCCCCCCCC
SCATTER_INITIALIZED_SLOT = 0x42E39D
SLOT_TARGETS = [0x2003F001, 0x2003F101]
INIT_REGIONS = [
    (0x40, 24),
    (0x20000000, 1371),
    (0x2000055C, 0x26C6C),
    (0x20080000, 4096),
    (0x20081000, 0x74100),
]
EXPECTED_REGION_SHA256 = {
    0x40: "0676154418085b0630f2a20cc50fbbe3967dd2d9b7794fe1aad3f6af14f2fb83",
    0x20000000: "e3bea7ccd46bc324829152b5b5a9069aecce5db243876273084d29bd7d47b843",
    0x2000055C: "0ef445b0c24370d5770a5de60bfaa2d1a51a6c59788b222b6d9ab81c9eefd323",
    0x20080000: "ad7facb2586fc6e966c004d7d1d16b024f5805ff7cb47c7a85dabd8b48892ca7",
    0x20081000: "467cada3810e8ed4535c260186dc229bb66359356b5280f5170a92e7ddd7f04e",
}
TABLE = (0x4330D8, 0x433120)
COMPRESSED_INPUTS = [(0x434461, 22), (0x4341C0, 625), (0x434431, 48)]


class IntegratedMachine(mainv.MainInitMachine):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_entry = (self.symbols["opencfw_boot_main_init"] & ~1
                           if self.source else 0x41B862)
        self.slot_injected = False
        self.post_scatter_regions = None
        self.slot_before_injection = None
        self.main_entry_argument = None

    def code(self, uc, pc, size, user):
        if pc == self.main_entry:
            assert not self.slot_injected, "main initializer entered twice"
            self.main_entry_argument = self.args()[0]
            assert self.main_entry_argument == 0, hex(self.main_entry_argument)
            self.slot_before_injection = self.u(SLOT)
            assert self.slot_before_injection == SCATTER_INITIALIZED_SLOT, hex(self.slot_before_injection)
            self.post_scatter_regions = {
                address: bytes(self.cpu.mem_read(address, length))
                for address, length in INIT_REGIONS
            }
            self.w(SLOT, self.slot_target)
            self.slot_injected = True
        super().code(uc, pc, size, user)


def seed_source_inputs(machine, blob):
    if not machine.source:
        return
    table_start, table_end = TABLE
    machine.cpu.mem_write(table_start,
                          blob[table_start - v.BASE:table_end - v.BASE])
    for address, length in COMPRESSED_INPUTS:
        machine.cpu.mem_write(address,
                              blob[address - v.BASE:address - v.BASE + length])


def source_hashes():
    files = [
        HERE / "main_init.c", HERE / "main_init.h", HERE / "startup_integrated.ld",
        HERE / "verify_main_init.py", HERE / "verify_startup_integrated.py", HERE / "Makefile",
        ROOT / "g2/components/bootloader/startup/initialize.c",
        ROOT / "g2/components/bootloader/startup/initialize.h",
        ROOT / "g2/components/bootloader/startup/record_dispatch.c",
        ROOT / "g2/components/bootloader/startup/record_adapters.S",
        ROOT / "g2/components/bootloader/startup/system_entry.c",
    ]
    return {str(path.relative_to(ROOT)): v.sha(path) for path in files}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--elf", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    assert v.sha(v.BLOB) == v.SHA
    blob = v.BLOB.read_bytes()
    _, segments, symbols = v.elf.elf_info(args.elf)

    # Separate small LOAD segments keep fixed strings and the relocated
    # callback adapters from creating a large synthetic ELF memory interval.
    for segment in segments:
        assert segment["memory_size"] < 0x10000, segment

    trace, cases = {}, []
    for mode_result in [0, 7]:
        for slot_target in SLOT_TARGETS:
            machines = [IntegratedMachine(),
                        IntegratedMachine(True, segments, symbols)]
            for machine in machines:
                machine.mode_result = mode_result
                machine.slot_target = slot_target
                machine.w(SLOT, SLOT_SENTINEL)
                for address, length in INIT_REGIONS:
                    machine.cpu.mem_write(address, b"\xcc" * length)
                machine.cpu.reg_write(v.a.UC_ARM_REG_R9, 0)
                seed_source_inputs(machine, blob)

            results = [machine.run("system_entry", []) for machine in machines]
            assert all(machine.slot_injected for machine in machines)
            assert all(machine.u(SLOT) == slot_target for machine in machines)
            assert results[0]["events"] == results[1]["events"]
            assert results[0]["events"] == mainv.expected_events(mode_result, slot_target), (
                mode_result, hex(slot_target), results[0]["events"]
            )

            region_reports = []
            for address, length in INIT_REGIONS:
                stock = machines[0].post_scatter_regions[address]
                source = machines[1].post_scatter_regions[address]
                assert stock == source, hex(address)
                digest = hashlib.sha256(stock).hexdigest()
                assert digest == EXPECTED_REGION_SHA256[address], (hex(address), digest)
                if address in {0x2000055C, 0x20081000}:
                    assert stock == b"\0" * length, hex(address)
                region_reports.append({
                    "address": hex(address), "bytes": length, "sha256": digest,
                })

            trace.update(machines[0].trace)
            cases.append({
                "entry": "0x43297c",
                "mode_status": mode_result,
                "main_init_argument": machines[0].main_entry_argument,
                "slot_sentinel_before_scatter": hex(SLOT_SENTINEL),
                "slot_value_after_scatter_before_injection": hex(machines[0].slot_before_injection),
                "slot_target_injected_at_main_entry": hex(slot_target),
                "ram_after_scatter_before_slot_injection": region_reports,
                "calls_through_terminal_spin": results[0]["events"],
            })

    used = {
        int(pc, 0) + offset
        for pc, raw in trace.items()
        for offset in range(len(bytes.fromhex(raw)))
    }
    report = {
        "status": "PASS",
        "cases": len(cases),
        "distinct_original_trace_bytes": len(used),
        "original_trace": trace,
        "original_sha256": v.SHA,
        "elf_sha256": v.sha(args.elf),
        "compiler_profile": "Cortex-M4 compatibility build for offline Unicorn; this is not a hardware or target-compiler claim.",
        "source_sha256": source_hashes(),
        "comparisons": cases,
        "synthetic_provider_entries": [
            "0x41f9d8", "0x41f9f8", "0x41f846", "0x41ac44", "0x41ac5a",
            "0x41fa50", "0x41e1e8", "0x41e266", "0x41ba80", "0x415fae",
            "0x41fd70", "0x420476", "0x421210", "0x4176ce",
            "fixture callback targets 0x2003f000 and 0x2003f100",
        ],
        "limits": [
            "Original execution starts at 0x43297C, traverses real vector-base and scatter dispatch/helper instructions, reaches real 0x41B862, then runs the bounded source-matched dispatcher to its spin loop.",
            "The valid scatter table and three compressed payload streams are authenticated fixture inputs; they are not reconstructed compressed source data. Source-defined dispatcher strings are separate fixed-address ELF load segments.",
            "The callback slot at 0x200004F4 is seeded with a sentinel before scatter init and overwritten by a fixture observer only at main-init entry after all scatter work; neither startup source chain writes the slot.",
            "The Cortex-M55 build of startup helpers emits low-overhead-loop instructions that this Unicorn profile rejects; only the separate Cortex-M4 compatibility ELF is used for the end-to-end emulation.",
            "Init-table/platform services, mode-status provider, allocator, NOR/MSPI, filesystem, loggers and indirect callback are synthetic cuts. No allocator contents, peripheral effects, filesystem state, or actual runtime callback behavior are established.",
            "Only valid locked scatter records and mode statuses 0 and 7 are exercised. This does not establish full bootloader source coverage, byte identity, physical hardware behavior, or a complete boot claim.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in
                      ["status", "cases", "distinct_original_trace_bytes"]}))


if __name__ == "__main__":
    main()
