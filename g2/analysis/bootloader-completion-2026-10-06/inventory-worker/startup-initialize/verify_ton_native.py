"""Stock/source behavioral comparison for the two tone trim callbacks."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import itertools
import json
import struct
from pathlib import Path

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn import arm_const as a

ROOT = Path(__file__).resolve().parents[5]
BOOT = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
EXPECTED = "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"
EXTENTS = {"cache": (0x42F41A, 0x42F4B2), "apply": (0x42F4B2, 0x42F5F0)}
STOP = 0x08000000
CUTS = {0x41C838: "cut_41c838", 0x41D1C0: "cut_41d1c0",
        0x08000100: "cut_41c838", 0x08000120: "cut_41d1c0"}

ap = argparse.ArgumentParser()
ap.add_argument("--elf", type=Path, required=True)
ap.add_argument("--output", type=Path, required=True)
args = ap.parse_args()
blob = BOOT.read_bytes()
assert hashlib.sha256(blob).hexdigest() == EXPECTED
reader = ROOT / "g2/components/bootloader/update_core/elf_reader.py"
spec = importlib.util.spec_from_file_location("elf_reader", reader)
elf_reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(elf_reader)
_, segments, symbols = elf_reader.elf_info(args.elf)
entries = {"cache": ("opencfw_ton_trim_cache", 0x42F41A),
           "apply": ("opencfw_ton_trim_apply", 0x42F4B2)}

def u32(cpu, address):
    return struct.unpack("<I", cpu.mem_read(address, 4))[0]

def put32(cpu, address, value):
    cpu.mem_write(address, struct.pack("<I", value & 0xffffffff))

def intervals(addresses):
    out = []
    for value in sorted(addresses):
        if not out or value != out[-1][1]:
            out.append([value, value + 1])
        else:
            out[-1][1] += 1
    return [[hex(lo), hex(hi)] for lo, hi in out]

def run(source, name, f, trace):
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
    for lo, size in [(0x410000, 0x25000), (0x10000, 0x10000),
                     (0x08000000, 0x1000), (0x20000000, 0x40000),
                     (0x40000000, 0x100000)]:
        u.mem_map(lo, size)
    if not source:
        u.mem_write(0x410000, blob)
    else:
        # Locked 3-row configuration table is data only; no stock executable fallback.
        u.mem_write(0x433f20, blob[0x23f20:0x23f29])
    if source:
        for seg in segments:
            u.mem_write(seg["address"], seg["data"])
    put32(u, 0x4002000c, f.get("revision", 0))
    put32(u, 0x20000098, f.get("variant", 0))
    put32(u, 0x40020344, f.get("reg344", 0xa53c7691))
    put32(u, 0x4002034c, f.get("reg34c", 0x91e2b75a))
    put32(u, 0x40020354, f.get("reg354", 0x23456789))
    put32(u, 0x40020358, f.get("reg358", 0x89abcdef))
    put32(u, 0x40020340, f.get("reg340", 0x13579bdf))
    put32(u, 0x40021100, (f.get("state", 0) & 1) | 0xa5a5a5a0)
    for p, value in zip(range(0x20000554, 0x2000055a),
                        f.get("cache", [14, 31, 11, 7, 21, 31])):
        u.mem_write(p, bytes([value & 0xff]))

    done = False
    cuts = []
    writes = []
    def code_hook(cpu, pc, size, _):
        nonlocal done
        pc &= ~1
        if pc == STOP:
            done = True
            cpu.emu_stop()
            return
        if not source and EXTENTS[name][0] <= pc < EXTENTS[name][1]:
            trace.setdefault(name, {})[pc] = size
        if pc in CUTS and CUTS[pc] == "cut_41d1c0":
            ident = CUTS[pc]
            value = cpu.reg_read(a.UC_ARM_REG_R0)
            cuts.append([ident, value])
            # Both cut return values are ignored by these callers.
            cpu.reg_write(a.UC_ARM_REG_R0, f.get("cut_status", 0))
            cpu.reg_write(a.UC_ARM_REG_PC, cpu.reg_read(a.UC_ARM_REG_LR))
    def write_hook(cpu, access, address, size, value, _):
        if 0x20000000 <= address < 0x20040000 or 0x40000000 <= address < 0x40100000:
            writes.append([address, size, value & ((1 << (size * 8)) - 1)])
    u.hook_add(UC_HOOK_CODE, code_hook)
    u.hook_add(UC_HOOK_MEM_WRITE, write_hook, begin=0x40000000, end=0x400fffff)
    u.reg_write(a.UC_ARM_REG_SP, 0x2003f000)
    u.reg_write(a.UC_ARM_REG_LR, STOP | 1)
    if name == "apply":
        u.reg_write(a.UC_ARM_REG_R0, f.get("gpu_on", 0))
        u.reg_write(a.UC_ARM_REG_R1, f.get("gpu_mode", 0))
    entry = (symbols[entries[name][0]] & ~1) if source else entries[name][1]
    u.emu_start(entry | 1, STOP + 2, count=10000)
    assert done, (source, name, f, hex(u.reg_read(a.UC_ARM_REG_PC)))
    memory = {}
    ranges = ([(0x20000554, 6)] if name == "cache" else [])
    ranges += [(p, 4) for p in [0x40020340, 0x40020344, 0x4002034c,
                                0x40020354, 0x40020358, 0x40021100, 0x40020060]]
    for p, n in ranges:
        memory[hex(p)] = bytes(u.mem_read(p, n)).hex()
    return {"return": u.reg_read(a.UC_ARM_REG_R0), "cuts": cuts,
            "writes": writes, "memory": memory}

fixtures = []
for revision, variant in itertools.product([0, 32, 33, 34, 35, 255], [0, 1, 3, 0xffffffff]):
    fixtures.append(("cache", {"revision": revision, "variant": variant,
                                "reg344": 0xa53c7691, "reg34c": 0x91e2b75a,
                                "reg354": 0x23456789, "reg358": 0x89abcdef}))
for gpu_on, gpu_mode, state, cache in itertools.product(
        [0, 1, 2, 0x100, 0xffffffff], [0, 1, 2, 0x100, 0xffffffff],
        [0, 1], [[1, 2, 3, 4, 5, 6], [31, 30, 29, 28, 27, 26]]):
    fixtures.append(("apply", {"gpu_on": gpu_on, "gpu_mode": gpu_mode,
                                "state": state, "cache": cache,
                                "cut_status": 7}))

trace = {}
rows = []
for name, fixture in fixtures:
    stock = run(False, name, fixture, trace)
    source = run(True, name, fixture, trace)
    if stock != source:
        args.output.with_suffix(".failure.json").write_text(json.dumps(
            {"name": name, "fixture": fixture, "stock": stock, "source": source}, indent=2) + "\n")
        raise AssertionError((name, fixture, stock, source))
    rows.append({"name": name, "fixture": fixture, "result": stock})

coverage = {}
for name, (lo, hi) in EXTENTS.items():
    visited = set()
    # Hooks report instruction widths; executions cover each address byte.
    for pc, size in trace.get(name, {}).items():
        visited.update(range(pc, pc + size))
    image = set(range(lo, hi))
    assert visited <= image
    for pc in trace.get(name, {}):
        size = trace[name][pc]
        off = pc - 0x410000
        assert lo <= pc < hi and blob[off:off + size]
    coverage[name] = {"extent": [hex(lo), hex(hi)], "extent_bytes": hi - lo,
                      "visited_bytes": len(visited),
                      "unvisited_bytes": len(image - visited),
                      "unvisited_ranges": intervals(image - visited)}

source_hashes = {}
for filename in ["ton_hooks.c", "ton_hooks.h", "module.ld"]:
    source_hashes[filename] = hashlib.sha256((ROOT / "g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-ton-hooks" / filename).read_bytes()).hexdigest()
function_hashes = {}
for name, (lo, hi) in EXTENTS.items():
    function_hashes[name] = hashlib.sha256(blob[lo - 0x410000:hi - 0x410000]).hexdigest()

result = {
    "status": "PASS", "cases": len(rows),
    "original_sha256": hashlib.sha256(blob).hexdigest(),
    "elf_sha256": hashlib.sha256(args.elf.read_bytes()).hexdigest(),
    "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "source_sha256": source_hashes,
    "original_function_sha256": function_hashes,
    "coverage": coverage, "comparisons": rows,
    "limits": [
        "Stock/source synchronous behavior compared under Unicorn Cortex-M33 with synthetic MMIO/register seeds; this is not physical hardware validation.",
        "Enable helper 41c838 executes natively on both sides. Delay41d1c0 remains an explicit synthetic elapsed-time cut. Source machine contains no locked executable bytes; only nine authenticated configuration data bytes.",
        "Behavioral correspondence to these locked bytes does not establish identity with Apollo510 HAL 5.1 or any other source release.",
    ],
}
args.output.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"status": result["status"], "cases": result["cases"], "coverage": coverage}, indent=2))
