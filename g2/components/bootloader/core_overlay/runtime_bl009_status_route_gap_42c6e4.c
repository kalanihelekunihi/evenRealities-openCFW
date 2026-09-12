/* SPDX-License-Identifier: MIT */
/* Clean-room in-place data: twenty-byte literal cell at 0x0042C6E4
 * between the hardware interrupt-clear helper (ends 0x0042C6E4) and the
 * hardware event/descriptor/callback/command-queue service (starts
 * 0x0042C6F8).
 *
 * Cells, each consumed by original literal loads in already source-routed
 * neighbours (so this is original-layout residue, reproduced to preserve
 * the authenticated image bytes from named constants):
 * - 0x0042C6E4: zero word (pool alignment head; no original referent).
 * - 0x0042C6E8: 0x40050000, peripheral register-block base. Original
 *   consumers (e.g. 0x0042C034 `ldr.w r2, [pc, #0x6b0]`) compute
 *   `r2 + r0 << 12` and issue indexed field loads such as
 *   `ldr.w r3, [r3, #0x11c]`, i.e. the base of an indexed register
 *   block walked by the status-route selector and its peers.
 * - 0x0042C6EC / 0x0042C6F0: 0x08000001 / 0x08000002, read-path selector
 *   words. Original consumers (0x0042C098 / 0x0042C0A2) select one of
 *   the two by testing flag bits in r1/r2 and return the selected word
 *   in r0 as the read-path status word.
 * - 0x0042C6F4: 0xDEADBEEF sentinel literal loaded by original code
 *   (0x0042C0E6 `ldr.w r3, [pc, #0x60c]`) for a debug-compare path in
 *   the status-route helper.
 */
typedef __UINT32_TYPE__ open_cfw_bl009_u32;

struct open_cfw_bl009_gap_42c6e4 {
    open_cfw_bl009_u32 align_zero;
    open_cfw_bl009_u32 reg_block_base;
    open_cfw_bl009_u32 read_path_word0;
    open_cfw_bl009_u32 read_path_word1;
    open_cfw_bl009_u32 debug_sentinel;
};

__attribute__((used))
const struct open_cfw_bl009_gap_42c6e4
open_cfw_bootloader_bl009_gap_42c6e4 = {
    0x00000000u, 0x40050000u, 0x08000001u, 0x08000002u, 0xDEADBEEFu
};
