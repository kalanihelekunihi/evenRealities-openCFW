/* SPDX-License-Identifier: MIT */
/* Clean-room in-place data: nine peripheral register addresses from the
 * shared literal pool at 0x0042D79E..0x0042D848, consumed by the
 * reconstructed trim-state leaves at 0x0042D5C2..0x0042D6C0 and by
 * already source-routed neighbours in the 0x0042CDF8..0x0042D562
 * cluster (whose successors materialise equivalent constants in their
 * own pools, so these cells are live originals for the leaves routed
 * here).
 *
 * Cells, in runtime order:
 * - 0x0042D7E0: 0x40020080, LDOREG1 power-trim register (identified by
 *   the SPOTmgr transition closure); target of the 10-bit field
 *   publisher at 0x0042D5F8.
 * - 0x0042D7E8: 0x40020088, next register in the same power-trim
 *   block; first target of the dual field setter at 0x0042D61E.
 * - 0x0042D7FC: 0x400201B0, global-control register; second target of
 *   the dual field setter at 0x0042D61E.
 * - 0x0042D818..0x0042D82C: 0x400211A0, 0x400211A8, 0x400211A4,
 *   0x400211AC, 0x400211B4, 0x400211BC, a six-word peripheral
 *   register block programmed with fixed calibration constants by
 *   the block programmer at 0x0042D63A and bit-flipped by the
 *   raise/clear pair at 0x0042D692/0x0042D6A6.
 * The pool's SRAM-address cells (0x0042D7A0, 0x0042D7BC, 0x0042D814,
 * 0x0042D830) stay retained: their layout role is unattributed, and
 * the portable leaf models take them as parameters rather than
 * depending on the addresses.
 */
typedef __UINT32_TYPE__ open_cfw_bl009_trim_u32;

struct __attribute__((packed)) open_cfw_bl009_trim_pool_42d7e0 {
    open_cfw_bl009_trim_u32 ldo_trim_field_reg;
    open_cfw_bl009_trim_u32 ldo_trim_adjacent_reg;
    open_cfw_bl009_trim_u32 global_control_reg;
    open_cfw_bl009_trim_u32 trim_block_head;
    open_cfw_bl009_trim_u32 trim_block_word_a;
    open_cfw_bl009_trim_u32 trim_block_word_b;
    open_cfw_bl009_trim_u32 trim_block_word_c;
    open_cfw_bl009_trim_u32 trim_block_word_d;
    open_cfw_bl009_trim_u32 trim_block_word_e;
};

__attribute__((used))
const struct open_cfw_bl009_trim_pool_42d7e0
open_cfw_bootloader_bl009_trim_pool_42d7e0 = {
    0x40020080u, 0x40020088u, 0x400201B0u,
    0x400211A0u, 0x400211A8u, 0x400211A4u,
    0x400211ACu, 0x400211B4u, 0x400211BCu
};
