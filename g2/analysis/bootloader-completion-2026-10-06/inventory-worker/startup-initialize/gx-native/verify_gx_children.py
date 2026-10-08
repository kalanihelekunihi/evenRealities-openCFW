#!/usr/bin/env python3
"""Standalone original-instruction differential tests for reconstructed leaves."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import math
import struct

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS
from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn import arm_const as a

ROOT = Path(__file__).resolve().parents[6]
HERE = Path(__file__).resolve().parent
IMAGE = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
ELF_READER = ROOT / "g2/components/bootloader/update_core/elf_reader.py"
IMAGE_HASH = "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"
CASES = {
    "temperature": (0x42AD40, 0x42ADB8, "89f71050cf7850205a7a5ef9ccfb09dfadaadd5a6046355844d800589b65607d"),
    "transition_effect": (0x42B014, 0x42B068, "b3da01a94a3c08eb7eb0d7d344b6760d929296878e2dfbf9c4770373aedd3d88"),
    "state_decode": (0x42B6B8, 0x42B9BA, "74f4304f6e3aa59022a29eb5e5f5479c77072b33355825b7c9409897001bb9d1"),
    "buck_deepsleep_scan": (0x42AEF0, 0x42B010, "7a54959ea8247c505df0f3139ce607b4d1fabb5d0015054b89bd44b5d79cc31b"),
}
PREDICATE = (0x41F3F0, 0x41F424, "2629a71d82c78f7602d8f37273ae02bcf42f237cdaab9da0d4db6d57a1045692")
spec = importlib.util.spec_from_file_location("elf_reader", ELF_READER)
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


def u32(data): return struct.unpack("<I", bytes(data))[0]
def pack(v): return struct.pack("<I", v & 0xffffffff)


def float_inputs():
    values = [-math.inf, -1000.0, -300.0001, -300.0, -299.9999,
              -273.0001, -273.0, -272.9999,
              -20.0001, -20.0, -19.9999, -0.0001, -0.0, 0.0,
              0.0001, 49.9999, 50.0, 50.0001, 999.9999, 1000.0,
              1000.0001, math.inf, math.nan]
    return [(f"f32-{v!r}", struct.unpack("<I", struct.pack("<f", v))[0])
            for v in values]


def effect_inputs():
    pairs = {(requested, current) for requested in range(3) for current in range(3)}
    pairs.update({(0, 1), (2, 1), (2, 0), (1, 2), (1, 0), (0, 0)})
    return sorted(pairs)


def decoder_inputs():
    rows = []
    for mode in (0, 1):
        for cfg_hi in range(8):
            config = cfg_hi << 21
            for temp in range(16):
                for state in (0, 1):
                    for auxiliary in range(4):
                        for powered in (0, 1):
                            words = [1 if powered else 0,
                                     0x4c4 if powered else 0, 0x12345678,
                                     0xabcdef00]
                            rows.append((f"m{mode}-cfg{cfg_hi:x}-t{temp}-s{state}-a{auxiliary}-p{powered}",
                                         words, temp, state, auxiliary, config, 0, mode))
    for mode in (0, 1):
        for temp in range(16):
            for state in (2, 255):
                for hw in (0, 2):
                    for auxiliary in range(4):
                        rows.append((f"m{mode}-t{temp}-s{state}-hw{hw}-a{auxiliary}",
                                     [0, 0, 0, 0], temp, state, auxiliary,
                                     0, hw, mode))
    for mode in (0, 1):
        for temp in range(16):
            for high in (0x400000, 0x800000, 0xc00000):
                rows.append((f"high-bus-{mode}-{temp}-{high:x}",
                             [high, 0, 0, 0], temp, 1, 0,
                             0, 0, mode))
    for config in (0x000ffcff, 0x00011001, 0x00012001, 0x000fffff, 0xffffffff):
        for mode in (0, 1):
            for temp in (0, 1, 2, 3, 15):
                rows.append((f"cfg-{config:08x}-m{mode}-t{temp}",
                             [0, 0, 0, 0], temp, 1, 0,
                             config, 2, mode))
    return rows


def scanner_inputs():
    base = dict(snapshot=[0, 0, 0, 0], temperature=0, gate=0,
                predicate_enable=0, mode=0, active=0, channels={})
    rows = []
    def add(name, **kw):
        f = dict(base); f.update(kw); f["name"] = name; rows.append(f)
    add("temperature-fast-exit", temperature=3)
    add("snapshot-fast-exit", snapshot=[1, 0, 0, 0])
    add("snapshot-fast-exit-secondary", snapshot=[0, 0x4c4, 0, 0])
    add("global-gate-bit29", gate=0x20000000)
    add("predicate-valid-power1", predicate_enable=1, mode=1)
    add("predicate-valid-power2", predicate_enable=1, mode=2)
    add("predicate-invalid-zero", predicate_enable=1, mode=0)
    add("predicate-negative-bit31", predicate_enable=1, mode=0x80000001)
    add("predicate-invalid-topbit", predicate_enable=1, mode=0x40000001)
    for kind, want in ((0, 1), (5, 1), (6, 0), (18, 0), (19, 1),
                       (24, 1), (25, 0), (255, 0), (256, 1),
                       (300, 1), (479, 1), (480, 0)):
        channels = {0: 1 | (kind << 8)}
        add(f"class-{kind}-want-{want}", active=1, channels=channels)
    for slot in range(16):
        add(f"active-slot-{slot}", active=1 << slot,
            channels={slot: 1 | (300 << 8)})
    add("inactive-channel", active=0, channels={15: 1 | (5 << 8)})
    add("mixed-late-invalid", active=1 << 15,
        channels={0: 1 | (300 << 8), 15: 1 | (25 << 8)})
    return rows


def run_scanner(stock, image, segments, symbols, fixture):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
    for lo, size in [(0, 0x1000), (0x08000000, 0x1000),
                     (0x10000, 0x10000), (0x30000, 0x10000), (0x20000000, 0x40000),
                     (0x40000000, 0x100000), (0x410000, 0x25000)]:
        cpu.mem_map(lo, size)
    if stock:
        cpu.mem_write(0x410000, image)
        start = CASES["buck_deepsleep_scan"][0]
    else:
        for seg in segments: cpu.mem_write(seg["address"], seg["data"])
        start = symbols["native_spot_buck_deepsleep_scan"] & ~1
    inp = 0x20001000
    data = b"".join(pack(w) for w in fixture["snapshot"])
    data += bytes([fixture["temperature"]]) + b"\x00" * 3
    cpu.mem_write(inp, data)
    cpu.mem_write(0x200271C0, b"\xa5")
    cpu.mem_write(0x200271BF, bytes([fixture["predicate_enable"]]))
    cpu.mem_write(0x400204D8, pack(fixture["gate"]))
    cpu.mem_write(0x40008800, pack(fixture["mode"]))
    cpu.mem_write(0x40008010, pack(fixture["active"]))
    for slot, value in fixture["channels"].items():
        cpu.mem_write(0x40008200 + slot * 0x20, pack(value))
    cpu.reg_write(a.UC_ARM_REG_SP, 0x2003F000)
    cpu.reg_write(a.UC_ARM_REG_LR, 0x08000001)
    cpu.reg_write(a.UC_ARM_REG_R0, inp)
    cpu.reg_write(a.UC_ARM_REG_R1, fixture["temperature"])
    visited, done = set(), [False]
    begin, end = CASES["buck_deepsleep_scan"][:2]
    def code(uc, pc, size, _):
        if pc == 0x08000000:
            done[0] = True; uc.emu_stop(); return
        if stock and begin <= pc < end: visited.update(range(pc, pc + size))
        if not stock and 0x410000 <= pc < 0x435000:
            raise AssertionError(f"source entered locked firmware at {pc:#x}")
    cpu.hook_add(UC_HOOK_CODE, code)
    cpu.emu_start(start | 1, 0, count=20000)
    assert done[0], (fixture["name"], hex(cpu.reg_read(a.UC_ARM_REG_PC)))
    return {"result_flag": bytes(cpu.mem_read(0x200271C0, 1)).hex(),
            "input": bytes(cpu.mem_read(inp, 20)).hex()}, visited


def run_decoder(stock, image, segments, symbols, fixture):
    name, words, temp, state, auxiliary, config, hw, mode = fixture
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
    for lo, size in [(0, 0x1000), (0x08000000, 0x1000),
                     (0x10000, 0x10000), (0x30000, 0x10000), (0x20000000, 0x40000),
                     (0x40000000, 0x100000), (0x410000, 0x25000)]:
        cpu.mem_map(lo, size)
    if stock:
        cpu.mem_write(0x410000, image)
        entry, end = CASES["state_decode"][:2]
        start = entry
    else:
        for seg in segments: cpu.mem_write(seg["address"], seg["data"])
        start = symbols["native_spot_state_decode"] & ~1
    inp, out_major, out_minor = 0x20001000, 0x20002000, 0x20002004
    data = b"".join(struct.pack("<I", w) for w in words) + bytes([temp, state, auxiliary])
    cpu.mem_write(inp, data + b"\x00" * (20 - len(data)))
    cpu.mem_write(out_major, pack(0xaaaaaaaa) + pack(0xbbbbbbbb))
    cpu.mem_write(0x434164, pack(config))
    cpu.mem_write(0x40021000, pack(hw))
    cpu.mem_write(0x2002708c, bytes([mode]))
    cpu.reg_write(a.UC_ARM_REG_SP, 0x2003F000)
    cpu.reg_write(a.UC_ARM_REG_LR, 0x08000001)
    cpu.reg_write(a.UC_ARM_REG_R0, inp)
    cpu.reg_write(a.UC_ARM_REG_R1, out_major)
    cpu.reg_write(a.UC_ARM_REG_R2, out_minor)
    visited, done = set(), [False]

    def code(uc, pc, size, _):
        if pc == 0x08000000: done[0] = True; uc.emu_stop(); return
        if stock and start <= pc < end: visited.update(range(pc, pc + size))
        if not stock and 0x410000 <= pc < 0x435000:
            raise AssertionError(f"source entered locked firmware at {pc:#x}")

    cpu.hook_add(UC_HOOK_CODE, code)
    cpu.emu_start(start | 1, 0, count=20000)
    assert done[0], (name, hex(cpu.reg_read(a.UC_ARM_REG_PC)))
    result = {"status": cpu.reg_read(a.UC_ARM_REG_R0),
              "major": u32(cpu.mem_read(out_major, 4)),
              "minor": u32(cpu.mem_read(out_minor, 4)),
              "input": bytes(cpu.mem_read(inp, 20)).hex()}
    return result, visited


def run(stock, image, segments, symbols, kind, arg0, arg1=0, flag=0, mark=0):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
    for lo, size in [(0, 0x1000), (0x08000000, 0x1000),
                     (0x10000, 0x10000), (0x30000, 0x10000), (0x20000000, 0x40000),
                     (0x40000000, 0x100000), (0x410000, 0x25000)]:
        cpu.mem_map(lo, size)
    if stock:
        cpu.mem_write(0x410000, image)
        entry, end = CASES[kind][0:2]
        start = entry
    else:
        for seg in segments: cpu.mem_write(seg["address"], seg["data"])
        start = symbols["native_spot_temperature_range" if kind == "temperature"
                        else "native_spot_transition_effect"] & ~1
        end = 0x20000
    cpu.reg_write(a.UC_ARM_REG_SP, 0x2003F000)
    cpu.reg_write(a.UC_ARM_REG_LR, 0x08000001)
    cpu.reg_write(a.UC_ARM_REG_R0, arg0)
    cpu.reg_write(a.UC_ARM_REG_R1, arg1)
    if kind == "temperature": cpu.reg_write(a.UC_ARM_REG_S0, arg0)
    cpu.mem_write(0x200271B0, bytes([mark & 0xff]))
    cpu.mem_write(0x200271B2, bytes([flag & 0xff]))
    cpu.mem_write(0x4002037C, pack(0xA5FF03FF))
    visited, mmio, done = set(), [], [False]

    def code(uc, pc, size, _):
        if pc == 0x08000000:
            done[0] = True; uc.emu_stop(); return
        if stock and start <= pc < end:
            visited.update(range(pc, pc + size))
        if not stock and 0x410000 <= pc < 0x435000:
            raise AssertionError(f"source entered locked firmware at {pc:#x}")

    def write(uc, access, address, size, value, _):
        mmio.append([address, size, value & ((1 << (8 * size)) - 1)])

    cpu.hook_add(UC_HOOK_CODE, code)
    cpu.hook_add(UC_HOOK_MEM_WRITE, write, begin=0x40000000, end=0x400fffff)
    cpu.emu_start(start | 1, 0, count=20000)
    assert done[0], (kind, hex(cpu.reg_read(a.UC_ARM_REG_PC)))
    state = {"flag": bytes(cpu.mem_read(0x200271B2, 1)).hex(),
             "mark": bytes(cpu.mem_read(0x200271B0, 1)).hex(),
             "mmio_word": u32(cpu.mem_read(0x4002037C, 4)), "mmio": mmio}
    if kind == "temperature": state["result"] = cpu.reg_read(a.UC_ARM_REG_R0)
    return state, visited


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--elf", type=Path, default=HERE / "child-native.elf")
    ap.add_argument("--output", type=Path, default=HERE / "child-comparison-decoder.json")
    args = ap.parse_args()
    image = IMAGE.read_bytes()
    assert hashlib.sha256(image).hexdigest() == IMAGE_HASH
    elf_bytes, segments, symbols = reader.elf_info(args.elf)
    rows, coverage = [], {}
    pstart, pend, pdigest = PREDICATE
    predicate_body = image[pstart - 0x410000:pend - 0x410000]
    assert hashlib.sha256(predicate_body).hexdigest() == pdigest
    assert hashlib.sha256(predicate_body[:-1]).hexdigest() != pdigest
    assert hashlib.sha256(image[pstart - 0x410000:pend + 1 - 0x410000]).hexdigest() != pdigest
    for kind, (entry, end, digest) in CASES.items():
        body = image[entry - 0x410000:end - 0x410000]
        assert hashlib.sha256(body).hexdigest() == digest
        assert hashlib.sha256(image[entry - 0x410000:(end - 1) - 0x410000]).hexdigest() != digest, \
            f"wrong-extent negative control failed for {kind}"
        assert hashlib.sha256(image[entry - 0x410000:(end + 1) - 0x410000]).hexdigest() != digest, \
            f"oversized-extent negative control failed for {kind}"
        if kind == "buck_deepsleep_scan":
            continue
        cases = (float_inputs() if kind == "temperature" else
                 decoder_inputs() if kind == "state_decode" else [
            (f"requested={x},current={y},flag={flag}", x, y, flag)
            for x, y in effect_inputs() for flag in (0, 1)])
        visited = set()
        for item in cases:
            if kind == "temperature":
                name, raw = item
                stock, svis = run(True, image, segments, symbols, kind, raw)
                source, _ = run(False, image, segments, symbols, kind, raw)
            elif kind == "state_decode":
                name = item[0]
                stock, svis = run_decoder(True, image, segments, symbols, item)
                source, _ = run_decoder(False, image, segments, symbols, item)
            else:
                name, req, cur, flag = item
                stock, svis = run(True, image, segments, symbols, kind, req, cur, flag, 0xA7)
                source, _ = run(False, image, segments, symbols, kind, req, cur, flag, 0xA7)
            assert stock == source, (kind, name, stock, source)
            rows.append({"kind": kind, "case": name, "result": stock})
            visited |= svis
        extent = set(range(entry, end))
        coverage[kind] = {"start": hex(entry), "end_exclusive": hex(end),
                          "bytes": end-entry, "sha256": digest,
                          "visited_original_bytes": len(visited & extent),
                          "unvisited_bytes": len(extent - visited),
                          "unvisited_addresses": [hex(p) for p in sorted(extent - visited)]}
    scanner_visited = set()
    for fixture in scanner_inputs():
        stock, svis = run_scanner(True, image, segments, symbols, fixture)
        source, _ = run_scanner(False, image, segments, symbols, fixture)
        assert stock == source, (fixture["name"], stock, source)
        if fixture["name"].startswith("class-"):
            expected = fixture["name"].rsplit("-", 1)[-1]
            assert stock["result_flag"] == f"{int(expected):02x}", (fixture, stock)
        rows.append({"kind": "buck_deepsleep_scan", "case": fixture["name"], "result": stock})
        scanner_visited |= svis
    entry, end, digest = CASES["buck_deepsleep_scan"]
    extent = set(range(entry, end))
    coverage["buck_deepsleep_scan"] = {"start": hex(entry), "end_exclusive": hex(end),
        "bytes": end-entry, "sha256": digest,
        "visited_original_bytes": len(scanner_visited & extent),
        "unvisited_bytes": len(extent-scanner_visited),
        "unvisited_addresses": [hex(p) for p in sorted(extent-scanner_visited)],
        "predicate": {"start": hex(pstart), "end_exclusive": hex(pend),
                      "bytes": pend-pstart, "sha256": pdigest,
                      "existing_independent_comparison": "startup-spot-handlers/events-comparison.json"}}
    result = {"status": "PASS", "image_sha256": IMAGE_HASH,
              "source_elf_sha256": hashlib.sha256(elf_bytes).hexdigest(),
              "cases": len(rows), "native_children": coverage,
              "source_machine_loaded_locked_image": False, "comparisons": rows,
              "limits": ["The decoder config word at 0x434164 and the state bytes at input offsets +16..+18 are explicitly seeded per case.",
                         "Cortex-M33 emulation is a baseline subset check, not Apollo510 hardware validation."]}
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print("PASS", len(rows), "cases", coverage)


if __name__ == "__main__": main()
