#!/usr/bin/env python3
"""Differentially exercise the initialized callback and its failure branch."""
import argparse
import importlib.util
import json
import struct
from pathlib import Path
from unicorn import UcError, UC_HOOK_MEM_INVALID

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
spec = importlib.util.spec_from_file_location(
    "main_callback_v", ROOT / "g2/components/bootloader/update_core/verify.py"
)
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
v.ENTRIES["main_callback"] = 0x42E39C

HANDLE = 0x200004FC
CONTEXT = 0x200004F4
ATTRIBUTES = 0x433024
MANAGER_NAME = 0x434134
THREAD_ENTRY = 0x42E2F9
PROVIDERS = {0x416058, 0x4160FE, 0x4160B0, 0x41B2F8}
ATTRIBUTE_WORDS = [0x434134, 0, 0x20026AC0, 0x70, 0x20018AA0,
                   0x4000, 0x30, 1, 0]


class CallbackMachine(v.Machine):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.created_handle = 0x51
        self.invalid_write = None
        self.cpu.hook_add(UC_HOOK_MEM_INVALID, self.invalid)

    def invalid(self, uc, access, address, size, value, _user):
        self.invalid_write = {
            "access": access, "address": address, "size": size,
            "value": value,
        }
        self.events.append(["invalid_memory_access", access, address, size, value])
        return False

    def code(self, uc, pc, size, user):
        if pc in PROVIDERS:
            r0, r1, r2, r3 = self.args()
            if pc == 0x416058:
                self.events.append(["0x416058"])
            elif pc == 0x4160FE:
                assert [r0, r1, r2] == [THREAD_ENTRY, 0, ATTRIBUTES]
                words = list(struct.unpack(
                    "<9I", bytes(uc.mem_read(r2, 36))))
                assert words == ATTRIBUTE_WORDS, words
                assert bytes(uc.mem_read(MANAGER_NAME, 8)) == b"manager\0"
                self.events.append(["0x4160fe", r0, r1, r2, words])
                self.ret(self.created_handle)
            elif pc == 0x4160B0:
                self.events.append(["0x4160b0"])
            else:
                assert pc == 0x41B2F8
                self.events.append(["0x41b2f8"])
            if pc != 0x4160FE:
                self.ret()
            return
        super().code(uc, pc, size, user)

    def invoke(self):
        self.finished = False
        self.events = []
        self.invalid_write = None
        entry = ((self.symbols["opencfw_boot_main_callback"] & ~1)
                 if self.source else v.ENTRIES["main_callback"])
        self.cpu.reg_write(v.a.UC_ARM_REG_R0, 0xA0A0A0A0)
        self.cpu.reg_write(v.a.UC_ARM_REG_R1, 0xB1B1B1B1)
        self.cpu.reg_write(v.a.UC_ARM_REG_R2, 0xC2C2C2C2)
        self.cpu.reg_write(v.a.UC_ARM_REG_R3, 0xD3D3D3D3)
        self.cpu.reg_write(v.a.UC_ARM_REG_SP, v.SP)
        self.cpu.reg_write(v.a.UC_ARM_REG_LR, v.STOP | 1)
        try:
            self.cpu.emu_start(entry | 1, v.STOP + 2, count=10000)
        except UcError:
            if self.invalid_write is None:
                raise
            self.finished = True
        assert self.finished, ("execution did not terminate", hex(
            self.cpu.reg_read(v.a.UC_ARM_REG_PC)))
        return {
            "events": self.events,
            "handle": self.u(HANDLE),
            "context_bytes": bytes(self.cpu.mem_read(CONTEXT, 16)).hex(),
            "fault": self.invalid_write,
        }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--elf", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    assert v.sha(v.BLOB) == v.SHA
    _, segments, symbols = v.elf.elf_info(args.elf)
    trace, comparisons = {}, []

    for created_handle in [0, 1, 0x51, 0xFFFFFFFF]:
        machines = [CallbackMachine(),
                    CallbackMachine(True, segments, symbols)]
        for machine in machines:
            machine.created_handle = created_handle
            machine.cpu.mem_write(CONTEXT, bytes(range(16)))
            machine.w(HANDLE, 0xDEADBEEF)
        results = [machine.invoke() for machine in machines]
        assert results[0] == results[1], (created_handle, results)
        expected_context = bytearray(range(16))
        expected_context[8:12] = struct.pack("<I", created_handle)
        assert bytes.fromhex(results[0]["context_bytes"]) == expected_context
        assert results[0]["handle"] == created_handle
        if created_handle == 0:
            assert [e[0] for e in results[0]["events"]] == [
                "0x416058", "0x4160fe", "0x41b2f8",
                "invalid_memory_access"]
            assert results[0]["fault"]["address"] == 0xFFFFFFFF
        else:
            assert [e[0] for e in results[0]["events"]] == [
                "0x416058", "0x4160fe", "0x4160b0"]
            assert results[0]["fault"] is None
        trace.update(machines[0].trace)
        comparisons.append({
            "provider_handle": hex(created_handle),
            "events": results[0]["events"],
            "creator_handle_at_0x200004fc": hex(results[0]["handle"]),
            "callback_context_bytes_at_0x200004f4": results[0]["context_bytes"],
            "failure_store": results[0]["fault"],
        })

    used = {
        int(pc, 0) + offset
        for pc, raw in trace.items()
        for offset in range(len(bytes.fromhex(raw)))
    }
    sources = [p for p in HERE.iterdir()
               if p.suffix in {".c", ".h", ".ld", ".py"}
               or p.name == "Makefile"]
    report = {
        "status": "PASS",
        "cases": len(comparisons),
        "distinct_original_trace_bytes": len(used),
        "original_sha256": v.SHA,
        "elf_sha256": v.sha(args.elf),
        "source_sha256": {p.name: v.sha(p) for p in sources},
        "original_trace": trace,
        "comparisons": comparisons,
        "synthetic_providers": [hex(pc) for pc in sorted(PROVIDERS)],
        "limits": [
            "Original instructions at 0x42E39C-0x42E3C8 execute. Calls at 0x416058, 0x4160FE, 0x4160B0 and 0x41B2F8 are synthetic providers; their implementations are outside this component.",
            "The 36-byte manager attribute record and its name string are source-defined at their stock addresses. Other runtime object state, thread scheduling, and callback 0x42E2F9 execution are not modeled.",
            "The callback context base is the slot initialized at 0x200004F4; its creator handle is written at +8 (0x200004FC). Temporal ownership beyond the bounded startup/callback path is not established.",
            "Allocation failure follows the observed path: call 0x41B2F8, then store word 0 at 0xFFFFFFFF. The verifier observes that invalid memory access; exception/HardFault entry and recovery behavior are not modeled.",
            "Cortex-M4 compatibility ELF is used for offline Unicorn only. No hardware behavior, byte identity, or full bootloader completeness is claimed.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in
                      ["status", "cases", "distinct_original_trace_bytes"]}))


if __name__ == "__main__":
    main()
