/* SPDX-License-Identifier: MIT */
/* Clean-room in-place data: routed cells of the ten-byte literal cell at
 * 0x0042EDF6 between adjacent hardware-channel normalisation services
 * (predecessor ends 0x0042EDF6, successor starts 0x0042EE00).
 *
 * Layout: two zero alignment bytes, the word 0xC2F6E979 (a binary32
 * calibration literal with no identified original referent, left as
 * retained stock), then the word 0x43910000 = 290.0f. The 290.0f cell
 * is loaded by the original `vldr` at 0x0042ECCC in the already-routed
 * configuration-operation dispatcher region, whose successor
 * materialises the equivalent bound in its own pool. Only the pad and
 * the 290.0f cell are routed here; the middle word stays retained.
 */
typedef __UINT16_TYPE__ open_cfw_bl009_u16;

struct __attribute__((packed)) open_cfw_bl009_gap_42edf6 {
    open_cfw_bl009_u16 align_pad;
    float cal_limit;
};

__attribute__((used))
const struct open_cfw_bl009_gap_42edf6
open_cfw_bootloader_bl009_gap_42edf6 = { 0x0000u, 290.0f };
