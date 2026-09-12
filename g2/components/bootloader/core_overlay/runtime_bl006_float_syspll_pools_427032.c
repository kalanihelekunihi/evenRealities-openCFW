/* SPDX-License-Identifier: MIT */
/* Clean-room in-place data: the floating-point literal pools at
 * 0x00427032 (14 bytes), 0x0042714C (20 bytes), and 0x00427308
 * (8 bytes), between the functionally replaced float/System-PLL
 * service spans.
 *
 * Every loader of every slot below lives in an entry-redirect stock
 * span (the float gcd/ratio/multiplier/encoding-select bodies at
 * 0x00426D48/0x00426DB4/0x00426EAC/0x00426F6C and the System PLL
 * minimum-VCO body at 0x00427040), verified by bounded Capstone
 * decode of all routed spans; no byte-exact shipped body loads any
 * of these slots. The pools are therefore admitted as authenticated
 * layout reproductions with reviewed meanings, not as address-live
 * traffic. Each value below names its reviewed spelling in the
 * replacement consumer source, except the two explicitly marked
 * reserved slots (the 0x00427032 alignment halfword with no loader,
 * and the 0x00427150 zero word with no reviewed spelling), which
 * preserve layout only; see
 * docs/research/g2-bootloader-bl006-cluster-426d2c-427754-source-closure.md.
 */

typedef __UINT16_TYPE__ open_cfw_bl006_u16;
typedef __UINT32_TYPE__ open_cfw_bl006_u32;

/* Pool at 0x00427032: alignment pad plus the float-ratio bounds. */
struct __attribute__((packed)) open_cfw_bl006_pool_427032 {
    open_cfw_bl006_u16 align_pad; /* 0x0000: alignment halfword;
        no loader in any routed span. */
    open_cfw_bl006_u32 tiny_bound; /* 0x34000000: 0x1p-23f, the
        subnormal divisor bound (float-gcd loader 0x00426D94,
        float-ratio loader 0x00426DD2, float-multiplier loader
        0x00426EDA; reviewed spellings in
        runtime_float_gcd_426d48.c, runtime_float_ratio_426db4.c,
        runtime_float_multiplier_426eac.c). */
    open_cfw_bl006_u32 epsilon_bound; /* 0x34000001: 0x1.000002p-23f,
        the fractional-part epsilon (float-ratio loader 0x00426DEC;
        reviewed spelling in runtime_float_ratio_426db4.c). */
    open_cfw_bl006_u32 large_bound; /* 0x44700001: 0x1.e00002p+9f,
        the 960-count bound (float-ratio loader 0x00426E0E,
        float-encoding-select loader 0x00426FA8; reviewed spellings
        in runtime_float_ratio_426db4.c and
        runtime_float_encoding_select_426f6c.c). */
};

__attribute__((used, section(".rodata.bl006_pool_427032")))
const struct open_cfw_bl006_pool_427032 open_cfw_bootloader_bl006_pool_427032 = {
    0x0000u, 0x34000000u, 0x34000001u, 0x44700001u
};

/* Pool at 0x0042714C: float-multiplier/select bounds between the
 * System PLL minimum-VCO and postdivider spans. */
struct __attribute__((packed)) open_cfw_bl006_pool_42714c {
    open_cfw_bl006_u32 count_bound; /* 0x427C0001: 0x1.f80002p+5f,
        the 63-count bound (float-ratio loader 0x00426E4E,
        float-multiplier loader 0x00426EE8; reviewed spellings in
        runtime_float_ratio_426db4.c and
        runtime_float_multiplier_426eac.c). */
    open_cfw_bl006_u32 reserved_zero; /* 0x00000000: zero word loaded
        by the replaced float-multiplier stock body (loaders
        0x00426EB8/0x00426EBC/0x00426EC0) with no reviewed spelling;
        reproduced as a named constant preserving layout, not as
        claimed data. */
    open_cfw_bl006_u32 scale_bound; /* 0x4B800000: 0x1p+24f, the
        fraction scale (float-multiplier loader 0x00426F12;
        reviewed spelling in runtime_float_multiplier_426eac.c). */
    open_cfw_bl006_u32 integer_bound; /* 0x42C00001:
        0x1.800002p+6f, the integer bound (float-multiplier loader
        0x00426F38; reviewed spelling in
        runtime_float_multiplier_426eac.c). */
    open_cfw_bl006_u32 rate_floor; /* 0x42700000: 60.0f, the low-rate
        floor (float-encoding-select loader 0x00426F9A; reviewed
        spelling in runtime_float_encoding_select_426f6c.c). */
};

__attribute__((used, section(".rodata.bl006_pool_42714c")))
const struct open_cfw_bl006_pool_42714c open_cfw_bootloader_bl006_pool_42714c = {
    0x427C0001u, 0x00000000u, 0x4B800000u, 0x42C00001u, 0x42700000u
};

/* Pool at 0x00427308: encoding-select/System-PLL bound words
 * between the initialization and deinitialization spans. */
struct __attribute__((packed)) open_cfw_bl006_pool_427308 {
    open_cfw_bl006_u32 high_rate_bound; /* 0x43700000: 240.0f, the
        high-rate bound (float-encoding-select loader 0x00426FF0;
        reviewed spelling in
        runtime_float_encoding_select_426f6c.c). */
    open_cfw_bl006_u32 hz_per_mhz; /* 0x49742400: 1000000.0f, hertz
        per megahertz (System-PLL-minimum-VCO loaders 0x00427054,
        0x00427064, 0x004270F2, 0x00427102; reviewed spelling in
        runtime_syspll_min_fvco_427040.c). */
};

__attribute__((used, section(".rodata.bl006_pool_427308")))
const struct open_cfw_bl006_pool_427308 open_cfw_bootloader_bl006_pool_427308 = {
    0x43700000u, 0x49742400u
};
