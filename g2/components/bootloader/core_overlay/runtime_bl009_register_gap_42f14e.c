/* SPDX-License-Identifier: MIT */
/* Clean-room in-place data: routed scalar cells of the 122-byte
 * register/pointer table at 0x0042F14E before the register power
 * toggle (predecessor ends 0x0042F14E, toggle region starts
 * 0x0042F1C8 via the routed 0x0042F1C8 head).
 *
 * The table is consumed ~84 times by original literal loads in already
 * source-routed hardware-context, handle, enumeration, and
 * register-profile code (0x0042E8D0..0x0042F14E), whose successors embed
 * equivalents in their own pools. Only cells with an identified scalar
 * meaning are routed here; seven unattributed SRAM addresses stay
 * retained stock.
 *
 * Routed cells: two zero alignment bytes; the pack word 0x1F01600D;
 * calibration floats 299.5f, 1.02809f (0x3F839874), -0.004281f
 * (0xBB8C47A1); the config base 0x4002010C; the masked-identifier
 * compare constant 0x01AFAFAF (original consumers, e.g. 0x0042EA42,
 * mask with BIC #0xFE000000 and compare); the 0x40038000-block
 * register addresses (0x40038000, 0x4003800C, 0x40038040, 0x4003802C,
 * 0x40038030, 0x40038034); the -290.0f bound with 0x40038200; and the
 * 0x4003803C..0x40038008 tail run (0x4003803C, 0x40038010, 0x40038014,
 * 0x40038018, 0x4003801C, 0x40038020, 0x40038024, 0x40038028,
 * 0x40038008).
 */
typedef __UINT32_TYPE__ open_cfw_bl009_u32;
typedef __UINT16_TYPE__ open_cfw_bl009_u16;

struct __attribute__((packed)) open_cfw_bl009_gap_42f14e {
    open_cfw_bl009_u16 align_pad;
    open_cfw_bl009_u32 pack_word;
    float cal_a;
    float cal_b;
    float cal_c;
    open_cfw_bl009_u32 cfg_base;
    open_cfw_bl009_u32 id_compare;
    open_cfw_bl009_u32 regs0[6];
    float bound_neg290;
    open_cfw_bl009_u32 reg_extra;
    open_cfw_bl009_u32 regs1[9];
};

__attribute__((used))
const struct __attribute__((packed)) open_cfw_bl009_gap_42f14e
open_cfw_bootloader_bl009_gap_42f14e = {
    0x0000u, 0x1F01600Du, 299.5f, 0x1.0730e8p+0f, -0x1.188f42p-8f,
    0x4002010Cu, 0x01AFAFAFu,
    { 0x40038000u, 0x4003800Cu, 0x40038040u, 0x4003802Cu, 0x40038030u,
      0x40038034u },
    -290.0f, 0x40038200u,
    { 0x4003803Cu, 0x40038010u, 0x40038014u, 0x40038018u, 0x4003801Cu,
      0x40038020u, 0x40038024u, 0x40038028u, 0x40038008u }
};
