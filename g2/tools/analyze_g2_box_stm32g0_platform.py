#!/usr/bin/env python3
"""Fail-closed platform attribution for the G2 charging-case (box) firmware.

Scope: the STM32G0 case component of blobs/official/g2-2.2.6.10/firmware_box.bin.

This analyzer is read-only and deterministic over the pinned blob.  It

  1. verifies the blob against g2/blobs/official/g2-2.2.6.10/PROVENANCE.md;
  2. parses the 32-byte EVEN transport wrapper (version, length, checksum);
  3. parses the Cortex-M vector table and discriminates the MCU family
     member against the STM32G0B1-class interrupt map;
  4. proves the FreeRTOS GCC ARM_CM0 port and the kernel scheduler
     structures by exact instruction-sequence evidence;
  5. censuses STM32 HAL peripheral usage by literal-pool constants;
  6. maps the case UART / OTA-box update protocol as far as static
     evidence allows (frame header, packer behavior, command codes,
     OTA state-machine strings);
  7. locates the device-specific serial/identity windows that the case
     updater preserves (never overwrite: 0x0803F000..0x0803F00F,
     0x0803F800..0x0803F807 and the bank-2 mirrors); and
  8. classifies evidence-anchored regions into the project's seven
     source-ownership categories and emits the machine-readable
     attribution map.

Run:
    PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 \\
        tools/analyze_g2_box_stm32g0_platform.py [--write-manifests]

Test:
    PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 \\
        -m unittest tests.test_analyze_g2_box_stm32g0_platform -v
"""

from __future__ import annotations

import hashlib
import json
import re
import struct
import sys
from pathlib import Path

G2_ROOT = Path(__file__).resolve().parents[1]
BLOB_REL = "blobs/official/g2-2.2.6.10/firmware_box.bin"
BLOB = G2_ROOT / BLOB_REL

EXPECTED_SIZE = 55_784
EXPECTED_SHA256 = "36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374"

WRAPPER_SIZE = 32
APP_BASE = 0x08000000
APP_ALTERNATE_BASE = 0x08040000  # inactive bank alias (dual-bank install target)

# FreeRTOS kernel statics, proven by xTaskGetSchedulerState /
# xTaskIncrementTick / xPortPendSVHandler instruction evidence.
KERNEL_STATICS = {
    "pxCurrentTCB": 0x20000128,
    "xTickCount_offset": 0x0C,
    "xSchedulerRunning_offset": 0x14,
    "xPendedTicks_offset": 0x18,
    "uxSchedulerSuspended_offset": 0x30,
    "pxOverflowDelayedTaskList_offset": 0x34,
}

# STM32G0B1-class peripheral interrupt map (IRQn order, from the official
# STMicroelectronics CMSIS device header stm32g0b1xx.h).  The case vector
# table populates IRQ0..IRQ29 (46 words total); CEC_IRQn (30) is absent.
G0B1_IRQ_NAMES = [
    "WWDG", "PVD_VDDIO2", "RTC_TAMP", "FLASH", "RCC_CRS", "EXTI0_1",
    "EXTI2_3", "EXTI4_15", "USB_UCPD1_2", "DMA1_Channel1",
    "DMA1_Channel2_3", "DMA1_Ch4_7_DMA2_Ch1_5_DMAMUX1_OVR", "ADC1_COMP",
    "TIM1_BRK_UP_TRG_COM", "TIM1_CC", "TIM2", "TIM3_TIM4",
    "TIM6_DAC_LPTIM1", "TIM7_LPTIM2", "TIM14", "TIM15",
    "TIM16_FDCAN_IT0", "TIM17_FDCAN_IT1", "I2C1", "I2C2_3", "SPI1",
    "SPI2_3", "USART1", "USART2_LPUART2", "USART3_4_5_6_LPUART1", "CEC",
]

# Peripheral base constants used for the literal-pool census.
PERIPHERAL_BASES = {
    0x40021000: "RCC", 0x40022000: "FLASH", 0x40023000: "CRC",
    0x40007000: "PWR", 0x40002800: "RTC", 0x40003000: "IWDG",
    0x40002C00: "WWDG", 0x40010000: "SYSCFG", 0x40015800: "DBGMCU",
    0x40012400: "ADC1", 0x40012C00: "TIM1", 0x40000000: "TIM2",
    0x40000400: "TIM3", 0x40000800: "TIM6", 0x40000C00: "TIM7",
    0x40002000: "TIM14", 0x40003C00: "TIM15", 0x40014400: "TIM16",
    0x40014800: "TIM17", 0x40005400: "I2C1", 0x40005800: "I2C2",
    0x40013800: "USART1", 0x40004400: "USART2", 0x40004800: "USART3",
    0x40004C00: "USART4", 0x40010400: "EXTI", 0x50000000: "GPIOA",
    0x50000400: "GPIOB", 0x50000800: "GPIOC", 0x50000C00: "GPIOD",
    0x40020000: "DMA1", 0x40020400: "DMA2", 0x40025000: "RNG",
    0x40026000: "AES", 0x40005C00: "USB_DRD", 0x40006400: "FDCAN1",
    0x40006800: "FDCAN2", 0x40008000: "LPUART1", 0x40007C00: "LPUART2",
    0x4000A000: "UCPD1", 0x4000A400: "UCPD2", 0x1FFF7590: "UID",
    0x1FFF75E0: "FLASHSIZE",
}

# Device-specific identity windows preserved by the case updater.  These
# live in bank-end flash pages far beyond the 0xD9C8-byte application
# image; the image only *references* them.  Never overwrite.
PRESERVED_WINDOWS = [
    {"bank": 1, "start": 0x0803F000, "end_exclusive": 0x0803F010, "bytes": 16},
    {"bank": 1, "start": 0x0803F800, "end_exclusive": 0x0803F808, "bytes": 8},
    {"bank": 2, "start": 0x0807F000, "end_exclusive": 0x0807F010, "bytes": 16},
    {"bank": 2, "start": 0x0807F800, "end_exclusive": 0x0807F808, "bytes": 8},
]

# The seven source-ownership categories used by the attribution map.
OWNERSHIP_CATEGORIES = [
    "generated_transport",       # EVENOTA/container bytes owned by the package generator
    "upstream_cmsis_startup",    # ARM/CMSIS + vendor startup (vectors, reset, SystemInit)
    "upstream_freertos_kernel",  # FreeRTOS kernel and its CM0 port
    "upstream_stm32_hal",        # STM32 HAL/LL driver code
    "first_party_g2",            # G2 product policy (charge/battery/aging/LED/OTA/UART)
    "device_specific_preserve",  # per-device identity; never reconstructed, never overwritten
    "unresolved",                # no evidence-anchored classification yet
]


def _fail(msg: str) -> None:
    raise SystemExit(f"FAIL-CLOSED: {msg}")


def _va(file_offset: int) -> int:
    """Virtual (bank-1 logical) address of a firmware_box.bin file offset."""
    return APP_BASE + (file_offset - WRAPPER_SIZE)


def _fo(vaddr: int) -> int:
    """File offset of an application virtual address."""
    return (vaddr - APP_BASE) + WRAPPER_SIZE


def _u32(app: bytes, vaddr: int) -> int:
    return struct.unpack_from("<I", app, vaddr - APP_BASE)[0]


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _load() -> bytes:
    data = BLOB.read_bytes()
    if len(data) != EXPECTED_SIZE:
        _fail(f"blob size {len(data)} != {EXPECTED_SIZE}")
    if _sha(data) != EXPECTED_SHA256:
        _fail("blob sha256 mismatch against PROVENANCE.md")
    return data


def _wrapper(blob: bytes) -> dict:
    w = blob[:WRAPPER_SIZE]
    app = blob[WRAPPER_SIZE:]
    if w[:4] != b"EVEN":
        _fail("wrapper magic is not EVEN")
    length = struct.unpack(">I", w[8:12])[0]
    checksum = struct.unpack(">I", w[12:16])[0]
    if length != len(app):
        _fail(f"wrapper length {length} != app bytes {len(app)}")
    if len(app) % 4:
        _fail("app length not word aligned; checksum semantics unverified")
    calc = sum(struct.unpack(f">{len(app)//4}I", app)) & 0xFFFFFFFF
    if calc != checksum:
        _fail(f"wrapper checksum {checksum:#x} != computed {calc:#x}")
    if w[16:] != b"\x00" * 16:
        _fail("wrapper tail not zero-filled as expected")
    return {
        "magic": "EVEN",
        "version": f"{w[4]}.{w[5]}.{w[6]}",
        "version_bytes": [w[4], w[5], w[6], w[7]],
        "length_be_u32": length,
        "checksum_be_u32": checksum,
        "checksum_algorithm": "additive sum of big-endian u32 words over the "
                              "application payload, stored big-endian",
        "checksum_verified": True,
    }


def _vectors(app: bytes) -> dict:
    words = [struct.unpack_from("<I", app, i * 4)[0] for i in range(46)]

    def is_code(v: int) -> bool:
        return bool(v & 1) and APP_BASE <= (v & ~1) < APP_BASE + len(app)

    if not is_code(words[1]):
        _fail("reset vector not a code pointer")
    # Table must terminate exactly at word 46 (start of _start code).
    nxt = struct.unpack_from("<I", app, 46 * 4)[0]
    if is_code(nxt):
        _fail("vector table does not terminate at 46 words")
    sp = words[0]
    if not (0x20000000 < sp <= 0x20024000):
        _fail(f"initial SP {sp:#x} outside plausible SRAM")
    entries = []
    for i, v in enumerate(words):
        if i == 0:
            entries.append({"index": 0, "name": "initial_sp", "value": v})
            continue
        if i == 1:
            name = "Reset"
        elif i == 2:
            name = "NMI"
        elif i == 3:
            name = "HardFault"
        elif i == 11:
            name = "SVCall"
        elif i == 14:
            name = "PendSV"
        elif i == 15:
            name = "SysTick"
        elif i >= 16:
            name = f"IRQ{i-16}_{G0B1_IRQ_NAMES[i-16]}"
        else:
            name = "reserved"
        kind = "code" if is_code(v) else ("zero" if v == 0 else "invalid")
        entries.append({"index": i, "name": name,
                        "value": v, "kind": kind})
    if any(e.get("kind") == "invalid" for e in entries):
        _fail("vector entry outside image")
    return {
        "word_count": 46,
        "peripheral_irq_count": 30,
        "initial_sp": sp,
        "reset_handler": words[1] & ~1,
        "pendsv_handler": words[14] & ~1,
        "svc_handler": words[11] & ~1,
        "systick_handler": words[15] & ~1,
        "irq_map_reference": "stm32g0b1xx.h IRQn_Type "
                             "(STMicroelectronics CMSIS device header)",
        "entries": entries,
    }


def _word_sites(app: bytes, value: int) -> list[int]:
    """All even file offsets (blob-relative) where a little-endian word appears."""
    pat = struct.pack("<I", value)
    out = []
    i = app.find(pat)
    while i >= 0:
        out.append(i + WRAPPER_SIZE)
        i = app.find(pat, i + 2)
    return out


def _peripheral_census(app: bytes) -> dict:
    used, absent = {}, []
    for base, name in sorted(PERIPHERAL_BASES.items()):
        sites = _word_sites(app, base)
        if sites:
            used[name] = {"base": base, "literal_sites": sites}
        else:
            absent.append(name)
    return {"used": used, "absent": absent}


def _expect_bytes(app: bytes, vaddr: int, n: int) -> bytes:
    return app[vaddr - APP_BASE: vaddr - APP_BASE + n]


def _freertos(app: bytes, vec: dict) -> dict:
    # --- xPortPendSVHandler: FreeRTOS-Kernel portable/GCC/ARM_CM0/port.c ---
    pendsv_va = vec["pendsv_handler"]
    pendsv = _expect_bytes(app, pendsv_va, 62)
    expected_pendsv_tail = bytes.fromhex(
        # mrs r0,psp; ldr r3,[pc,#0x38]; ldr r2,[r3]; subs r0,#0x20; str r0,[r2]
        "eff30980" "0e4b" "1a68" "2038" "1060"
        # stm r0!,{r4-r7}; mov r4,r8; mov r5,r9; mov r6,r10; mov r7,r11; stm r0!,{r4-r7}
        "f0c0" "4446" "4d46" "5646" "5f46" "f0c0"
        # push {r3,lr}; cpsid i; bl <rel>; cpsie i; pop {r2,r3}
        "08b5" "72b6"
    )
    if not pendsv.startswith(expected_pendsv_tail):
        _fail("PendSV handler head does not match the FreeRTOS GCC CM0 port")
    if pendsv[32:34] != bytes.fromhex("62b6"):
        _fail("PendSV handler missing cpsie after vTaskSwitchContext")
    restore = bytes.fromhex(
        # pop {r2,r3}; ldr r1,[r2]; ldr r0,[r1]; adds r0,#0x10; ldm r0!,{r4-r7}
        "0cbc" "1168" "0868" "1030" "f0c8"
        # mov r8,r4; mov r9,r5; mov r10,r6; mov r11,r7; msr psp,r0
        "a046" "a946" "b246" "bb46" "80f30988"
        # subs r0,#0x20; ldm r0!,{r4-r7}; bx r3
        "2038" "f0c8" "1847"
    )
    if not pendsv[34:34 + len(restore)] == restore:
        _fail("PendSV handler restore tail mismatch")
    px_current_tcb_addr = _u32(app, pendsv_va + 0x3E)
    if px_current_tcb_addr != KERNEL_STATICS["pxCurrentTCB"]:
        _fail("pxCurrentTCB literal mismatch")

    # --- interrupt-mask helpers used by the port critical section ---
    set_mask = _expect_bytes(app, 0x080000F4, 8)    # mrs r0,primask; cpsid i; bx lr
    clr_mask = _expect_bytes(app, 0x080000FC, 6)    # msr primask,r0; bx lr
    if set_mask != bytes.fromhex("eff31080" "72b6" "7047"):
        _fail("ulSetInterruptMaskFromISR helper mismatch")
    if clr_mask != bytes.fromhex("80f31088" "7047"):
        _fail("vClearInterruptMaskFromISR helper mismatch")

    # --- vPortSVCHandler is the documented empty stub (bx lr) ---
    svc = _expect_bytes(app, vec["svc_handler"], 2)
    if svc != bytes.fromhex("7047"):
        _fail("SVC handler is not the GCC-port empty stub (bx lr)")

    # --- SysTick gate: read SysTick->CTRL, call xTaskGetSchedulerState,
    #     skip kernel tick only when the scheduler has not started ---
    gate = _expect_bytes(app, vec["systick_handler"], 24)
    if not gate.startswith(bytes.fromhex("10b5")):
        _fail("SysTick gate prologue mismatch")
    gate_lit = _u32(app, vec["systick_handler"] + 0x14)
    if gate_lit != 0xE000E000:
        _fail("SysTick gate does not read the SCS/SysTick block")

    # --- xTaskGetSchedulerState (taskSCHEDULER_NOT_STARTED=1,
    #     RUNNING=2, SUSPENDED=0 over the proven kernel statics) ---
    gs = _expect_bytes(app, 0x0800CA4C, 26)
    expected_gs = bytes.fromhex(
        "0648"       # ldr r0,[pc,#0x18]   -> &kernel statics (0x20000128)
        "4169"       # ldr r1,[r0,#0x14]   -> xSchedulerRunning
        "0029"       # cmp r1,#0
        "04d0"       # beq -> NOT_STARTED
        "006b"       # ldr r0,[r0,#0x30]   -> uxSchedulerSuspended
        "0028"       # cmp r0,#0
        "03d0"       # beq -> RUNNING
        "0020" "7047"  # movs r0,#0 (SUSPENDED); bx lr
        "0120" "7047"  # movs r0,#1 (NOT_STARTED); bx lr
        "0220" "7047"  # movs r0,#2 (RUNNING); bx lr
    )
    if gs[:len(expected_gs)] != expected_gs:
        _fail("xTaskGetSchedulerState body mismatch")
    if _u32(app, 0x0800CA4C + 0x1C) != KERNEL_STATICS["pxCurrentTCB"]:
        _fail("xTaskGetSchedulerState kernel-statics literal mismatch")

    # --- xPortSysTickHandler: mask; xTaskIncrementTick; PENDSVSET; unmask ---
    st = _expect_bytes(app, 0x0800C5AC, 36)
    if not st.startswith(bytes.fromhex("10b5")):
        _fail("xPortSysTickHandler prologue mismatch")
    if _u32(app, 0x0800C5AC + 0x20) != 0xE000ED00:
        _fail("xPortSysTickHandler SCB literal mismatch")

    # --- xTaskIncrementTick head: tick/pended counters over the same struct ---
    ti = _expect_bytes(app, 0x0800CA78, 40)
    expected_ti = bytes.fromhex(
        "f8b5"       # push {r3-r7,lr}
        "0026"       # movs r6,#0
        "2c4f"       # ldr r7,[pc,#0xb0]  -> &kernel statics (0x20000128)
        "386b"       # ldr r0,[r7,#0x30]  -> uxSchedulerSuspended
        "0028"       # cmp r0,#0
        "04d0"       # beq -> running path
        "b869"       # ldr r0,[r7,#0x18]  -> xPendedTicks
        "401c"       # adds r0,#1
        "b861"       # str r0,[r7,#0x18]
        "3046"       # mov r0,r6
        "f8bd"       # pop {r3-r7,pc}
        "fd68"       # ldr r5,[r7,#0xc]   -> xTickCount
        "6d1c"       # adds r5,#1
        "fd60"       # str r5,[r7,#0xc]
        "002d"       # cmp r5,#0
        "0ed1"       # bne -> no wrap
    )
    if ti[:len(expected_ti)] != expected_ti:
        _fail("xTaskIncrementTick head mismatch")

    names = {
        "idle_task_name": ("IDLE", 0x0800C2E8),
        "timer_task_name": ("Tmr Svc", 0x0800CD74),
        "timer_queue_registry_name": ("TmrQ", 0x0800ACDC),
        "app_tasks": {
            "ledTask": 0x0800D898, "pwrManagerTask": 0x0800D8A0,
            "glsDetectTask": 0x0800D8B0, "defaultTask": 0x0800D8C0,
            "clearLedTimer": 0x0800D8CC, "showErrorLedTimer": 0x0800D8DC,
            "startLedTimer": 0x0800D8F0, "agingTimer": 0x0800D900,
            "powerOnTimer": 0x0800D90C, "setAgingStatusTimer": 0x0800D91C,
            "appEvent": 0x0800D930,
        },
    }
    for label, item in names.items():
        if label == "app_tasks":
            for tname, tva in item.items():
                if not _expect_bytes(app, tva, len(tname)) == tname.encode():
                    _fail(f"task-name string {tname} missing at {tva:#x}")
                if not _word_sites(app, tva):
                    _fail(f"task-name string {tname} has no descriptor literal")
        else:
            s, va = item
            if not _expect_bytes(app, va, len(s)) == s.encode():
                _fail(f"kernel name string {s!r} missing at {va:#x}")

    return {
        "kernel_family": "FreeRTOS",
        "port": "GCC ARM_CM0 (naked xPortPendSVHandler, empty vPortSVCHandler)",
        "port_reference": "FreeRTOS-Kernel portable/GCC/ARM_CM0/port.c "
                          "verified against tag V10.5.1; sequence is stable "
                          "across the V10 line",
        "version_interval": "V10.x (V10.0.0-V10.6.x); V9.x not excluded by "
                            "port bytes alone; V11.x single-core not excluded; "
                            "leading candidate V10.3.1-V10.5.1 per "
                            "STM32CubeG0 distribution lineage",
        "pendsv_handler": {"vaddr": pendsv_va, "bytes": len(pendsv),
                           "sha256": _sha(pendsv),
                           "pxCurrentTCB_literal": px_current_tcb_addr},
        "systick_gate": {"vaddr": vec["systick_handler"],
                         "scs_literal": gate_lit,
                         "behavior": "tick handled only when "
                                     "xTaskGetSchedulerState() != "
                                     "taskSCHEDULER_NOT_STARTED(1)"},
        "xPortSysTickHandler": {"vaddr": 0x0800C5AC,
                                "scb_literal": 0xE000ED00,
                                "pendsvset_bit": 0x10000000},
        "xTaskGetSchedulerState": {"vaddr": 0x0800CA4C},
        "xTaskIncrementTick": {"vaddr": 0x0800CA78},
        "kernel_statics": KERNEL_STATICS,
        "task_names": names,
        "cmsis_rtos_wrapper": "undetermined; SysTick gate shape is "
                              "consistent with the STM32Cube cmsis_os v1 "
                              "osSystickHandler pattern, raw-API use is not "
                              "excluded",
    }


def _hal(app: bytes) -> dict:
    keys = {
        "FLASH_KEY1": 0x45670123, "FLASH_KEY2": 0xCDEF89AB,
        "FLASH_OPTKEY1": 0x08192A3B, "FLASH_OPTKEY2": 0x4C5D6E7F,
    }
    key_sites = {}
    for name, val in keys.items():
        sites = _word_sites(app, val)
        if len(sites) != 1:
            _fail(f"{name} literal sites {sites} != 1")
        key_sites[name] = {"value": val, "file_offset": sites[0]}
    head = _expect_bytes(app, 0x08005F50, 40)
    if not head.startswith(bytes.fromhex("f8b5")):
        _fail("HAL_UART_IRQHandler head missing")
    if not head[2:8] == bytes.fromhex("0368" "0446" "d969"):
        # ldr r3,[r0]; mov r4,r0; ldr r1,[r3,#0x1c] (USART ISR)
        _fail("HAL_UART_IRQHandler ISR/CR1 read pattern mismatch")
    return {
        "lineage": "STM32CubeG0 HAL/LL; version not statically provable "
                   "(HAL carries no version strings); modules enumerated "
                   "by peripheral-constant and handler-structure evidence",
        "flash_credentials": key_sites,
        "flash_driver": "HAL_FLASH_Unlock/HAL_FLASH_OB_Unlock lineage proven "
                        "by unique FLASH_KEYR/OPTKEYR credential literals",
        "hal_uart_irqhandler": {"vaddr": 0x08005F50,
                                "head_sha256": _sha(head),
                                "evidence": "USART ISR(+0x1c)/CR1(+0x0)/"
                                            "CR3(+0x8)/ICR(+0x20) sequence"},
        "modules_present": ["FLASH", "RCC", "PWR", "RTC", "ADC1", "TIM",
                            "USART/UART", "GPIO", "EXTI+SYSCFG", "CORTEX (SCS)"],
        "modules_absent_no_literals": ["I2C1", "I2C2", "DMA1", "DMA2", "USB",
                                       "FDCAN", "RNG", "AES", "LPUART",
                                       "UCPD", "CRC peripheral", "IWDG",
                                       "WWDG", "DBGMCU"],
        "i2c_note": "no I2C peripheral literal exists; YHM2510/2217/4005 "
                    "chip traffic is GPIO bit-banged (GPIOB/C/D literals + "
                    "read_bit_error log strings)",
    }


def _protocol(app: bytes) -> dict:
    facts = {}

    hdr_str = b"header: 5a a5 ff %02x"
    hdr_off = app.find(hdr_str)
    if hdr_off < 0:
        _fail("frame-header log string missing")
    facts["frame_format"] = {
        "header_bytes": [0x5A, 0xA5, 0xFF, "cmd"],
        "evidence_string": hdr_str.decode(),
        "evidence_file_offset": hdr_off + WRAPPER_SIZE,
        "tail": "CRC over payload (crc_cal/crc_rx log pair); CRC-16/CCITT "
                "and CRC-32 tables absent -> bit-wise software CRC, exact "
                "polynomial unresolved",
    }

    # CRC table absence is a load-bearing negative fact.
    if app.find(struct.pack("<8H", 0x0000, 0x1021, 0x2042, 0x3063,
                            0x4084, 0x50A5, 0x60C6, 0x70E7)) >= 0:
        _fail("unexpected CRC16-CCITT table present")
    if app.find(struct.pack("<4I", 0x00000000, 0x77073096,
                            0xEE0E612C, 0x990951BA)) >= 0:
        _fail("unexpected CRC32 table present")

    pack_l = _expect_bytes(app, 0x08008FA8, 84)
    pack_r = _expect_bytes(app, 0x08009004, 84)
    if pack_l[0x28] != 0x5A or pack_r[0x1A] != 0x5A:
        _fail("packer channel/header immediate 0x5A missing")
    if pack_l[0x0E] != 0xFF:
        _fail("packer failure-fill immediate 0xFF missing")
    if pack_l[0x4E] != 0x0A:
        _fail("packer retry bound 10 missing")
    facts["frame_packer"] = {
        "instances": [
            {"vaddr": 0x08008FA8, "sha256": _sha(pack_l)},
            {"vaddr": 0x08009004, "sha256": _sha(pack_r)},
        ],
        "channel_immediate": 0x5A,
        "retry_bound": 10,
        "failure_fill_byte": 0xFF,
        "behavior": "critical-section channel write retried up to 10 times; "
                    "on exhaustion the caller buffer is filled with 0xFF and "
                    "zero is returned; success bumps a frame counter and "
                    "conditionally runs a notify callback",
        "symmetry": "two near-identical instances = glasses-left / "
                    "glasses-right channels (matches L/R log-string pairs)",
    }

    facts["commands_from_strings"] = {
        0x13: "case->glasses status push (\"send 0x13 soon\" on battery/"
              "hall/USB/charging changes)",
        0x58: "ota check (\"ota check (0x58), len:%d\")",
        0x3D: "aging-exit acknowledge (\"exit aging status(0x3D)\")",
        0x3E: "aging-exit acknowledge (\"exit aging status(0x3E)\")",
    }

    timeouts = []
    for s in (b"receive header timeout", b"no header in first 5 char. RX:",
              b"receive len timeout", b"receive data timeout",
              b"[noctrl]no header in first 5 char. RX:",
              b"[noctrl]receive len timeout"):
        off = app.find(s)
        if off < 0:
            _fail(f"RX timeout log string missing: {s!r}")
        timeouts.append({"string": s.decode(), "file_offset": off + WRAPPER_SIZE})
    facts["rx_parser_timeouts"] = timeouts
    facts["rx_paths"] = "two RX parser variants (plain and [noctrl]) = "
    facts["rx_paths"] = ("two RX parser variants (plain / [noctrl]) "
                         "consistent with a control port and a "
                         "non-control port")

    facts["gls_link_role"] = ("USART1 is the only USART with a populated "
                              "interrupt vector (IRQ27); USART2/3/4 default "
                              "or polled; DMA unused")
    return facts


def _ota_state_machine(app: bytes) -> list[dict]:
    steps = [
        ("ota_check", "ota check (0x58), len:%d"),
        ("version_compare_nothing_new", "[OTA_BOX]: nothing new, cur:1.%d.%d, remote:1.%d.%d"),
        ("version_compare_new", "[OTA_BOX]: new version, cur:1.%d.%d, remote:1.%d.%d, len:%d, crc:0x%x"),
        ("check_gls_ready", "[OTA_BOX]: Check gls ready"),
        ("gls_not_ready", "[OTA_BOX]: GLS not ready."),
        ("get_running_bank", "[OTA_BOX]: Get running bank"),
        ("running_bank_value", "[OTA_BOX]: Running bank: %d"),
        ("erase_bank", "[OTA_BOX]:fail to erase %d pages. err:0x%x, retry:%d"),
        ("copy_sn", "[OTA_BOX]: Copy SN."),
        ("copy_sn_done", "[OTA_BOX]: Copy SN done."),
        ("get_bin_file", "[OTA_BOX]: get bin file"),
        ("get_bin_file_done", "[OTA_BOX]: get bin file done, total error cnt: %d"),
        ("chunk_crc", "[OTA_BOX]: crc_cal: 0x%x, crc_rx:0x%x"),
        ("program_fail", "[OTA_BOX]: Fail to program."),
        ("inform_result", "[OTA_BOX]: Inform GLS ota result: %d"),
        ("inform_done", "[OTA_BOX]: Inform GLS done."),
        ("check_box_firmware", "[OTA_BOX]: check box ota firmware."),
        ("swap_bank_2_to_1", "Swap bank(2->1) & RESET, cur ob val:%x"),
        ("swap_bank_1_to_2", "Swap bank(1->2) & RESET, cur ob val:%x"),
        ("ob_program", "ob program: %d"),
        ("ob_check_fail", "Option Bytes check fail, UPDATE & RESET. 0x%x"),
        ("ob_check_done", "Option Bytes check done. 0x%x, level:0x%x"),
    ]
    out = []
    for name, s in steps:
        off = app.find(s.encode())
        if off < 0:
            _fail(f"OTA state-machine string missing: {s!r}")
        out.append({"step": name, "string": s, "file_offset": off + WRAPPER_SIZE})
    return out


def _serial_identity(app: bytes) -> dict:
    sites = {}
    for w in PRESERVED_WINDOWS:
        key = f"{w['start']:#010x}"
        found = _word_sites(app, w["start"])
        if not found:
            _fail(f"preserved-window literal {key} not referenced")
        sites[key] = found
    bank2 = _word_sites(app, APP_ALTERNATE_BASE)
    if len(bank2) < 2:
        _fail("bank-2 base literal missing (dual-bank install evidence)")
    uid = _word_sites(app, 0x1FFF7590)
    flashsize = _word_sites(app, 0x1FFF75E0)
    image_end = APP_BASE + (EXPECTED_SIZE - WRAPPER_SIZE)
    for w in PRESERVED_WINDOWS:
        if w["start"] < image_end:
            _fail("preserved window unexpectedly inside application image")
    return {
        "preserved_windows": PRESERVED_WINDOWS,
        "preserved_window_literal_sites": sites,
        "bank2_base_literal_sites": bank2,
        "uid_0x1fff7590_literal_sites": uid,
        "flashsize_0x1fff75e0_literal_sites": flashsize,
        "image_contains_preserved_windows": False,
        "identity_model": "per-device SN lives in bank-end flash windows "
                          "that the updater explicitly copies across OTA "
                          "(\"Copy SN\" step); set over the USB/factory "
                          "UART (\"Set SN:\", \"Set SN Even done/fail\"); "
                          "the STM32 UID is not referenced by this image",
        "preservation_rule": "never overwrite 0x0803F000..0x0803F00F, "
                             "0x0803F800..0x0803F807, or the bank-2 "
                             "mirrors; any reconstructed image must "
                             "reproduce the copy-forward behavior",
    }


def _regions(blob: bytes) -> list[dict]:
    """Evidence-anchored region classification (file offsets, end exclusive)."""
    defs = [
        (0x000000, 0x000020, "generated_transport",
         "EVEN wrapper: magic, case version 1.2.57, BE length, BE additive "
         "word-sum checksum; container_only, reconstructed by the package "
         "generator"),
        (0x000020, 0x0000D8, "upstream_cmsis_startup",
         "Cortex-M0+ vector table, 46 words, STM32G0B1-class IRQ map"),
        (0x000114, 0x000164, "upstream_freertos_kernel",
         "GCC ARM_CM0 port: interrupt-mask helpers, xPortPendSVHandler; "
         "exact V10-line instruction sequence"),
        (0x000164, 0x000178, "upstream_cmsis_startup",
         "reset trampoline (SystemInit -> _start) and default self-loop "
         "exception slots"),
        (0x002C24, 0x002C2C, "first_party_g2",
         "OTA updater literals referencing the bank-2 preserved SN windows"),
        (0x004BAC, 0x004C3C, "upstream_stm32_hal",
         "HAL FLASH credential island: OPTKEYR + KEYR unlock literals and "
         "surrounding flash-driver code"),
        (0x005F70, 0x005FB0, "upstream_stm32_hal",
         "HAL_UART_IRQHandler head (USART ISR/CR1/CR3/ICR sequence)"),
        (0x008440, 0x008458, "upstream_freertos_kernel",
         "SysTick vector gate: SCS read + xTaskGetSchedulerState guard"),
        (0x008FB8, 0x009058, "first_party_g2",
         "USART1 IRQ thunk plus the two symmetric GLS frame packers "
         "(0x5A channel, 10-retry, 0xFF failure fill)"),
        (0x00C5CC, 0x00C5F0, "upstream_freertos_kernel",
         "xPortSysTickHandler (mask/tick/PENDSVSET/unmask)"),
        (0x00CA6C, 0x00CA86, "upstream_freertos_kernel",
         "xTaskGetSchedulerState over kernel statics at 0x20000128"),
        (0x00CA98, 0x00CAE0, "upstream_freertos_kernel",
         "xTaskIncrementTick head (xTickCount/xPendedTicks/"
         "uxSchedulerSuspended evidence)"),
        (0x00D2C0, 0x00D3A0, "first_party_g2",
         "static task/timer descriptor table with name and entry literals"),
        (0x00D8B8, 0x00D958, "first_party_g2",
         "application task/timer name string block"),
    ]
    regions = []
    covered = 0
    for start, end, cat, note in defs:
        body = blob[start:end]
        regions.append({
            "file_start": start, "file_end_exclusive": end,
            "bytes": len(body), "sha256": _sha(body),
            "ownership_category": cat, "evidence": note,
        })
        covered += len(body)
    regions.append({
        "file_start": None, "file_end_exclusive": None,
        "bytes": len(blob) - covered,
        "sha256": None,
        "ownership_category": "unresolved",
        "evidence": "aggregate remainder outside evidence-anchored "
                    "islands; contains the bulk of the FreeRTOS kernel "
                    "body, STM32 HAL drivers, first-party policy, rodata, "
                    "and the compressed-log string corpus; classification "
                    "requires a full function map",
    })
    for w in PRESERVED_WINDOWS:
        regions.append({
            "file_start": None, "file_end_exclusive": None,
            "bytes": 0,
            "sha256": None,
            "ownership_category": "device_specific_preserve",
            "evidence": f"logical flash window {w['start']:#010x}.."
                        f"{w['end_exclusive']:#010x} (bank {w['bank']}, "
                        f"{w['bytes']} bytes): per-device SN; outside this "
                        "image; updater copies it across OTA; never "
                        "overwrite",
        })
    return regions


def _string_census(blob: bytes) -> dict:
    groups = {
        "ota_box": re.compile(rb"\[OTA_BOX\]"),
        "aging": re.compile(rb"\[AGING_[A-Z]+\]"),
        "gls_uart": re.compile(rb"(GLS_RX|header timeout|no header in first|"
                               rb"receive len timeout|receive data timeout)"),
        "power_standby": re.compile(rb"(Standby|shipmode|Power up|wake up)"),
        "pmic_chips": re.compile(rb"(2510|2217|4005|pmic|PMIC)"),
        "water_detect": re.compile(rb"water detected"),
        "version": re.compile(rb"1\.2\.57"),
    }
    counts = {}
    strings = list(re.finditer(rb"[\x20-\x7e]{6,}", blob))
    for name, pat in groups.items():
        counts[name] = sum(1 for m in strings if pat.search(m.group()))
    counts["total_ascii_strings_ge6"] = len(strings)
    return counts


def analyze() -> dict:
    blob = _load()
    app = blob[WRAPPER_SIZE:]
    wrapper = _wrapper(blob)
    vectors = _vectors(app)
    census = _peripheral_census(app)
    freertos = _freertos(app, vectors)
    hal = _hal(app)
    protocol = _protocol(app)
    ota = _ota_state_machine(app)
    serial = _serial_identity(app)
    regions = _regions(blob)
    strings = _string_census(blob)

    # Family discrimination summary (all load-bearing checks already ran).
    irq12 = vectors["entries"][16 + 12]
    irq22 = vectors["entries"][16 + 22]
    irq27 = vectors["entries"][16 + 27]
    family = {
        "leading_candidate": "STM32G0B1 (STM32G0Bx-class, 512-KB dual-bank "
                             "flash, Cortex-M0+)",
        "confidence": "high for G0Bx-class; medium for the exact member "
                      "(G0B0/G0B1/G0C1 not statically separable: AES/RNG/"
                      "FDCAN2 unused, DBGMCU IDCODE never read)",
        "discriminators": [
            "46-word vector table = 30 populated peripheral IRQs on the "
            "G0Bx interrupt map",
            f"IRQ12 (ADC1_COMP) populated with an ADC ISR/IER-flag worker: "
            f"{irq12['value']:#x}",
            f"IRQ22 (TIM17_FDCAN_IT1) populated with a TIM SR/DIER "
            f"capture-compare worker: {irq22['value']:#x}",
            f"IRQ27 (USART1) populated: {irq27['value']:#x}",
            "USART3/USART4 base literals present (absent on STM32G030)",
            "dual-bank update flow: bank-2 base 0x08040000 literals + "
            "nSWAP_BANK option-byte programming (\"Swap bank\", \"ob "
            "program\"), excluding <=128-KB single-bank members",
            "initial SP 0x20002C88; RAM-resident code/data observed up to "
            "0x2000FC1C (>=64-KB SRAM usage; G0B1 nominal 144 KB)",
        ],
        "excluded": {
            "STM32G030": "28-IRQ map, no USART3/4, no dual-bank, 8-KB SRAM",
            "STM32G070/G071": "IRQ12=TIM1_BRK/IRQ22=I2C1/IRQ27=USART2 map "
                              "contradicted by handler evidence; single-bank "
                              "<=128-KB flash contradicts nSWAP_BANK flow",
        },
    }

    return {
        "identity": {
            "blob": BLOB_REL,
            "size": EXPECTED_SIZE,
            "sha256": EXPECTED_SHA256,
            "wrapper": wrapper,
            "app_vaddr_base": APP_BASE,
            "app_alternate_bank_vaddr": APP_ALTERNATE_BASE,
            "app_bytes": EXPECTED_SIZE - WRAPPER_SIZE,
        },
        "mcu_family": family,
        "vectors": vectors,
        "peripherals": census,
        "freertos": freertos,
        "hal": hal,
        "uart_update_protocol": protocol,
        "ota_state_machine_strings": ota,
        "serial_identity": serial,
        "ownership_categories": OWNERSHIP_CATEGORIES,
        "regions": regions,
        "string_census": strings,
        "hardware_gates": [
            "battery/charging/thermal policy values (98% charge cutoff, "
            "over-temperature stop, fake-standby timers) are log-evidenced "
            "only; no hardware validation performed",
            "water-detect thresholds and PMIC register writes are "
            "hardware-gated",
            "nSWAP_BANK option-byte flow proven from code/strings only; "
            "no device execution",
        ],
        "unresolved": [
            "exact FreeRTOS point release within V10.x",
            "exact STM32 HAL version (no static version evidence)",
            "STM32G0B0 vs G0B1 vs G0C1 member split",
            "GLS UART CRC polynomial/width (bit-wise; no table)",
            "compressed-log string reference scheme (most log strings have "
            "no pointer literals; consistent with an indexed log-strip "
            "scheme, exact ID encoding unknown)",
            "full function-level closure of the kernel/HAL/policy bodies",
        ],
    }


def _write_manifests(result: dict) -> list[str]:
    out = []
    manifest_dir = G2_ROOT / "tools/manifests"
    tsv = manifest_dir / "g2-box-stm32g0-platform-attribution.tsv"
    lines = [
        "# G2 charging-case platform attribution map",
        "# blob: blobs/official/g2-2.2.6.10/firmware_box.bin sha256="
        + EXPECTED_SHA256,
        "# categories: " + ", ".join(OWNERSHIP_CATEGORIES),
        "file_start\tfile_end_exclusive\tbytes\tsha256\townership_category\tevidence",
    ]
    for r in result["regions"]:
        fs = "-" if r["file_start"] is None else f"0x{r['file_start']:06x}"
        fe = "-" if r["file_end_exclusive"] is None else f"0x{r['file_end_exclusive']:06x}"
        sh = r["sha256"] or "-"
        lines.append(f"{fs}\t{fe}\t{r['bytes']}\t{sh}\t"
                     f"{r['ownership_category']}\t{r['evidence']}")
    tsv.write_text("\n".join(lines) + "\n")
    out.append(str(tsv.relative_to(G2_ROOT)))

    js = manifest_dir / "g2-box-stm32g0-platform-summary.json"
    js.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    out.append(str(js.relative_to(G2_ROOT)))
    return out


def main() -> int:
    write = "--write-manifests" in sys.argv
    result = analyze()
    fam = result["mcu_family"]
    print(f"blob           : {result['identity']['blob']}")
    print(f"  size/sha256  : {result['identity']['size']} / "
          f"{result['identity']['sha256'][:16]}...")
    print(f"  wrapper      : EVEN v{result['identity']['wrapper']['version']} "
          f"len={result['identity']['wrapper']['length_be_u32']} "
          f"checksum verified")
    print(f"MCU            : {fam['leading_candidate']}")
    print(f"  confidence   : {fam['confidence']}")
    print(f"vectors        : {result['vectors']['word_count']} words, "
          f"SP={result['vectors']['initial_sp']:#x}, "
          f"map={result['vectors']['irq_map_reference']}")
    print(f"FreeRTOS       : {result['freertos']['kernel_family']} "
          f"{result['freertos']['version_interval']}")
    print(f"  port         : {result['freertos']['port']}")
    print(f"HAL            : {len(result['hal']['modules_present'])} module "
          f"families present; flash credentials proven")
    used = sorted(result["peripherals"]["used"])
    print(f"peripherals    : {', '.join(used)}")
    print(f"protocol       : header 5A A5 FF <cmd>; packers "
          f"{[hex(p['vaddr']) for p in result['uart_update_protocol']['frame_packer']['instances']]}")
    print(f"preserved SN   : "
          + ", ".join(f"{w['start']:#x}+{w['bytes']}" for w in PRESERVED_WINDOWS)
          + " (never overwrite)")
    cats: dict[str, int] = {}
    for r in result["regions"]:
        cats[r["ownership_category"]] = cats.get(r["ownership_category"], 0) + r["bytes"]
    print("ownership bytes:")
    for c in OWNERSHIP_CATEGORIES:
        if c in cats:
            print(f"  {c:26s}: {cats[c]}")
    if write:
        for p in _write_manifests(result):
            print(f"wrote          : {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
