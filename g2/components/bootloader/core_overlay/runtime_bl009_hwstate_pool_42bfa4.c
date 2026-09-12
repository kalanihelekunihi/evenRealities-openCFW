/* SPDX-License-Identifier: MIT */
/* Clean-room in-place data: routed scalar cells of the 144-byte
 * hardware-state literal pool at 0x0042BFA4 between the
 * hardware-readiness gate (ends 0x0042BFA4) and the status-route
 * selector (starts 0x0042C034).
 *
 * The head of this pool serves original loads in the already-routed
 * hardware-state decoder (0x0042B6BA -> 0x0042BFA8,
 * 0x0042B6E4 -> 0x0042BFAC); the body and tail serve the retained
 * 0x0042BA00 function (BL-009 code span) and the routed composer/gate
 * tails (0x0042BDF4 -> 0x0042C02C, 0x0042BF86 -> 0x0042C030). Routed
 * successors embed equivalents of the scalar cells in their own pools;
 * the retained consumer keeps reading the cells routed here, which is
 * ordinary data reuse and claims no functionality.
 *
 * Only cells with an identified scalar meaning are routed; the head
 * word 0xC2200000 (no original referent), the BL-012 pointer
 * 0x00434164, and ten unattributed SRAM addresses stay retained stock.
 * Routed runs (six placements): bitmask/config words 0x40021000,
 * 0x00F00FFF, 0x000FFCFF, 0x000FF00F, 0x00011001, 0x00012001,
 * 0x40021108, 0x1F01600D; peripheral register addresses 0x40021008,
 * 0x40021010, 0x40021018, 0x40021028, 0x4002037C, 0x40020080,
 * 0x40020088, 0x400201B0, 0x400201BC, 0x400083E0; calibration floats
 * -273.0f, -20.0f, -22.0f, 50.0f, 48.0f, 1000.0f.
 */
typedef __UINT32_TYPE__ open_cfw_bl009_u32;

struct open_cfw_bl009_gap_42bfa4 {
    open_cfw_bl009_u32 cfg_a0;
    open_cfw_bl009_u32 mask_a0;
    open_cfw_bl009_u32 mask_a1;
    open_cfw_bl009_u32 mask_b0;
    open_cfw_bl009_u32 cfg_b0;
    open_cfw_bl009_u32 cfg_b1;
    open_cfw_bl009_u32 reg_c0;
    open_cfw_bl009_u32 pack_c0;
    open_cfw_bl009_u32 reg_d0;
    open_cfw_bl009_u32 reg_d1;
    open_cfw_bl009_u32 reg_d2;
    open_cfw_bl009_u32 reg_d3;
    float cal_e0;
    float cal_e1;
    float cal_e2;
    float cal_e3;
    float cal_e4;
    float cal_e5;
    open_cfw_bl009_u32 reg_f0;
    open_cfw_bl009_u32 reg_f1;
    open_cfw_bl009_u32 reg_f2;
    open_cfw_bl009_u32 reg_f3;
    open_cfw_bl009_u32 reg_f4;
    open_cfw_bl009_u32 reg_f5;
};

__attribute__((used))
const struct open_cfw_bl009_gap_42bfa4
open_cfw_bootloader_bl009_gap_42bfa4 = {
    0x40021000u, 0x00F00FFFu, 0x000FFCFFu, 0x000FF00Fu, 0x00011001u,
    0x00012001u, 0x40021108u, 0x1F01600Du, 0x40021008u, 0x40021010u,
    0x40021018u, 0x40021028u, -273.0f, -20.0f, -22.0f, 50.0f, 48.0f,
    1000.0f, 0x4002037Cu, 0x40020080u, 0x40020088u, 0x400201B0u,
    0x400201BCu, 0x400083E0u
};
