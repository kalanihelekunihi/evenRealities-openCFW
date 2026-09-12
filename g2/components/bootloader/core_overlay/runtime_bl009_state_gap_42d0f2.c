/* SPDX-License-Identifier: MIT */
/* Clean-room in-place data: eighteen-byte floating-point literal cell at
 * 0x0042D0F2 between the sixteen-channel state/event fault classifier
 * (ends 0x0042D0F2) and the state-one tuning service (starts
 * 0x0042D104).
 *
 * Layout: two zero alignment bytes, then four IEEE-754 binary32 range
 * bounds consumed by original loads in already source-routed neighbours:
 * - 0x0042D0F4: 0x420C0000 = 35.0f, loaded by original `vldr`
 *   at 0x0042CEE0 in the floating-point range-update service.
 * - 0x0042D0F8: 0xC3888000 = -273.0f (original consumer 0x0042CF7C).
 * - 0x0042D0FC: 0x42480000 = 50.0f (original consumer 0x0042CFAA).
 * - 0x0042D100: 0x447A0000 = 1000.0f (original consumer 0x0042CFCE).
 * The routed successors materialise equivalent bounds in their own
 * pools, so this cell is original-layout residue reproduced here to
 * preserve the authenticated image bytes from named constants.
 */
typedef __UINT16_TYPE__ open_cfw_bl009_u16;

struct __attribute__((packed)) open_cfw_bl009_gap_42d0f2 {
    open_cfw_bl009_u16 align_pad;
    float bound_a;
    float bound_b;
    float bound_c;
    float bound_d;
};

__attribute__((used))
const struct open_cfw_bl009_gap_42d0f2
open_cfw_bootloader_bl009_gap_42d0f2 = {
    0x0000u, 35.0f, -273.0f, 50.0f, 1000.0f
};
