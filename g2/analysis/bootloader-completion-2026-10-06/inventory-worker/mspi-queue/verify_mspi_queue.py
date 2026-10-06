#!/usr/bin/env python3
"""Original/source comparison for the bootloader MSPI queue leaf family.

Only the clock-request API and microsecond-delay call are controlled provider
boundaries. Queue state, MMIO reads/writes, critical save/restore, and the
stock wrapper instructions run directly in Unicorn against synthetic memory.
"""
import argparse
import hashlib
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

ENTRIES = {
    "clockgen": 0x4249A0,
    "cq_init": 0x423F28,
    "cq_enable": 0x423F8E,
    "cq_disable": 0x423FAC,
    "cq_term": 0x423F54,
    "cmdq_init": 0x427794,
    "cmdq_enable": 0x427878,
    "cmdq_disable": 0x4278C8,
    "cmdq_term": 0x427AD6,
}
SYMBOLS = {
    "clockgen": "opencfw_bl_mspi_clockgen_control",
    "cq_init": "opencfw_hal_mspi_cq_init",
    "cq_enable": "opencfw_bl_mspi_cq_enable",
    "cq_disable": "opencfw_hal_mspi_cq_disable",
    "cq_term": "opencfw_hal_mspi_cq_term",
    "cmdq_init": "opencfw_provider_427794",
    "cmdq_enable": "opencfw_provider_427878",
    "cmdq_disable": "opencfw_provider_4278c8",
    "cmdq_term": "opencfw_provider_427ad6",
}
for name, address in ENTRIES.items():
    v.ENTRIES["mspi_queue_" + name] = address

MSPI_STATE_BASE = 0x2001CAA0
MSPI_STATE_STRIDE = 0x8D0
MSPI_QUEUE_OFFSET = 0x828
CMDQ_STATE_BASE = 0x200262F0
CMDQ_STATE_STRIDE = 0x2C
CMDQ_OPS_BASE = 0x430880
CMDQ_OPS_STRIDE = 0x28
CONFIG = 0x20005000
HANDLE_SLOT = 0x20006000
QUEUE_BUFFER = 0x20010000
MMIO_INIT = 0x40050000
MMIO_SIZE = 0x14000
CLKGEN_MMIO = 0x40000000
CLKGEN_MMIO_SIZE = 0x10000


class Machine(v.Machine):
    def __init__(self, source=False, segments=(), symbols=None, fixture=None):
        super().__init__(source, segments, symbols)
        self.fixture = fixture or {}
        self.calls = []
        self.cpu.mem_map(CLKGEN_MMIO, CLKGEN_MMIO_SIZE)
        self.cpu.mem_map(MMIO_INIT, MMIO_SIZE)
        if source:
            self.exec_ranges.append((0x41B8EC, 0x41B8F4))
            self.cpu.mem_write(0x41B8EC,
                v.BLOB.read_bytes()[0x41B8EC - v.BASE:0x41B8F4 - v.BASE])
            for name, symbol in SYMBOLS.items():
                self.symbols["opencfw_boot_mspi_queue_" + name] = \
                    self.symbols[symbol]

    def code(self, uc, pc, size, user):
        if pc == 0x4222F0:
            clock, user_id = self.args()[:2]
            status = self.fixture.get("clock_status", 0)
            self.calls.append(["clock_request", clock, user_id, status])
            self.ret(status)
            return
        if pc == 0x41D1C0:
            duration = self.args()[0]
            self.calls.append(["delay", duration])
            self.ret(0)
            return
        super().code(uc, pc, size, user)

    def invoke(self, name, args, fixture=None):
        self.fixture = fixture or {}
        self.calls = []
        result = self.run("mspi_queue_" + name, args)
        # Several stock HAL adapters have a void ABI. Their final R0 is a
        # caller-visible scratch value, not a specified return contract.
        if name in {"clockgen", "cq_init", "cq_enable", "cq_term"}:
            return {"providers": self.calls}
        return {"return": result["return"], "providers": self.calls}

    def set_primask(self, value):
        self.cpu.reg_write(v.a.UC_ARM_REG_PRIMASK, value & 1)

    def u32(self, address):
        return struct.unpack("<I", self.cpu.mem_read(address, 4))[0]

    def put32(self, address, value):
        self.cpu.mem_write(address, struct.pack("<I", value & 0xFFFFFFFF))

    def snapshots(self):
        return {
            "primask": self.cpu.reg_read(v.a.UC_ARM_REG_PRIMASK),
            "clockgen": self.u32(0x40004110),
            "mspi_global": bytes(self.cpu.mem_read(MSPI_STATE_BASE, 4 * 0x8D0)),
            "cmdq_state": bytes(self.cpu.mem_read(CMDQ_STATE_BASE,
                                                   12 * CMDQ_STATE_STRIDE)),
            "cmdq_ops": bytes(self.cpu.mem_read(CMDQ_OPS_BASE,
                                                 12 * CMDQ_OPS_STRIDE)),
            "peripherals": bytes(self.cpu.mem_read(MMIO_INIT, MMIO_SIZE)),
        }

    def prepare_cmdq(self, interface_id=8, flags=0x01CDCDCD,
                     buffer=QUEUE_BUFFER, size_bytes=4096, end=0):
        queue = CMDQ_STATE_BASE + interface_id * CMDQ_STATE_STRIDE
        ops = CMDQ_OPS_BASE + interface_id * CMDQ_OPS_STRIDE
        words = [flags, buffer, buffer + size_bytes, buffer, buffer, buffer,
                 size_bytes, 0, end, ops, 0]
        self.cpu.mem_write(queue, struct.pack("<11I", *words))
        self.put32(ops + 0, 0x400602A0 + (interface_id - 8) * 0x1000)
        self.put32(ops + 4, 0x400602A8 + (interface_id - 8) * 0x1000)
        self.put32(ops + 8, 0x400602C0 + (interface_id - 8) * 0x1000)
        self.put32(ops + 12, 0x400602C4 + (interface_id - 8) * 0x1000)
        self.put32(ops + 16, 0x400602B8 + (interface_id - 8) * 0x1000)
        self.put32(ops + 20, 0x4000)
        return queue, ops


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pair(segments, symbols, fixture=None):
    return [Machine(fixture=fixture),
            Machine(True, segments, dict(symbols), fixture=fixture)]


def compare(cases, trace, name, args, fixtures, segments, symbols, prepare):
    for fixture in fixtures:
        machines = pair(segments, symbols, fixture)
        prepare(machines)
        results = [machine.invoke(name, args, fixture) for machine in machines]
        assert results[0] == results[1], (name, args, fixture, results)
        state = [machine.snapshots() for machine in machines]
        assert state[0] == state[1], (name, args, fixture, state)
        trace.update(machines[0].trace)
        cases.append({"function": name, "arguments": args,
                      "fixture": fixture,
                      "result": results[0], "state_sha256":
                      hashlib.sha256(json.dumps({k: (v.hex() if isinstance(v, bytes) else v)
                          for k, v in state[0].items()}, sort_keys=True).encode()).hexdigest()})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--elf", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assert v.sha(v.BLOB) == v.SHA
    _, segments, symbols = v.elf.elf_info(args.elf)
    stock_resource = v.BLOB.read_bytes()[CMDQ_OPS_BASE - v.BASE:
                                          CMDQ_OPS_BASE - v.BASE +
                                          12 * CMDQ_OPS_STRIDE]
    source_resource = next((s["data"] for s in segments
                            if s["address"] == CMDQ_OPS_BASE), None)
    assert source_resource == stock_resource, (
        "CMDQ resource table must be emitted byte-for-byte at 0x430880",
        None if source_resource is None else len(source_resource))
    cases, trace = [], {}

    clock_fixtures = []
    for module in [0, 1, 2, 3, 6, 7, 0xFFFFFFFF]:
        for enable, configure, source in [
                (0, 0, 0), (1, 0, 0), (1, 1, 2), (1, 1, 0x80),
                (1, 1, 0xFF), (0x101, 0x100, 0x104)]:
            clock_fixtures.append((module, enable, configure, source,
                                   (module + enable + source) & 1))
    for module, enable, configure, source, primask in clock_fixtures:
        machines = pair(segments, symbols)
        initial = 0xA5A5F00F ^ module
        for machine in machines:
            machine.put32(0x40004110, initial)
            machine.set_primask(primask)
        results = [machine.invoke("clockgen",
                   [module, enable, configure, source]) for machine in machines]
        observed = [{"providers": r["providers"], **m.snapshots()} for r, m in
                    zip(results, machines)]
        assert observed[0] == observed[1], (module, enable, configure, source,
                                            primask, observed)
        trace.update(machines[0].trace)
        cases.append({"function": "clockgen", "arguments": [module, enable,
            configure, source], "initial_register": initial,
            "initial_primask": primask, "result": {"providers": results[0]["providers"],
            "register": observed[0]["clockgen"], "primask": observed[0]["primask"]}})

    # Full stock wrapper -> exact source command-queue initializer.
    for module, length, buffer in [(0, 1024, 0x20010000),
                                    (1, 3, 0x20018000),
                                    (2, 0x12345678, 0x20021000),
                                    (3, 0xFFFFFFFF, 0x20030000)]:
        machines = pair(segments, symbols)
        for machine in machines:
            machine.put32(MSPI_STATE_BASE + module * MSPI_STATE_STRIDE + 4,
                          module)
        results = [machine.invoke("cq_init", [module, length, buffer])
                   for machine in machines]
        states = [machine.snapshots() for machine in machines]
        assert states[0] == states[1], ("cq_init", module, length, states)
        trace.update(machines[0].trace)
        cases.append({"function": "cq_init", "arguments": [module, length,
            buffer], "result": results[0], "state_sha256": hashlib.sha256(
                states[0]["mspi_global"] + states[0]["cmdq_state"] +
                states[0]["peripherals"]).hexdigest()})

    # The CMDQ initializer's errors, handle slot, state row and register writes.
    init_cases = [
        (8, 2, QUEUE_BUFFER, HANDLE_SLOT, 0),
        (11, 3, 0x20018000, HANDLE_SLOT, 0),
        (12, 2, QUEUE_BUFFER, HANDLE_SLOT, 0),
        (8, 1, QUEUE_BUFFER, HANDLE_SLOT, 0),
        (8, 2, 0, HANDLE_SLOT, 0),
        (8, 2, QUEUE_BUFFER, 0, 0),
        (8, 2, QUEUE_BUFFER, HANDLE_SLOT, 0x01000000),
    ]
    for interface, size, buffer, slot, active in init_cases:
        machines = pair(segments, symbols)
        for machine in machines:
            machine.put32(CONFIG, size)
            machine.put32(CONFIG + 4, buffer)
            machine.cpu.mem_write(CONFIG + 8, b"\x01\xa5\x5a\xc3")
            machine.put32(HANDLE_SLOT, 0xAABBCCDD)
            machine.put32(CMDQ_STATE_BASE + interface * CMDQ_STATE_STRIDE,
                          active)
        results = [machine.invoke("cmdq_init", [interface, CONFIG, slot])
                   for machine in machines]
        snapshots = [machine.snapshots() for machine in machines]
        assert results[0] == results[1] and snapshots[0] == snapshots[1], (
            "cmdq_init", interface, size, buffer, slot, active, results,
            snapshots)
        trace.update(machines[0].trace)
        cases.append({"function": "cmdq_init", "arguments":
            [interface, size, buffer, slot, active], "return": results[0]["return"],
            "state_sha256": hashlib.sha256(json.dumps({k:
                (v.hex() if isinstance(v, bytes) else v) for k, v in
                snapshots[0].items()}, sort_keys=True).encode()).hexdigest()})

    # Direct CMDQ enable/disable validity, existing state and DMB threshold.
    for name, flags, queue_end, option, threshold in [
            ("cmdq_enable", 0x01CDCDCD, 0, 0xA0, QUEUE_BUFFER + 4096),
            ("cmdq_enable", 0x03CDCDCD, 0, 0xA0, QUEUE_BUFFER + 4096),
            ("cmdq_enable", 0x01CDCDCD, 0, 0xA0, 0x20080000),
            ("cmdq_enable", 0, 0, 0xA0, QUEUE_BUFFER),
            ("cmdq_disable", 0x03CDCDCD, 0, 0xA1, QUEUE_BUFFER + 4096),
            ("cmdq_disable", 0x01CDCDCD, 0, 0xA1, QUEUE_BUFFER + 4096),
            ("cmdq_disable", 0, 0, 0xA1, QUEUE_BUFFER + 4096)]:
        machines = pair(segments, symbols)
        queue_address = CMDQ_STATE_BASE + 8 * CMDQ_STATE_STRIDE
        ops_address = CMDQ_OPS_BASE + 8 * CMDQ_OPS_STRIDE
        for machine in machines:
            queue, ops = machine.prepare_cmdq(8, flags, end=queue_end)
            machine.put32(queue + 8, threshold)
            machine.put32(ops, 0x400602A0)
            machine.put32(0x400602A0, option)
        results = [machine.invoke(name, [queue_address]) for machine in machines]
        snapshots = [machine.snapshots() for machine in machines]
        assert results[0] == results[1] and snapshots[0] == snapshots[1], (
            name, flags, option, threshold, results, snapshots)
        trace.update(machines[0].trace)
        cases.append({"function": name, "arguments": [queue_address],
            "fixture": {"flags": flags, "option": option, "queue_word2": threshold},
            "return": results[0]["return"], "state_sha256": hashlib.sha256(
                snapshots[0]["cmdq_state"] + snapshots[0]["peripherals"]).hexdigest()})

    # Direct forced/non-forced termination and index refresh semantics.
    term_cases = [
        (0x01CDCDCD, 10, 9, 0, 0x400602C0, 0x400602A8),
        (0x01CDCDCD, 10, 9, 1, 0x400602C0, 0x400602A8),
        (0x01CDCDCD, 9, 10, 0, 0x400602C0, 0x400602A8),
        (0x03CDCDCD, 10, 10, 0, 0x400602C0, 0x400602A8),
        (0, 10, 10, 1, 0x400602C0, 0x400602A8),
    ]
    for flags, end, hw_index, force, index_register, head_register in term_cases:
        machines = pair(segments, symbols)
        queue_address = CMDQ_STATE_BASE + 8 * CMDQ_STATE_STRIDE
        for machine in machines:
            queue, ops = machine.prepare_cmdq(8, flags, end=end)
            machine.put32(index_register, hw_index)
            machine.put32(head_register, 0x20012340)
            machine.put32(0x400602A0, 0xBEEF)
            machine.put32(0x400602B8, 0xFFFFFFFF)
        results = [machine.invoke("cmdq_term", [queue_address, force])
                   for machine in machines]
        snapshots = [machine.snapshots() for machine in machines]
        assert results[0] == results[1] and snapshots[0] == snapshots[1], (
            "cmdq_term", flags, end, hw_index, force, results, snapshots)
        trace.update(machines[0].trace)
        cases.append({"function": "cmdq_term", "arguments":
            [queue_address, force], "fixture": {"flags": flags, "end": end,
            "hw_index": hw_index}, "return": results[0]["return"],
            "state_sha256": hashlib.sha256(snapshots[0]["cmdq_state"] +
                snapshots[0]["peripherals"]).hexdigest()})

    # CQ enable status gating, CQ disable return propagation and CQ term's
    # global-slot selection/clear behavior.
    for clock_status in [0, 7]:
        machines = pair(segments, symbols, {"clock_status": clock_status})
        state_address = MSPI_STATE_BASE
        queue_address = CMDQ_STATE_BASE + 8 * CMDQ_STATE_STRIDE
        for machine in machines:
            machine.put32(state_address + 4, 0)
            machine.put32(state_address + MSPI_QUEUE_OFFSET, queue_address)
            queue, ops = machine.prepare_cmdq(8, 0x01CDCDCD)
            machine.put32(ops, 0x400602A0)
            machine.put32(0x400602A0, 0)
        results = [machine.invoke("cq_enable", [state_address],
                    {"clock_status": clock_status}) for machine in machines]
        snapshots = [machine.snapshots() for machine in machines]
        assert results[0] == results[1] and snapshots[0] == snapshots[1], (
            "cq_enable", clock_status, results, snapshots)
        trace.update(machines[0].trace)
        cases.append({"function": "cq_enable", "arguments": [state_address],
            "fixture": {"clock_status": clock_status},
            "providers": results[0]["providers"],
            "state_sha256": hashlib.sha256(snapshots[0]["cmdq_state"] +
                snapshots[0]["peripherals"]).hexdigest()})

    for flags in [0x01CDCDCD, 0x03CDCDCD, 0]:
        machines = pair(segments, symbols)
        state_address = MSPI_STATE_BASE
        queue_address = CMDQ_STATE_BASE + 8 * CMDQ_STATE_STRIDE
        for machine in machines:
            machine.put32(state_address + MSPI_QUEUE_OFFSET, queue_address)
            queue, ops = machine.prepare_cmdq(8, flags)
            machine.put32(ops, 0x400602A0)
            machine.put32(0x400602A0, 1)
        results = [machine.invoke("cq_disable", [state_address])
                   for machine in machines]
        snapshots = [machine.snapshots() for machine in machines]
        assert results[0] == results[1] and snapshots[0] == snapshots[1], (
            "cq_disable", flags, results, snapshots)
        trace.update(machines[0].trace)
        cases.append({"function": "cq_disable", "arguments": [state_address],
            "return": results[0]["return"], "state_sha256": hashlib.sha256(
                snapshots[0]["cmdq_state"] + snapshots[0]["peripherals"]).hexdigest()})

    for module_field in [0, 1, 2]:
        machines = pair(segments, symbols)
        caller_state = MSPI_STATE_BASE
        global_slot = MSPI_STATE_BASE + module_field * MSPI_STATE_STRIDE + MSPI_QUEUE_OFFSET
        selected_queue = CMDQ_STATE_BASE + (8 + module_field) * CMDQ_STATE_STRIDE
        other_slot = MSPI_STATE_BASE + MSPI_QUEUE_OFFSET
        for machine in machines:
            machine.put32(caller_state + 4, module_field)
            machine.put32(global_slot, selected_queue)
            if global_slot != other_slot:
                machine.put32(other_slot, 0x20033000)
            queue, ops = machine.prepare_cmdq(8 + module_field,
                                               0x03CDCDCD)
            machine.put32(ops, 0x400602A0 + module_field * 0x1000)
        results = [machine.invoke("cq_term", [caller_state]) for machine in machines]
        snapshots = [machine.snapshots() for machine in machines]
        assert results[0] == results[1] and snapshots[0] == snapshots[1], (
            "cq_term", module_field, results, snapshots)
        trace.update(machines[0].trace)
        cases.append({"function": "cq_term", "arguments": [caller_state],
            "fixture": {"module_from_state": module_field},
            "providers": results[0]["providers"], "global_slot_after":
                machines[0].u32(global_slot), "other_slot_after":
                machines[0].u32(other_slot)})

    used = {int(pc, 0) + offset for pc, raw in trace.items()
            for offset in range(len(bytes.fromhex(raw)))}
    original = v.BLOB.read_bytes()
    ranges = {
        "clkgen_control": (0x4249A0, 0x424A18),
        "cq_init": (0x423F28, 0x423F54),
        "cq_enable": (0x423F8E, 0x423FAC),
        "cq_disable": (0x423FAC, 0x423FB8),
        "cq_term": (0x423F54, 0x423F8E),
        "cmdq_init": (0x427794, 0x427878),
        "cmdq_enable": (0x427878, 0x4278C8),
        "cmdq_disable": (0x4278C8, 0x42790A),
        "cmdq_term": (0x427AD6, 0x427B38),
        "cmdq_update_indices": (0x427754, 0x427794),
    }
    function_hashes = {name: hashlib.sha256(original[start - v.BASE:
        end - v.BASE]).hexdigest() for name, (start, end) in ranges.items()}
    sources = [HERE / "verify_mspi_queue.py",
        ROOT / "g2/components/bootloader/nor_mspi_queue/nor_mspi_queue.c",
        ROOT / "g2/components/bootloader/nor_mspi_queue/resources.c",
        ROOT / "g2/components/bootloader/nor_mspi_queue/nor_mspi_queue.h",
        ROOT / "g2/components/bootloader/nor_mspi_queue/module.ld",
        ROOT / "g2/components/bootloader/nor_mspi_queue/Makefile"]
    result = {
        "status": "PASS", "cases": len(cases),
        "original_sha256": v.SHA,
        "source_elf_sha256": sha(args.elf),
        "source_sha256": {str(path.relative_to(ROOT)): sha(path)
                           for path in sources},
        "stock_function_ranges_sha256": function_hashes,
        "stock_resource_table": {
            "address": f"0x{CMDQ_OPS_BASE:08x}",
            "bytes": len(stock_resource),
            "sha256": hashlib.sha256(stock_resource).hexdigest(),
            "classification": "12x10 scalar words; pointer-shaped words are MMIO addresses; no code pointers or callbacks",
        },
        "distinct_original_instruction_bytes": len(used),
        "original_trace": trace,
        "comparisons": cases,
        "limits": [
            "CLKGEN register 0x40004110, MSPI register regions, queue state, and interface operation tables use synthetic mapped memory; there is no peripheral or board access.",
            "Clock request 0x4222F0 and delay 0x41D1C0 are injected; critical-save 0x41B8EC, PRIMASK restore, MMIO instructions, queue-index update, and CMDQ state transitions execute directly from stock/source code.",
            "The local CMDQ source reconstructs only init/enable/disable/forced-term and their index update helper; allocation/post/release/interrupt flows are outside this test.",
            "The Apollo510 public SDK's MSPI helper signatures/intent corroborate the leaf names; exact behavior is grounded in the pinned bootloader instruction ranges listed above.",
            "This is a local source candidate and original/source comparison, not a complete boot image or byte-identical build.",
        ]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in
        ("status", "cases", "distinct_original_instruction_bytes",
         "stock_function_ranges_sha256")}, indent=2))


if __name__ == "__main__":
    main()
