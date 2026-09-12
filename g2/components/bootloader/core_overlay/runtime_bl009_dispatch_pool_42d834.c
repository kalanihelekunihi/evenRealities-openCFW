/* SPDX-License-Identifier: MIT */
/* Clean-room in-place data: the two identified scalar cells of the
 * shared literal pool consumed by the reconstructed state-flag
 * dispatcher at 0x0042D6C0 (original Thumb literal loads at
 * 0x0042D6C2/0x0042D6E4/0x0042D6F6/0x0042D708/0x0042D728/0x0042D73A
 * for the register cell and at 0x0042D750 for the mask cell).
 *
 * Cells, in runtime order:
 * - 0x0042D834: 0x4002000C, trim-block state register in the same
 *   0x400200xx power-trim block as the routed LDOREG1 cells; the
 *   dispatcher reads its low byte as the 0x21/0x22/0x23 mode
 *   selector.
 * - 0x0042D840: 0x3FE00000, field mask ANDed with the guarded
 *   status word before the 0x31800000 match compare.
 * The dispatcher's SRAM-address cells (0x0042D7AC, 0x0042D810,
 * 0x0042D838, 0x0042D83C, 0x0042D844) stay retained: their layout
 * role is unattributed, and the portable dispatcher model takes
 * them as parameters rather than depending on the addresses.
 */
typedef __UINT32_TYPE__ open_cfw_bl009_dispatch_u32;

struct __attribute__((packed)) open_cfw_bl009_dispatch_pool_42d834 {
    open_cfw_bl009_dispatch_u32 trim_state_reg;
    open_cfw_bl009_dispatch_u32 status_field_mask;
};

__attribute__((used))
const struct open_cfw_bl009_dispatch_pool_42d834
open_cfw_bootloader_bl009_dispatch_pool_42d834 = {
    0x4002000Cu, 0x3FE00000u
};
