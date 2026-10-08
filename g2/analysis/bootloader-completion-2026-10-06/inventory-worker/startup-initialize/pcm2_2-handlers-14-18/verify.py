#!/usr/bin/env python3
"""Compare PCM2.2 handlers 14/18 from locked instructions vs compiled C."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import struct

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS
from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn import arm_const as a

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
IMAGE = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
FUNCTIONS = ROOT / "g2/research/corpus/apollo-bootloader/ghidra/open-2026-09-29/functions-000.jsonl"
ELF_READER = ROOT / "g2/components/bootloader/update_core/elf_reader.py"
ROOT_TARGETS = HERE.parent / "pcm2_2-native/stock-root-targets.json"
IMAGE_SHA = "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"
STOP = 0x08000000
HANDLERS = {
    14: (0x42944A, 0x42951C, "7c3fc667225097109aae57cd92a34f6858a8bdfff93e2fb6d9a700d042ce3760",
         "opencfw_spot_pcm22_transition14"),
    18: (0x42984E, 0x429A1E, "ebb8217a646d3261e01b47fa26f9ca9195377c11a6eefe3e47970b5b0dc77651",
         "opencfw_spot_pcm22_transition18"),
}
STATE = [0x200270B0, 0x200270B4, 0x200270B8, 0x200270BC,
         0x200270C0, 0x200270C4, 0x40020044, 0x40020048,
         0x4002004C, 0x40020080, 0x400083E0, 0x40008064,
         0x20026C04, 0x400083E8, 0x40008010, 0x40008068,
         0x4002037C, 0x40021000, 0x40004030, 0x40004044,
         0x20000550, 0x20027030, 0x20027044, 0x2002719C,
         0x2002719E, 0x2000055A, 0x47FF0000, 0xE000E108,
         0xE000E188, 0xE000E288, 0xE000ED14, 0xE000EF50]

spec = importlib.util.spec_from_file_location("elf_reader", ELF_READER)
elf_reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(elf_reader)


def p32(v): return struct.pack("<I", v & 0xffffffff)
def u32(b): return struct.unpack("<I", bytes(b))[0]


def pack_profile(vddf, core_active, core_tempco, vddc):
    return ((vddf & 0x7f) | ((core_active & 0x3ff) << 7) |
            ((core_tempco & 0xf) << 17) | ((vddc & 0x7f) << 21))


def fixtures():
    rows = []
    # These are the actual arguments recorded at each installed handler target.
    # Stock root traces report 240 calls to each target, all with (3,0,0,0).
    args = [3, 0, 0, 0]
    rows.append({"name": "observed-root-zero-profile", "args": args,
                 "profiles": [0] * 21, "low_voltage": [0, 0, 0, 0],
                 "mode": 0, "timer_control": 0, "timer_status": 0})
    for i in range(16):
        prof = [pack_profile((13 + i*7 + j*11) & 0x7f,
                             (31 + i*43 + j*71) & 0x3ff,
                             (i + 3*j) & 0xf,
                             (17 + i*9 + j*13) & 0x7f)
                for j in range(21)]
        rows.append({"name": f"observed-root-args-profile-{i}", "args": args,
                     "profiles": prof,
                     "low_voltage": [(i*11 + j*37) & 0x7f for j in range(4)],
                     "mode": 0, "timer_control": 0, "timer_status": 0})
    # Additional valid state indices exercise low-trim arithmetic; root's
    # encountered [3,0,0,0] calls remain separately named above.
    for i, (new, old) in enumerate(((1, 0), (2, 3), (7, 4), (19, 20), (20, 1))):
        prof = [pack_profile((i*17 + j*9) & 0x7f,
                             (i*97 + j*63) & 0x3ff,
                             (i + j) & 0xf,
                             (i*13 + j*19) & 0x7f) for j in range(21)]
        rows.append({"name": f"valid-index-pair-{new}-{old}",
                     "args": [new, old, i & 7, (i+1) & 7],
                     "profiles": prof,
                     "low_voltage": [(i*31 + j*41) & 0x7f for j in range(4)],
                     "mode": 0, "timer_control": 0, "timer_status": 0})
    for state in (2, 7, 26):
        for timer_status in (0x40000000, 0):
            i = state + (1 if timer_status else 7)
            prof = [pack_profile((13 + i*7 + j*11) & 0x7f,
                                 (31 + i*43 + j*71) & 0x3ff,
                                 (i + 3*j) & 0xf,
                                 (17 + i*9 + j*13) & 0x7f)
                    for j in range(21)]
            rows.append({"name": f"timer-state-{state}-status-{timer_status:08x}",
                         "args": [3, 0, 0, 0], "profiles": prof,
                         "low_voltage": [(i*11 + j*37) & 0x7f for j in range(4)],
                         "mode": 0, "timer_control": 0x80001235,
                         "timer_status": timer_status,
                         "timer_state": state, "clock_user": True})
    return rows


def seed(cpu, f):
    info = bytearray(0x6c)
    struct.pack_into("<I", info, 0, 0x1f01600d)
    for i, word in enumerate(f["profiles"]):
        struct.pack_into("<I", info, 4 + 4*i, word)
    info[0x64:0x68] = bytes(f["low_voltage"])
    cpu.mem_write(0x20026ba0, bytes(info))
    for addr in [0x200270b0, 0x200270b4, 0x200270b8, 0x200270bc,
                 0x200270c0, 0x200270c4]:
        cpu.mem_write(addr, p32(0x5a5a0000 | (addr & 0xffff)))
    for addr in [0x40020044, 0x40020048, 0x4002004c, 0x40020080]:
        cpu.mem_write(addr, p32(0xa5a50000 | (addr & 0xffff)))
    cpu.mem_write(0x40021000, p32(f["mode"]))
    cpu.mem_write(0x400083e0, p32(f["timer_control"]))
    cpu.mem_write(0x40008064, p32(f["timer_status"]))
    cpu.mem_write(0x400083e8, p32(0x1234))
    cpu.mem_write(0x40008010, p32(0x8000))
    cpu.mem_write(0x40008068, p32(0x76543210))
    cpu.mem_write(0x4002037c, p32(0xa5123456))
    cpu.mem_write(0x40004030, p32(0x01000000))
    cpu.mem_write(0x40004044, p32(0x20))
    cpu.mem_write(0x20000550, b"\x01")
    cpu.mem_write(0x20027030, p32(0))
    cpu.mem_write(0x20027044, p32(0))
    cpu.mem_write(0x2002719c, b"\x00")
    cpu.mem_write(0x2002719e, b"\x00")
    cpu.mem_write(0x20026e74, bytes(56))
    cpu.mem_write(0x47ff0000, p32(0x12345678))
    cpu.mem_write(0x2000055a, bytes([f.get("timer_state", 0)]))
    if f.get("clock_user"):
        cpu.mem_write(0x20026ea8, p32(1 << 17))
    cpu.reg_write(a.UC_ARM_REG_SP, 0x2003f000)
    cpu.reg_write(a.UC_ARM_REG_LR, STOP | 1)
    for i, v in enumerate(f["args"]):
        cpu.reg_write(getattr(a, f"UC_ARM_REG_R{i}"), v)
    cpu.reg_write(a.UC_ARM_REG_PRIMASK, 0)


def run(stock, image, segments, symbols, f, target):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
    for lo, sz in [(0, 0x1000), (0x08000000, 0x1000),
                   (0x10000, 0x30000), (0x20000000, 0x40000),
                   (0x40000000, 0x100000), (0x410000, 0x25000),
                   (0xE0000000, 0x200000), (0x47FF0000, 0x1000)]:
        cpu.mem_map(lo, sz)
    if stock:
        cpu.mem_write(0x410000, image)
        start = target[0]
    else:
        for seg in segments:
            cpu.mem_write(seg["address"], seg["data"])
        start = symbols[target[3]] & ~1
    seed(cpu, f)
    writes, waits, visited = [], [], set()
    done = [False]

    def code(uc, pc, size, _):
        if pc == STOP:
            done[0] = True
            uc.emu_stop()
            return
        if pc == 0x40:
            waits.append(uc.reg_read(a.UC_ARM_REG_R0))
            uc.reg_write(a.UC_ARM_REG_PC, uc.reg_read(a.UC_ARM_REG_LR))
            return
        if stock and target[0] <= pc < target[1]:
            visited.update(range(pc, pc + size))
        if not stock and 0x410000 <= pc < 0x435000:
            raise AssertionError(f"source entered locked code at {pc:#x}")

    def write(uc, access, addr, size, value, _):
        if (0x40000000 <= addr < 0x40100000 or
                0xE0000000 <= addr < 0xE0020000):
            writes.append([addr, size, value & ((1 << (size * 8)) - 1)])

    cpu.hook_add(UC_HOOK_CODE, code)
    cpu.hook_add(UC_HOOK_MEM_WRITE, write, begin=0x40000000, end=0x400fffff)
    try:
        cpu.emu_start(start | 1, 0, count=200000)
    except Exception as exc:
        raise RuntimeError(f"{f['name']} handler{target[0]:#x} {'stock' if stock else 'source'} pc={cpu.reg_read(a.UC_ARM_REG_PC):#x}") from exc
    assert done[0], (f["name"], "did not return", hex(cpu.reg_read(a.UC_ARM_REG_PC)))
    return ({"return": cpu.reg_read(a.UC_ARM_REG_R0),
             "state": {f"{addr:08x}": bytes(cpu.mem_read(addr, 4)).hex()
                       for addr in STATE},
             "writes": writes, "rom_wait_values": waits,
             "callee_saved": [cpu.reg_read(getattr(a, f"UC_ARM_REG_R{i}"))
                              for i in range(4, 12)],
             "sp": cpu.reg_read(a.UC_ARM_REG_SP),
             "primask": cpu.reg_read(a.UC_ARM_REG_PRIMASK)}, visited)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--elf", type=Path, default=HERE / "handlers.elf")
    ap.add_argument("--output", type=Path, default=HERE / "comparison.json")
    args = ap.parse_args()
    image = IMAGE.read_bytes()
    assert hashlib.sha256(image).hexdigest() == IMAGE_SHA
    _, segments, symbols = elf_reader.elf_info(args.elf)
    funcs = {int((d := json.loads(line))["entry"], 16): d
             for line in FUNCTIONS.read_text().splitlines()}
    root = json.loads(ROOT_TARGETS.read_text())
    assert root["original_sha256"] == IMAGE_SHA
    for n in (14, 18):
        entry, end, digest, _ = HANDLERS[n]
        selected = root["selected_targets"][str(n)]
        assert selected["entry"] == hex(entry) and selected["calls"] == 240
        assert all(args == [3, 0, 0, 0] for args in selected["arguments"])
        record = funcs[entry]
        body = image[entry - 0x410000:end - 0x410000]
        assert int(record["body_end_inclusive"], 16) + 1 == end
        assert len(body) == end - entry and hashlib.sha256(body).hexdigest() == digest
        assert hashlib.sha256(body[:-1]).hexdigest() != digest
        assert hashlib.sha256(image[entry-0x410000:end+1-0x410000]).hexdigest() != digest
    rows = []
    coverage = {n: set() for n in HANDLERS}
    for f in fixtures():
        for n, target in HANDLERS.items():
            stock, visited = run(True, image, segments, symbols, f, target)
            source, _ = run(False, image, segments, symbols, f, target)
            assert stock == source, (n, f["name"], stock, source)
            rows.append({"handler": n, "fixture": f, "result": stock})
            coverage[n] |= visited
    output = {
        "status": "PASS", "image_sha256": IMAGE_SHA,
        "source_elf_sha256": hashlib.sha256(args.elf.read_bytes()).hexdigest(),
        "root_argument_evidence": {str(n): {"calls": root["selected_targets"][str(n)]["calls"],
            "observed_args": root["selected_targets"][str(n)]["arguments"]}
            for n in (14, 18)},
        "handlers": {str(n): {"entry": hex(x[0]), "end_exclusive": hex(x[1]),
            "bytes": x[1]-x[0], "sha256": x[2],
            "visited_stock_bytes": len(coverage[n]),
            "unvisited_addresses": [hex(a) for a in sorted(set(range(x[0],x[1])) - coverage[n])]} 
            for n, x in HANDLERS.items()},
        "cases_per_handler": len(fixtures()), "comparisons": rows,
        "limits": ["Timer-enabled cases enter the reconstructed timer service and exercise sequence states 2, 7, and 26; peripheral/MMIO behavior remains offline emulation.",
                   "No hardware or complete PCM2.2 source/build equivalence is claimed."]}
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    print("PASS", len(rows), "handler/fixture pairs",
          {n: len(v) for n, v in coverage.items()}, "stock instruction bytes visited")


if __name__ == "__main__":
    main()
