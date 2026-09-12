/* SPDX-License-Identifier: MIT */
/* Clean-room in-place data: the identified peripheral-address cell of
 * the literal pool consumed by the reconstructed hardware-state
 * field helper at 0x0042BD8C (original Thumb literal load at
 * 0x0042BD8C).
 *
 * Cells, in runtime order:
 * - 0x0042BDE4: 0x4002034C, peripheral register whose bits 29:25 the
 *   helper overwrites with the fixed value 6. The same address is
 *   also referenced from the retained 0x0041CBA8 and 0x0042F65C
 *   regions, which stay opaque; routing this cell records the
 *   identified address, not those consumers.
 * The neighbouring pool words (0x0042BDE8 SRAM address, 0x0042BDEC
 * peripheral word, both without an identified routed consumer) stay
 * retained, as does the 0x0042BD9C inter-function pad.
 */
typedef __UINT32_TYPE__ open_cfw_bl009_hwstate_u32;

struct __attribute__((packed)) open_cfw_bl009_hwstate_cell_42bde4 {
    open_cfw_bl009_hwstate_u32 field_reg;
};

__attribute__((used))
const struct open_cfw_bl009_hwstate_cell_42bde4
open_cfw_bootloader_bl009_hwstate_cell_42bde4 = {
    0x4002034Cu
};
