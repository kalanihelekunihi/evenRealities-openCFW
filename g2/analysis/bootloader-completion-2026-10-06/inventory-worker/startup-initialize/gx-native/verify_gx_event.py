#!/usr/bin/env python3
"""Differentially compare stock 42ba00 with source C plus explicit child cuts.

Stock child bodies are intercepted and supplied deterministic contracts. The
source machine loads only the compiled hypothesis ELF and source-compiled cut
providers plus the separately reconstructed critical-save assembly.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import struct

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS
from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn import arm_const as a

ROOT = Path(__file__).resolve().parents[6]
HERE = Path(__file__).resolve().parent
IMAGE = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
ELF_READER = ROOT / "g2/components/bootloader/update_core/elf_reader.py"
IMAGE_SHA = "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"
BODY_START, BODY_END = 0x42BA00, 0x42BD8C
STOP = 0x08000000
ARGS = 0x20001000
CHILDREN = {0x42AD40: "temperature", 0x42AEF0: "scan",
            0x42B014: "effect", 0x42B294: "transition",
            0x42B6B8: "decode"}
STATE_WORDS = [0x20000144, 0x2000014C, 0x20026BA0, 0x4002037C]
STATE_BYTES = [0x200271BA, 0x200271BB, 0x20000553, 0x200271AF,
               0x2002708C, 0x200271B0, 0x200271B2, 0x200271C0]
DATA_WORDS = [0x40021008, 0x40021010, 0x40021018, 0x40021028]

spec = importlib.util.spec_from_file_location("elf_reader", ELF_READER)
elf_reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(elf_reader)


def pack(value):
    return struct.pack("<I", value & 0xFFFFFFFF)


def unpack(data):
    return struct.unpack("<I", data)[0]


def rd32(cpu, address):
    return unpack(bytes(cpu.mem_read(address, 4)))


def wr32(cpu, address, value):
    cpu.mem_write(address, pack(value))


def default_fixture(name, **kw):
    f = {
        "name": name, "stimulus": 1, "option": 0, "arg": 0x11111111,
        "null_args": False, "gate": 0x30, "marker": 0x1F01600D,
        "current": 0, "temp_category": 0, "aux_byte": 0,
        "mode_byte": 1, "major": 4, "minor": 2,
        "snapshot": [0x20000000, 0x00000000, 0x12345678, 0xABCDEF00],
        "scan_xor": [0, 0, 0, 0], "temp_result": 2,
        "scan_gate": 0, "scan_enable": 0, "scan_mode": 0,
        "scan_active": 0, "scan_channels": {}, "scan_result": 0xA5,
        "decode_status": 0, "decode_major": 4, "decode_minor": 2,
        "decoder_config": 0, "decoder_hw": 0,
        "primask": 0,
    }
    f.update(kw)
    f["args"] = 0 if f["null_args"] else ARGS
    return f


def fixtures():
    out = [
        default_fixture("clock-gate-off", gate=0),
        default_fixture("profile-marker-mismatch", marker=0),
        default_fixture("state-null", stimulus=0, null_args=True),
        default_fixture("state-0-to-1", stimulus=0, current=0, arg=1,
                        decode_major=8, decode_minor=1, major=4, minor=2),
        default_fixture("state-1-to-0-deferred", stimulus=0, current=1, arg=0,
                        decode_major=13, decode_minor=3, major=12, minor=2,
                        primask=1),
        default_fixture("state-0-to-2-scan", stimulus=0, current=0, arg=2,
                        mode_byte=0, snapshot=[0, 0, 0x12345678, 0xABCDEF00],
                        scan_enable=1, scan_mode=1,
                        scan_active=1 << 15,
                        scan_channels={15: 1 | (300 << 8)},
                        scan_result=0xA5, decode_major=9,
                        decode_minor=2, major=8, minor=1),
        default_fixture("state-0-to-2-scan-fast-exit", stimulus=0, current=0,
                        arg=2, temp_category=3, scan_result=0xA5),
        default_fixture("state-0-to-2-scan-channel-trigger", stimulus=0,
                        current=0, arg=2, scan_active=1,
                        scan_channels={0: 1 | (25 << 8)}, scan_result=0xA5),
        default_fixture("state-other-pair-skip-decode", stimulus=0, current=2,
                        arg=3, decode_major=11, decode_minor=5),
        default_fixture("state-equal-no-effect", stimulus=0, current=2, arg=2),
    ]
    for old in (2, 3, 4):
        for new in (0, 1):
            out.append(default_fixture(f"state-shortcut-{old}-{new}", stimulus=0,
                                       current=old, arg=new))
    out.extend([
        default_fixture("system-state-null", stimulus=1, null_args=True),
        default_fixture("system-state", stimulus=1, arg=3),
        default_fixture("temperature-null", stimulus=2, null_args=True),
    ])
    for cat in range(6):
        out.append(default_fixture(f"temperature-category-{cat}", stimulus=2,
                                   arg=0x41C80000, temp_result=cat))
    out.extend([
        default_fixture("decoder-stack-temp0-state1-aux1", stimulus=0, current=0,
                        arg=1, temp_category=3, snapshot=[0x00040000, 0, 0, 0],
                        aux_byte=0, decoder_config=0x200000, mode_byte=0),
        default_fixture("decoder-stack-temp4-state0-aux2", stimulus=0, current=1,
                        arg=0, temp_category=4, snapshot=[0x00040000, 0x4c4, 0, 0],
                        aux_byte=2, decoder_config=0x400000, mode_byte=1),
        default_fixture("decoder-stack-powered-fields", stimulus=1, current=2,
                        temp_category=15, snapshot=[0x00400001, 0x4c4, 0, 0],
                        aux_byte=1, decoder_config=0xA00000,
                        decoder_hw=2, mode_byte=1),
        default_fixture("dev-power-off-null", stimulus=3, option=0, null_args=True),
        default_fixture("dev-power-on", stimulus=3, option=1, arg=0x80),
        default_fixture("dev-power-lowbyte-zero", stimulus=3, option=0x100,
                        arg=0x80),
        default_fixture("audio-power-off-null", stimulus=4, option=0,
                        null_args=True),
        default_fixture("audio-power-on", stimulus=4, option=1,
                        arg=0x44),
        default_fixture("memory-null", stimulus=5, null_args=True),
        default_fixture("memory-replace", stimulus=5, option=0, arg=0xDEADBEEF),
        default_fixture("ssram-off-null", stimulus=6, option=0, null_args=True),
        default_fixture("ssram-on-null", stimulus=6, option=1, null_args=True),
        default_fixture("ssram-on", stimulus=6, option=1, arg=0xCAFE),
        default_fixture("bad-stimulus", stimulus=7),
        default_fixture("decode-error", stimulus=1, decode_status=5,
                        decode_major=99, decode_minor=101),
        default_fixture("major-12-to-13", stimulus=1, major=12, minor=3,
                        decode_major=13, decode_minor=4),
        default_fixture("major-8-to-11", stimulus=1, major=8, minor=2,
                        decode_major=11, decode_minor=5),
        default_fixture("major-outside-transition", stimulus=1, major=12,
                        decode_major=16, decode_minor=1),
        default_fixture("state-high-input-byte", stimulus=0x100,
                        current=1, arg=0),
    ])
    return out


def init_common(cpu, f):
    wr32(cpu, 0x40021108, f["gate"])
    wr32(cpu, 0x20026BA0, f["marker"])
    wr32(cpu, 0x434164, f.get("decoder_config", 0))
    wr32(cpu, 0x40021000, f.get("decoder_hw", 0))
    wr32(cpu, 0x20000144, f["major"])
    wr32(cpu, 0x2000014C, f["minor"])
    wr32(cpu, 0x40021008, f["snapshot"][0])
    wr32(cpu, 0x40021010, f["snapshot"][1])
    wr32(cpu, 0x40021018, f["snapshot"][2])
    wr32(cpu, 0x40021028, f["snapshot"][3])
    cpu.mem_write(0x200271BA, bytes([f["temp_category"] & 0xff]))
    cpu.mem_write(0x200271BB, bytes([f["current"] & 0xff]))
    cpu.mem_write(0x200271A5, bytes([f["aux_byte"] & 0xff]))
    cpu.mem_write(0x2002708C, bytes([f["mode_byte"] & 0xff]))
    cpu.mem_write(0x200271B0, b"\xA7")
    cpu.mem_write(0x200271B2, b"\x00")
    cpu.mem_write(0x200271C0, bytes([f["scan_result"] & 0xff]))
    cpu.mem_write(0x200271BF, bytes([f["scan_enable"] & 0xff]))
    wr32(cpu, 0x400204D8, f["scan_gate"])
    wr32(cpu, 0x40008800, f["scan_mode"])
    wr32(cpu, 0x40008010, f["scan_active"])
    for slot, value in f["scan_channels"].items():
        wr32(cpu, 0x40008200 + int(slot) * 0x20, value)
    cpu.mem_write(0x20000553, b"\xA5")
    wr32(cpu, 0x4002037C, 0xA5000000)
    cpu.mem_write(ARGS, pack(f["arg"]) + pack(0xA1A2A3A4) + pack(0xB1B2B3B4))
    cpu.reg_write(a.UC_ARM_REG_SP, 0x2003F000)
    cpu.reg_write(a.UC_ARM_REG_LR, STOP | 1)
    cpu.reg_write(a.UC_ARM_REG_PRIMASK, f["primask"])


def provider_records_from_source(cpu, symbols, child_cuts=False):
    count = rd32(cpu, symbols["event_cut_count"])
    result = []
    base = symbols["event_cut_records"]
    for i in range(count):
        p = base + i * 44
        kind = rd32(cpu, p)
        n = {1: 1, 2: 8 if child_cuts else 10, 3: 2, 4: 10,
             5: 4 if child_cuts else 5}[kind]
        result.append({"kind": kind,
                       "args": [rd32(cpu, p + 4 + 4*j) for j in range(n)]})
    return result


def run(stock, image, segments, symbols, f, child_cuts=False):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
    for lo, size in [(0, 0x1000), (0x08000000, 0x20000),
                     (0x10000, 0x10000), (0x30000, 0x10000), (0x20000000, 0x40000),
                     (0x40000000, 0x100000), (0x410000, 0x25000),
                     (0xE0000000, 0x200000), (0x47FF0000, 0x1000)]:
        cpu.mem_map(lo, size)
    if stock:
        cpu.mem_write(0x410000, image)
    else:
        for segment in segments:
            cpu.mem_write(segment["address"], segment["data"])

    init_common(cpu, f)
    calls = []
    mmio = []
    trace = {}
    done = [False]
    pending_decode = []
    pending_scan = []
    pending_transition = []

    def hook(uc, pc, size, _):
        if pc == STOP:
            done[0] = True
            uc.emu_stop()
            return
        # The stock delay helper calls the ROM cycle-wait service at 0x40.
        # Its ABI is void; record/control flow only, with no fabricated status.
        if pc == 0x40:
            uc.reg_write(a.UC_ARM_REG_PC, uc.reg_read(a.UC_ARM_REG_LR))
            return
        if not stock and 0x410000 <= pc < 0x435000:
            raise AssertionError(f"source machine entered locked image at {pc:#x}")
        if stock and BODY_START <= pc < BODY_END:
            trace[pc] = bytes(uc.mem_read(pc, size)).hex()
        if not stock and (0x10000 <= pc < 0x20000 or 0x30000 <= pc < 0x40000):
            trace[pc] = bytes(uc.mem_read(pc, size)).hex()
        if stock and pending_decode and pc == pending_decode[-1]["return_pc"]:
            pending = pending_decode.pop()
            calls.append({"kind": 4, "args": pending["input"] + [
                uc.reg_read(a.UC_ARM_REG_R0), rd32(uc, pending["out_major"]),
                rd32(uc, pending["out_minor"])]})
        if stock and pending_scan and pc == pending_scan[-1]["return_pc"]:
            pending = pending_scan.pop()
            calls.append({"kind": 2, "args": pending["input"] +
                          [pending["temperature"]] +
                          [rd32(uc, pending["pointer"] + 4*i) for i in range(4)] +
                          [uc.mem_read(0x200271C0, 1)[0]]})
        if stock and pending_transition and pc == pending_transition[-1]["return_pc"]:
            pending = pending_transition.pop()
            calls.append({"kind": 5, "args": pending["args"] +
                          [uc.reg_read(a.UC_ARM_REG_R0)]})
        if stock and pc == 0x42B6B8 and not child_cuts:
            p = uc.reg_read(a.UC_ARM_REG_R0)
            pending_decode.append({
                "return_pc": uc.reg_read(a.UC_ARM_REG_LR) & ~1,
                "out_major": uc.reg_read(a.UC_ARM_REG_R1),
                "out_minor": uc.reg_read(a.UC_ARM_REG_R2),
                "input": [rd32(uc, p + 4*i) for i in range(4)] +
                         list(bytes(uc.mem_read(p + 16, 3))),
            })
            return
        if stock and pc == 0x42AEF0 and not child_cuts:
            p = uc.reg_read(a.UC_ARM_REG_R0)
            pending_scan.append({
                "return_pc": uc.reg_read(a.UC_ARM_REG_LR) & ~1,
                "pointer": p,
                "input": [rd32(uc, p + 4*i) for i in range(4)],
                "temperature": uc.mem_read(p + 16, 1)[0],
            })
            return
        if stock and pc == 0x42B294 and not child_cuts:
            pending_transition.append({
                "return_pc": uc.reg_read(a.UC_ARM_REG_LR) & ~1,
                "args": [uc.reg_read(getattr(a, f"UC_ARM_REG_R{i}"))
                         for i in range(4)],
            })
            return
        if not stock or pc not in CHILDREN:
            return
        kind = CHILDREN[pc]
        if kind == "temperature":
            raw = uc.reg_read(a.UC_ARM_REG_S0)
            calls.append({"kind": 1, "args": [raw]})
            if child_cuts:
                uc.reg_write(a.UC_ARM_REG_R0, f["temp_result"])
                uc.reg_write(a.UC_ARM_REG_PC, uc.reg_read(a.UC_ARM_REG_LR))
            return
        elif kind == "scan":
            p = uc.reg_read(a.UC_ARM_REG_R0)
            before = [rd32(uc, p + 4*i) for i in range(4)]
            if child_cuts:
                after = [before[i] ^ f["scan_xor"][i] for i in range(4)]
                for i, value in enumerate(after): wr32(uc, p + 4*i, value)
                calls.append({"kind": 2, "args": before + after})
            else:
                raise AssertionError("native scanner entry should execute original instructions")
        elif kind == "effect":
            calls.append({"kind": 3, "args": [uc.reg_read(a.UC_ARM_REG_R0) & 0xff,
                                                   uc.reg_read(a.UC_ARM_REG_R1) & 0xff]})
            if child_cuts:
                uc.reg_write(a.UC_ARM_REG_PC, uc.reg_read(a.UC_ARM_REG_LR))
            return
        elif kind == "decode":
            if not child_cuts:
                raise AssertionError("native decoder entry should execute original instructions")
            p = uc.reg_read(a.UC_ARM_REG_R0)
            before = [rd32(uc, p + 4*i) for i in range(4)]
            out_major = uc.reg_read(a.UC_ARM_REG_R1)
            out_minor = uc.reg_read(a.UC_ARM_REG_R2)
            wr32(uc, out_major, f["decode_major"])
            wr32(uc, out_minor, f["decode_minor"])
            calls.append({"kind": 4, "args": before +
                          list(bytes(uc.mem_read(p + 16, 3))) +
                          [f["decode_status"], f["decode_major"], f["decode_minor"]]})
            uc.reg_write(a.UC_ARM_REG_R0, f["decode_status"])
        elif kind == "transition":
            calls.append({"kind": 5, "args": [uc.reg_read(a.UC_ARM_REG_R0),
                                                 uc.reg_read(a.UC_ARM_REG_R1),
                                                 uc.reg_read(a.UC_ARM_REG_R2),
                                                 uc.reg_read(a.UC_ARM_REG_R3)]})
        uc.reg_write(a.UC_ARM_REG_PC, uc.reg_read(a.UC_ARM_REG_LR))

    def write_hook(uc, access, address, size, value, _):
        if address >= 0x40000000:
            mmio.append([address, size, value & ((1 << (size * 8)) - 1)])

    cpu.hook_add(UC_HOOK_CODE, hook)
    cpu.hook_add(UC_HOOK_MEM_WRITE, write_hook,
                 begin=0x40000000, end=0x400fffff)
    # AAPCS callers extend narrow integer arguments before a call. Keep the
    # upper register bits canonical so the harness does not test a caller that
    # violates the observed byte/char ABI.
    cpu.reg_write(a.UC_ARM_REG_R0, f["stimulus"] & 0xff)
    cpu.reg_write(a.UC_ARM_REG_R1, f["option"] & 0xff)
    cpu.reg_write(a.UC_ARM_REG_R2, f["args"])
    pc = BODY_START if stock else symbols["opencfw_boot_spot_state_power_event"] & ~1
    try:
        cpu.emu_start(pc | 1, 0, count=20000)
    except Exception as exc:
        raise RuntimeError(f"{f['name']} {'stock' if stock else 'source'} fault pc={cpu.reg_read(a.UC_ARM_REG_PC):#x} sp={cpu.reg_read(a.UC_ARM_REG_SP):#x}") from exc
    assert done[0], (f["name"], "did not return", hex(cpu.reg_read(a.UC_ARM_REG_PC)))
    calls = []  # No instrumentation providers linked; compare external effects.
    result = {
        "status": cpu.reg_read(a.UC_ARM_REG_R0),
        "rom_boundary_note": "Only absent ROM40 wait controlled; direct child code executes",
        "mmio": mmio,
        "words": {f"{p:08x}": rd32(cpu, p) for p in STATE_WORDS + DATA_WORDS},
        "bytes": {f"{p:08x}": cpu.mem_read(p, 1).hex() for p in STATE_BYTES},
        "args": bytes(cpu.mem_read(ARGS, 12)).hex(),
        "primask": cpu.reg_read(a.UC_ARM_REG_PRIMASK),
    }
    return result, trace


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--elf", type=Path, default=HERE / "event.elf")
    ap.add_argument("--output", type=Path, default=HERE / "comparison.json")
    ap.add_argument("--child-cuts", action="store_true",
                    help="preserve the original wrapper receipt with all five children cut")
    args = ap.parse_args()
    image = IMAGE.read_bytes()
    image_sha = hashlib.sha256(image).hexdigest()
    assert image_sha == IMAGE_SHA, image_sha
    elf_bytes, segments, symbols = elf_reader.elf_info(args.elf)
    assert not args.child_cuts, "native-only candidate; child cuts forbidden"
    cases = fixtures()
    rows = []
    stock_union = set()
    source_union = set()
    for f in cases:
        stock, stock_trace = run(True, image, segments, symbols, f, args.child_cuts)
        source, source_trace = run(False, image, segments, symbols, f, args.child_cuts)
        if stock != source:
            args.output.with_suffix(".failure.json").write_text(json.dumps(
                {"case": f, "stock": stock, "source": source}, indent=2) + "\n")
            raise SystemExit(f"MISMATCH {f['name']}: stock={stock} source={source}")
        rows.append({"case": f["name"], "input": f, "result": stock})
        for pc, raw in stock_trace.items():
            stock_union.update(range(pc, pc + len(bytes.fromhex(raw))))
        for pc, raw in source_trace.items():
            source_union.update(range(pc, pc + len(bytes.fromhex(raw))))
    extent = set(range(BODY_START, BODY_END))
    stock_coverage = len(stock_union & extent)
    gaps = sorted(extent - stock_union)
    result = {
        "status": "PASS",
        "image_sha256": image_sha,
        "source_elf_sha256": hashlib.sha256(elf_bytes).hexdigest(),
        "cases": len(rows),
        "stock_body": {"start": hex(BODY_START), "end_exclusive": hex(BODY_END),
                       "extent_bytes": len(extent), "visited_original_bytes": stock_coverage,
                       "unvisited_bytes": len(gaps),
                       "unvisited_addresses": [hex(p) for p in gaps]},
        "source_machine": {"loaded_locked_image": False,
                            "source_code_bytes_visited": len(source_union)},
        "native_descendants": [] if args.child_cuts else [
            {"entry": "0x42ad40", "end_exclusive": "0x42adb8", "bytes": 120,
             "sha256": "89f71050cf7850205a7a5ef9ccfb09dfadaadd5a6046355844d800589b65607d"},
            {"entry": "0x42aef0", "end_exclusive": "0x42b010", "bytes": 288,
             "sha256": "7a54959ea8247c505df0f3139ce607b4d1fabb5d0015054b89bd44b5d79cc31b",
             "predicate": {"entry": "0x41f3f0", "end_exclusive": "0x41f424", "bytes": 52,
                           "sha256": "2629a71d82c78f7602d8f37273ae02bcf42f237cdaab9da0d4db6d57a1045692"}},
            {"entry": "0x42b014", "end_exclusive": "0x42b068", "bytes": 84,
             "sha256": "b3da01a94a3c08eb7eb0d7d344b6760d929296878e2dfbf9c4770373aedd3d88"},
            {"entry": "0x42b6b8", "end_exclusive": "0x42b9ba", "bytes": 770,
             "sha256": "74f4304f6e3aa59022a29eb5e5f5479c77072b33355825b7c9409897001bb9d1"},
            {"entry": "0x42b294", "end_exclusive": "0x42b69c", "bytes": 1032,
             "sha256": "0393f03222d8b7e8c67ed0e7ffbba640f8030dac259a909ec7dbb20846325c2b",
             "direct_cases": 30, "direct_bytes_visited": 858,
             "unvisited_bytes": 174},
        ],
        "lower_cuts": (["0x42ad40", "0x42aef0", "0x42b014", "0x42b294", "0x42b6b8"]
                       if args.child_cuts else []),
        "decoder_call_contract": {
            "stock_sp_frame": "32 bytes",
            "r0_input": "sp+4",
            "r1_major_output": "sp+0",
            "r2_minor_output": "sp+24",
            "input_plus_16": "sp+20 temperature category",
            "input_plus_17": "sp+21 current/request state byte",
            "input_plus_18": "sp+22 auxiliary category",
        },
        "critical_save": "source-side compiled opencfw_boot_control_critical_save from platform_control/critical_save.S; stock 0x41b8ec executes in stock machine",
        "comparisons": rows,
        "limits": ["174 bytes of the transition child were not visited by its 30 direct fixtures; see transition-comparison.json for exact gaps.",
                   "Source-side executes only compiled C/provider/critical-save source ELF; no locked instruction bytes are injected.",
                   "Cortex-M33 offline emulation is not physical Apollo510 hardware or full firmware source/build equivalence."],
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    args.output.with_name("native-disassembly.txt").write_text(
        __import__("subprocess").run(["arm-none-eabi-objdump", "-D", str(args.elf)],
                                    check=True, capture_output=True, text=True).stdout)
    print("PASS", len(rows), "cases", stock_coverage, "/", len(extent),
          "stock bytes visited", "source bytes", len(source_union))
    if gaps:
        print("unvisited", ", ".join(hex(p) for p in gaps[:30]))


if __name__ == "__main__":
    main()
