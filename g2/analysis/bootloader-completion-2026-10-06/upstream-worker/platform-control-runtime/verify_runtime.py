#!/usr/bin/env python3
"""Platform-control source/image differential with explicit hardware cuts."""
import argparse
import hashlib
import json
from pathlib import Path

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as a

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
BLOB = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
BLOB_SHA = "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"
BASE = 0x410000
STOP = 0x08000000
FINISH_TARGET = STOP + 0x100
MODE_HOOK_TARGET = STOP + 0x200
NOTIFY_HOOK_TARGET = STOP + 0x300
RECORDS = 0x20000454
OBJECTS = 0x20032000
REGIDS = 0x20032100
POWER = 0x40010000
POWER_SIZE = 0x1000

from importlib.util import spec_from_file_location, module_from_spec
spec = spec_from_file_location(
    "elf_reader", ROOT / "g2/components/bootloader/update_core/elf_reader.py")
elf_reader = module_from_spec(spec)
spec.loader.exec_module(elf_reader)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Machine:
    def __init__(self, source=False, segments=(), symbols=None):
        self.cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        self.cpu.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
        self.source = source
        self.symbols = symbols or {}
        self.trace = {}
        self.apply_calls = []
        self.apply_result = 0
        # Stock execution gets the locked image. Source execution deliberately
        # receives only the two literal inputs read from that image, so it
        # cannot silently fall back to stock instructions.
        if source:
            self.cpu.mem_map(0x434000, 0x1000)
            self.cpu.mem_write(0x434158, (3).to_bytes(4, "little"))
            self.cpu.mem_write(0x43415C, (0xE083).to_bytes(4, "little"))
        else:
            self.cpu.mem_map(BASE, 0x25000)
            self.cpu.mem_write(BASE, BLOB.read_bytes())
        self.cpu.mem_map(0x10000, 0x10000)
        self.cpu.mem_map(0x20000000, 0x40000)
        self.cpu.mem_map(POWER, 0x1000)
        self.cpu.mem_map(0x40004000, 0x1000)
        self.cpu.mem_map(0x40020000, 0x2000)
        self.cpu.mem_map(STOP, 0x1000)
        if source:
            for seg in segments:
                self.cpu.mem_write(seg["address"], seg["data"])
            self.entry = self.symbols["opencfw_boot_control_mode_one"] & ~1
            self.apply_entry = self.symbols["opencfw_boot_control_power_apply"] & ~1
            self.apply_configure_entry = self.symbols[
                "opencfw_boot_control_power_apply_configure"] & ~1
            self.transition_entry = self.symbols["opencfw_boot_control_transition"] & ~1
            self.delay_entry = self.symbols["opencfw_boot_control_delay_us"] & ~1
            self.delay_status_entry = self.symbols[
                "opencfw_boot_control_delay_status_change"] & ~1
            self.query_entry = self.symbols["opencfw_boot_control_query"] & ~1
            self.query_copy_entry = self.symbols[
                "opencfw_boot_control_query_descriptor_copy"] & ~1
            self.finish_entry = FINISH_TARGET
        else:
            self.entry = 0x41F8BA
            self.apply_entry = 0x422BA8
            self.apply_configure_entry = None
            self.transition_entry = 0x41B954
            self.delay_entry = 0x41D1C0
            self.delay_status_entry = 0x41D21C
            self.query_entry = 0x41C2D8
            self.query_copy_entry = 0x41B8F8
            self.finish_entry = FINISH_TARGET
        self.mode_two_entry = (self.symbols["opencfw_boot_control_mode_two"] & ~1
                               if source else 0x41BA80)
        self.cleanup_entry = (self.symbols["opencfw_boot_control_cleanup"] & ~1
                              if source else 0x41C990)
        self.cpu.hook_add(UC_HOOK_CODE, self.code)

    def u32(self, address):
        return int.from_bytes(self.cpu.mem_read(address, 4), "little")

    def w32(self, address, value):
        self.cpu.mem_write(address, int(value & 0xFFFFFFFF).to_bytes(4, "little"))

    def code(self, uc, pc, size, _):
        if pc == STOP:
            uc.emu_stop()
            return
        if not self.source and BASE <= pc < BASE + len(BLOB.read_bytes()) \
                and pc not in (self.apply_entry, self.delay_entry,
                               self.delay_status_entry):
            self.trace[pc] = bytes(uc.mem_read(pc, size))
        if pc == self.apply_entry:
            args = [uc.reg_read(a.UC_ARM_REG_R0), uc.reg_read(a.UC_ARM_REG_R1),
                    uc.reg_read(a.UC_ARM_REG_R2)]
            self.apply_calls.append(args)
        if pc == self.apply_configure_entry:
            uc.reg_write(a.UC_ARM_REG_R0, self.apply_result)
            uc.reg_write(a.UC_ARM_REG_PC, uc.reg_read(a.UC_ARM_REG_LR))
            return
        if pc == self.transition_entry:
            self.transition_calls.append(uc.reg_read(a.UC_ARM_REG_R0))
        if pc == self.query_entry:
            self.query_calls.append([
                uc.reg_read(a.UC_ARM_REG_R0),
                uc.reg_read(a.UC_ARM_REG_R1) != 0])
        if pc == self.query_copy_entry:
            self.query_copy_calls.append([
                uc.reg_read(a.UC_ARM_REG_R0) != 0,
                uc.reg_read(a.UC_ARM_REG_R1)])
        if pc == self.delay_entry:
            self.delay_calls.append(uc.reg_read(a.UC_ARM_REG_R0))
            if (self.delay_complete_after is not None and
                    len(self.delay_calls) >= self.delay_complete_after):
                self.w32(0x40021000, self.u32(0x40021000) | 4)
            uc.reg_write(a.UC_ARM_REG_PC, uc.reg_read(a.UC_ARM_REG_LR))
            return
        if pc == self.delay_status_entry:
            args = [uc.reg_read(a.UC_ARM_REG_R0), uc.reg_read(a.UC_ARM_REG_R1),
                    uc.reg_read(a.UC_ARM_REG_R2), uc.reg_read(a.UC_ARM_REG_R3)]
            self.delay_status_calls.append(args)
            if self.delay_status_ready:
                self.w32(args[1], (self.u32(args[1]) & ~args[2]) | args[3])
            uc.reg_write(a.UC_ARM_REG_R0, 0)
            uc.reg_write(a.UC_ARM_REG_PC, uc.reg_read(a.UC_ARM_REG_LR))
            return
        if pc == MODE_HOOK_TARGET:
            pointer = uc.reg_read(a.UC_ARM_REG_R2)
            byte = uc.mem_read(pointer, 1)[0] if pointer else None
            self.mode_hook_calls.append([
                uc.reg_read(a.UC_ARM_REG_R0), uc.reg_read(a.UC_ARM_REG_R1),
                pointer != 0, byte])
            uc.reg_write(a.UC_ARM_REG_R0, 0)
            uc.reg_write(a.UC_ARM_REG_PC, uc.reg_read(a.UC_ARM_REG_LR))
            return
        if pc == NOTIFY_HOOK_TARGET:
            self.notify_calls += 1
            uc.reg_write(a.UC_ARM_REG_R0, 0)
            uc.reg_write(a.UC_ARM_REG_PC, uc.reg_read(a.UC_ARM_REG_LR))
            return
        if pc == self.finish_entry:
            self.finish_calls += 1
            uc.reg_write(a.UC_ARM_REG_R0, self.finish_result)
            uc.reg_write(a.UC_ARM_REG_PC, uc.reg_read(a.UC_ARM_REG_LR))
            return

    def setup(self, mode, primask, object_kind="zero"):
        self.cpu.mem_write(0x20000000, b"\0" * 0x40000)
        self.cpu.mem_write(POWER, b"\0" * POWER_SIZE)
        for selector in range(4):
            record = RECORDS + selector * 0x1C
            obj = OBJECTS + selector * 0x40
            ids = REGIDS + selector * 0x10
            self.w32(record + 4, obj)
            self.w32(record + 8, ids)
            self.cpu.mem_write(record + 0x18, b"\x5a")
            # The selected mode's pair is read as [1] then [0]. The values
            # come from stock ROM words at 0x434158 (3) and 0x43415c (0xe083).
            self.w32(ids, 0)
            self.w32(ids + 4, 10)
        selected = mode & 0xFF
        if selected < 4:
            record = RECORDS + selected * 0x1C
            if object_kind == "null":
                self.w32(record + 4, 0)
            elif object_kind == "wrong":
                self.w32(OBJECTS, 0xFFFFFFFF)
        self.cpu.reg_write(a.UC_ARM_REG_PRIMASK, primask)
        self.cpu.reg_write(a.UC_ARM_REG_SP, 0x2002F000)
        self.cpu.reg_write(a.UC_ARM_REG_LR, STOP | 1)
        self.apply_calls = []
        self.trace = {}
        self.transition_calls = []
        self.delay_calls = []
        self.delay_status_calls = []
        self.mode_hook_calls = []
        self.notify_calls = 0
        self.query_calls = []
        self.query_copy_calls = []
        self.finish_calls = 0
        self.finish_result = 0
        self.cpu.reg_write(a.UC_ARM_REG_R0, mode & 0xFFFFFFFF)

    def run(self, mode, primask, object_kind="zero"):
        self.setup(mode, primask, object_kind)
        self.cpu.emu_start(self.entry | 1, STOP + 2, count=50000)
        selected = mode & 0xFF
        record = RECORDS + selected * 0x1C if selected < 4 else RECORDS
        return {
            "status": self.cpu.reg_read(a.UC_ARM_REG_R0),
            "apply_calls": self.apply_calls,
            "primask": self.cpu.reg_read(a.UC_ARM_REG_PRIMASK),
            "mode_record": bytes(self.cpu.mem_read(record, 0x1C)).hex(),
            "power_area": bytes(self.cpu.mem_read(POWER, POWER_SIZE)).hex(),
        }

    def run_power_apply(self, object_pointer, object_header, operation, enable):
        self.cpu.mem_write(0x20000000, b"\0" * 0x40000)
        self.cpu.mem_write(POWER, b"\0" * POWER_SIZE)
        if object_pointer:
            self.w32(object_pointer, object_header)
        self.cpu.reg_write(a.UC_ARM_REG_SP, 0x2002F000)
        self.cpu.reg_write(a.UC_ARM_REG_LR, STOP | 1)
        self.apply_calls = []
        self.trace = {}
        self.cpu.reg_write(a.UC_ARM_REG_R0, object_pointer)
        self.cpu.reg_write(a.UC_ARM_REG_R1, operation)
        self.cpu.reg_write(a.UC_ARM_REG_R2, enable)
        self.cpu.emu_start(self.apply_entry | 1, STOP + 2, count=50000)
        return {"status": self.cpu.reg_read(a.UC_ARM_REG_R0),
                "apply_calls": self.apply_calls,
                "power_area": bytes(self.cpu.mem_read(POWER, POWER_SIZE)).hex()}

    def run_query(self, selector, output_present, status_bits):
        self.cpu.mem_write(0x20000000, b"\0" * 0x40000)
        self.w32(0x40021004, 0xA5A55A5A)
        self.w32(0x40021008, status_bits)
        self.w32(0x4002100C, 0x5AA5A55A)
        self.w32(0x40021010, status_bits)
        out = 0x20030100 if output_present else 0
        if out:
            self.cpu.mem_write(out, b"\xa5")
        self.query_calls = []
        self.query_copy_calls = []
        self.trace = {}
        self.cpu.reg_write(a.UC_ARM_REG_SP, 0x2002F000)
        self.cpu.reg_write(a.UC_ARM_REG_LR, STOP | 1)
        self.cpu.reg_write(a.UC_ARM_REG_R0, selector & 0xFFFFFFFF)
        self.cpu.reg_write(a.UC_ARM_REG_R1, out)
        self.cpu.emu_start(self.query_entry | 1, STOP + 2, count=50000)
        return {"status": self.cpu.reg_read(a.UC_ARM_REG_R0),
                "output": self.cpu.mem_read(out, 1)[0] if out else None,
                "query_calls": self.query_calls,
                "copy_calls": self.query_copy_calls}

    def run_query_copy(self, selector, destination_present):
        self.cpu.mem_write(0x20000000, b"\0" * 0x40000)
        destination = 0x20030200 if destination_present else 0
        if destination:
            self.cpu.mem_write(destination, b"\xa5" * 16)
        self.query_copy_calls = []
        self.trace = {}
        self.cpu.reg_write(a.UC_ARM_REG_SP, 0x2002F000)
        self.cpu.reg_write(a.UC_ARM_REG_LR, STOP | 1)
        self.cpu.reg_write(a.UC_ARM_REG_R0, destination)
        self.cpu.reg_write(a.UC_ARM_REG_R1, selector & 0xFFFFFFFF)
        self.cpu.emu_start(self.query_copy_entry | 1, STOP + 2, count=50000)
        return {"status": self.cpu.reg_read(a.UC_ARM_REG_R0),
                "copy_calls": self.query_copy_calls,
                "output": bytes(self.cpu.mem_read(destination, 16)).hex()
                if destination else None}

    def run_mode_two(self, mode, current, config_mode, saved_mode,
                     wake_ready, complete_after, wake_already_on=False,
                     primask=0):
        self.cpu.mem_write(0x20000000, b"\0" * 0x40000)
        self.cpu.mem_write(POWER, b"\0" * POWER_SIZE)
        self.w32(0x40021000, ((current & 3) << 3) |
                 (4 if complete_after == 0 else 0))
        self.w32(0x40021108, (config_mode & 3) << 4)
        self.cpu.mem_write(0x20000552, bytes([saved_mode & 0xFF]))
        self.w32(0x40004044, 0x20 if wake_already_on else 0)
        self.w32(0x40004030,
                 0x01000000 if (wake_ready and wake_already_on) else 0)
        self.w32(0x20026e38 + 4, MODE_HOOK_TARGET | 1)
        self.w32(0x20026e38 + 0x28, NOTIFY_HOOK_TARGET | 1)
        self.cpu.reg_write(a.UC_ARM_REG_SP, 0x2002F000)
        self.cpu.reg_write(a.UC_ARM_REG_LR, STOP | 1)
        self.cpu.reg_write(a.UC_ARM_REG_PRIMASK, primask)
        self.transition_calls = []
        self.delay_calls = []
        self.delay_status_calls = []
        self.mode_hook_calls = []
        self.notify_calls = 0
        self.delay_complete_after = complete_after
        self.delay_status_ready = wake_ready
        self.trace = {}
        self.cpu.reg_write(a.UC_ARM_REG_R0, mode & 0xFFFFFFFF)
        self.cpu.emu_start(self.mode_two_entry | 1, STOP + 2, count=100000)
        return {"status": self.cpu.reg_read(a.UC_ARM_REG_R0),
                "transition_calls": self.transition_calls,
                "current": self.u32(0x40021000),
                "saved_mode": self.cpu.mem_read(0x20000552, 1)[0],
                "config": self.u32(0x40021108),
                "wake_control": self.u32(0x40004044),
                "wake_status": self.u32(0x40004030),
                "delay_calls": self.delay_calls,
                "delay_status_calls": self.delay_status_calls,
                "mode_hook_calls": self.mode_hook_calls,
                "notify_calls": self.notify_calls,
                "primask": self.cpu.reg_read(a.UC_ARM_REG_PRIMASK)}

    def run_cleanup(self, context_mode, query_hit, finish_result,
                    hook_installed=True):
        self.cpu.mem_write(0x20000000, b"\0" * 0x40000)
        self.cpu.mem_write(POWER, b"\0" * POWER_SIZE)
        self.w32(0x40021000, (context_mode & 3) << 3)
        self.w32(0x40021008, 0x00040000 if query_hit else 0)
        self.w32(0x20026e38 + 8,
                 (self.finish_entry | 1) if hook_installed else 0)
        self.cpu.reg_write(a.UC_ARM_REG_SP, 0x2002F000)
        self.cpu.reg_write(a.UC_ARM_REG_LR, STOP | 1)
        self.query_calls = []
        self.query_copy_calls = []
        self.finish_calls = 0
        self.finish_result = finish_result
        self.trace = {}
        self.cpu.emu_start(self.cleanup_entry | 1, STOP + 2, count=100000)
        return {"status": self.cpu.reg_read(a.UC_ARM_REG_R0),
                "query_calls": self.query_calls,
                "query_copy_calls": self.query_copy_calls,
                "finish_calls": self.finish_calls,
                "context": self.u32(0x40021000)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--elf", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    assert sha(BLOB) == BLOB_SHA
    _, segments, symbols = elf_reader.elf_info(args.elf)
    cases = []
    all_trace = {}
    for mode in [0, 1, 2, 3]:
        for primask in [0, 1]:
            for object_kind in ["null", "zero", "wrong"]:
                stock = Machine()
                source = Machine(True, segments, symbols)
                left = stock.run(mode, primask, object_kind)
                right = source.run(mode, primask, object_kind)
                assert left == right, (mode, primask, object_kind, left, right)
                all_trace.update(stock.trace)
                cases.append({"mode": mode, "primask": primask,
                              "object_kind": object_kind, "state": left})
    for mode in [4, 0x100, 0x104, 0xFFFFFFFF]:
        for primask in [0, 1]:
            stock, source = Machine(), Machine(True, segments, symbols)
            left = stock.run(mode, primask)
            right = source.run(mode, primask)
            assert left == right, (mode, primask, left, right)
            all_trace.update(stock.trace)
            cases.append({"mode": mode, "primask": primask, "state": left})
    apply_cases = [(0, 0, 2, 1), (OBJECTS, 0, 2, 1),
                   (OBJECTS, 0xFFFFFFFF, 2, 1),
                   (OBJECTS, 0x01EA9E06, 3, 1)]
    for pointer, header, operation, enable in apply_cases:
        stock, source = Machine(), Machine(True, segments, symbols)
        left = stock.run_power_apply(pointer, header, operation, enable)
        right = source.run_power_apply(pointer, header, operation, enable)
        assert left == right, ("power-apply", pointer, header, operation,
                               enable, left, right)
        all_trace.update(stock.trace)
        cases.append({"operation": "power_apply",
                      "args": [pointer, header, operation, enable],
                      "state": left})
    mode_two_cases = [
        (1, 0, 3, 0, False, 0, False),
        (1, 1, 3, 0, False, 2, False),
        (1, 0, 0, 0, False, None, False),
        (1, 0, 3, 1, False, 0, False),
        (2, 2, 3, 0, True, 0, False),
        (2, 0, 3, 0, True, 0, False),
        (2, 2, 0, 0, True, 0, False),
        (2, 2, 3, 2, False, None, False),
        (2, 2, 3, 0, False, 0, False),
        (2, 2, 3, 0, True, None, False),
        (2, 2, 3, 0, True, 0, True),
        (1, 1, 3, 0, False, 1, False, 1),
        (0x102, 2, 3, 0, True, 0, False),
        (3, 2, 3, 0, False, 0, False),
    ]
    for case in mode_two_cases:
        stock, source = Machine(), Machine(True, segments, symbols)
        left = stock.run_mode_two(*case)
        right = source.run_mode_two(*case)
        assert left == right, ("mode-two", case, left, right)
        all_trace.update(stock.trace)
        cases.append({"operation": "mode_two", "args": list(case),
                      "state": left})

    query_cases = []
    for selector in range(34):
        query_cases.extend([(selector, True, 0), (selector, True, 0xFFFFFFFF)])
    query_cases.extend([
        (0x114, True, 0xFFFFFFFF), (0x100, True, 0),
        (34, True, 0xFFFFFFFF), (0x122, True, 0xFFFFFFFF),
        (255, True, 0), (0xFFFFFFFF, True, 0xFFFFFFFF),
        (0, False, 0xFFFFFFFF), (34, False, 0xFFFFFFFF),
    ])
    for case in query_cases:
        stock, source = Machine(), Machine(True, segments, symbols)
        left = stock.run_query(*case)
        right = source.run_query(*case)
        assert left == right, ("query", case, left, right)
        all_trace.update(stock.trace)
        cases.append({"operation": "query", "args": list(case), "state": left})

    copy_cases = [(selector, True) for selector in range(34)]
    copy_cases.extend([(34, True), (0x100, True), (255, True),
                       (0, False), (34, False)])
    for case in copy_cases:
        stock, source = Machine(), Machine(True, segments, symbols)
        left = stock.run_query_copy(*case)
        right = source.run_query_copy(*case)
        assert left == right, ("query-copy", case, left, right)
        all_trace.update(stock.trace)
        cases.append({"operation": "query_copy", "args": list(case),
                      "state": left})

    cleanup_cases = [(2, False, 0, True), (0, True, 0, True),
                     (0, False, 0, True), (0, False, 7, True),
                     (1, False, 3, True), (0, False, 0, False)]
    for context, query_hit, finish_result, hook_installed in cleanup_cases:
        stock, source = Machine(), Machine(True, segments, symbols)
        left = stock.run_cleanup(context, query_hit, finish_result, hook_installed)
        right = source.run_cleanup(context, query_hit, finish_result,
                                   hook_installed)
        assert left == right, ("cleanup", context, query_hit, finish_result,
                               hook_installed, left, right)
        all_trace.update(stock.trace)
        cases.append({"operation": "cleanup", "args": [context, query_hit,
                      finish_result, hook_installed], "state": left})
    used = {pc + i for pc, raw in all_trace.items() for i in range(len(raw))}
    report = {
        "status": "PASS",
        "cases": len(cases),
        "distinct_original_instruction_bytes": len(used),
        "original_image_sha256": BLOB_SHA,
        "source_elf_sha256": sha(args.elf),
        "source_sha256": {
            str(path.relative_to(ROOT)): sha(path)
            for path in [ROOT / "g2/components/bootloader/platform_control/runtime.c",
                         ROOT / "g2/components/bootloader/platform_control/runtime.h",
                         ROOT / "g2/components/bootloader/platform_control/runtime_transition.c",
                         ROOT / "g2/components/bootloader/platform_control/runtime_transition.h",
                         ROOT / "g2/components/bootloader/platform_control/runtime_query.c",
                         ROOT / "g2/components/bootloader/platform_control/runtime_query.h",
                         ROOT / "g2/components/bootloader/platform_control/critical_save.S",
                         ROOT / "g2/components/bootloader/clock_manager/clock_class_providers.c",
                         HERE / "fixture_apply.c", HERE / "verify_runtime.py"]
        },
        "trace_addresses": [hex(pc) for pc in sorted(all_trace)],
        "comparisons": cases,
        "limits": [
            "Mode one and power-register update execute in source and stock. The 0x422ba8 null/object-magic checks and operation-greater-than-2 error branch are source-recovered; accepted objects continue through the explicit power-apply-configure cut.",
            "The stock 0x41b954 transition and source runtime_transition.c execute with source critical_save.S matching raw 0x41b8ec. Delay routines at 0x41d1c0/0x41d21c are explicit synthetic timing/status cuts; callback table calls are dispatched through synthetic targets.",
            "Cleanup query 0x41c2d8 and descriptor copier 0x41b8f8 execute in stock and source for all 34 selectors; stock 0x4156ac copy instructions execute in the original profile. Source execution maps no stock executable image, only required literal inputs and synthetic RAM/MMIO.",
            "All MMIO, callbacks, and completion timing are synthetic. This validates instruction/control/data effects for these profiles, not hardware timing, peripheral behavior, or the accepted-object power configuration tail."
        ]
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in
                      ["status", "cases", "distinct_original_instruction_bytes"]}))


if __name__ == "__main__":
    main()
