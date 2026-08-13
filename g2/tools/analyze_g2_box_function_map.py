#!/usr/bin/env python3
"""Per-function attribution for the G2 charging-case (box) firmware.

Consumes the deterministic Ghidra 12.1.2 export artifacts produced on the
lorelei lane by tools/ghidra_scripts/BoxExportFunctionMap.java:

  tools/manifests/g2-box-ghidra-functions.tsv
  tools/manifests/g2-box-ghidra-strings.tsv
  tools/manifests/g2-box-ghidra-string-xrefs.tsv
  tools/manifests/g2-box-ghidra-meta.tsv
  tools/manifests/g2-box-ghidra-SHA256SUMS   (integrity envelope)

and classifies every discovered function of the 55,752-byte case
application into the project's seven source-ownership categories:

  upstream_cmsis_startup  - vector/default handlers, reset, SystemInit,
                            _start, and the toolchain runtime leaves
  upstream_freertos_kernel- FreeRTOS V10-line kernel, GCC ARM_CM0 port,
                            and the CMSIS-RTOS2 (cmsis_os2) wrapper
  upstream_stm32_hal      - STM32CubeG0 HAL driver bodies (UART IRQ
                            cluster, FLASH credential cluster)
  first_party_g2          - G2 charging/battery/aging/LED/OTA/UART
                            policy, task/timer entries, log sink
  unresolved              - no evidence-anchored classification yet
  generated_transport     - wrapper-level only; no function rows
  device_specific_preserve- external SN windows; no function rows

Anchors are the pinned islands from
tools/analyze_g2_box_stm32g0_platform.py; every anchored address must
appear in the Ghidra map with the exact expected size, or the analysis
fails closed.

Run:
    PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 \\
        tools/analyze_g2_box_function_map.py [--write-manifests]

Test:
    PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 \\
        -m unittest tests.test_analyze_g2_box_function_map -v
"""

from __future__ import annotations

import hashlib
import json
import struct
import sys
from pathlib import Path

G2_ROOT = Path(__file__).resolve().parents[1]
BLOB_REL = "blobs/official/g2-2.2.6.10/firmware_box.bin"
BLOB = G2_ROOT / BLOB_REL
MANIFEST_DIR = G2_ROOT / "tools/manifests"

ARTIFACTS = {
    "functions.tsv": "g2-box-ghidra-functions.tsv",
    "strings.tsv": "g2-box-ghidra-strings.tsv",
    "string_xrefs.tsv": "g2-box-ghidra-string-xrefs.tsv",
    "meta.tsv": "g2-box-ghidra-meta.tsv",
}
ENVELOPE = "g2-box-ghidra-SHA256SUMS"

BLOB_SHA256 = "36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374"
APP_BASE = 0x08000000
APP_BYTES = 55_752
WRAPPER = 32

OWNERSHIP_CATEGORIES = [
    "generated_transport",
    "upstream_cmsis_startup",
    "upstream_freertos_kernel",
    "upstream_stm32_hal",
    "first_party_g2",
    "device_specific_preserve",
    "unresolved",
]

# --- pinned island anchors (from analyze_g2_box_stm32g0_platform.py) ---
ANCHORS = {
    0x08000102: ("xPortPendSVHandler", "upstream_freertos_kernel",
                 "exact GCC ARM_CM0 V10-line port sequence; pinned island"),
    0x08008420: ("systick_gate", "upstream_freertos_kernel",
                 "SysTick vector: SCS read + xTaskGetSchedulerState guard"),
    0x0800C5AC: ("xPortSysTickHandler", "upstream_freertos_kernel",
                 "mask/xTaskIncrementTick/PENDSVSET/unmask; SCB literal "
                 "0xE000ED00"),
    0x0800CA4C: ("xTaskGetSchedulerState", "upstream_freertos_kernel",
                 "exact body over kernel statics at 0x20000128"),
    0x0800CA78: ("xTaskIncrementTick", "upstream_freertos_kernel",
                 "exact head over xTickCount/xPendedTicks/"
                 "uxSchedulerSuspended"),
    0x080000F4: ("ulSetInterruptMaskFromISR", "upstream_freertos_kernel",
                 "port helper: mrs primask/cpsid/bx"),
    0x080000FC: ("vClearInterruptMaskFromISR", "upstream_freertos_kernel",
                 "port helper: msr primask/bx"),
    0x08005F50: ("HAL_UART_IRQHandler", "upstream_stm32_hal",
                 "USART ISR/CR1/CR3/ICR handler sequence; pinned island"),
    0x08008FA8: ("gls_frame_pack_l", "first_party_g2",
                 "GLS frame packer L: 0x5A channel, 10-retry, 0xFF fill"),
    0x08009004: ("gls_frame_pack_r", "first_party_g2",
                 "GLS frame packer R: 0x5A channel, 10-retry, 0xFF fill"),
}

EXPECTED_ANCHOR_SIZES = {
    0x08000102: 62, 0x08008420: 20, 0x0800C5AC: 32, 0x0800CA4C: 26,
    0x0800CA78: 184, 0x080000F4: 8, 0x080000FC: 6, 0x08005F50: 732,
    0x08008FA8: 84, 0x08009004: 54,
}

# Structurally verified names (checked against decomp.c this increment).
VERIFIED_NAMES = {
    0x080000CC: "vPortStartFirstTask",
    0x0800C390: "vTaskSwitchContext",
    0x0800BF2C: "uxListRemove",
    0x0800C9A8: "xTaskCreate",
    0x0800B3E8: "pvPortMalloc",
    0x0800B4C0: "pxPortInitialiseStack",
    0x0800B0FC: "prvTimerTask",
    0x0800AA48: "os_timer_or_thread_create_wrapper",
    0x0800A93C: "os_timer_or_thread_create_wrapper",
    0x0800A836: "os_event_flags_create_wrapper",
    0x08009170: "g2_log_printf",
    0x08001E94: "gls_frame_validate_dispatch",
    0x08002CC0: "ota_image_be32_sum_verify",
    0x08006968: "app_rtos_init",
    0x08004B6C: "HAL_FLASH_Unlock",
    0x08004BF4: "HAL_FLASH_OB_Unlock",
}

# CMSIS/startup + toolchain runtime (verified addresses only).
CMSIS_STARTUP = {
    0x08000144: "Reset_Handler trampoline (SystemInit -> _start)",
    0x080084AE: "SystemInit",
    0x080000B8: "_start",
    0x080000C0: "startup trampoline to runtime init",
    0x08000156: "default exception self-loop",
    0x08006D70: "NMI default self-loop",
    0x08006778: "HardFault default self-loop",
    0x08000160: "__aeabi runtime divide leaf",
    0x0800018C: "__aeabi runtime divmod",
    0x080001B4: "__aeabi runtime helper",
    0x080001D8: "__aeabi runtime helper",
    0x080001E6: "__aeabi runtime helper",
    0x080001EA: "__aeabi runtime helper",
    0x080001FC: "__aeabi runtime helper",
    0x08000210: "toolchain runtime block op",
}

# Task/timer entry functions from app_rtos_init literal cells
# (DAT_08006A14..0x08006A3C, thumb-bit cleared).  Ghidra only discovers
# the three that are otherwise reachable; all ten are G2 entry code.
TASK_TIMER_ENTRIES = {
    0x08009D70: "g2_rtos_entry_1",
    0x0800BB4C: "g2_rtos_entry_2",
    0x08009684: "g2_rtos_entry_3",
    0x0800B7EC: "g2_rtos_entry_4",
    0x0800BB90: "g2_rtos_entry_5",
    0x0800AB70: "g2_rtos_entry_6",
    0x08006E1C: "g2_rtos_entry_7",
    0x08007F2C: "g2_rtos_entry_8",
    0x08007200: "g2_rtos_entry_9",
    0x080082EC: "g2_rtos_entry_10",
}

FIRST_PARTY_EXPLICIT = {
    0x08009170: "log sink: direct format-string pointer via ADR/literal",
    0x08006968: "RTOS object init; references all task/timer descriptors",
    0x08001E94: "GLS RX frame validator: 5A A5 FF header scan, 8-bit "
                "additive checksum seeded with (len-2), command dispatch",
    0x08002CC0: "OTA image verify: 32-bit additive sum of big-endian "
                "u32 words (EVEN-wrapper checksum algorithm)",
    0x08002F60: "OTA updater: bank-1 SN window 0x0803F800 scalar",
    0x08002F88: "OTA updater: bank-1 SN window 0x0803F000 scalar",
    0x0800373C: "OTA updater: bank-1 SN window 0x0803F000 scalar",
    0x08000420: "GLS channel writer (packer callee)",
    0x0800056C: "GLS channel writer (packer callee)",
    0x0800856C: "descriptor-table consumer",
    0x08008BD8: "descriptor-table consumer",
    0x08009A9C: "descriptor-table consumer",
}

KERNEL_STATICS = range(0x20000128, 0x200001A0)
KERNEL_BAND = (0x0800A800, 0x0800D100)
FLASH_CRED_CELLS = {0x08004B8C, 0x08004B90, 0x08004C14, 0x08004C18}
CREATE_APIS = {0x0800AA48, 0x0800A93C, 0x0800A836}


def _fail(msg: str) -> None:
    raise SystemExit(f"FAIL-CLOSED: {msg}")


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _verify_blob() -> None:
    data = BLOB.read_bytes()
    if _sha(data) != BLOB_SHA256:
        _fail("blob sha256 mismatch")


def _verify_artifacts() -> dict:
    envelope = {}
    for line in (MANIFEST_DIR / ENVELOPE).read_text().splitlines():
        digest, name = line.split()
        envelope[name] = digest
    for name, local in ARTIFACTS.items():
        path = MANIFEST_DIR / local
        if not path.exists():
            _fail(f"missing artifact {local}")
        if name in envelope and _sha(path.read_bytes()) != envelope[name]:
            _fail(f"artifact {local} hash mismatch against envelope")
    meta = {}
    for line in (MANIFEST_DIR / ARTIFACTS["meta.tsv"]).read_text().splitlines()[1:]:
        k, _, v = line.partition("\t")
        meta[k] = v
    if meta.get("image_base") != f"0x{APP_BASE:08x}":
        _fail("meta image_base mismatch")
    if meta.get("image_bytes") != str(APP_BYTES):
        _fail("meta image_bytes mismatch")
    if meta.get("functions") != "428":
        _fail("meta function count mismatch")
    if meta.get("strings") != "308":
        _fail("meta string count mismatch")
    return meta


def _load_functions() -> dict:
    funcs = {}
    for line in (MANIFEST_DIR / ARTIFACTS["functions.tsv"]).read_text().splitlines()[1:]:
        p = line.split("\t")
        entry = int(p[0], 16)
        funcs[entry] = {
            "size": int(p[1]),
            "callees": {int(x, 16) for x in p[3].split(",")} if p[3] else set(),
            "datarefs": {int(x, 16) for x in p[4].split(",")} if p[4] else set(),
            "scalars": {int(x, 16) for x in p[5].split(",")} if p[5] else set(),
        }
    return funcs


def _load_strings() -> set:
    out = set()
    for line in (MANIFEST_DIR / ARTIFACTS["strings.tsv"]).read_text().splitlines()[1:]:
        out.add(int(line.split("\t")[0], 16))
    return out


def _classify(funcs: dict, strings: set) -> dict:
    """Return {entry: (category, evidence)} for every discovered function."""
    def refs_g2_string(f):
        # ADR/label+offset variants land within +-3 of the scanned start.
        return any((d + dl) in strings
                   for d in f["datarefs"] for dl in range(-3, 4))

    string_referencers = {e for e, f in funcs.items() if refs_g2_string(f)}

    cat = {}

    # 1. exact anchors
    for e, (name, c, ev) in ANCHORS.items():
        if e not in funcs:
            _fail(f"anchor {e:#x} missing from Ghidra function map")
        if funcs[e]["size"] != EXPECTED_ANCHOR_SIZES[e]:
            _fail(f"anchor {e:#x} size {funcs[e]['size']} != "
                  f"{EXPECTED_ANCHOR_SIZES[e]}")
        cat[e] = (c, f"anchor: {ev}")

    # 2. FreeRTOS kernel closure
    seeds = {e for e, f in funcs.items()
             if f["datarefs"] & set(KERNEL_STATICS)}
    seeds |= {e for e, (n, c, ev) in ANCHORS.items()
              if c == "upstream_freertos_kernel"}
    seeds |= CREATE_APIS
    freertos = set(seeds)
    changed = True
    while changed:
        changed = False
        for e in list(freertos):
            for c in funcs.get(e, {"callees": set()})["callees"]:
                if (c in funcs and c not in freertos
                        and KERNEL_BAND[0] <= c < KERNEL_BAND[1]
                        and c not in string_referencers):
                    freertos.add(c)
                    changed = True
    for e in freertos:
        if e not in cat:
            cat[e] = ("upstream_freertos_kernel",
                      "kernel-statics reference and/or banded call-graph "
                      "closure from pinned port/scheduler anchors")

    # 3. HAL clusters
    uart = {0x08005F50}
    changed = True
    while changed:
        changed = False
        for e in list(uart):
            for c in funcs[e]["callees"]:
                if (c in funcs and c not in uart
                        and 0x08004000 <= c < 0x08006600
                        and c not in string_referencers):
                    uart.add(c)
                    changed = True
    EXPECTED_UART = {0x0800487A, 0x080048E6, 0x08005E6A, 0x08005E6C,
                     0x08005EFC, 0x08005EFE, 0x08005F42, 0x08005F50}
    if uart != EXPECTED_UART:
        _fail(f"HAL UART cluster drift: {sorted(hex(x) for x in uart)}")
    for e in uart:
        if e not in cat:
            cat[e] = ("upstream_stm32_hal",
                      "HAL_UART_IRQHandler cluster (bounded callee closure)")

    flash = {e for e, f in funcs.items() if f["datarefs"] & FLASH_CRED_CELLS}
    EXPECTED_FLASH = {0x08004B6C, 0x08004BF4}
    if flash != EXPECTED_FLASH:
        _fail(f"HAL FLASH credential users drift: "
              f"{sorted(hex(x) for x in flash)}")
    for e in flash:
        if e not in cat:
            cat[e] = ("upstream_stm32_hal",
                      "FLASH_KEYR/OPTKEYR credential literal user "
                      "(HAL_FLASH_Unlock/HAL_FLASH_OB_Unlock)")

    # 4. CMSIS startup + toolchain runtime
    for e, ev in CMSIS_STARTUP.items():
        if e in funcs and e not in cat:
            cat[e] = ("upstream_cmsis_startup", ev)

    # 5. first-party G2
    for e in sorted(string_referencers):
        if e not in cat:
            cat[e] = ("first_party_g2",
                      "references G2 log/status strings")
    for e, ev in FIRST_PARTY_EXPLICIT.items():
        if e in funcs and e not in cat:
            cat[e] = ("first_party_g2", ev)
    for e in TASK_TIMER_ENTRIES:
        if e in funcs and e not in cat:
            cat[e] = ("first_party_g2",
                      "RTOS task/timer entry pointer from app_rtos_init "
                      "literal pool")

    # 6. residue
    for e in funcs:
        if e not in cat:
            cat[e] = ("unresolved",
                      "no kernel-statics/HAL/string/descriptor evidence")
    return cat


def analyze() -> dict:
    _verify_blob()
    meta = _verify_artifacts()
    funcs = _load_functions()
    strings = _load_strings()
    cat = _classify(funcs, strings)

    rows = []
    for e in sorted(funcs):
        name = ANCHORS.get(e, (None,))[0] or VERIFIED_NAMES.get(
            e, f"FUN_{e:08x}")
        c, ev = cat[e]
        rows.append({
            "entry": e, "size": funcs[e]["size"], "name": name,
            "ownership_category": c, "evidence": ev, "discovered": True,
        })
    for e, name in sorted(TASK_TIMER_ENTRIES.items()):
        if e not in funcs:
            rows.append({
                "entry": e, "size": 0, "name": name,
                "ownership_category": "first_party_g2",
                "evidence": "RTOS task/timer entry pointer from "
                            "app_rtos_init literal pool; body outside the "
                            "discovered map (no direct callers); bytes "
                            "remain in unresolved accounting",
                "discovered": False,
            })

    totals: dict[str, int] = {c: 0 for c in OWNERSHIP_CATEGORIES}
    counts: dict[str, int] = {c: 0 for c in OWNERSHIP_CATEGORIES}
    for r in rows:
        totals[r["ownership_category"]] += r["size"]
        counts[r["ownership_category"]] += 1
    discovered_bytes = sum(r["size"] for r in rows if r["discovered"])
    app_tail = APP_BYTES - discovered_bytes

    freertos_members = sorted(
        r["entry"] for r in rows
        if r["ownership_category"] == "upstream_freertos_kernel")

    # Gap accounting: app bytes outside every discovered function body.
    body_spans = sorted((e, e + funcs[e]["size"]) for e in funcs)
    gaps = []
    cursor = APP_BASE
    for start, end in body_spans:
        if start > cursor:
            gaps.append((cursor, start))
        cursor = max(cursor, end)
    if cursor < APP_BASE + APP_BYTES:
        gaps.append((cursor, APP_BASE + APP_BYTES))

    DESCRIPTOR = (0x0800D2C0, 0x0800D958)
    gap_rows = []
    gap_totals: dict[str, int] = {c: 0 for c in OWNERSHIP_CATEGORIES}
    for gstart, gend in gaps:
        gbytes = gend - gstart
        if gstart == APP_BASE:
            gc, gev = ("upstream_cmsis_startup",
                       "vector table and pre-code gap")
        elif gstart < DESCRIPTOR[1] and gend > DESCRIPTOR[0]:
            gc, gev = ("first_party_g2",
                       "task/timer descriptor and name-string rodata")
        elif any(gstart <= s < gend for s in strings):
            gc, gev = ("first_party_g2",
                       "log/status string rodata corpus")
        else:
            gc, gev = ("unresolved",
                       "literal pools, data, alignment, or undiscovered "
                       "code outside discovered function bodies")
        gap_rows.append({"start": gstart, "end": gend, "bytes": gbytes,
                         "ownership_category": gc, "evidence": gev})
        gap_totals[gc] += gbytes
    if sum(gap_totals.values()) != app_tail:
        _fail("gap accounting does not reconcile with app tail")
    combined_bytes = {c: totals[c] + gap_totals[c]
                      for c in OWNERSHIP_CATEGORIES}
    if sum(combined_bytes.values()) != APP_BYTES:
        _fail("combined byte accounting does not reconcile with app size")

    return {
        "identity": {
            "blob": BLOB_REL,
            "sha256": BLOB_SHA256,
            "app_bytes": APP_BYTES,
            "ghidra_artifact_envelope": ENVELOPE,
            "decomp_c_sha256": meta["decomp_c_sha256"],
            "language": meta["language"],
        },
        "map": {
            "discovered_functions": len(funcs),
            "supplemental_entry_rows": sum(1 for r in rows
                                           if not r["discovered"]),
            "discovered_function_bytes": discovered_bytes,
            "app_bytes_outside_discovered_functions": app_tail,
            "category_counts": counts,
            "category_bytes": totals,
            "gap_region_count": len(gap_rows),
            "gap_category_bytes": gap_totals,
            "combined_category_bytes": combined_bytes,
            "freertos_kernel_members": freertos_members,
        },
        "rows": rows,
        "gap_rows": gap_rows,
        "ownership_categories": OWNERSHIP_CATEGORIES,
        "resolutions": {
            "crc_verdict": "no polynomial CRC anywhere in the case image; "
                           "GLS frame check is an 8-bit additive sum over "
                           "the payload seeded with (len-2), verified by "
                           "FUN_08001E94; the OTA image check is a 32-bit "
                           "additive sum of big-endian u32 words (the EVEN "
                           "wrapper checksum algorithm), verified by "
                           "FUN_08002CC0",
            "log_scheme_verdict": "no string-stripping/ID scheme: the log "
                                  "sink FUN_08009170 takes a direct "
                                  "format-string pointer, materialized by "
                                  "ARMv6-M ADR (PC-relative) for nearby "
                                  "strings and LDR literals for distant "
                                  "ones; 153 of 308 strings are "
                                  "referenced, all by exactly one site",
            "rtos_wrapper_verdict": "CMSIS-RTOS2 (cmsis_os2) wrapper over "
                                    "the FreeRTOS kernel: create APIs use "
                                    "isCurrentModePrivileged and "
                                    "osThreadNew/osTimerNew-shaped "
                                    "signatures; kernel remains the V10 "
                                    "line per the pinned port evidence",
        },
        "unresolved": [
            "exact FreeRTOS point release within V10.x",
            "exact STM32 HAL version",
            "precise task-name to entry-function pairing (descriptor fn "
            "fields are runtime-patched; six create calls use "
            "descriptor-table names)",
            "boundaries of the seven entry bodies outside the discovered "
            "map",
            "first-party policy function naming beyond the verified set",
        ],
    }


def _write_manifests(result: dict) -> list[str]:
    out = []
    tsv = MANIFEST_DIR / "g2-box-function-map.tsv"
    lines = [
        "# G2 charging-case per-function attribution map",
        "# blob: blobs/official/g2-2.2.6.10/firmware_box.bin sha256="
        + BLOB_SHA256,
        "# ghidra lane: tools/ghidra_scripts/BoxExportFunctionMap.java "
        "on lorelei, Ghidra 12.1.2, ARM:LE:32:Cortex @0x08000000",
        "# categories: " + ", ".join(OWNERSHIP_CATEGORIES),
        "entry\tsize\tname\townership_category\tevidence",
    ]
    for r in result["rows"]:
        lines.append(f"0x{r['entry']:08x}\t{r['size']}\t{r['name']}\t"
                     f"{r['ownership_category']}\t{r['evidence']}")
    tsv.write_text("\n".join(lines) + "\n")
    out.append(str(tsv.relative_to(G2_ROOT)))
    js = MANIFEST_DIR / "g2-box-function-map-summary.json"
    slim = {k: v for k, v in result.items() if k != "rows"}
    slim["row_count"] = len(result["rows"])
    js.write_text(json.dumps(slim, indent=2, sort_keys=True) + "\n")
    out.append(str(js.relative_to(G2_ROOT)))
    return out


def main() -> int:
    write = "--write-manifests" in sys.argv
    result = analyze()
    m = result["map"]
    print(f"blob            : {result['identity']['blob']}")
    print(f"functions       : {m['discovered_functions']} discovered + "
          f"{m['supplemental_entry_rows']} supplemental entry rows")
    print(f"discovered bytes: {m['discovered_function_bytes']} / "
          f"{result['identity']['app_bytes']} app bytes")
    print("category counts/bytes:")
    for c in OWNERSHIP_CATEGORIES:
        if m["category_counts"][c]:
            print(f"  {c:26s}: {m['category_counts'][c]:4d} funcs "
                  f"{m['category_bytes'][c]:8d} bytes")
    print("combined app-byte accounting (functions + gaps):")
    for c in OWNERSHIP_CATEGORIES:
        if m["combined_category_bytes"][c]:
            print(f"  {c:26s}: {m['combined_category_bytes'][c]:8d} bytes")
    print(f"CRC verdict     : additive checksums only; no polynomial CRC")
    print(f"log scheme      : direct ADR/literal string pointers; no ID scheme")
    print(f"RTOS wrapper    : CMSIS-RTOS2 (cmsis_os2) over FreeRTOS V10 line")
    if write:
        for p in _write_manifests(result):
            print(f"wrote           : {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
