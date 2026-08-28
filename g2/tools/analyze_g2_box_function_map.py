#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
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

from capstone import (
    CS_ARCH_ARM,
    CS_GRP_CALL,
    CS_GRP_JUMP,
    CS_GRP_RET,
    CS_MODE_LITTLE_ENDIAN,
    CS_MODE_MCLASS,
    CS_MODE_THUMB,
    Cs,
)
from capstone.arm import ARM_INS_CBNZ, ARM_INS_CBZ, ARM_OP_IMM

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
    0x08000160: "__aeabi_uidiv",
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
    0x0800502C: "NVIC_SystemReset",
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
    0x0800502C: "CMSIS-Core NVIC_SystemReset: DSB, AIRCR VECTKEY + "
                "SYSRESETREQ, DSB, terminal loop",
}

STM32_HAL_EXPLICIT = {
    0x0800598C: ("stm32_hal_peripheral_init",
                 "HAL handle state/error transitions, HAL tick timeout, "
                 "instance-register configuration, and HAL status returns; "
                 "exact public symbol remains unresolved"),
    0x08005094: ("HAL_PWR_DisableWakeUpPin",
                 "clears the selected EWUP bits in PWR_CR3"),
    0x080050A8: ("HAL_PWR_EnableWakeUpPin",
                 "programs PWR_CR4 polarity then sets PWR_CR3 EWUP bits"),
    0x080050C4: ("HAL_PWR_EnterSTANDBYMode",
                 "LPMS=standby, SCB SLEEPDEEP, WFI sequence"),
    0x080050E8: ("HAL_PWR_EnterSLEEPMode",
                 "LPMS regulator selection, WFI/WFE entry, SLEEPDEEP clear"),
}

# Task/timer entry functions from app_rtos_init literal cells
# (DAT_08006A14..0x08006A3C, thumb-bit cleared).  Ghidra only discovers
# the three that are otherwise reachable; all ten are G2 entry code.
TASK_TIMER_ENTRIES = {
    0x08009D70: "g2_timer_callback_1",
    0x0800BB4C: "g2_timer_callback_2",
    0x08009684: "g2_timer_callback_3",
    0x0800B7EC: "g2_timer_callback_4",
    0x0800BB90: "g2_timer_callback_5",
    0x0800AB70: "g2_timer_callback_6",
    0x08006E1C: "g2_thread_entry_1",
    0x08007F2C: "g2_thread_entry_2",
    0x08007200: "g2_thread_entry_3",
    0x080082EC: "g2_thread_entry_4",
}

# The seven entries omitted by the original Ghidra auto-analysis.  Limits are
# the next independently discovered function/entry and are only traversal
# guards, not inferred body ends.  The control-flow walk below determines the
# reachable instruction spans and fails closed against their authenticated
# byte digests.
SUPPLEMENTAL_TASK_LIMITS = {
    0x08009D70: 0x08009DF4,
    0x0800B7EC: 0x0800BA44,
    0x0800BB90: 0x0800BE74,
    0x08006E1C: 0x08007200,
    0x08007F2C: 0x080082EC,
    0x08007200: 0x08007F2C,
    0x080082EC: 0x08008420,
}

SUPPLEMENTAL_TASK_EXPECTED = {
    0x08009D70: (28, 66, "81a7269653585774491fd60647f2638a1b81b20a6e05971ed2166b7ff2abd042"),
    0x0800B7EC: (153, 342, "416ba65f58f649e802b918d655413efa75fa03fc7a3127fe330cb2b8e4226bce"),
    0x0800BB90: (170, 374, "593d88b92adcfd73a350e395354d5ccbfdd8d0db10bb81c9d53fe60f882e1b07"),
    0x08006E1C: (344, 790, "5bc749b960d9ff1231136dab10fc0b200ccf96d600b2ff1ba7235fa7d3d206c2"),
    0x08007F2C: (269, 616, "fa9446f10a6a07052b075c4f902d65af20799b46d9ec6f79e9dd3c0d1ec2292f"),
    0x08007200: (974, 2184, "48b30df1daa0fb53f4ab64f0d953c2a59fdc444c734e2be6dbb5bc34cbd3a61f"),
    0x080082EC: (93, 200, "70132a07ef998723788b75fbbb74b683d66c0404f611898cff51091a94e47a76"),
}

# Exact CMSIS-RTOS2 wrappers identified from their argument validation,
# privilege/exception checks, and calls into the already classified FreeRTOS
# primitives.  These are upstream wrapper bodies, not G2 policy.
CMSIS_OS2_WRAPPERS = {
    0x0800A7B0: ("osDelay", "nonzero ticks -> vTaskDelay; ISR rejected"),
    0x0800A7D2: ("osEventFlagsClear", "24-bit flag validation; task/ISR clear paths"),
    0x0800A816: ("osEventFlagsGet", "task/ISR event-group read paths"),
    0x0800A888: ("osEventFlagsSet", "task/ISR event-group set and wake paths"),
    0x0800AA24: ("osThreadTerminate", "task handle validation -> vTaskDelete"),
    0x0800AAF0: ("osTimerStart", "timer command 4 with tick argument"),
    0x0800AB26: ("osTimerStop", "active check then timer command 3"),
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
    0x08006B80: "G2 board policy: GPIOA pin 6 output helper",
    0x08006B98: "G2 board policy: GPIOA pin 7 output helper",
    0x08003848: "G2 charge-side selection policy over PA6/PA7 helpers",
    0x0800D154: "G2 aging-state indicator command sequence",
    0x08002C30: "G2 retrying peripheral mode-write policy",
    0x08002C8E: "G2 glasses-channel command packing policy",
    0x08002CB8: "G2 periodic case-policy adapter",
    0x080035D4: "G2 guarded peripheral transaction adapter",
    0x080039C8: "G2 guarded left-channel transaction adapter",
    0x080039E4: "G2 guarded right-channel transaction adapter",
    0x0800085C: "G2 GLS receive-buffer parser and dispatcher",
    0x08003A00: "G2 per-glasses charge-state reset policy",
    0x08003A3C: "G2 left-glasses state reset",
    0x08003A60: "G2 right-glasses state reset",
    0x08003B90: "G2 one-byte peripheral status probe adapter",
    0x080068D0: "G2 fixed-width case command builder",
    0x08009A14: "G2 dual-side indicator-state command policy",
    0x08009DF4: "G2 peripheral initialization retry adapter",
    0x08009EBC: "G2 bounded percentage conversion adapter",
    0x08009F18: "G2 calibrated sensor-value conversion policy",
    0x08009FF0: "G2 sensor default-value adapter",
    0x0800A01E: "G2 scaled sensor-value adapter",
    0x0800B600: "G2 board peripheral initialization policy",
    0x0800BB74: "G2 periodic timer restart adapter",
    0x0800BE90: "G2 left-side indicator command sequence",
    0x0800BEDE: "G2 right-side indicator command sequence",
}

FIRST_PARTY_SEMANTIC_NAMES = {
    0x0800085C: "gls_rx_buffer_parse_dispatch",
    0x080012E4: "aging_led_status_clear",
    0x08001334: "aging_sequence_start",
    0x080013B8: "idle_mode_exit",
    0x08001574: "case_ota_execute",
    0x080018E4: "glasses_status_poll_dispatch",
    0x08001C1C: "glasses_status_force_refresh",
    0x08001D68: "ota_result_inform_glasses",
    0x080023F4: "aging_status_set_left",
    0x080024C0: "aging_status_set_right",
    0x0800258C: "gls_uart_transfer_controlled",
    0x08002744: "gls_uart_transfer_uncontrolled",
    0x08002A68: "pmic_boost_status_check",
    0x08002C30: "peripheral_mode_write_retry",
    0x08002C8E: "glasses_channel_command_pack",
    0x08002CB8: "case_periodic_policy_adapter",
    0x080035D4: "peripheral_transaction_guard",
    0x08003848: "glasses_charge_side_select",
    0x080038E0: "option_byte_bank_swap",
    0x080039C8: "left_channel_transaction_guard",
    0x080039E4: "right_channel_transaction_guard",
    0x08003A00: "glasses_charge_state_reset",
    0x08003A3C: "left_glasses_state_reset",
    0x08003A60: "right_glasses_state_reset",
    0x08003B90: "peripheral_status_probe",
    0x080068D0: "case_command_build_fixed",
    0x080067C8: "log_hex_buffer",
    0x08006B80: "case_gpio_pa6_write",
    0x08006B98: "case_gpio_pa7_write",
    0x08007214: "case_policy_iteration",
    0x08009A14: "dual_side_indicator_update",
    0x08009A9C: "glasses_sides_reset",
    0x08009DF4: "peripheral_init_retry",
    0x08009EBC: "bounded_percentage_convert",
    0x08009F18: "calibrated_sensor_value_convert",
    0x08009FF0: "sensor_default_value_read",
    0x0800A01E: "scaled_sensor_value_read",
    0x0800B600: "board_peripheral_init",
    0x0800BB74: "periodic_timer_restart",
    0x0800BE90: "left_indicator_sequence",
    0x0800BEDE: "right_indicator_sequence",
    0x0800D154: "aging_indicator_apply",
    0x0800CE34: "glasses_charge_control_policy",
}

KERNEL_STATICS = range(0x20000128, 0x200001A0)
KERNEL_BAND = (0x0800A800, 0x0800D100)
FLASH_CRED_CELLS = {0x08004B8C, 0x08004B90, 0x08004C14, 0x08004C18}
CREATE_APIS = {0x0800AA48, 0x0800A93C, 0x0800A836}


def _fail(msg: str) -> None:
    raise SystemExit(f"FAIL-CLOSED: {msg}")


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _verify_blob() -> bytes:
    data = BLOB.read_bytes()
    if _sha(data) != BLOB_SHA256:
        _fail("blob sha256 mismatch")
    return data[WRAPPER:]


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


def _recover_supplemental_task_bodies(app: bytes, funcs: dict) -> list[dict]:
    """Recover the seven unseeded RTOS entries by direct Thumb CFG walk.

    BL/BLX destinations are recorded as callees but are not traversed.  Direct
    conditional and unconditional branches inside the guarded entry window are
    traversed; returns terminate a path.  The stock image is Cortex-M0+, so an
    indirect computed jump would make this recovery ambiguous and is rejected.
    """
    decoder = Cs(
        CS_ARCH_ARM,
        CS_MODE_THUMB | CS_MODE_LITTLE_ENDIAN | CS_MODE_MCLASS,
    )
    decoder.detail = True
    discovered_bytes = set()
    for entry, f in funcs.items():
        discovered_bytes.update(range(entry, entry + f["size"]))

    bodies = []
    for entry, limit in sorted(SUPPLEMENTAL_TASK_LIMITS.items()):
        pending = [entry]
        instructions = {}
        call_sites = []
        while pending:
            address = pending.pop()
            if address in instructions:
                continue
            if address & 1 or not (entry <= address < limit):
                _fail(
                    f"task entry {entry:#x} branch escaped guarded window "
                    f"to {address:#x}"
                )
            offset = address - APP_BASE
            insn = next(decoder.disasm(app[offset:offset + 4], address, count=1), None)
            if insn is None:
                _fail(f"task entry {entry:#x} failed to decode at {address:#x}")
            instructions[address] = insn

            direct_target = None
            if (
                insn.operands
                and insn.operands[-1].type == ARM_OP_IMM
                and (
                    insn.group(CS_GRP_JUMP)
                    or insn.id in (ARM_INS_CBZ, ARM_INS_CBNZ)
                    or insn.group(CS_GRP_CALL)
                )
            ):
                direct_target = insn.operands[-1].imm & ~1
            is_call = insn.group(CS_GRP_CALL)
            if is_call:
                if direct_target is None:
                    _fail(f"task entry {entry:#x} has indirect call at {address:#x}")
                call_sites.append((address, direct_target))
            is_return = (
                insn.group(CS_GRP_RET)
                or (insn.mnemonic == "pop" and "pc" in insn.op_str)
                or (insn.mnemonic == "bx" and insn.op_str == "lr")
            )
            is_jump = (
                insn.group(CS_GRP_JUMP)
                or insn.id in (ARM_INS_CBZ, ARM_INS_CBNZ)
            ) and not is_call
            is_unconditional = insn.mnemonic in ("b", "b.w", "bx")
            if is_jump:
                if direct_target is None:
                    if not is_return:
                        _fail(
                            f"task entry {entry:#x} has indirect jump at "
                            f"{address:#x}"
                        )
                else:
                    pending.append(direct_target)
            if not is_return and not is_unconditional:
                pending.append(address + insn.size)

        ordered = sorted(instructions)
        spans = []
        for address in ordered:
            end = address + instructions[address].size
            if spans and address == spans[-1][1]:
                spans[-1] = (spans[-1][0], end)
            else:
                spans.append((address, end))
        instruction_blob = b"".join(
            app[address - APP_BASE:address - APP_BASE + instructions[address].size]
            for address in ordered
        )
        expected = SUPPLEMENTAL_TASK_EXPECTED[entry]
        observed = (len(ordered), len(instruction_blob), _sha(instruction_blob))
        if observed != expected:
            _fail(
                f"task entry {entry:#x} CFG drift: {observed!r} != {expected!r}"
            )
        recovered_only = sum(
            1
            for address in ordered
            for byte in range(address, address + instructions[address].size)
            if byte not in discovered_bytes
        )
        bodies.append({
            "entry": entry,
            "name": TASK_TIMER_ENTRIES[entry],
            "role": "timer_callback" if entry >= 0x08009000 else "thread_entry",
            "guard_limit": limit,
            "instruction_count": len(ordered),
            "instruction_bytes": len(instruction_blob),
            "previously_unmapped_instruction_bytes": recovered_only,
            "instruction_sha256": observed[2],
            "spans": [
                {"start": start, "end": end, "bytes": end - start}
                for start, end in spans
            ],
            "calls": [
                {"site": site, "target": target}
                for site, target in sorted(call_sites)
            ],
            "direct_callees": sorted({target for _, target in call_sites}),
        })
    return bodies


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
    for e, (name, ev) in CMSIS_OS2_WRAPPERS.items():
        if e not in funcs:
            _fail(f"CMSIS-RTOS2 wrapper {name} missing at {e:#x}")
        cat[e] = ("upstream_freertos_kernel",
                  f"CMSIS-RTOS2 {name}: {ev}")

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
    for e, (name, ev) in STM32_HAL_EXPLICIT.items():
        if e not in funcs:
            _fail(f"STM32 HAL function {name} missing at {e:#x}")
        cat[e] = ("upstream_stm32_hal", f"STM32G0 HAL {name}: {ev}")

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
    app = _verify_blob()
    meta = _verify_artifacts()
    funcs = _load_functions()
    strings = _load_strings()
    task_bodies = _recover_supplemental_task_bodies(app, funcs)
    cat = _classify(funcs, strings)

    rows = []
    for e in sorted(funcs):
        name = (
            ANCHORS.get(e, (None,))[0]
            or VERIFIED_NAMES.get(e)
            or CMSIS_OS2_WRAPPERS.get(e, (None,))[0]
            or STM32_HAL_EXPLICIT.get(e, (None,))[0]
            or FIRST_PARTY_SEMANTIC_NAMES.get(e)
            or TASK_TIMER_ENTRIES.get(e)
            or f"FUN_{e:08x}"
        )
        c, ev = cat[e]
        rows.append({
            "entry": e, "size": funcs[e]["size"], "name": name,
            "ownership_category": c, "evidence": ev, "discovered": True,
        })
    for e, name in sorted(TASK_TIMER_ENTRIES.items()):
        if e not in funcs:
            body = next(body for body in task_bodies if body["entry"] == e)
            rows.append({
                "entry": e, "size": 0, "name": name,
                "ownership_category": "first_party_g2",
                "evidence": "RTOS task/timer entry pointer from "
                            "app_rtos_init literal pool; independently "
                            f"bounded CFG has {body['instruction_bytes']} "
                            "instruction bytes; zero here prevents overlap "
                            "with gap/Ghidra accounting; see "
                            "g2-box-task-entry-bodies.tsv",
                "discovered": False,
            })

    rows_by_entry = {row["entry"]: row for row in rows}
    task_direct_callees = sorted({
        target
        for body in task_bodies
        for target in body["direct_callees"]
    })
    task_helpers = []
    for target in task_direct_callees:
        if target not in rows_by_entry:
            _fail(f"task direct callee {target:#x} absent from function map")
        row = rows_by_entry[target]
        callers = sorted(
            body["entry"] for body in task_bodies
            if target in body["direct_callees"]
        )
        task_helpers.append({
            "entry": target,
            "name": row["name"],
            "ownership_category": row["ownership_category"],
            "task_callers": callers,
            "task_caller_count": len(callers),
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
            "supplemental_task_instruction_bytes": sum(
                body["instruction_bytes"] for body in task_bodies
            ),
            "supplemental_task_previously_unmapped_instruction_bytes": sum(
                body["previously_unmapped_instruction_bytes"]
                for body in task_bodies
            ),
            "task_direct_helpers": len(task_helpers),
            "task_direct_helpers_unresolved": sum(
                row["ownership_category"] == "unresolved"
                for row in task_helpers
            ),
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
        "task_bodies": task_bodies,
        "task_helpers": task_helpers,
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
            "semantic task-name pairing for the seven now-bounded entry "
            "bodies (descriptor names are runtime-patched)",
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

    tasks = MANIFEST_DIR / "g2-box-task-entry-bodies.tsv"
    task_lines = [
        "# G2 charging-case RTOS entries omitted by the original Ghidra map",
        "# reachable instruction bytes are concatenated in address order for sha256",
        "entry\tname\trole\tguard_limit\tinstructions\tinstruction_bytes\t"
        "previously_unmapped_instruction_bytes\tinstruction_sha256\tspans",
    ]
    for body in result["task_bodies"]:
        spans = ",".join(
            f"0x{span['start']:08x}-0x{span['end']:08x}"
            for span in body["spans"]
        )
        task_lines.append(
            f"0x{body['entry']:08x}\t{body['name']}\t{body['role']}\t"
            f"0x{body['guard_limit']:08x}\t{body['instruction_count']}\t"
            f"{body['instruction_bytes']}\t"
            f"{body['previously_unmapped_instruction_bytes']}\t"
            f"{body['instruction_sha256']}\t{spans}"
        )
    tasks.write_text("\n".join(task_lines) + "\n")
    out.append(str(tasks.relative_to(G2_ROOT)))

    helpers = MANIFEST_DIR / "g2-box-task-helper-map.tsv"
    helper_lines = [
        "# Direct callees reached from the seven recovered task/timer entries",
        "entry\tname\townership_category\ttask_caller_count\ttask_callers",
    ]
    for helper in result["task_helpers"]:
        callers = ",".join(f"0x{x:08x}" for x in helper["task_callers"])
        helper_lines.append(
            f"0x{helper['entry']:08x}\t{helper['name']}\t"
            f"{helper['ownership_category']}\t"
            f"{helper['task_caller_count']}\t{callers}"
        )
    helpers.write_text("\n".join(helper_lines) + "\n")
    out.append(str(helpers.relative_to(G2_ROOT)))
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
    print("task CFGs       : "
          f"{m['supplemental_task_instruction_bytes']} instruction bytes, "
          f"{m['supplemental_task_previously_unmapped_instruction_bytes']} "
          "previously unmapped")
    print("task helpers    : "
          f"{m['task_direct_helpers']} direct, "
          f"{m['task_direct_helpers_unresolved']} unresolved")
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
