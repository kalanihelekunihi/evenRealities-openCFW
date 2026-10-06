#!/usr/bin/env python3
"""Run source scatter startup through the callback actually published at 42E39D."""
import argparse
import hashlib
import importlib.util
import json
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
main_spec = importlib.util.spec_from_file_location(
    "main_init_v", ROOT / "g2/components/bootloader/main_init/verify_main_init.py"
)
mainv = importlib.util.module_from_spec(main_spec)
main_spec.loader.exec_module(mainv)
startup = mainv.startup
v = mainv.v
v.ENTRIES.update(system_entry=0x43297C, init_records_run=0x43299C,
                 vector_base_init=0x432910)

SLOT = 0x200004F4
HANDLE = 0x200004FC
PUBLISHED_CALLBACK = 0x42E39D
CALLBACK_ENTRY = 0x42E39C
THREAD_ENTRY = 0x42E2F9
ATTRIBUTES = 0x433024
MANAGER_NAME = 0x434134
CALLBACK_PROVIDERS = {0x416058, 0x4160FE, 0x4160B0, 0x41B2F8}
ATTRIBUTE_WORDS = [0x434134, 0, 0x20026AC0, 0x70, 0x20018AA0,
                   0x4000, 0x30, 1, 0]
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
SLOT_SENTINEL = 0xCCCCCCCC


class StartupCallbackMachine(mainv.MainInitMachine):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_entry = (self.symbols["opencfw_boot_main_init"] & ~1
                           if self.source else 0x41B862)
        self.callback_seen = False
        self.callback_slot_at_entry = None
        self.ram_after_scatter = None
        self.main_entry_argument = None
        self.created_handle = 0x51

    def code(self, uc, pc, size, user):
        if pc == self.main_entry:
            assert self.main_entry_argument is None, "main initializer entered twice"
            self.main_entry_argument = self.args()[0]
            assert self.main_entry_argument == 0
            self.callback_slot_at_entry = self.u(SLOT)
            assert self.callback_slot_at_entry == PUBLISHED_CALLBACK, hex(
                self.callback_slot_at_entry)
            self.ram_after_scatter = {
                address: bytes(self.cpu.mem_read(address, length))
                for address, length in INIT_REGIONS
            }

        if pc == CALLBACK_ENTRY:
            assert not self.callback_seen, "manager callback executed twice"
            self.callback_seen = True
            assert self.u(SLOT) == PUBLISHED_CALLBACK
            self.events.append(["callback-entry-from-slot", self.u(SLOT)])

        if pc in CALLBACK_PROVIDERS:
            r0, r1, r2, r3 = self.args()
            if pc == 0x416058:
                self.events.append(["0x416058"])
            elif pc == 0x4160FE:
                assert [r0, r1, r2] == [THREAD_ENTRY, 0, ATTRIBUTES]
                words = list(struct.unpack("<9I", bytes(uc.mem_read(r2, 36))))
                assert words == ATTRIBUTE_WORDS
                assert bytes(uc.mem_read(MANAGER_NAME, 8)) == b"manager\0"
                self.events.append(["0x4160fe", r0, r1, r2, words])
                self.ret(self.created_handle)
            elif pc == 0x4160B0:
                self.events.append(["0x4160b0"])
            else:
                raise AssertionError("failure provider was reached in success fixture")
            if pc != 0x4160FE:
                self.ret()
            return
        super().code(uc, pc, size, user)


def seed_source_inputs(machine, blob):
    if machine.source:
        assert bytes(machine.cpu.mem_read(TABLE[0], TABLE[1] - TABLE[0])) == blob[
            TABLE[0] - v.BASE:TABLE[1] - v.BASE]
        for address, length in COMPRESSED_INPUTS:
            machine.cpu.mem_write(
                address, blob[address - v.BASE:address - v.BASE + length])


def callback_events():
    return [
        ["callback-entry-from-slot", PUBLISHED_CALLBACK],
        ["0x416058"],
        ["0x4160fe", THREAD_ENTRY, 0, ATTRIBUTES, ATTRIBUTE_WORDS],
        ["0x4160b0"],
    ]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--elf", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    assert v.sha(v.BLOB) == v.SHA
    blob = v.BLOB.read_bytes()
    _, segments, symbols = v.elf.elf_info(args.elf)
    for segment in segments:
        assert segment["memory_size"] < 0x10000, segment
    assert (symbols["opencfw_boot_main_callback"] & ~1) == CALLBACK_ENTRY

    trace, comparisons = {}, []
    for mode_status in [0, 7]:
        for created_handle in [1, 0x51]:
            machines = [StartupCallbackMachine(),
                        StartupCallbackMachine(True, segments, symbols)]
            for machine in machines:
                machine.mode_result = mode_status
                machine.created_handle = created_handle
                machine.w(SLOT, SLOT_SENTINEL)
                for address, length in INIT_REGIONS:
                    machine.cpu.mem_write(address, b"\xcc" * length)
                machine.cpu.reg_write(v.a.UC_ARM_REG_R9, 0)
                seed_source_inputs(machine, blob)

            results = [machine.run("system_entry", []) for machine in machines]
            assert all(machine.callback_seen for machine in machines)
            assert all(machine.u(SLOT) == PUBLISHED_CALLBACK for machine in machines)
            assert all(machine.u(HANDLE) == created_handle for machine in machines)
            assert results[0]["events"] == results[1]["events"], (
                mode_status, created_handle, results[0]["events"],
                results[1]["events"])
            expected = mainv.expected_events(mode_status, 0x2003F001)
            expected = expected[:-2] + callback_events() + [["terminal-spin"]]
            assert results[0]["events"] == expected, (
                mode_status, created_handle, results[0]["events"], expected)

            ram_reports = []
            for address, length in INIT_REGIONS:
                original = machines[0].ram_after_scatter[address]
                source = machines[1].ram_after_scatter[address]
                assert original == source, hex(address)
                digest = hashlib.sha256(original).hexdigest()
                assert digest == EXPECTED_REGION_SHA256[address], (
                    hex(address), digest)
                ram_reports.append({
                    "address": hex(address), "bytes": length,
                    "sha256": digest,
                })
            trace.update(machines[0].trace)
            comparisons.append({
                "mode_status": mode_status,
                "manager_handle": hex(created_handle),
                "scatter_callback_slot": hex(machines[0].callback_slot_at_entry),
                "callback_entry": hex(CALLBACK_ENTRY),
                "post_scatter_ram": ram_reports,
                "calls_through_terminal_spin": results[0]["events"],
            })

    used = {
        int(pc, 0) + offset
        for pc, raw in trace.items()
        for offset in range(len(bytes.fromhex(raw)))
    }
    source_files = [
        HERE / "main_callback.c", HERE / "main_callback.h",
        HERE / "module.ld", HERE / "startup_callback_integrated.ld",
        HERE / "verify_main_callback.py", HERE / "verify_startup_callback_integrated.py",
        HERE / "Makefile",
        ROOT / "g2/components/bootloader/startup/initialize.c",
        ROOT / "g2/components/bootloader/startup/initialize.h",
        ROOT / "g2/components/bootloader/startup/record_dispatch.c",
        ROOT / "g2/components/bootloader/startup/record_adapters.S",
        ROOT / "g2/components/bootloader/startup/system_entry.c",
        ROOT / "g2/components/bootloader/startup/init_records.S",
        ROOT / "g2/components/bootloader/startup/records_table.ld",
        ROOT / "g2/components/bootloader/main_init/main_init.c",
        ROOT / "g2/components/bootloader/main_init/verify_main_init.py",
    ]
    report = {
        "status": "PASS",
        "cases": len(comparisons),
        "distinct_original_trace_bytes": len(used),
        "original_sha256": v.SHA,
        "elf_sha256": v.sha(args.elf),
        "source_sha256": {
            str(path.relative_to(ROOT)): v.sha(path) for path in source_files
        },
        "source_record_table": {
            "address": hex(TABLE[0]), "bytes": TABLE[1] - TABLE[0],
            "sha256": hashlib.sha256(blob[TABLE[0] - v.BASE:
                                           TABLE[1] - v.BASE]).hexdigest(),
        },
        "original_trace": trace,
        "comparisons": comparisons,
        "synthetic_providers": [
            "main-init platform/allocator/NOR/filesystem/log providers from the bounded main-init profile",
            "0x416058 (context setup), 0x4160FE (creator returns a fixture handle), 0x4160B0 (post-creation setup)",
            "compressed payload spans at 0x434461/22, 0x4341C0/625, 0x434431/48 are authenticated fixture inputs",
        ],
        "limits": [
            "Original execution begins at system entry 0x43297C, executes vector-base and source-defined 72-byte scatter-table dispatch/helpers, initializes RAM, calls the actual slot value 0x42E39D, runs callback source placed at 0x42E39C, returns through main init, and reaches terminal spin.",
            "The callback context handle is stored at 0x200004FC (+8 from the scatter-published callback slot at 0x200004F4). The callback pointer is not replaced by a synthetic target.",
            "The 72-byte scatter table and manager attribute/name record are source-defined. Three compressed payload spans remain authenticated fixture inputs, not source-reconstructed compression streams.",
            "Main-init services and callback runtime providers are synthetic cuts; no task scheduling, manager callback body at 0x42E2F9, allocator state, NOR/MSPI, filesystem state, or physical hardware behavior is established.",
            "Only valid scatter inputs, mode statuses 0 and 7, and successful manager creation handles are exercised end-to-end; callback allocation failure is tested separately in comparison-first.json.",
            "Cortex-M4 compatibility ELF is used for offline Unicorn; this is not a Cortex-M55 hardware or byte-identity claim. Full bootloader source completeness is not claimed.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({key: report[key] for key in
                      ["status", "cases", "distinct_original_trace_bytes"]}))


if __name__ == "__main__":
    main()
