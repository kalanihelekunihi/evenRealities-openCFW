#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Fail-closed identity and memory-map audit of the G2 touch-controller blob.

Component: G2 touch controller (FWPK type 3, /firmware/touch.bin).
Verdict audited here: Infineon/Cypress PSoC 4000T (CY8C4046FNI), ARM
Cortex-M0+, 64 KiB flash, 8 KiB SRAM, fifth-generation CapSense (MSCLP).

Every check is a pure function of the blob bytes and the constants pinned
below.  Any deviation raises AuditError before manifests are written.  The
analyzer never modifies the blob and performs no device or flash operation.
"""

from __future__ import annotations

import csv
import hashlib
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOB = ROOT / "blobs/official/g2-2.2.6.10/firmware_touch.bin"
MANIFEST_DIR = ROOT / "tools/manifests"
BLOB_SHA256 = "0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d"
BLOB_SIZE = 34_464

# FWPK wrapper: 16-byte header + one 16-byte record, payload at 0x20.
FWPK_MAGIC = b"FWPK"
FWPK_FIELD_0x04 = 0x02020001  # bytes 01 00 02 02; observed; semantics unresolved
FWPK_VERSION = 1
FWPK_FLAGS = 0
RECORD_TYPE = 3
RECORD_SIZE = 0x8680  # 34,432-byte raw Cortex-M image
RECORD_OFFSET = 0x20
RECORD_CRC32C = 0x48674BC7  # reflected CRC-32C over the full payload
TRAILING_CRC32C = 0xF75CF6F4  # reflected CRC-32C over payload[:-4]

# Vector table (48 slots = 16 core + 32 external; 13 external populated).
STACK_TOP = 0x20002000
RESET_VECTOR = 0x00004675
HARDFAULT_VECTOR = 0x0000465F
DEFAULT_VECTOR = 0x0000465D
EXTERNAL_IRQ_COUNT = 13
VECTOR_DIGEST = "62575e83fb7b4718742d51d7b5e007ef00a51604b7ed801f4e59a748956e8261"

# Flash-linear regions, offsets relative to the payload start.
REGIONS = (
    # name, start, end, sha256, class, status, notes
    ("vectors", 0x0000, 0x00C0,
     "62575e83fb7b4718742d51d7b5e007ef00a51604b7ed801f4e59a748956e8261",
     "vector-table", "confirmed",
     "ARMv6-M shape; reserved core slots 4-10/12-13 zero; 13 external IRQ slots"),
    ("code", 0x00C0, 0x775C,
     "fe450d33b3e8e3b8d657ea33f4624fba832f2064a3eadb85c287d7fcd2fa67e0",
     "code+pools", "confirmed",
     "Thumb code with embedded literal pools; GCC newlib init-array at 0xC0"),
    ("strings", 0x775C, 0x7DC4,
     "73fc960cd33e4d9ef33451d5d835c35fcb7e169804e9ee672014e138c599a941",
     "const-strings", "confirmed",
     "EasyLogger-format log strings; version 2.2.0.1; power/gesture telemetry"),
    ("const_tables_a", 0x7DC4, 0x8110,
     "f65e342c33de6c249321e27b1029f717b78e719ca7866e0b2535671b85d9d224",
     "const-data", "inferred",
     "nine uint32 tuning constants (0x370E-0x384C, ~14094-14412) at 0x7DC4; runtime descriptors"),
    ("zero_gap_1", 0x8110, 0x8120,
     "374708fff7719dd5979ec875d56cd2286f6d3cf7ec317a3b25632aab28ec37bb",
     "fill-zero", "confirmed", "16-byte zero gap"),
    ("const_tables_b", 0x8120, 0x8430,
     "02c6e186eca0ae9038a8c52c34026c23658104af3354bce067a47939accf0419",
     "const-data", "inferred",
     "configuration tables with SRAM descriptors; likely CapSense/MSC tuning"),
    ("zero_gap_2", 0x8430, 0x85D0,
     "4cc7e6272db6b1ad7581f76c63c694e926e20698e9b02223d5041a55960463f2",
     "fill-zero", "confirmed", "416-byte zero gap"),
    ("config_block", 0x85D0, 0x8650,
     "269eea7cd1cf52a8818b95b756ae17ec776ff6a2f231be58dc8ff0da7f2c6c17",
     "const-config", "inferred",
     "128-byte descriptor referencing MSCLP0 and GPIO PRT4; one flash row"),
    ("ff_pad", 0x8650, 0x867C,
     "463d5921a6bfd5c98f6047f561495800372e627c07ce458c23b7ac164a22be51",
     "fill-ff", "confirmed", "44-byte erased-flash pad"),
    ("trailing_crc", 0x867C, 0x8680,
     "589f84e105896025c0a2a6c20d780e4e9618cb26072abc6b062630692812b52f",
     "checksum", "confirmed",
     "reflected CRC-32C of payload[0:0x867C]; programmed length excludes it"),
)

# PSoC 4000T peripheral block constants (Infineon mtb-pdl-cat2 psoc4000t.svd).
# class: ldr = confirmed PC-relative LDR reference; pool = aligned-word pool,
# inferred; structural = referenced from the const config block.
PERIPHERALS = (
    # address, block, detail, pool occurrences, ldr refs, evidence class
    (0x40010000, "PERI", "peripheral clock dividers", 5, 5, "ldr"),
    (0x40020080, "HSIOM+0x80", "I/O mux port register", 2, 0, "pool"),
    (0x40020100, "HSIOM+0x100", "I/O mux port register", 1, 0, "pool"),
    (0x40030000, "SRSSLT", "power/clock/reset/WDT base", 15, 15, "ldr"),
    (0x40040200, "GPIO_PRT2", "port 2 data registers", 1, 1, "ldr"),
    (0x40040300, "GPIO_PRT3", "port 3 data registers", 1, 1, "ldr"),
    (0x40040400, "GPIO_PRT4", "port 4 data registers", 5, 5, "ldr"),
    (0x40100000, "CPUSS", "SYSREQ/SYSARG SROM syscall interface", 6, 9, "ldr"),
    (0x40100008, "CPUSS+0x8", "SYSARG syscall argument register", 1, 0, "pool"),
    (0x40250000, "SCB1", "I2C slave interface to the host", 4, 14, "ldr"),
    (0x40290000, "MSCLP0", "5th-gen CapSense multi-sense converter", 1, 1, "ldr"),
    (0x40290000, "MSCLP0", "config-block structural reference @0x85F8", 1, 0, "structural"),
)

# NVIC external interrupts, PSoC 4000T SVD order; all vectors -> 0x465D.
NVIC = (
    (0, "ioss_interrupts_gpio_0"), (1, "ioss_interrupts_gpio_1"),
    (2, "ioss_interrupts_gpio_2"), (3, "ioss_interrupts_gpio_3"),
    (4, "ioss_interrupt_gpio"), (5, "srss_interrupt_wdt"),
    (6, "scb_0_interrupt"), (7, "scb_1_interrupt"),
    (8, "msclp_interrupt_lp"), (9, "cpuss_interrupt_spcif"),
    (10, "msclp_interrupt"), (11, "tcpwm_interrupts_0"),
    (12, "tcpwm_interrupts_1"),
)

# Digests over deterministic censuses (see census functions below).
MMIO_POOL_DIGEST = "24a02e80d84c4004fbd68610a39724fd725902aa8010b7ea58b9beee7874a7cb"
SRAM_PTR_DIGEST = "9baa756c5fdcf0863497bc0abe3fb063410a80ecb5a7aa940aa24439df5dd2f5"
SROM_DECODER_DIGEST = "e6c7aeccd7e4d673fbda29f4cff209ea48398c6683bfbedbc36b9405f5c5e1f2"
SROM_DECODER_SPAN = (0x58F4, 0x5946)

JUMP_TABLE_OFFSET = 0x7DC4
JUMP_TABLE = (0x370E, 0x3746, 0x382C, 0x370E, 0x384C, 0x37A0, 0x3766, 0x37C8, 0x3780)

UNVE_MAGIC = 0x45564E55
UNVE_POOL_OFFSETS = (0x06FC, 0x0734, 0x0770)

CONFIG_BLOCK_KEY_WORDS = ((0x85F8, 0x40290000), (0x8600, 0x40040400), (0x8608, 0x40040400))

REQUIRED_STRINGS = (
    b"2.2.0.1", b"TP VER:%s", b"ACT->ALR", b"ALR->WOT", b"WOT->ACT",
    b"WOT->ALR", b"LEFT", b"RIGHT", b"EEPROM", b"5-fast-clicks",
)

CODE_SPAN = (0x00C0, 0x775C)
TABLE_SPANS = ((0x7DC4, 0x8650),)


class AuditError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def crc32c(data: bytes) -> int:
    """Reflected CRC-32C (Castagnoli), init/xorout 0xFFFFFFFF."""
    crc = 0xFFFFFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ (0x82F63B78 if crc & 1 else 0)
    return crc ^ 0xFFFFFFFF


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def mmio_pool_census(payload: bytes) -> list[tuple[int, int]]:
    """Every 4-aligned word in the code span inside the PSoC 4 MMIO window.

    The list deliberately includes Thumb instruction pairs that alias the
    window (e.g. 0x4003xxxx = movs/ands halfword pairs); the digest is an
    integrity census, not a peripheral claim.  Confirmed peripheral blocks
    are pinned separately in PERIPHERALS.
    """
    out = []
    for off in range(CODE_SPAN[0], CODE_SPAN[1], 4):
        word = struct.unpack_from("<I", payload, off)[0]
        if 0x40000000 <= word < 0x41000000:
            out.append((off, word))
    return out


def sram_pointer_census(payload: bytes) -> list[tuple[int, int]]:
    spans = [CODE_SPAN, *TABLE_SPANS]
    out = []
    for start, end in spans:
        for off in range(start, end, 4):
            word = struct.unpack_from("<I", payload, off)[0]
            if 0x20000000 <= word < STACK_TOP:
                out.append((off, word))
    return out


def census_digest(pairs: list[tuple[int, int]]) -> str:
    return sha256(b"".join(struct.pack("<II", *pair) for pair in pairs))


def audit(blob: bytes) -> dict:
    checks = []

    def ok(name: str, detail: str) -> None:
        checks.append({"check": name, "result": "pass", "detail": detail})

    require(len(blob) == BLOB_SIZE, f"blob size {len(blob)} != {BLOB_SIZE}")
    require(sha256(blob) == BLOB_SHA256, "blob SHA-256 mismatch")
    ok("blob-authenticity", "size 34,464 and SHA-256 match PROVENANCE.md")

    require(blob[0:4] == FWPK_MAGIC, "FWPK magic missing")
    field04, version, flags = struct.unpack_from("<III", blob, 4)
    require(field04 == FWPK_FIELD_0x04, f"FWPK field@0x04 {field04:#x} changed")
    require(version == FWPK_VERSION and flags == FWPK_FLAGS, "FWPK version/flags changed")
    rtype, rsize, roff, rcrc = struct.unpack_from("<IIII", blob, 16)
    require(rtype == RECORD_TYPE, "FWPK record type != 3 (touch)")
    require(rsize == RECORD_SIZE and roff == RECORD_OFFSET, "FWPK record size/offset changed")
    payload = blob[roff:roff + rsize]
    require(len(payload) == rsize, "payload truncated")
    require(rcrc == RECORD_CRC32C, "record CRC field changed")
    require(crc32c(payload) == rcrc, "record CRC-32C does not cover payload")
    ok("fwpk-wrapper", "16B header + 16B type-3 record; CRC-32C(reflected) = 0x48674BC7")

    trailing = struct.unpack_from("<I", payload, rsize - 4)[0]
    require(trailing == TRAILING_CRC32C, "trailing checksum changed")
    require(crc32c(payload[:-4]) == trailing, "trailing CRC-32C does not cover payload[:-4]")
    ok("trailing-checksum", "payload[:-4] CRC-32C = 0xF75CF6F4; programmed length = 0x867C")

    vectors = struct.unpack_from("<48I", payload, 0)
    require(vectors[0] == STACK_TOP, "initial SP != 0x20002000 (8 KiB SRAM top)")
    require(vectors[1] == RESET_VECTOR, "reset vector != 0x00004675")
    require(vectors[2] == DEFAULT_VECTOR, "NMI vector changed")
    require(vectors[3] == HARDFAULT_VECTOR, "HardFault vector != 0x0000465F")
    require(all(w == 0 for w in vectors[4:11]), "ARMv6-M reserved slots 4-10 nonzero")
    require(all(w == 0 for w in vectors[12:14]), "ARMv6-M reserved slots 12-13 nonzero")
    require(vectors[11] == DEFAULT_VECTOR and vectors[14] == DEFAULT_VECTOR
            and vectors[15] == DEFAULT_VECTOR, "SVC/PendSV/SysTick vectors changed")
    for slot in range(EXTERNAL_IRQ_COUNT):
        require(vectors[16 + slot] == DEFAULT_VECTOR,
                f"external IRQ{slot} vector != default 0x465D")
    require(all(w == 0 for w in vectors[16 + EXTERNAL_IRQ_COUNT:]),
            "IRQ slots beyond PSoC 4000T count populated")
    require(sha256(payload[:0xC0]) == VECTOR_DIGEST, "vector table digest mismatch")
    ok("vector-table", "ARMv6-M shape; 13 external IRQs = PSoC 4000T NVIC count; all default 0x465D")

    for name, start, end, digest, _class, _status, _notes in REGIONS:
        require(sha256(payload[start:end]) == digest, f"region {name} digest mismatch")
    require(all(b == 0 for b in payload[0x8110:0x8120]), "zero_gap_1 not zero")
    require(all(b == 0 for b in payload[0x8430:0x85D0]), "zero_gap_2 not zero")
    require(all(b == 0xFF for b in payload[0x8650:0x867C]), "ff_pad not 0xFF")
    ok("region-map", "10 pinned regions authenticated byte-for-byte")

    pools = mmio_pool_census(payload)
    require(census_digest(pools) == MMIO_POOL_DIGEST, "MMIO pool census digest mismatch")
    pool_words = {}
    for _off, word in pools:
        pool_words[word] = pool_words.get(word, 0) + 1
    for address, block, _detail, count, _refs, _cls in PERIPHERALS[:10]:
        require(pool_words.get(address, 0) == count,
                f"{block} pool occurrence count changed at {address:#x}")
    ok("peripheral-census",
       "PERI/HSIOM/SRSSLT/GPIO PRT2-4/CPUSS/SCB1/MSCLP0 block bases match PSoC 4000T SVD")

    require(sha256(payload[SROM_DECODER_SPAN[0]:SROM_DECODER_SPAN[1]]) == SROM_DECODER_DIGEST,
            "SROM syscall status decoder changed")
    ok("srom-decoder", "CPUSS SYSARG 0xA/0xF status-class decoder at 0x58F4 (PSoC 4 flash syscalls)")

    table = struct.unpack_from("<9I", payload, JUMP_TABLE_OFFSET)
    require(tuple(table) == JUMP_TABLE, "0x7DC4 tuning-constant table changed")
    ok("tuning-table", "9 uint32 tuning constants at 0x7DC4 (0x370E-0x384C; MSC/tuning class; "
                       "earlier switch-table reading corrected in g2-touch-i2c-protocol-recovery.md)")

    for off in UNVE_POOL_OFFSETS:
        require(struct.unpack_from("<I", payload, off)[0] == UNVE_MAGIC,
                f"UNVE magic pool at {off:#x} changed")
    ok("config-magic", "0x45564E55 ('UNVE') EEPROM-config magic pools at 0x6FC/0x734/0x770")

    for off, word in CONFIG_BLOCK_KEY_WORDS:
        require(struct.unpack_from("<I", payload, off)[0] == word,
                f"config block word at {off:#x} changed")
    ok("config-block", "128B config block references MSCLP0 and GPIO PRT4")

    strings = payload[0x775C:0x7DC4]
    for needle in REQUIRED_STRINGS:
        require(needle in strings, f"required string missing: {needle!r}")
    ok("strings", "version 2.2.0.1, TP VER, ACT/ALR/WOT power states, gesture/EEPROM logs present")

    sram = sram_pointer_census(payload)
    require(census_digest(sram) == SRAM_PTR_DIGEST, "SRAM pointer census digest mismatch")
    sram_values = sorted({word for _off, word in sram if word >= 0x20000400})
    ok("sram-census", f"{len(sram)} pointer-like words; plausible data {hex(min(sram_values))}.."
                      f"{hex(max(sram_values))}; stack top 0x20002000")

    return {
        "checks": checks,
        "mmio_pools": pools,
        "sram_pointers": sram,
        "sram_plausible_min": min(sram_values),
        "sram_plausible_max": max(sram_values),
    }


def write_manifests(report: dict) -> list[Path]:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    written = []

    regions_tsv = MANIFEST_DIR / "g2-touch-identity-regions.tsv"
    with regions_tsv.open("w", newline="") as fh:
        wr = csv.writer(fh, delimiter="\t", lineterminator="\n")
        wr.writerow(["region", "start", "end_exclusive", "size", "sha256", "class", "status", "notes"])
        for name, start, end, digest, cls, status, notes in REGIONS:
            wr.writerow([name, f"0x{start:05X}", f"0x{end:05X}", end - start, digest, cls, status, notes])
    written.append(regions_tsv)

    census_tsv = MANIFEST_DIR / "g2-touch-identity-peripheral-census.tsv"
    with census_tsv.open("w", newline="") as fh:
        wr = csv.writer(fh, delimiter="\t", lineterminator="\n")
        wr.writerow(["address", "psoc4000t_block", "detail", "pool_occurrences",
                     "ldr_confirmed_refs", "evidence_class"])
        for address, block, detail, count, refs, cls in PERIPHERALS:
            wr.writerow([f"0x{address:08X}", block, detail, count, refs, cls])
    written.append(census_tsv)

    memory_map = {
        "component": "g2-touch",
        "blob": {"path": "blobs/official/g2-2.2.6.10/firmware_touch.bin",
                 "size": BLOB_SIZE, "sha256": BLOB_SHA256},
        "identity": {
            "verdict": "Infineon/Cypress PSoC 4000T, ordering part CY8C4046FNI",
            "cpu": "ARM Cortex-M0+ (ARMv6-M), 48 MHz max",
            "flash_kb": 64, "sram_kb": 8, "package": "WLCSP-25 (T412T) or QFN (T442T/T452T)",
            "capsense": "5th-generation multi-sense converter (MSCLP0)",
            "confidence": "high (family); OPN rests on retained host driver path drv_cy8c4046fni.c",
            "firmware_version_string": "2.2.0.1",
        },
        "container": {
            "format": "FWPK",
            "header": {"magic": "FWPK", "field_0x04": FWPK_FIELD_0x04,
                       "version": FWPK_VERSION, "flags": FWPK_FLAGS},
            "record": {"type": RECORD_TYPE, "size": RECORD_SIZE, "offset": RECORD_OFFSET,
                       "crc32c_reflected": RECORD_CRC32C},
            "trailing_crc32c_reflected": TRAILING_CRC32C,
            "programmed_length": RECORD_SIZE - 4,
        },
        "memory_map": {
            "flash_base": 0x00000000,
            "initial_sp": STACK_TOP,
            "reset_vector": RESET_VECTOR,
            "regions": [
                {"name": n, "start": s, "end": e, "size": e - s, "sha256": d,
                 "class": c, "status": st, "notes": nt}
                for n, s, e, d, c, st, nt in REGIONS],
            "peripherals": [
                {"address": a, "block": b, "detail": dt, "pool_occurrences": c,
                 "ldr_confirmed_refs": r, "evidence_class": cl}
                for a, b, dt, c, r, cl in PERIPHERALS],
            "nvic": [{"irq": i, "name": n, "vector": DEFAULT_VECTOR} for i, n in NVIC],
            "sram": {"stack_top": STACK_TOP,
                     "plausible_data_min": report["sram_plausible_min"],
                     "plausible_data_max": report["sram_plausible_max"],
                     "pointer_like_words": len(report["sram_pointers"])},
        },
        "update_format": {
            "transport_commands_host_side": {
                "0x38": "enter DFU", "0x4C": "set application metadata",
                "0x37": "send one 32-byte packet", "0x49": "program 128-byte block",
                "0x31": "verify application", "0x3B": "exit DFU",
                "source": "g2-service-touch-dfu-recovery.md (host-side closure)",
            },
            "frame": "0x01 | cmd | len16le | payload(<=32B) | cksum16 | 0x17",
            "program_block_bytes": 128,
            "packet_payload_bytes": 32,
            "device_side_corroboration": [
                "CPUSS SYSREQ/SYSARG SROM flash-syscall decoder at 0x58F4",
                "enter-DFU handoff: mailbox write + NVIC_SystemReset at 0x4B30 "
                "(see g2-touch-i2c-protocol-recovery.md)",
                "trailing CRC-32C self-checksum consistent with verify-app step",
            ],
        },
        "audit": {"checks": report["checks"]},
    }
    map_json = MANIFEST_DIR / "g2-touch-identity-memory-map.json"
    map_json.write_text(json.dumps(memory_map, indent=2, sort_keys=True) + "\n")
    written.append(map_json)
    return written


def main() -> int:
    blob = BLOB.read_bytes()
    report = audit(blob)
    written = write_manifests(report)
    for path in written:
        print(f"wrote {path.relative_to(ROOT)}")
    print(f"PASS: {len(report['checks'])} checks; PSoC 4000T identity and memory map authenticated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
