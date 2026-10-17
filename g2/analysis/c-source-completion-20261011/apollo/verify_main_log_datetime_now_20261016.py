#!/usr/bin/env python3
"""Compare native/C date-provider call sequence and timezone arithmetic."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_SP

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/log_datetime_now_44a19a.c"
CONTEXT = G2 / "components/audio/audio_log_format_source_candidate/context.c"
BASE = G2 / "build/c-firmware/20261016/main-log-time-string/candidate.o"
OUT = G2 / "build/c-firmware/20261016/main-log-datetime-now"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def machine():
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    for address, size in ((0x100000, 0x100000), (0x300000, 0x1000),
                          (0x400000, 0x400000), (0x20000000, 0x80000)):
        uc.mem_map(address, size)
    uc.reg_write(UC_ARM_REG_SP, 0x2007f000)
    uc.reg_write(UC_ARM_REG_LR, 0x300001)
    return uc


def execute(entry, image, cuts, zone_cell, seconds, zone):
    uc = machine()
    for address, data in image:
        if data:
            uc.mem_write(address, data)
    uc.mem_write(zone_cell, (0x20004000).to_bytes(4, "little"))
    uc.mem_write(0x20004008, bytes([zone & 0xff]))
    uc.reg_write(UC_ARM_REG_R0, 0x20005000)
    trace = []

    def hook(engine, address, size, _):
        role = cuts.get(address)
        if role is None:
            return
        if role == "snapshot":
            trace.append(role)
        elif role == "epoch":
            trace.append(role)
            engine.reg_write(UC_ARM_REG_R0, seconds)
        else:
            value = engine.reg_read(UC_ARM_REG_R0)
            dest = engine.reg_read(UC_ARM_REG_R1)
            trace.append({"role": role, "seconds": value, "dest": hex(dest)})
            engine.mem_write(dest, (0x12345678).to_bytes(4, "little"))
        engine.reg_write(UC_ARM_REG_PC, engine.reg_read(UC_ARM_REG_LR))

    uc.hook_add(UC_HOOK_CODE, hook)
    uc.emu_start(entry | 1, 0x300000, count=10000)
    return trace, bytes(uc.mem_read(0x20005000, 4))


def main():
    payload = STOCK.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PAYLOAD_SHA or \
            int.from_bytes(payload[0x44a40c-0x438000:0x44a410-0x438000], "little") != 0x200036fc:
        raise RuntimeError("Main datetime stock mapping changed")
    stubs = OUT / "datetime-oracle-stubs.c"
    stubs.write_text("""#include <stdint.h>
const uint8_t *g2_audio_log_timezone;
void audio_time_snapshot(uint8_t out[40]) { (void)out; }
uint32_t audio_time_epoch_seconds(const uint8_t in[40]) { (void)in; return 0; }
void audio_time_epoch_to_calendar_449fda(uint32_t s, void *p) { (void)s; (void)p; }
""")
    oracle = OUT / "datetime-oracle.elf"
    subprocess.run(["/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-O2", "-nostdlib", "-ffreestanding", "-fno-builtin",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,g2_log_datetime_now_44a19a",
                    str(SOURCE), str(CONTEXT), str(stubs), "-o", str(oracle)], check=True)
    with oracle.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(seg["p_vaddr"], seg.data()) for seg in elf.iter_segments()
                    if seg["p_type"] == "PT_LOAD"]
        symbols = {sym.name: sym["st_value"] for sym in elf.get_section_by_name(".symtab").iter_symbols()}
    native_cuts = {0x47ef10: "snapshot", 0x44a108: "epoch", 0x449fda: "calendar"}
    source_cuts = {symbols["audio_time_snapshot"] & ~1: "snapshot",
                   symbols["audio_time_epoch_seconds"] & ~1: "epoch",
                   symbols["audio_time_epoch_to_calendar_449fda"] & ~1: "calendar"}
    rows = []
    for seconds, zone in ((0, 0), (123456789, 4), (0, -4),
                          (0xffffffff, 1), (86400, -12)):
        old = execute(0x44a19a, [(0x438000, payload)], native_cuts,
                      0x200036fc, seconds, zone)
        new = execute(symbols["g2_log_datetime_now_44a19a"], segments, source_cuts,
                      symbols["g2_audio_log_timezone"], seconds, zone)
        expected = (seconds + zone * 900) & 0xffffffff
        if old != new or old[0] != ["snapshot", "epoch",
                                   {"role": "calendar", "seconds": expected,
                                    "dest": "0x20005000"}]:
            raise RuntimeError(f"datetime mismatch {seconds} {zone}: {old!r} vs {new!r}")
        rows.append({"epoch_seconds": seconds, "zone_quarters": zone,
                     "calendar_seconds": expected})
    candidate = OUT / "candidate.o"
    before = {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(BASE)], text=True).splitlines() if line.strip()}
    after = {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(candidate)], text=True).splitlines() if line.strip()}
    if (len(before) != 132 or len(after) != 132 or
            before - after != {"g2_log_datetime_now_44a19a"} or
            after - before != {"audio_time_epoch_to_calendar_449fda"}):
        raise RuntimeError("Main datetime import frontier changed")
    result = {"status": "PASS_BOUNDED_MAIN_LOG_DATETIME_NOW_C",
              "stock_payload_sha256": PAYLOAD_SHA,
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "context_source": str(CONTEXT.relative_to(ROOT)), "context_source_sha256": sha(CONTEXT),
              "baseline_object": str(BASE.relative_to(ROOT)), "baseline_object_sha256": sha(BASE),
              "candidate_object": str(candidate.relative_to(ROOT)), "candidate_object_sha256": sha(candidate),
              "oracle_elf": str(oracle.relative_to(ROOT)), "oracle_elf_sha256": sha(oracle),
              "oracle_stubs": str(stubs.relative_to(ROOT)), "oracle_stubs_sha256": sha(stubs),
              "cases": rows, "case_count": len(rows), "unresolved_before": 132,
              "unresolved_after": 132, "replaced_import": "g2_log_datetime_now_44a19a",
              "new_explicit_import": "audio_time_epoch_to_calendar_449fda",
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Five stock/C cases compare child-call order and timezone-adjusted seconds, not RTC hardware.",
                         "Seconds-to-calendar child 0x449fda remains an unresolved C provider.",
                         "Complete logger, layout, and whole Main image remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], len(rows), sha(path))


if __name__ == "__main__":
    main()
