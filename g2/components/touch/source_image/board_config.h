/* SPDX-License-Identifier: MIT */
/*
 * G2 Touch controller source-image board contract.
 *
 * This header collects the non-code configuration assumptions that the
 * freestanding Touch source image currently relies on. Values marked
 * CONFIRMED come from public PSoC 4000T/CY8C4046FNI device facts or from the
 * already-authenticated identity audit in
 * docs/research/g2-touch-identity-recovery.md. Values marked HARDWARE-BLOCKED
 * are intentionally named here but not driven by this image: they require a
 * responsive physical part, board-level routing evidence, or the resident DFU
 * handoff behavior that this source tree cannot infer safely.
 */
#ifndef OPEN_CFW_TOUCH_BOARD_CONFIG_H
#define OPEN_CFW_TOUCH_BOARD_CONFIG_H

#include <stdint.h>

#define OPEN_CFW_TOUCH_PART_FAMILY "CY8C4046FNI / PSoC 4000T" /* CONFIRMED */

/* ---- Flash/SRAM geometry (CONFIRMED: identity audit + public datasheet) ---- */
#define OPEN_CFW_TOUCH_FLASH_BASE      UINT32_C(0x00000000)
#define OPEN_CFW_TOUCH_FLASH_BYTES     UINT32_C(0x00010000) /* 64 KiB */
#define OPEN_CFW_TOUCH_SRAM_BASE       UINT32_C(0x20000000)
#define OPEN_CFW_TOUCH_SRAM_BYTES      UINT32_C(0x00002000) /* 8 KiB */
#define OPEN_CFW_TOUCH_STACK_TOP       UINT32_C(0x20002000)

/* ---- Transport/package identity (CONFIRMED: G2 type-3 FWPK contract) ---- */
#define OPEN_CFW_TOUCH_FWPK_MAGIC      UINT32_C(0x4B505746) /* "FWPK" LE */
#define OPEN_CFW_TOUCH_FWPK_VERSION    UINT32_C(0x01000202)
#define OPEN_CFW_TOUCH_FWPK_RECORD_TYPE UINT32_C(3)
#define OPEN_CFW_TOUCH_FWPK_PAYLOAD_OFFSET UINT32_C(0x20)

/* ---- Explicitly unresolved resident/board contracts ----
 * The source image names the affected services but keeps the handlers inert.
 * Do not promote production_routed without evidence for these contracts. */
#define OPEN_CFW_TOUCH_HARDWARE_BLOCKED_CONTRACTS(X) \
    X(SCB1_I2C_SHIFT_REGISTER_SERVICE) \
    X(MSCLP_CAPSENSE_SCAN_RESULT_DRAIN) \
    X(SPCIF_FLASH_SROM_ROW_PROGRAMMING) \
    X(GPIO_PIN_AND_ATTENTION_LINE_ROUTING) \
    X(RESIDENT_DFU_MAILBOX_RESET_HANDOFF)

#endif
