#!/usr/bin/env python3
"""Differential checks for 42b294 and its bounded trim/clock children."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import struct

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS
from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn import arm_const as a

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
IMAGE = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
ELF_READER = ROOT / "g2/components/bootloader/update_core/elf_reader.py"
IMAGE_SHA = "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"
EXTENTS = {
    0x42B294: (0x42B69C, "0393f03222d8b7e8c67ed0e7ffbba640f8030dac259a909ec7dbb20846325c2b"),
    0x42B06C: (0x42B294, "44271365df4592f33c91286690e4e75e328a8dd11127aa934bec2c571292c377"),
    0x42ADB8: (0x42AE24, "7b25d7dae842d5787345a5360a32fbf21f4adadc88e216b2eaa272cc77d7feda"),
    0x42AE24: (0x42AE6C, "73da1f0b69f23d583009d5dfbc2f46007ee0f8b9f56a5c8a3b4fccd58136f538"),
    0x42AE6C: (0x42AE9C, "fbc7ca52270345ca6b251d1c8c805a06e33af456500f9b17e05cfa7743af79f8"),
    0x41CC48: (0x41CC92, "aef74a1657eee6d89e50c7452789a0aff1c7e25bb9dd81f3a1db74ed173d5e49"),
    0x41CC92: (0x41CCD6, "bcbc39a968d90e534a70b68e4dcda7a2bf30bcd02725a4a4ecf539b8d50cfbc6"),
    0x41CCD6: (0x41CD1A, "53ecf1cc50f77949e880de53ecfed6a2d18c3ea803c457a13e77d1b2ac548a3a"),
    0x41D1C0: (0x41D210, "c336d5c93475c6521bab00509a8ad8aaa1078b3bdc313ae43107777520af1895"),
    0x41E1E8: (0x41E22E, "4f10536463c4fd13679ef30c2fabc9876f052bcc90cb6100837d849e19fc09dd"),
    0x41E22E: (0x41E266, "0e250a57f88ce12c21f0691cc8de447aa6a9808529c3668c6e54d653fe6dec45"),
    0x4222F0: (0x422364, "53cfb358989e68ae979d2814964a3e779ae0f0eba76836f99d409393d0e78d51"),
    0x422364: (0x4223D8, "6a131868a276083764d4714178857124ccb4209a5f3e7552d874aba7f7c1a54e"),
}
STOP = 0x08000000

spec = importlib.util.spec_from_file_location("elf_reader", ELF_READER)
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


def pack(v): return struct.pack("<I", v & 0xffffffff)
def u32(data): return struct.unpack("<I", bytes(data))[0]


def pack_profile(vfact, core, co, vtrg):
    return ((vfact & 0x7f) | ((core & 0x3ff) << 7) |
            ((co & 0xf) << 17) | ((vtrg & 0x7f) << 21))


def fixtures():
    rows = []
    for i in range(21):
        new = i
        old = (i + 1) % 21
        rows.append({"name": f"rotating-major-{i}", "new": new, "old": old,
                     "new_minor": i % 9, "old_minor": (i + 1) % 9,
                     "current": (i + 5) % 21, "syspll": i & 1,
                     "busy": (i >> 1) & 1, "rank_direction": i & 1})
    rows.extend([
        {"name": "same-major-same-minor", "new": 4, "old": 4,
         "new_minor": 2, "old_minor": 2, "current": 4, "syspll": 0, "busy": 0},
        {"name": "same-major-minor-change", "new": 4, "old": 4,
         "new_minor": 4, "old_minor": 2, "current": 4, "syspll": 1, "busy": 0},
        {"name": "down-ramp", "new": 9, "old": 2, "new_minor": 2,
         "old_minor": 2, "current": 2, "syspll": 0, "busy": 0},
        {"name": "down-wait-busy", "new": 9, "old": 2, "new_minor": 7,
         "old_minor": 2, "current": 2, "syspll": 0, "busy": 1},
        {"name": "down-syspll", "new": 9, "old": 2, "new_minor": 5,
         "old_minor": 2, "current": 6, "syspll": 1, "busy": 0},
        {"name": "special-enter-high", "new": 9, "old": 3, "new_minor": 1,
         "old_minor": 1, "current": 3, "syspll": 0, "busy": 0,
         "scb": 0x20000},
        {"name": "special-enter-high-no-flush", "new": 12, "old": 17,
         "new_minor": 3, "old_minor": 2, "current": 17, "syspll": 1, "busy": 1},
        {"name": "up-current-lower-release", "new": 9, "old": 3,
         "new_minor": 6, "old_minor": 4, "current": 1, "syspll": 1, "busy": 0,
         "clock_user": 1},
        {"name": "up-no-release", "new": 5, "old": 9,
         "new_minor": 0, "old_minor": 0, "current": 10, "syspll": 0, "busy": 0},
    ])
    return rows


def seed(cpu, f):
    info = bytearray(0x6c)
    struct.pack_into("<I", info, 0, 0x1f01600d)
    for i in range(21):
        word = pack_profile((11 + i * 3) % 128, (81 + i * 17) % 1024,
                            (2 + i) % 16, (23 + i * 5) % 128)
        struct.pack_into("<I", info, 4 + 4*i, word)
    struct.pack_into("<I", info, 0x54, 0x00a952a5)
    struct.pack_into("<I", info, 0x58, 0x00123456)
    struct.pack_into("<I", info, 0x5c, 0x0019b5c6)
    struct.pack_into("<I", info, 0x60, 0x0000e789)
    struct.pack_into("<I", info, 0x64, 0x0000c321)
    struct.pack_into("<I", info, 0x68, 0x0002a135)
    cpu.mem_write(0x20026ba0, bytes(info))
    ranks = list(range(21))
    if f.get("rank_direction", 0): ranks.reverse()
    for i, rank in enumerate(ranks):
        cpu.mem_write(0x200000a4 + 4*i, pack(rank))
        cpu.mem_write(0x200000f4 + 4*i, pack(rank))
    # The stock worker and source model receive the same explicit current-index,
    # PLL, ramp-busy, and clock-manager entry state.
    cpu.mem_write(0x20000148, pack(f["current"]))
    cpu.mem_write(0x400083e0, pack((f["syspll"] & 1) | 0x00001234))
    cpu.mem_write(0x40020080, pack(0x15550000 | (f["current"] * 23 + 900)))
    cpu.mem_write(0x40020088, pack(0x80000000 | (f["current"] * 3 + 60)))
    cpu.mem_write(0x200270a4, pack(5))
    cpu.mem_write(0x200270a8, pack(41))
    cpu.mem_write(0x200270ac, pack(37))
    cpu.mem_write(0x200271ae, bytes([f["busy"]]))
    cpu.mem_write(0x200271b2, b"\x00")
    cpu.mem_write(0x40020044, pack(0xa5000000 | (17 + f["old"])))
    cpu.mem_write(0x4002004c, pack(0x5a000000 | (31 + f["new"])))
    cpu.mem_write(0x400201b0, pack(0x40000000 | f["old"]))
    cpu.mem_write(0x40020344, pack(0x11112222))
    cpu.mem_write(0x4002034c, pack(0x33334444))
    cpu.mem_write(0x40020354, pack(0x55556666))
    cpu.mem_write(0x40020358, pack(0x77778888))
    cpu.mem_write(0x4002037c, pack(0x80000000))
    cpu.mem_write(0x40020380, pack(0x90000000))
    cpu.mem_write(0xe000e000, bytes(0x20000))
    cpu.mem_write(0xe000ed14, pack(f.get("scb", 0)))
    # The clock-4 owner/config fields are real, explicitly initialized input
    # state; no request status is synthesized by the harness.
    cpu.mem_write(0x20000550, b"\x01")
    cpu.mem_write(0x20027030, pack(0))
    cpu.mem_write(0x20027044, pack(0))
    cpu.mem_write(0x2002719c, b"\x00")
    cpu.mem_write(0x2002719e, b"\x00")
    cpu.mem_write(0x20026e74, bytes(56))
    cpu.mem_write(0x47ff0000, pack(f.get("sync_read", 0x12345678)))
    if f.get("clock_user"):
        # Class 4 row begins at bitmap base + 32; user 49 is bit 17 in word 1.
        cpu.mem_write(0x20026ea8, pack(1 << 17))
    cpu.reg_write(a.UC_ARM_REG_SP, 0x2003f000)
    cpu.reg_write(a.UC_ARM_REG_LR, STOP | 1)


def run(stock, image, segments, symbols, f):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
    for lo, size in [(0, 0x1000), (0x08000000, 0x1000),
                     (0x10000, 0x30000), (0x20000000, 0x40000),
                     (0x40000000, 0x100000), (0x410000, 0x25000),
                     (0xE0000000, 0x200000), (0x47FF0000, 0x1000)]:
        cpu.mem_map(lo, size)
    if stock:
        cpu.mem_write(0x410000, image)
        start = 0x42B294
    else:
        for seg in segments: cpu.mem_write(seg["address"], seg["data"])
        start = symbols["native_spot_state_transition"] & ~1
    seed(cpu, f)
    cpu.reg_write(a.UC_ARM_REG_R0, f["new"])
    cpu.reg_write(a.UC_ARM_REG_R1, f["old"])
    cpu.reg_write(a.UC_ARM_REG_R2, f["new_minor"])
    cpu.reg_write(a.UC_ARM_REG_R3, f["old_minor"])
    visited, rom_waits, writes, done = set(), [], [], [False]

    def code(uc, pc, size, _):
        if pc == STOP:
            done[0] = True; uc.emu_stop(); return
        if pc == 0x40:
            rom_waits.append(uc.reg_read(a.UC_ARM_REG_R0))
            uc.reg_write(a.UC_ARM_REG_PC, uc.reg_read(a.UC_ARM_REG_LR))
            return
        if stock and 0x410000 <= pc < 0x435000:
            visited.update(range(pc, pc + size))
        if not stock and 0x410000 <= pc < 0x435000:
            raise AssertionError(f"source executed locked firmware at {pc:#x}")

    def write(uc, access, address, size, value, _):
        if 0x40000000 <= address < 0x40100000 or 0xE0000000 <= address < 0xE0020000:
            writes.append([address, size, value & ((1 << (8*size))-1)])

    cpu.hook_add(UC_HOOK_CODE, code)
    cpu.hook_add(UC_HOOK_MEM_WRITE, write)
    try:
        cpu.emu_start(start | 1, 0, count=500000)
    except Exception as exc:
        raise RuntimeError(f"{f['name']} {'stock' if stock else 'source'} PC={cpu.reg_read(a.UC_ARM_REG_PC):#x}") from exc
    assert done[0], (f["name"], "did not return", hex(cpu.reg_read(a.UC_ARM_REG_PC)))
    state_addresses = [0x20000148, 0x200270a4, 0x200270a8, 0x200270ac,
                       0x200271ae, 0x200271b2, 0x20026e74, 0x20000550,
                       0x20027030, 0x20027044, 0x2002719c, 0x2002719e]
    state_addresses += [0x400083e0, 0x400083e8, 0x40008010, 0x40008068,
                        0x40020044, 0x4002004c, 0x40020080, 0x40020088,
                        0x400201b0, 0x40020344, 0x4002034c, 0x40020354,
                        0x40020358, 0x4002037c, 0x40020380, 0x40004020,
                        0x40004044, 0xe000e108, 0xe000e114, 0xe000e188,
                        0xe000e288, 0xe000ed14, 0xe000ef50, 0x47ff0000]
    state = {f"{address:08x}": bytes(cpu.mem_read(address, 4)).hex()
             for address in state_addresses}
    state["profile"] = bytes(cpu.mem_read(0x20026ba0, 0x6c)).hex()
    state["major_ranks"] = bytes(cpu.mem_read(0x200000a4, 21*4)).hex()
    state["minor_ranks"] = bytes(cpu.mem_read(0x200000f4, 21*4)).hex()
    state["primask"] = cpu.reg_read(a.UC_ARM_REG_PRIMASK)
    return {"return": cpu.reg_read(a.UC_ARM_REG_R0), "state": state,
            "writes": writes, "rom_wait_values": rom_waits}, visited


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--elf", type=Path, default=HERE / "child-native.elf")
    ap.add_argument("--output", type=Path, default=HERE / "transition-comparison.json")
    args = ap.parse_args()
    image = IMAGE.read_bytes()
    assert hashlib.sha256(image).hexdigest() == IMAGE_SHA
    _, segments, symbols = reader.elf_info(args.elf)
    functions_path = ROOT / "g2/research/corpus/apollo-bootloader/ghidra/open-2026-09-29/functions-000.jsonl"
    functions = {int((d := json.loads(line))["entry"], 16): d
                 for line in functions_path.read_text().splitlines()}
    for entry, (end, digest) in EXTENTS.items():
        record = functions[entry]
        body = image[entry-0x410000:end-0x410000]
        assert int(record["body_end_inclusive"], 16) + 1 == end
        assert len(body) == end-entry and hashlib.sha256(body).hexdigest() == digest
        assert hashlib.sha256(body[:-1]).hexdigest() != digest
        assert hashlib.sha256(image[entry-0x410000:end+1-0x410000]).hexdigest() != digest
    rows, all_visited = [], set()
    for f in fixtures():
        stock, visited = run(True, image, segments, symbols, f)
        source, _ = run(False, image, segments, symbols, f)
        assert stock == source, (f["name"], stock, source)
        assert stock["return"] == f["old_minor"]
        rows.append({"fixture": f, "result": stock})
        all_visited |= visited
    body = set(range(0x42B294, 0x42B69C))
    result = {"status": "PASS", "image_sha256": IMAGE_SHA,
              "source_elf_sha256": hashlib.sha256(args.elf.read_bytes()).hexdigest(),
              "cases": len(rows), "stock_transition": {
                  "entry": "0x42b294", "end_exclusive": "0x42b69c", "bytes": 1032,
                  "sha256": EXTENTS[0x42B294][1],
                  "visited_bytes": len(all_visited & body),
                  "unvisited_addresses": [hex(x) for x in sorted(body-all_visited)]},
              "executed_original_bytes": len(all_visited),
              "source_machine_loaded_locked_image": False,
              "external_inputs": [
                  "Runtime SPOT info1/profile table, major/minor rank arrays, trim-busy flag, SYSPLL status and initial peripheral words are explicitly seeded per fixture.",
                  "ROM cycle-wait address 0x40 is intercepted as a void timing service; its input cycle counts are recorded. The original/source delay conversion code executes.",
                  "Apollo510 SYNC_READ at 0x47ff0000 is explicitly seeded and read by the release path; its value is not treated as a guessed status.",
                  "Clock request/release dispatch and class-4 source/image bodies execute; status values are consumed only where stock does, and all state is compared."],
              "comparisons": rows,
              "limits": ["Tests compare compiled-source execution with the actual locked transition and reachable stock descendants, using the same explicit runtime state inputs.",
                         "This is not hardware validation, complete firmware source, or byte-identical build evidence."]}
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print("PASS", len(rows), "cases;", len(all_visited & body), "/ 1032 transition bytes;", len(all_visited), "original bytes")


if __name__ == "__main__": main()
