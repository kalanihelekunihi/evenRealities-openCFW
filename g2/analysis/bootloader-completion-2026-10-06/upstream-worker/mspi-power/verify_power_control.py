#!/usr/bin/env python3
"""Unicorn stock/source comparison for locked MSPI power-control 0x426808."""
import argparse
import hashlib
import importlib.util
import json
import random
import struct
from pathlib import Path

from unicorn import Uc, UcError, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as a

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
spec = importlib.util.spec_from_file_location(
    "elf_reader", ROOT / "g2/components/bootloader/update_core/elf_reader.py")
elf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(elf)
spec = importlib.util.spec_from_file_location(
    "update_verify", ROOT / "g2/components/bootloader/update_core/verify.py")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

IMAGE = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
IMAGE_SHA = "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"
FUNC = 0x426808
END = 0x426bfe
STOP = 0x08000000
HANDLE = 0x20001000
OPS = 0x20002000
STACK = 0x2003f000
MMIO = 0x40060000
MODULE_STRIDE = 0x1000

STOCK = {
    0x41bf84: "mode_enter",
    0x41c17a: "mode_leave",
    0x4222f0: "clock_request",
    0x4223d8: "clock_release_all",
    0x4249a0: "clockgen",
    0x423fac: "cq_disable",
    0x423f8e: "cq_enable",
    0x426484: "interrupt_disable",
    0x41d1c0: "delay_us",
}
SHIMS = {0x08000100 + i * 0x20: name for i, name in enumerate((
    "mode_enter", "mode_leave", "clock_request", "clock_release_all",
    "clockgen", "cq_disable", "cq_enable", "interrupt_disable",
    "delay_us", "mmio_read", "mmio_write"))}
SHIM_ADDR = {name: address for address, name in SHIMS.items()}

sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Machine:
    def __init__(self, source, segments=(), symbols=None, *,
                 clock_status=None, release_status=0):
        self.source = source
        self.symbols = symbols or {}
        self.clock_status = dict(clock_status or {})
        self.release_status = release_status
        self.clock_calls = 0
        self.events = []
        self.trace = {}
        self.debug = []
        self.finished = False
        self.uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        self.uc.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
        self.uc.mem_map(0x410000, 0x25000)
        if not source:
            blob = IMAGE.read_bytes()
            self.uc.mem_write(0x410000, blob)
            self.exec_ranges = [(0x410000, 0x410000 + len(blob))]
        else:
            self.exec_ranges = []
            for seg in segments:
                lo = seg["address"] & ~0xfff
                hi = (seg["address"] + seg["memory_size"] + 0xfff) & ~0xfff
                if not (0x410000 <= lo < 0x435000):
                    self.uc.mem_map(lo, hi - lo)
                self.uc.mem_write(seg["address"], seg["data"])
                if seg["flags"] & 1:
                    self.exec_ranges.append((seg["address"],
                                             seg["address"] + len(seg["data"])))
        self.uc.mem_map(0x20000000, 0x40000)
        self.uc.mem_map(STOP, 0x10000)
        self.uc.mem_map(MMIO, 0x200000)
        if source:
            ptrs = [SHIM_ADDR[k] | 1 for k in (
                "mode_enter", "mode_leave", "clock_request", "clock_release_all",
                "clockgen", "cq_disable", "cq_enable", "interrupt_disable",
                "delay_us", "mmio_read", "mmio_write")]
            self.uc.mem_write(OPS, struct.pack("<11I", *ptrs))
        self.uc.hook_add(UC_HOOK_CODE, self.code)

    def u32(self, address):
        return struct.unpack("<I", self.uc.mem_read(address, 4))[0]

    def w32(self, address, value):
        self.uc.mem_write(address, struct.pack("<I", value & 0xffffffff))

    def args(self):
        return [self.uc.reg_read(reg) for reg in (
            a.UC_ARM_REG_R0, a.UC_ARM_REG_R1,
            a.UC_ARM_REG_R2, a.UC_ARM_REG_R3)]

    def ret(self, value=0):
        self.uc.reg_write(a.UC_ARM_REG_R0, value & 0xffffffff)
        self.uc.reg_write(a.UC_ARM_REG_PC, self.uc.reg_read(a.UC_ARM_REG_LR))

    def helper(self, name, args):
        if name == "clock_request":
            clock, user = args[:2]
            result = self.clock_status.get(self.clock_calls, 0)
            self.clock_calls += 1
            self.events.append([name, clock & 0xff, user & 0xff, result])
            return result
        if name == "clock_release_all":
            self.events.append([name, args[0] & 0xff, self.release_status])
            return self.release_status
        if name in ("mode_enter", "mode_leave"):
            self.events.append([name, args[0] & 0xff])
            return 0
        if name == "clockgen":
            self.events.append([name, args[0], *[x & 0xff for x in args[1:4]]])
            return 0
        if name == "cq_disable":
            handle = args[0]
            cq = self.u32(handle + 0x828)
            self.events.extend([[name, handle], ["cmdq_disable", cq]])
            return 0
        if name == "cq_enable":
            handle = args[0]
            self.events.append([name, handle])
            status = self.helper("clock_request", [4, (self.u32(handle + 4) + 0x10) & 0xff])
            if status == 0:
                self.events.append(["cmdq_enable", self.u32(handle + 0x828)])
            return 0
        if name == "interrupt_disable":
            module = self.u32(args[0] + 4)
            address = MMIO + module * MODULE_STRIDE + 0x200
            self.w32(address, self.u32(address) & ~args[1])
            return 0
        if name == "delay_us":
            self.events.append([name, args[0]])
            return 0
        if name == "mmio_read":
            address = MMIO + args[0] * MODULE_STRIDE + args[1]
            return self.u32(address)
        if name == "mmio_write":
            address = MMIO + args[0] * MODULE_STRIDE + args[1]
            self.w32(address, args[2])
            return 0
        raise AssertionError(("unknown provider", name, [hex(x) for x in args]))

    def code(self, uc, pc, size, _):
        if not self.source and pc == 0x426bc2:
            r1 = uc.reg_read(a.UC_ARM_REG_R1)
            self.debug.append([hex(r1), hex(self.u32(r1 + 0x90))])
        if pc == STOP:
            self.finished = True
            uc.emu_stop()
            return
        if self.source and pc in SHIMS:
            name = SHIMS[pc]
            result = self.helper(name, self.args())
            self.ret(result)
            return
        if not self.source and pc in STOCK:
            name = STOCK[pc]
            result = self.helper(name, self.args())
            self.ret(result)
            return
        if self.source:
            assert any(lo <= pc < hi for lo, hi in self.exec_ranges), (
                "source execution escaped compiled provider", hex(pc))
        else:
            assert FUNC <= pc < END, ("unexpected stock callee", hex(pc))
            self.trace[hex(pc)] = bytes(uc.mem_read(pc, size)).hex()

    def setup(self, fixture):
        self.events.clear()
        self.trace.clear()
        self.clock_calls = 0
        self.finished = False
        h = bytearray(0x8d0)
        struct.pack_into("<I", h, 0, fixture.get("magic", 0x01bebebe))
        struct.pack_into("<I", h, 4, fixture.get("module", 1))
        struct.pack_into("<I", h, 8 * 4, fixture.get("handle_busy", 0))
        struct.pack_into("<I", h, 0x210 * 4, fixture.get("active", 0))
        h[0x860] = fixture.get("save_valid", 0)
        h[0x8c9] = fixture.get("clock_class", 4)
        struct.pack_into("<I", h, 0x233 * 4, fixture.get("delay", 37))
        self.uc.mem_write(HANDLE, bytes(h))
        region = bytearray(0x1000)
        rng = random.Random(fixture.get("seed", 0x426808))
        for off in range(0, 0x300, 4):
            struct.pack_into("<I", region, off, rng.getrandbits(32))
        struct.pack_into("<I", region, 0x090, fixture.get("xip", 0))
        struct.pack_into("<I", region, 0x2a0, fixture.get("cqcfg", 0))
        self.uc.mem_write(MMIO + fixture.get("module", 1) * MODULE_STRIDE,
                          bytes(region))

    def run(self, operation, retain):
        args = [HANDLE, operation, retain, OPS if self.source else 0]
        regs = [a.UC_ARM_REG_R0, a.UC_ARM_REG_R1,
                a.UC_ARM_REG_R2, a.UC_ARM_REG_R3]
        for reg, val in zip(regs, args):
            self.uc.reg_write(reg, val)
        self.uc.reg_write(a.UC_ARM_REG_SP, STACK)
        self.uc.reg_write(a.UC_ARM_REG_LR, STOP | 1)
        entry = ((self.symbols["opencfw_bl_power_control"] & ~1)
                 if self.source else FUNC)
        try:
            self.uc.emu_start(entry | 1, STOP + 0x10000, count=1000000)
        except UcError:
            pc = self.uc.reg_read(a.UC_ARM_REG_PC)
            print("execution fault", "source" if self.source else "stock",
                  hex(pc), bytes(self.uc.mem_read(pc, 8)).hex())
            raise
        assert self.finished, (self.source, "return sentinel not reached",
                               hex(self.uc.reg_read(a.UC_ARM_REG_PC)))
        module = struct.unpack_from("<I", self.uc.mem_read(HANDLE + 4, 4))[0]
        return {
            "return": self.uc.reg_read(a.UC_ARM_REG_R0),
            "events": list(self.events),
            "handle": bytes(self.uc.mem_read(HANDLE, 0x8d0)).hex(),
            "mmio": bytes(self.uc.mem_read(MMIO + module * MODULE_STRIDE,
                                            0x300)).hex(),
        }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--elf", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    assert sha(IMAGE) == IMAGE_SHA
    _, segments, symbols = elf.elf_info(args.elf)
    fixtures = [
        ("null-handle", {"null": 1}, 1, 0),
        ("bad-magic", {"magic": 0}, 1, 0),
        ("invalid-operation", {}, 3, 0),
        ("operation-byte-truncation", {}, 0x102, 0),
        ("busy-active-count", {"active": 1}, 1, 0),
        ("busy-handle-state", {"handle_busy": 1}, 2, 0),
        ("retain-without-saved-state", {}, 0, 1),
        ("retain-invalid-clock-class", {"save_valid": 1, "clock_class": 7}, 0, 1),
        ("clock-request-error", {}, 0, 0, {0: 9}),
        ("clock-request-error-retain", {"save_valid": 1, "clock_class": 5}, 0, 1, {0: 7}),
        ("operation-zero-enable", {}, 0, 0),
        ("operation-zero-restore", {"save_valid": 1, "clock_class": 3}, 0, 1),
        ("operation-zero-restore-cq", {"save_valid": 1, "clock_class": 4, "cqcfg": 1}, 0, 1),
        ("power-down-no-retain", {}, 1, 0),
        ("power-down-retain", {"cqcfg": 0}, 2, 1),
        ("power-down-retain-cq-enabled", {"cqcfg": 0x80000001}, 1, 1),
        ("xip-delay-power-down", {"xip": 1, "delay": 123}, 1, 0),
        ("release-all-error", {}, 2, 0, {}, 6),
        ("module-byte-and-user-byte", {"module": 0x101}, 0x101, 0),
    ]
    out = []
    trace = {}
    used = set()
    for item in fixtures:
        name, fixture, op, retain, *statuses = item
        clock_status = statuses[0] if statuses else {}
        release_status = statuses[1] if len(statuses) > 1 else 0
        if fixture.get("null"):
            # The exact entry null guard is compared in stock. The C ABI's
            # callbacks are required for other cases; handle-only null is
            # checked against a separate source wrapper call below.
            continue
        pair = [Machine(False, clock_status=clock_status,
                        release_status=release_status),
                Machine(True, segments, symbols, clock_status=clock_status,
                        release_status=release_status)]
        observed = []
        for machine in pair:
            machine.setup(fixture)
            observed.append(machine.run(op, retain))
        assert observed[0] == observed[1], (name, {
            key: [obs[key] for obs in observed]
            for key in observed[0] if observed[0][key] != observed[1][key]
        }, pair[0].trace, pair[0].events, pair[1].events, pair[0].debug)
        trace.update(pair[0].trace)
        used.update(int(pc, 0) + n for pc, raw in pair[0].trace.items()
                    for n in range(len(bytes.fromhex(raw))))
        out.append({"name": name, "operation": hex(op), "retain": hex(retain),
                    "fixture": fixture, "return": observed[0]["return"],
                    "events": observed[0]["events"],
                    "handle_sha256": hashlib.sha256(
                        bytes.fromhex(observed[0]["handle"])).hexdigest(),
                    "mmio_sha256": hashlib.sha256(
                        bytes.fromhex(observed[0]["mmio"])).hexdigest()})

    # The null branch is compared by direct call with ops=NULL; stock ignores
    # R3 and the source returns before dereferencing R3.
    pair = [Machine(False), Machine(True, segments, symbols)]
    null_results = []
    for machine in pair:
        machine.setup({})
        for reg, value in zip((a.UC_ARM_REG_R0, a.UC_ARM_REG_R1,
                               a.UC_ARM_REG_R2, a.UC_ARM_REG_R3),
                              (0, 1, 0, 0)):
            machine.uc.reg_write(reg, value)
        machine.uc.reg_write(a.UC_ARM_REG_SP, STACK)
        machine.uc.reg_write(a.UC_ARM_REG_LR, STOP | 1)
        entry = ((symbols["opencfw_bl_power_control"] & ~1)
                 if machine.source else FUNC)
        machine.uc.emu_start(entry | 1, STOP + 0x10000, count=100000)
        assert machine.finished
        null_results.append(machine.uc.reg_read(a.UC_ARM_REG_R0))
    assert null_results == [2, 2], null_results
    out.append({"name": "null-handle", "return": 2})

    report = {
        "status": "PASS",
        "cases": len(out),
        "original_sha256": IMAGE_SHA,
        "source_elf_sha256": sha(args.elf),
        "source_sha256": {
            str(p.relative_to(ROOT)): sha(p)
            for p in [*HERE.iterdir(),
                      ROOT / "g2/components/bootloader/nor_mspi_power/power_control.c",
                      ROOT / "g2/components/bootloader/nor_mspi_power/power_control.h",
                      ROOT / "g2/components/bootloader/nor_mspi_power/power_control_adapter.c",
                      ROOT / "g2/components/bootloader/nor_mspi_power/power_control_adapter.h"]
            if p.is_file() and p.suffix in {".c", ".h", ".ld", ".py"}
        },
        "distinct_original_instruction_bytes": len(used),
        "original_instruction_trace": trace,
        "comparisons": out,
        "limits": [
            "Original 0x426808 instruction bytes execute for each compared case; direct calls to the listed platform/CQ/interrupt/delay providers are intercepted and state-identical synthetic models are used for the source callbacks.",
            "MSPI register addresses at 0x40060000 + module*0x1000 are synthetic Unicorn memory; no physical hardware is accessed.",
            "Clock-generator and command-queue internals remain callback boundaries; their callback arguments and ordering are compared, not peripheral timing or physical CQ effects.",
            "This profile is not a firmware link or byte-identical rebuild claim.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "cases": report["cases"],
                      "distinct_original_instruction_bytes": len(used)}))


if __name__ == "__main__":
    main()
