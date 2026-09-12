/* SPDX-License-Identifier: MIT */
/* Clean-room in-place data: two retained branch-fragment
 * halfwords, one alignment halfword, and one lifecycle literal
 * word, none with a loader in any routed span.
 *
 * - 0x00425160 (0xF82F): orphaned second halfword of the
 *   replaced MSPI disable head's 32-bit `bl #0x0041D1C0` at
 *   0x0042515E (the authentic stock stream decoded anchored at
 *   0x00425140 shows the branch spanning 0x0042515E..0x00425162;
 *   the head entry is entry-redirect-replaced, orphaning this
 *   halfword). Bounded Capstone decode of every routed span
 *   finds no loader targeting it, so it is reproduced as a named
 *   fragment halfword preserving layout, not as claimed code.
 * - 0x00425166 (0x0000): canonical two-byte alignment NOP
 *   between the disable mini-tail (reconstructed in
 *   runtime_bl006_disable_tail_425162.c) and the lifecycle word.
 * - 0x00425168 (0x0007FFFF): lifecycle literal word closing the
 *   disable region. Bounded Capstone decode of every routed span
 *   finds no PC-relative or `adr` loader targeting it, and no
 *   reviewed consumer source names the value, so it is
 *   reproduced as a named reserved word preserving layout.
 * - 0x004264B0 (0x3200): orphaned second halfword of the
 *   replaced MSPI interrupt-disable head's 32-bit `adds.w r2,
 *   r2, r0, lsl #12` at 0x004264AE (spanning
 *   0x004264AE..0x004264B2). Same standing as the 0x00425160
 *   fragment: no loader, layout preservation only. The complete
 *   8-byte publish tail after it (0x004264B2) is reconstructed
 *   in runtime_bl006_irq_disable_tail_4264b2.c.
 *
 * If a future consumer is found for any of these slots, its
 * field must be re-derived with the loader PCs and reviewed
 * meaning. See
 * docs/research/g2-bootloader-bl006-tail-leaves-426c22-427d84-source-closure.md.
 */

typedef __UINT16_TYPE__ open_cfw_bl006_fg_u16;
typedef __UINT32_TYPE__ open_cfw_bl006_fg_u32;

/* Orphaned disable-head branch-fragment halfword at 0x00425160. */
__attribute__((used, section(".rodata.bl006_frag_425160")))
const open_cfw_bl006_fg_u16 open_cfw_bootloader_bl006_frag_425160 = 0xF82Fu;

/* Alignment halfword at 0x00425166. */
__attribute__((used, section(".rodata.bl006_pad_425166")))
const open_cfw_bl006_fg_u16 open_cfw_bootloader_bl006_pad_425166 = 0x0000u;

/* Lifecycle literal word at 0x00425168. */
__attribute__((used, section(".rodata.bl006_word_425168")))
const open_cfw_bl006_fg_u32 open_cfw_bootloader_bl006_word_425168 = 0x0007FFFFu;

/* Orphaned interrupt-disable-head fragment halfword at
 * 0x004264B0. */
__attribute__((used, section(".rodata.bl006_frag_4264b0")))
const open_cfw_bl006_fg_u16 open_cfw_bootloader_bl006_frag_4264b0 = 0x3200u;
