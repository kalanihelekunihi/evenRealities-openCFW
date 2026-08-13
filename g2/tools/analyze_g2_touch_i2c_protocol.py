#!/usr/bin/env python3
"""Fail-closed audit of the G2 touch-controller device-side I2C protocol.

Component: G2 touch controller (FWPK type 3, /firmware/touch.bin) on the
PSoC 4000T (CY8C4046FNI) established by analyze_g2_touch_identity.py.

Pins, re-derived from the blob:
  * the SCB1 I2C-slave init, IRQ handler, RX command dispatch sequence and
    all seven recovered command-body entry points;
  * the report builder, event dispatcher, EEPROM config module, DFU handoff
    (mailbox + NVIC_SystemReset), power management, FIFO descriptor helpers
    and the compiled-out logger stub;
  * every pool word fixing the SRAM state layout, the protocol constant
    0x01000202, and the payload->resident reference topology (switch tables
    and HAL descriptors outside the shipped prefix);
  * BL call-site counts for the key protocol functions.

Any deviation raises AuditError before manifests are written.  The analyzer
never modifies the blob and performs no device or flash operation.
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
RECORD_OFFSET = 0x20
RECORD_SIZE = 0x8680

# Pinned code spans (SHA-256 over payload[start:end]).
SPANS = (
    # name, start, end, sha256, role
    ("i2c_slave_init", 0x0378, 0x03DA,
     "14859a32e5cb14c433222df6ddf0e50eccc68a424161e9088db386d03f6da026",
     "SCB1 I2C-slave init: HAL tables, RX/TX descriptors, SCB1 IRQ7 enable"),
    ("i2c_irq_handler_and_cases", 0x0400, 0x05A0,
     "d8911073cd4696cc8e93bf1d15bda36ec7fe5f654837b3421b49ac58ca088076",
     "SCB1 IRQ handler: status demux, RX validation, 9-slot command dispatch, 7 case bodies"),
    ("report_builder", 0x0824, 0x0960,
     "2dfdebfc817b8de4a5cab6d0e046511c89edd817a8f5d51cc42575f352074128",
     "periodic 16-byte report build, prox-baseline EEPROM save policy, attention assert"),
    ("event_dispatcher", 0x37C0, 0x38CA,
     "a23e3a5e51a9e09ff72ba298701931212de059c566c48432f7898e2bbcdb3cc5",
     "generic device-event dispatcher, events 0-7, resident 8-entry table 0xB4FC"),
    ("dfu_handoff_and_reset", 0x4B14, 0x4B44,
     "56c6900e582fe22b2cbec6d71cde6979b68ba98e6dfe307ac2ed72ac9f3b3ebc",
     "NVIC_SystemReset plus boot-mode mailbox writer (enter-DFU)"),
    ("fifo_descriptors", 0x67D8, 0x680C,
     "6e882eca8aa4db5aec28f48319a4de30227ea7dad2719436275ae8c9171dd1f7",
     "RX/TX descriptor arm helpers and RX-position getter"),
    ("power_mgmt", 0x703A, 0x70A4,
     "57234a89b2cf1792dad138e8f0b00f84e85a19b229a6151ef94eebc9fd9d4ccf",
     "CPUSS power-mode setter, sleep/deep-sleep WFI entries, SFLASH trim load"),
    ("logger_stub", 0x0BE0, 0x0BE8,
     "d5af164eb1253e2dc1faf4d9271ca5119221d2f156233a278dcbf632803173de",
     "compiled-out logger: push args, return 0; all 38 call sites are no-ops"),
    ("eeprom_config_module", 0x0660, 0x0780,
     "0a97bda2b4b4f6eae1f6f23af5105a22dab792a1f79e35a00ac74a064db1d751",
     "EEPROM-emulation config load/save with UNVE magic 0x45564E55"),
    ("sensor_read_mux", 0x02F4, 0x0324,
     "42770c5c2e8b77f3b992a3d049d3b706082280b7dfb7ab13ed15b0900312ef3d",
     "per-channel sensor read multiplexer used by report and read-report command"),
)

# Pool words fixing the contract (offset, value, role).
POOLS = (
    (0x0334, 0x40250000, "SCB1 base (i2c_slave_init call)"),
    (0x03E4, 0x40250000, "SCB1 base (i2c_slave_init body)"),
    (0x05A8, 0x40250000, "SCB1 base (IRQ handler/cases)"),
    (0x0990, 0x40250000, "SCB1 base (report builder TX arm)"),
    (0x0994, 0x40040400, "GPIO_PRT4 base (attention DR_CLR in report builder)"),
    (0x05DC, 0x40040400, "GPIO_PRT4 base (attention DR_SET in TX rearm)"),
    (0x05B0, 0x01000202, "protocol compatibility word (== FWPK field@0x04)"),
    (0x4B40, 0x20000000, "boot-mode mailbox address (SRAM base)"),
    (0x4B28, 0xE000ED00, "SCB AIRCR window base"),
    (0x4B2C, 0x05FA0004, "AIRCR VECTKEY|SYSRESETREQ"),
    (0x03FC, 0xE000E100, "NVIC ISER base (SCB1 IRQ7 enable)"),
    (0x0960, 0x200004EC, "sensor context"),
    (0x0964, 0x200008E8, "event source pointer cell"),
    (0x0968, 0x20000940, "report preprocessor state"),
    (0x096C, 0x20000990, "report staging buffer (16 bytes)"),
    (0x0970, 0x200009CF, "save-prox-baseline request flag"),
    (0x0974, 0x200009D0, "config block: +4 prox baseline, +6 long-press threshold"),
    (0x0988, 0x200009B0, "TX reply buffer (16 bytes)"),
    (0x098C, 0x200008EC, "SCB1 driver state struct"),
    (0x099C, 0x200009CC, "report-pending flag"),
    (0x09A0, 0x200009C8, "report timeout (0x280)"),
    (0x05A0, 0x200008EC, "SCB1 driver state struct (IRQ handler)"),
    (0x05A4, 0x200009A0, "RX command buffer (16 bytes; [0]=command)"),
    (0x05B4, 0x200009B0, "TX reply buffer (cases)"),
    (0x05B8, 0x200009D0, "config block (cases)"),
    (0x05BC, 0x200009CF, "save-prox-baseline request flag (case C4)"),
    (0x05C8, 0x200009A1, "RX argument bytes (case C5 memcpy source)"),
    (0x05CC, 0x200004E8, "gesture-config mirror"),
    (0x05D0, 0x200009CE, "gesture-config dirty flag 1"),
    (0x05D4, 0x200009CD, "gesture-config dirty flag 2"),
)

# Payload->resident references (offset, resident address, role).
RESIDENT_REFS = (
    (0x05AC, 0xB0C4, "RX command dispatch switch table, 9 entries (commands 0-8)"),
    (0x38CC, 0xB4FC, "event-dispatcher switch table, 8 entries (events 0-7)"),
    (0x5954, 0xB51C, "SROM status-decoder switch table, 20 entries"),
    (0x03E0, 0xB374, "SCB1 HAL config table"),
    (0x03EC, 0xB0E8, "HAL callback registry table (payload callback 0x3624)"),
    (0x05C0, 0xAA5C, "log tag string (dead; logger stubbed)"),
    (0x097C, 0xAA5C, "log tag string (dead; logger stubbed)"),
)

# RX dispatch sequence halfwords at 0x42C-0x444 (re-derived, capstone-free).
DISPATCH_SITE = 0x42C
DISPATCH_HALFWORDS = (0xB2C0, 0x1E43, 0xB2DB, 0x2B0F, 0xD8EB, 0x4B5B, 0x781B,
                      0x2B08, 0xD8E7, 0x009B, 0x4A5A, 0x58D3, 0x469F)
#   uxtb r0,r0 / subs r3,r0,#1 / uxtb r3,r3 / cmp r3,#0xf / bhi ret /
#   ldr r3,[pc] / ldrb r3,[r3] / cmp r3,#8 / bhi ret / lsls r3,r3,#2 /
#   ldr r2,[pc] / ldr r3,[r2,r3] / mov pc,r3

# Recovered command bodies, in physical layout order.  Command indices are
# inferred from layout order because the 9-entry table lives in the resident
# region; roles are pinned by the case-body bytes.
COMMANDS = (
    # slot (inferred), body entry, role, reply contract, confidence
    (0, 0x0446, "version/identity query",
     "16B reply {02,02,00,01,01,00,02,02,...} = version 2.2.0.1 + protocol word 0x01000202",
     "body confirmed; index inferred from layout order"),
    (1, 0x0466, "read saved proximity baseline",
     "16B reply carrying u16 config[0x200009D4]", "body confirmed; index inferred"),
    (2, 0x0480, "read long-press threshold",
     "16B reply (zeroed) carrying u16 config[0x200009D6]", "body confirmed; index inferred"),
    (3, 0x04A0, "save proximity baseline to EEPROM",
     "sets flag 0x200009CF; reply {5,0,0x17}; deferred save in report builder",
     "body confirmed; index inferred"),
    (4, 0x04C8, "write gesture configuration (long-press ms)",
     "u16 arg from rx[1..2], arg!=0 else {7,0xFF,0x17}; stores config+mirror, dirty flags; {7,0,0x17}",
     "body confirmed; index inferred; validation matches host at_tp.c 1-65535ms rule"),
    (5, 0x052C, "enter DFU",
     "reply {2,0,0x17}; mailbox[0x20000000]=0; NVIC_SystemReset",
     "body confirmed; index inferred"),
    (6, 0x054C, "read current sensor report",
     "10B reply from two sensor_read_mux channels (proximity + slider)",
     "body confirmed; index inferred"),
    (7, None, "unresolved slot", "no distinct body in shipped prefix (default/shared)", "open"),
    (8, None, "unresolved slot", "no distinct body in shipped prefix (default/shared)", "open"),
)

CALL_COUNTS = {
    0x0BE0: 38,  # logger stub
    0x4B30: 1,   # enter-DFU mailbox+reset (only from the DFU command case)
    0x67D8: 10,  # TX descriptor arm
    0x67F0: 2,   # RX descriptor arm
    0x6806: 1,   # RX position getter
    0x4B14: 1,   # NVIC_SystemReset
    0x0824: 2,   # report builder
    0x0400: 0,   # SCB1 IRQ handler: indirect entry only (SRAM vector/callback)
}


class AuditError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def bl_target(hw1: int, hw2: int, pc: int) -> int | None:
    if hw1 & 0xF800 != 0xF000 or hw2 & 0xD000 != 0xD000:
        return None
    s = (hw1 >> 10) & 1
    j1 = (hw2 >> 13) & 1
    j2 = (hw2 >> 11) & 1
    i1 = 1 if (j1 ^ s) == 0 else 0
    i2 = 1 if (j2 ^ s) == 0 else 0
    off = (s << 24) | (i1 << 23) | (i2 << 22) | ((hw1 & 0x3FF) << 12) | ((hw2 & 0x7FF) << 1)
    if s:
        off -= 1 << 25
    return (pc + 4 + off) & 0xFFFFFFFF


def call_census(payload: bytes) -> dict[int, int]:
    counts: dict[int, int] = {}
    for a in range(0xC0, 0x775C - 3, 2):
        hw1, hw2 = struct.unpack_from("<HH", payload, a)
        t = bl_target(hw1, hw2, a)
        if t is not None and t < 0x775C and t % 2 == 0:
            counts[t] = counts.get(t, 0) + 1
    return counts


def audit(blob: bytes) -> dict:
    checks = []

    def ok(name: str, detail: str) -> None:
        checks.append({"check": name, "result": "pass", "detail": detail})

    require(len(blob) == BLOB_SIZE, "blob size mismatch")
    require(sha256(blob) == BLOB_SHA256, "blob SHA-256 mismatch")
    payload = blob[RECORD_OFFSET:RECORD_OFFSET + RECORD_SIZE]
    require(len(payload) == RECORD_SIZE, "payload truncated")
    ok("blob-authenticity", "touch blob authenticated; payload 0x8680 bytes")

    for name, start, end, digest, _role in SPANS:
        require(sha256(payload[start:end]) == digest, f"span {name} digest mismatch")
    ok("protocol-spans", f"{len(SPANS)} protocol code spans authenticated byte-for-byte")

    for off, value, role in POOLS:
        require(struct.unpack_from("<I", payload, off)[0] == value,
                f"pool at {off:#06x} ({role}) changed")
    ok("state-pools", f"{len(POOLS)} SRAM/peripheral/protocol pool words pinned")

    for off, value, role in RESIDENT_REFS:
        require(struct.unpack_from("<I", payload, off)[0] == value,
                f"resident reference at {off:#06x} ({role}) changed")
    ok("resident-references",
       "payload depends on resident switch tables 0xB0C4/0xB4FC/0xB51C and HAL tables 0xB374/0xB0E8")

    halfwords = struct.unpack_from("<13H", payload, DISPATCH_SITE)
    require(tuple(halfwords) == DISPATCH_HALFWORDS, "RX dispatch sequence changed")
    ok("rx-dispatch",
       "rx_len in [1,16]; switch on rx_buf[0] in [0,8]; lsls/ldr/mov-pc idiom at 0x42C-0x444")

    counts = call_census(payload)
    for target, expected in CALL_COUNTS.items():
        require(counts.get(target, 0) == expected,
                f"BL census for {target:#06x}: {counts.get(target, 0)} != {expected}")
    ok("call-topology",
       "logger stub x38; enter-DFU x1 (command case only); IRQ handler indirect-only; report builder x2")

    return {"checks": checks}


def write_manifests(report: dict) -> list[Path]:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    written = []

    cmd_tsv = MANIFEST_DIR / "g2-touch-i2c-command-map.tsv"
    with cmd_tsv.open("w", newline="") as fh:
        wr = csv.writer(fh, delimiter="\t", lineterminator="\n")
        wr.writerow(["slot_inferred", "body_entry", "role", "reply_contract", "confidence"])
        for slot, entry, role, reply, conf in COMMANDS:
            wr.writerow([slot if slot is not None else "",
                         f"0x{entry:04X}" if entry is not None else "-",
                         role, reply, conf])
    written.append(cmd_tsv)

    span_tsv = MANIFEST_DIR / "g2-touch-i2c-span-map.tsv"
    with span_tsv.open("w", newline="") as fh:
        wr = csv.writer(fh, delimiter="\t", lineterminator="\n")
        wr.writerow(["span", "start", "end_exclusive", "size", "sha256", "role"])
        for name, start, end, digest, role in SPANS:
            wr.writerow([name, f"0x{start:05X}", f"0x{end:05X}", end - start, digest, role])
    written.append(span_tsv)

    protocol = {
        "component": "g2-touch",
        "blob": {"path": "blobs/official/g2-2.2.6.10/firmware_touch.bin",
                 "size": BLOB_SIZE, "sha256": BLOB_SHA256},
        "transport": {
            "peripheral": "SCB1 (0x40250000) I2C slave",
            "irq": {"number": 7, "name": "scb_1_interrupt",
                    "handler": "0x0400 (indirect entry; SRAM vector/HAL callback)",
                    "nvic": "ISER/ICPR bit 7 via 0xE000E100"},
            "hal_tables": {"scb_config": "0xB374 (resident)", "callback_registry": "0xB0E8 (resident)",
                           "payload_callback": "0x3624"},
            "rx_buffer": {"address": "0x200009A0", "size": 16,
                          "layout": "[0]=command 0-8, [1..]=arguments"},
            "tx_buffer": {"address": "0x200009B0", "size": 16, "idle_fill": "0x5A"},
            "rx_length_rule": "received frame length must be in [1,16]",
            "attention_line": {"port": "GPIO_PRT4", "pin": 0, "polarity": "active-low",
                               "assert": "DR_CLR (0x40040444)=1 on report ready",
                               "release": "DR_SET (0x40040440)=1 after host read"},
            "driver_state_struct": "0x200008EC (rx desc +0x28, tx desc +0x38, +0x44 const 0x3701)",
        },
        "commands": [
            {"slot_inferred": s, "body_entry": e, "role": r, "reply_contract": rp, "confidence": c}
            for s, e, r, rp, c in COMMANDS],
        "reply_framing": "[0]=reply id, [1]=status (0 ok / 0xFF error), [2]=0x17 terminator; 16-byte frames",
        "report": {
            "staging": "0x20000990", "size": 16,
            "fields": ["[0] event type", "[1..3] event payload",
                       "[4..5] u16 proximity baseline", "[6..7] u16 channel value",
                       "[8..9] u16 proximity value", "[10..11] u16 gesture result"],
            "pending_flag": "0x200009CC", "timeout": "0x200009C8 = 0x280 (640)",
        },
        "config": {
            "saved_prox_baseline": "u16 @0x200009D4",
            "long_press_threshold_ms": "u16 @0x200009D6 (write validates arg != 0; host at_tp.c bounds 1-65535)",
            "gesture_mirror": "0x200004E8", "dirty_flags": ["0x200009CE", "0x200009CD"],
            "save_policy": "deferred: |current - saved| > 49 triggers EEPROM write in report cycle",
            "eeprom_magic": "0x45564E55 (UNVE)",
        },
        "dfu_handoff": {
            "command_case": "0x052C",
            "sequence": "reply {2,0,0x17}; 0x4B30(mode=0): mailbox[0x20000000]=mode; DSB; AIRCR=0x05FA0004; spin",
            "mailbox": "0x20000000 (SRAM base, preserved across reset)",
            "dfu_engine": "resident (not in shipped prefix); host-side commands 0x38/0x4C/0x37/0x49/0x31/0x3B "
                          "per g2-service-touch-dfu-recovery.md; device-side handler gated",
        },
        "resident_dependency": {
            "model": "payload = shipped prefix [0,0x8680) of one base-0 linked image; "
                     "rodata/tables continue to >=0xBDF8 in factory-programmed flash",
            "required_resident": ["switch tables 0xB0C4/0xB4FC/0xB51C",
                                  "HAL tables 0xB374/0xB0E8",
                                  "dead log strings 0xAA5C-0xB09C (logger stubbed)"],
            "logger": "compiled-out stub at 0x0BE0; 38 call sites are no-ops",
        },
        "audit": {"checks": report["checks"]},
    }
    map_json = MANIFEST_DIR / "g2-touch-i2c-protocol-map.json"
    map_json.write_text(json.dumps(protocol, indent=2, sort_keys=True) + "\n")
    written.append(map_json)
    return written


def main() -> int:
    blob = BLOB.read_bytes()
    report = audit(blob)
    written = write_manifests(report)
    for path in written:
        print(f"wrote {path.relative_to(ROOT)}")
    print(f"PASS: {len(report['checks'])} checks; touch I2C protocol map authenticated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
