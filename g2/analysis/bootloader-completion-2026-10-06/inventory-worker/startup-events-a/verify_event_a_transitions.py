#!/usr/bin/env python3
"""Native stock/source tests for event-A state selector and transition walker."""
from __future__ import annotations
from pathlib import Path
import argparse, hashlib, importlib.util, json, struct
from unicorn import Uc, UcError, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as a

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
IMAGE = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
TARGETS = ROOT / "g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-initialize/gx-native/scatter-selector-table.json"
EXPECTED_IMAGE = "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"
EXPECTED_SELECTOR = "c02ca4144181ebe16c3dffc47e1bec89a89fbb832fa8bb134b38dd8bf287444f"
EXPECTED_WALKER = "1075e4055c2ef66d985f8938f881a08d43a90791be3dc0b2700ff7e0074ed107"
EXPECTED_MATRIX = "d83c73b1f5370cc6063489aedc4f0701bdec2ca34a492233caa521c0cf2ea5e8"
STOP = 0x08000000
SENTINEL_BASE = 0x08000100
SEQUENCE_TABLE = 0x20000158

spec = importlib.util.spec_from_file_location(
    "elf_reader", ROOT / "g2/components/bootloader/update_core/elf_reader.py")
elf_reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(elf_reader)

ap = argparse.ArgumentParser()
ap.add_argument("--elf", type=Path, required=True)
ap.add_argument("--output", type=Path, required=True)
args = ap.parse_args()
blob = IMAGE.read_bytes()
assert hashlib.sha256(blob).hexdigest() == EXPECTED_IMAGE
stock_selector = blob[0x42A2B4 - 0x410000:0x42A43A - 0x410000]
stock_walker = blob[0x42A43A - 0x410000:0x42A4BC - 0x410000]
matrix = blob[0x433498 - 0x410000:0x433498 - 0x410000 + 28]
assert hashlib.sha256(stock_selector).hexdigest() == EXPECTED_SELECTOR
assert hashlib.sha256(stock_walker).hexdigest() == EXPECTED_WALKER
assert hashlib.sha256(matrix).hexdigest() == EXPECTED_MATRIX

table_receipt = json.loads(TARGETS.read_text())
assert table_receipt["status"] == "PASS"
assert table_receipt["original_sha256"] == EXPECTED_IMAGE
assert table_receipt["callback_table_address"] == hex(SEQUENCE_TABLE)
selectors = table_receipt["selectors"]
assert [x["selector"] for x in selectors] == list(range(27))
actual_targets = [int(x["thumb_target"], 16) for x in selectors]
assert actual_targets[24] == 0x42A031
assert actual_targets[25] == 0x42A033
assert actual_targets[26] == 0x42A035

_, segments, symbols = elf_reader.elf_info(args.elf)
for sym in ("event_a_state_transition_sequence",
            "event_a_temperature_transition_separate",
            "event_a_transition_sequence_24",
            "event_a_transition_sequence_8_timer_disabled"):
    assert sym in symbols, sym
source_entries = {k: symbols[k] & ~1 for k in (
    "event_a_state_transition_sequence",
    "event_a_temperature_transition_separate",
    "event_a_transition_sequence_24",
    "event_a_transition_sequence_8_timer_disabled")}

def pack(value):
    return struct.pack("<I", int(value) & 0xffffffff)

def get32(u, address):
    return struct.unpack("<I", u.mem_read(address, 4))[0]

def put32(u, address, value):
    u.mem_write(address, pack(value))

def machine(stock, table_targets=None):
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
    for lo, size in ((0x10000,0x10000),(0x410000,0x25000),
                     (0x08000000,0x1000),(0x20000000,0x40000),
                     (0x40000000,0x100000)):
        u.mem_map(lo, size)
    if stock:
        u.mem_write(0x410000, blob)
    else:
        for seg in segments:
            u.mem_write(seg["address"], seg["data"])
    u.reg_write(a.UC_ARM_REG_SP, 0x2003f000)
    u.reg_write(a.UC_ARM_REG_LR, STOP | 1)
    if table_targets is not None:
        for i, target in enumerate(table_targets):
            put32(u, SEQUENCE_TABLE + 4*i, target | 1)
    return u

def run_selector(stock, target, current):
    u = machine(stock)
    u.mem_write(0x20001000, b"\xa5")
    u.reg_write(a.UC_ARM_REG_R0, target)
    u.reg_write(a.UC_ARM_REG_R1, current)
    u.reg_write(a.UC_ARM_REG_R2, 0x20001000)
    done = [False]
    def hook(cpu, pc, size, _):
        if pc == STOP:
            done[0] = True
            cpu.emu_stop()
    u.hook_add(UC_HOOK_CODE, hook)
    entry = 0x42A2B4 if stock else source_entries["event_a_state_transition_sequence"]
    u.emu_start(entry | 1, 0, count=5000)
    assert done[0], ("selector did not return", stock, target, current)
    return (u.reg_read(a.UC_ARM_REG_R0), int(u.mem_read(0x20001000,1)[0]))

def run_walker(stock, target, current, ton, old_ton):
    # Use authenticated installed target addresses. For source selectors 0..23,
    # the hook cuts before the first instruction at the locked target address;
    # slot 24 executes its source no-op. Stock slot 24 executes authenticated
    # 0x42a030 (BX LR).
    table_targets = actual_targets[:]
    if not stock:
        table_targets[24] = source_entries["event_a_transition_sequence_24"] | 1
    u = machine(stock, table_targets)
    calls = []
    done = [False]
    def hook(cpu, pc, size, _):
        if pc == STOP:
            done[0] = True
            cpu.emu_stop()
            return
        selector = None
        for index, target_pc in enumerate(actual_targets):
            expected_pc = target_pc & ~1
            if ((stock or index != 24) and pc == expected_pc) or (
                not stock and index == 24 and
                pc == source_entries["event_a_transition_sequence_24"]):
                selector = index
                break
        if selector is not None:
            calls.append({
                "selector": selector,
                "args": [cpu.reg_read(getattr(a, f"UC_ARM_REG_R{i}")) for i in range(4)],
            })
            if selector != 24:
                # Stop before the first target instruction. No locked target
                # code or fake result/status provider executes in source.
                cpu.reg_write(a.UC_ARM_REG_PC, cpu.reg_read(a.UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE, hook)
    entry = 0x42A43A if stock else source_entries["event_a_temperature_transition_separate"]
    for reg, value in zip((a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,
                           a.UC_ARM_REG_R2,a.UC_ARM_REG_R3),
                          (target,current,ton,old_ton)):
        u.reg_write(reg, value)
    try:
        u.emu_start(entry | 1, 0, count=30000)
    except UcError as exc:
        raise AssertionError(("walker fault", stock, target, current,
                              hex(u.reg_read(a.UC_ARM_REG_PC)), str(exc))) from exc
    assert done[0], ("walker did not return", stock, target, current)
    return calls

selector_cases = 0
for current in range(20):
    for target in range(20):
        original = run_selector(True, target, current)
        source = run_selector(False, target, current)
        assert original == source, ("selector mismatch", target, current, original, source)
        selector_cases += 1

walker_cases = 0
selector_ids = set()
for current in range(20):
    for target in range(20):
        original = run_walker(True, target, current, 7, 11)
        source = run_walker(False, target, current, 7, 11)
        assert original == source, ("walker mismatch", target, current, original, source)
        selector_ids.update(call["selector"] for call in original)
        walker_cases += 1

def run_sequence8(stock, target, current, ton, old_ton):
    # Selector 8's source port covers the PCM2.2 timer-disabled path. The
    # timer-active branch is deliberately excluded because it enters 0x42a04a.
    u = machine(stock)
    profile = bytearray(0x6c)
    struct.pack_into("<I", profile, 0, 0x1f01600d)
    for index in range(20):
        value = ((index * 37 + 0x129a) & 0x7f) | \
                (((index * 19 + 0x12d) & 0x3ff) << 7) | \
                (((index * 7 + 3) & 0xf) << 17) | \
                (((index * 11 + 0x23) & 0x7f) << 21)
        struct.pack_into("<I", profile, 4 + index * 4, value)
    struct.pack_into("<I", profile, 0x54, 0x00123456)
    struct.pack_into("<I", profile, 0x58, 0x000fedcb)
    struct.pack_into("<I", profile, 0x5c, 0x000abcde)
    struct.pack_into("<I", profile, 0x60, 0x00013579)
    struct.pack_into("<I", profile, 0x64, 0x0a654321)
    u.mem_write(0x20026ba0, bytes(profile))
    put32(u, 0x400083e0, 0)  # TIMER_A disabled
    put32(u, 0x40008064, 0)
    put32(u, 0x40020344, 0x01020304)
    put32(u, 0x40020354, 0x00543210)
    put32(u, 0x40020358, 0x87654321)
    u.reg_write(a.UC_ARM_REG_SP, 0x2003f000)
    u.reg_write(a.UC_ARM_REG_LR, STOP | 1)
    for reg, value in zip((a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,
                           a.UC_ARM_REG_R2,a.UC_ARM_REG_R3),
                          (target,current,ton,old_ton)):
        u.reg_write(reg, value)
    done = [False]
    def hook(cpu, pc, size, _):
        if pc == STOP:
            done[0] = True
            cpu.emu_stop()
    u.hook_add(UC_HOOK_CODE, hook)
    entry = 0x428bb0 if stock else source_entries[
        "event_a_transition_sequence_8_timer_disabled"]
    try:
        u.emu_start(entry | 1, 0, count=10000)
    except UcError as exc:
        raise AssertionError(("sequence8 fault",stock,target,current,
                              hex(u.reg_read(a.UC_ARM_REG_PC)),str(exc))) from exc
    assert done[0], ("sequence8 did not return",stock,target,current)
    return {
        "r0": u.reg_read(a.UC_ARM_REG_R0),
        "globals": [get32(u,p) for p in
                    (0x200270b0,0x200270b4,0x200270b8,0x200270bc,
                     0x200270c0,0x200270c4)],
        "registers": [get32(u,p) for p in
                      (0x40020344,0x40020354,0x40020358)],
    }

sequence8_cases = 0
for current in range(20):
    for target in range(20):
        values = (target, current, (target * 3 + 1) & 0xf,
                  (current * 5 + 2) & 0xf)
        original = run_sequence8(True, *values)
        source = run_sequence8(False, *values)
        assert original == source, ("sequence8 mismatch",values,original,source)
        sequence8_cases += 1

# Raw bytes show the installed selectors 24..26 are three BX LR entries.
no_op_bytes = blob[0x42A030 - 0x410000:0x42A036 - 0x410000]
assert no_op_bytes == bytes.fromhex("704770477047")
out = {
    "status": "PASS",
    "image_sha256": EXPECTED_IMAGE,
    "source_elf_sha256": hashlib.sha256(args.elf.read_bytes()).hexdigest(),
    "source_runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "selector_entry": "0x42a2b4",
    "selector_extent_bytes": len(stock_selector),
    "selector_sha256": EXPECTED_SELECTOR,
    "temperature_walker_entry": "0x42a43a",
    "temperature_walker_extent_bytes": len(stock_walker),
    "temperature_walker_sha256": EXPECTED_WALKER,
    "transition_matrix": {"address":"0x433498","bytes":len(matrix),
                          "sha256":EXPECTED_MATRIX},
    "selector_cases": selector_cases,
    "walker_cases": walker_cases,
    "sequence8_timer_disabled_cases": sequence8_cases,
    "observed_sequence_ids": sorted(selector_ids),
    "authenticated_callback_table_receipt": str(TARGETS.relative_to(ROOT)),
    "authenticated_selector_targets": [
        {"selector": item["selector"], "thumb_target": item["thumb_target"],
         "body_bytes": item["body_bytes"], "body_sha256": item["body_sha256"]}
        for item in selectors],
    "native_callback_closed": {
        "selector":24,"target":"0x42a030",
        "original_bytes":"7047","meaning":"BX LR",
        "source_symbol":"event_a_transition_sequence_24",
        "sdk_semantics":"PCM2.2 transition_sequence_24 is a documented no-op",
    },
    "bounded_native_callback": {
        "selector":8,"target":"0x428bb0",
        "source_symbol":"event_a_transition_sequence_8_timer_disabled",
        "stock_body_bytes":selectors[8]["body_bytes"],
        "covered_cases":sequence8_cases,
        "precondition":"TIMER_A CTRL0 enable bit 31 at 0x400083e0 is clear",
        "timer_enabled_frontier":"0x41d1c0 delay_us and 0x42a04a timer ISR",
        "compared":"R0 return, six SRAM trim/target globals, and three MMIO trim registers",
    },
    "unresolved_callback_frontier": [
        {"selector": i, "target": selectors[i]["thumb_target"],
         "sdk_name": f"transition_sequence_{i}",
         "state": "explicit no-execution boundary"}
        for i in range(24)],
    "limits": [
        "For selectors 0..23 in walker coverage, the runner logs the actual selected target/arguments but stops before executing the callback. No callback return/status is fabricated or credited.",
        "Selector 8 is separately executed as authenticated stock code versus compiled source on 400 timer-disabled cases; its active-timer branch and descendants are not covered.",
        "The installed table target values are sourced from the passing scatter-selector-table receipt; this test does not recreate its startup decompression or table initialization.",
        "Tests cover documented states 0..19 and the helper-call boundary, not physical regulator, timer, or temperature behavior.",
    ],
}
args.output.write_text(json.dumps(out, indent=2) + "\n")
print("PASS", selector_cases, "selector pairs;", walker_cases,
      "walker pairs;", sequence8_cases, "selector-8 timer-disabled cases; IDs", sorted(selector_ids))
