/* SPDX-License-Identifier: MIT */
/* Clean-room in-place data: routed scalar cells of the 76-byte literal
 * cell at 0x004301F4 before the first NVIC enable helper (predecessor
 * ends 0x004301F4, helper region starts 0x00430240).
 *
 * The span mixes pointer cells into still-opaque BL-011/BL-012 code and
 * the retained 0x0042F674 dispatcher (0x00434170, 0x00431EA4,
 * 0x004325F8, 0x00433140, 0x0043402C, 0x00432C7C, 0x004329D4,
 * 0x00433160, 0x00431AB8, 0x00434174, 0x0042F674) with scalar cells.
 * Only the scalar cells are routed here; every pointer cell, the two
 * unreferenced float words (0x44610001, 0x447A0000), the SRAM word
 * 0x20027018, and the head/tail structure around them stay retained.
 *
 * Routed cells:
 * - 0x004301F4: zero word (pool alignment head; no original referent).
 * - 0x004301F8: 0x00000000 = +0.0f, loaded by the original `vldr` at
 *   0x00430024 in the already-routed platform bring-up region.
 * - 0x00430210: 0xC2F6E979 = -123.45600128173828f, calibration literal
 *   loaded by original code in the routed bring-up region (same value
 *   also appears as the unrouted middle word of the 0x0042EDF6 cell).
 * - 0x00430230: 0x40038038, status register polled by original code at
 *   0x00430126 (`ldr r0, [r0]` then `ubfx r0, #0x14, #8` field
 *   extraction with a zero-compare spin) in the routed NVIC helper
 *   region.
 */
typedef __UINT32_TYPE__ open_cfw_bl009_u32;

struct open_cfw_bl009_gap_4301f4 {
    open_cfw_bl009_u32 align_zero;
    float zero_bound;
    float cal_value;
    open_cfw_bl009_u32 status_register;
};

__attribute__((used))
const struct open_cfw_bl009_gap_4301f4
open_cfw_bootloader_bl009_gap_4301f4 = {
    0x00000000u, 0.0f, -0x1.edd2f2p+6f, 0x40038038u
};
