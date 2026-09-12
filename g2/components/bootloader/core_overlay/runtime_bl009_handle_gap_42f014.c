/* SPDX-License-Identifier: MIT */
/* Clean-room in-place data: the -1000.0f head cell of the twelve-byte
 * literal cell at 0x0042F014 before the register-profile transfer
 * service (predecessor ends 0x0042F014, transfer starts 0x0042F020).
 *
 * - 0x0042F014: 0xC47A0000 = -1000.0f, loaded by the original `vldr`
 *   at 0x0042EE3C in the already-routed calibrated packed-channel
 *   normalisation region.
 * The remaining two words (0x45800000 = 4096.0f, 0x4494C000 = 1190.0f)
 * have no identified original referent and stay retained stock.
 */
__attribute__((used))
const float
open_cfw_bootloader_bl009_gap_42f014 = -1000.0f;
