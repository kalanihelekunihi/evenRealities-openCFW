#!/usr/bin/env python3
"""Original/source comparison for recovered MSPI control request tail."""
import argparse
import hashlib
import importlib.util
import json
import random
import struct
from pathlib import Path
from unicorn import UC_HOOK_MEM_WRITE

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
spec = importlib.util.spec_from_file_location(
    "bootverify", ROOT / "g2/components/bootloader/update_core/verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
v.ENTRIES["control"] = 0x4251C0
HANDLE = 0x20006000
CONFIG = 0x20008000
MMIO = 0x40060000
MMIO_SIZE = 0x4000


class Machine(v.Machine):
    def __init__(self, source=False, segments=(), symbols=None):
        super().__init__(source, segments, symbols)
        self.cpu.mem_map(MMIO, MMIO_SIZE)
        self.cpu.hook_add(UC_HOOK_MEM_WRITE, self.mmio_write,
                          begin=MMIO, end=MMIO + MMIO_SIZE - 1)
        if source:
            self.symbols["opencfw_boot_control"] = \
                self.symbols["opencfw_hal_mspi_control"]

    def mmio_write(self, uc, access, address, size, value, user):
        self.events.append(["mmio-write", address, size, value])

    def code(self, uc, pc, size, user):
        if pc == 0x08002220:
            self.events.append(["unrecovered-request", *self.args()])
            self.ret(0xDEAD0001)
            return
        if pc == 0x41D1C0:
            self.events.append(["delay", self.args()[0]])
            self.ret(0)
            return
        super().code(uc, pc, size, user)

    def put32(self, address, value):
        self.cpu.mem_write(address, struct.pack("<I", value & 0xffffffff))

    def set_fixture(self, module, configured, latency, initial_mode,
                    config_data, null_config=False, tail_byte=0,
                    state838=0, state844=0):
        handle = bytearray(0x8d0)
        struct.pack_into("<II", handle, 0, 0x03BEBEBE, module)
        handle[8:12] = bytes([configured, latency, initial_mode, 0])
        handle[0x8c8] = tail_byte
        struct.pack_into("<I", handle, 0x838, state838)
        struct.pack_into("<I", handle, 0x844, state844)
        self.cpu.mem_write(HANDLE, bytes(handle))
        self.cpu.mem_write(CONFIG, config_data)
        self.cpu.mem_write(MMIO, bytes((i * 37 + 0xA5) & 0xff
                                      for i in range(MMIO_SIZE)))
        return [HANDLE, 0, 0 if null_config else CONFIG]

    def observed(self, result):
        return {
            "return": result["return"],
            "events": self.events.copy(),
            "handle": bytes(self.cpu.mem_read(HANDLE, 0x8d0)).hex(),
            "mmio": bytes(self.cpu.mem_read(MMIO, MMIO_SIZE)).hex(),
            "config": bytes(self.cpu.mem_read(CONFIG, 32)).hex(),
        }


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--elf", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assert v.sha(v.BLOB) == v.SHA
    _, segments, symbols = v.elf.elf_info(args.elf)
    rng = random.Random(20261006)
    cases = []
    failures = []
    trace = {}

    def run(request, module, data, latency=0, configured=1, null=False,
            tail_byte=0, state838=0, state844=0):
        machines = [Machine(), Machine(True, segments, dict(symbols))]
        run_args = []
        for machine in machines:
            call_args = machine.set_fixture(module, configured, latency,
                0x55, data, null, tail_byte, state838, state844)
            call_args[1] = request
            run_args.append(call_args)
        results = [machine.run("control", argv)
                   for machine, argv in zip(machines, run_args)]
        observed = [machine.observed(result)
                    for machine, result in zip(machines, results)]
        mismatches = {key: [row[key] for row in observed]
                      for key in observed[0]
                      if observed[0][key] != observed[1][key]}
        if any(event[0] == "unrecovered-request"
               for event in observed[0]["events"]):
            mismatches["unexpected_unrecovered_provider"] = True
        trace.update(machines[0].trace)
        case = {"request": request, "module": module,
                      "config": data.hex(), "latency_byte": latency,
                      "configured": configured, "null_config": null,
                      "tail_byte": tail_byte, "state838": state838,
                      "state844": state844,
                      "return": observed[0]["return"],
                      "ordered_mmio_writes": [event for event in
                          observed[0]["events"] if event[0] == "mmio-write"],
                      "handle_sha256": hashlib.sha256(bytes.fromhex(
                          observed[0]["handle"])).hexdigest(),
                      "mmio_sha256": hashlib.sha256(bytes.fromhex(
                          observed[0]["mmio"])).hexdigest()}
        cases.append(case)
        if mismatches:
            failure = {"case": {key: case[key] for key in
                        ("request", "module", "config", "latency_byte",
                         "configured", "null_config", "tail_byte",
                         "state838", "state844")},
                       "different_fields": list(mismatches)}
            if "events" in mismatches:
                failure["events"] = mismatches["events"]
            for field_name, base, limit in (("handle", HANDLE, 0x8d0),
                                             ("mmio", MMIO, MMIO_SIZE)):
                if field_name in mismatches:
                    left = bytes.fromhex(mismatches[field_name][0])
                    right = bytes.fromhex(mismatches[field_name][1])
                    word_diffs = []
                    for offset in range(0, limit, 4):
                        if left[offset:offset+4] != right[offset:offset+4]:
                            word_diffs.append({
                                "address": f"0x{base+offset:08x}",
                                "stock": f"0x{int.from_bytes(left[offset:offset+4], 'little'):08x}",
                                "source": f"0x{int.from_bytes(right[offset:offset+4], 'little'):08x}"})
                    failure[field_name + "_word_differences"] = word_diffs[:24]
            failures.append(failure)

    # Request 25's pConfig is a device-mode byte at offset 0, copied to
    # handle+10 before the private 0x424120 configure helper runs.
    for module in range(4):
        for mode in range(32):
            for latency in (0, 1, 2, 3, 0xff):
                run(25, module, bytes([mode]) + bytes(31), latency)
        run(25, module, bytes(32), null=True)

    # Request 28's conditional DMB depends on handle byte 0x8c8; request 32
    # updates two queue-state words and the raw CQ control register.
    for module in range(4):
        for tail_byte in (0, 1):
            run(28, module, bytes(32), null=True, tail_byte=tail_byte)
        run(32, module, bytes(32), null=True, state838=0xfeed1234,
            state844=0xabcd9876)

    # Request 35 validates both bytes before touching registers.
    for module in range(4):
        for first in range(6):
            for second in range(4):
                run(35, module, bytes([first, second]) + bytes(30))
        run(35, module, bytes(32), null=True)

    for module in range(4):
        for _ in range(24):
            payload = bytearray(rng.randbytes(32))
            run(36, module, bytes(payload))
        run(36, module, bytes(32), null=True)
        run(37, module, bytes(32), null=True)
        run(38, module, bytes(32), null=True)
        run(39, module, bytes([0, 0, 0, 0, 0]) + rng.randbytes(27))
        for _ in range(24):
            payload = bytearray(rng.randbytes(32))
            payload[4] = 1
            run(39, module, bytes(payload))
        run(39, module, bytes(32), null=True)
        run(40, module, bytes(32), null=True)

    used = {int(pc, 0) + offset for pc, raw in trace.items()
            for offset in range(len(bytes.fromhex(raw)))}
    ranges = {
        "control_dispatch": (0x4251C0, 0x4262E0),
        "device_configure_private": (0x424120, 0x42488E),
    }
    blob = v.BLOB.read_bytes()
    function_hashes = {name: hashlib.sha256(blob[start-v.BASE:end-v.BASE]
        ).hexdigest() for name, (start, end) in ranges.items()}
    source_files = [HERE / "verify_control_remaining.py",
        HERE / "module.ld", HERE / "Makefile",
        ROOT / "g2/components/bootloader/nor_mspi_init/control_read.c",
        ROOT / "g2/components/bootloader/nor_mspi_init/control_remaining.c",
        ROOT / "g2/components/bootloader/nor_mspi_init/control_remaining.h",
        ROOT / "g2/components/bootloader/nor_mspi_power/device_configure.c"]
    output = {
        "status": "PASS" if not failures else "FAIL",
        "cases": len(cases), "failures": failures,
        "original_sha256": v.SHA,
        "source_elf_sha256": sha(args.elf),
        "source_sha256": {str(path.relative_to(ROOT)): sha(path)
                           for path in source_files},
        "stock_function_ranges_sha256": function_hashes,
        "distinct_original_instruction_bytes": len(used),
        "original_trace": trace, "comparisons": cases,
        "coverage": [25, 28, 32, 35, 36, 37, 38, 39, 40],
        "requests_28_and_32_status": "PASS" if not any(
            failure["case"]["request"] in (28, 32)
            for failure in failures) else "FAIL",
        "requests_35_to_40_status": "PASS" if not any(
            failure["case"]["request"] in range(35, 41)
            for failure in failures) else "FAIL",
        "request_25_status": "PASS" if not any(
            failure["case"]["request"] == 25 for failure in failures)
            else "KNOWN_DIVERGENCE_IN_PRIVATE_0x424120_SOURCE_PROVIDER",
        "unrecovered_requests": {
            "26-27,29-31,33-34": "explicitly delegated to opencfw_hal_mspi_control_unrecovered_request; not modeled as success",
        },
        "limits": [
            "The test executes the pinned 0x4251c0 dispatcher and 0x424120 helper against mapped synthetic RAM/MMIO; no hardware is accessed.",
            "Request 25 uses source opencfw_bl_mspi_device_configure_private; register behavior is compared to stock helper instructions.",
            "Requests 26–27, 29–31, and 33–34 remain the explicit lower control provider boundary because they include CQ/clock transitions and callback-backed operations not recovered here.",
            "MMIO is synthetic at 0x40060000–0x40063fff; callback timing and physical peripheral behavior are outside this fixture.",
        ]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({key: output[key] for key in
        ("status", "cases", "distinct_original_instruction_bytes",
         "coverage", "stock_function_ranges_sha256")}, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
