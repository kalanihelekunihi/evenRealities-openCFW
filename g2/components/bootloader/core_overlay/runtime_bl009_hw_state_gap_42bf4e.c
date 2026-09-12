/* SPDX-License-Identifier: MIT */
/* Clean-room in-place data: six-byte literal/alignment cell at
 * 0x0042BF4E between the hardware-state composer (ends 0x0042BF4E) and the
 * hardware-readiness gate (starts 0x0042BF54).
 *
 * Layout: two zero alignment bytes, then the 32-bit ARM system-register
 * address 0xE000ED14 (SCB->CCR, Configuration and Control Register).
 * The original SPOT-manager state-transition code at 0x0042B4D4
 * (`ldr.w r0, [pc, #0xa78]` targeting 0x0042BF50, then `ldr r0, [r0]`,
 * `lsls r0, #14`, `bpl`) dereferences this cell to poll CCR bit 17
 * (instruction-cache enable) during power-state transition checks.
 * That consumer region is already source-routed
 * (runtime_spotmgr_state_transition_42b294.c and neighbours), so this
 * cell is original-layout literal residue with no live referent in the
 * source build; it is reproduced here to preserve the authenticated
 * image bytes from a named, understood constant.
 */
typedef __UINT32_TYPE__ open_cfw_bl009_u32;
typedef __UINT16_TYPE__ open_cfw_bl009_u16;

struct __attribute__((packed)) open_cfw_bl009_gap_42bf4e {
    open_cfw_bl009_u16 align_pad;
    open_cfw_bl009_u32 scb_ccr;
};

__attribute__((used))
const struct open_cfw_bl009_gap_42bf4e
open_cfw_bootloader_bl009_gap_42bf4e = { 0x0000u, 0xE000ED14u };
