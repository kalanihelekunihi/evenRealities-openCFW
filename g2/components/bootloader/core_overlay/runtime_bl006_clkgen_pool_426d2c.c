/* SPDX-License-Identifier: MIT */
/* Clean-room in-place data: the CLKGEN register-address literal pool
 * at 0x00426D2C..0x00426D48.
 *
 * One alignment word plus six CLKGEN block (0x400040xx) register
 * addresses. Every word's value is named by an already-reviewed
 * consumer source; stock loader PCs (bounded Capstone decode of the
 * authenticated image) sit only inside spans the shipped image
 * overwrites (entry-redirect spans) or inside functionally replaced
 * bodies that carry their own embedded copies (the shipped HFADJ
 * enable leaf embeds 0x40004044 as a body literal; the shipped
 * dual-switch leaf has only a CALL relocation, so its register
 * references are likewise body-internal). No byte-exact shipped body
 * loads any slot, so this pool is admitted as an authenticated layout
 * reproduction with reviewed meanings, not as address-live traffic;
 * see docs/research/g2-bootloader-bl006-cluster-426d2c-427754-source-closure.md.
 */

typedef __UINT32_TYPE__ open_cfw_bl006_u32;

/* Pool at 0x00426D2C: alignment fill plus the six CLKGEN register
 * addresses shared by the HFADJ/config/disable/dual-switch services. */
struct __attribute__((packed)) open_cfw_bl006_pool_426d2c {
    open_cfw_bl006_u32 align_fill; /* 0x00000000: pool alignment (the
        CLKGEN disable redirect span ends 0x00426D2C) */
    open_cfw_bl006_u32 hfadj_control; /* 0x40004044: HFADJ control
        register (reviewed hfadj-enable source names it as the
        bit-0 control register; reviewed dual-switch source names it
        as the clock-status register; stock loaders 0x00426C64 in
        the replaced HFADJ enable span and 0x00426C94/0x00426CBE in
        the replaced dual-switch span are stale -- both shipped
        bodies embed their own copies) */
    open_cfw_bl006_u32 clkgen_control; /* 0x40004020: CLKGEN control
        register (reviewed clkgen-config source
        OPEN_CFW_CLKGEN_CONFIG_CONTROL; reviewed hfadj-config and
        hfadj-disable sources; stock loaders 0x00426C76/0x00426C7E
        sit in overwritten redirect spans) */
    open_cfw_bl006_u32 dual_switch_status; /* 0x40004030: dual-clock
        switch status register (reviewed dual-switch source; stock
        loader 0x00426CB4 in the replaced dual-switch span is stale
        -- the shipped leaf has no data relocation) */
    open_cfw_bl006_u32 clkgen_mode; /* 0x4000404C: CLKGEN mode
        register (reviewed clkgen-config source
        OPEN_CFW_CLKGEN_CONFIG_MODE; stock loader 0x00426CD6 sits in
        an overwritten redirect span) */
    open_cfw_bl006_u32 clkgen_divider; /* 0x40004048: CLKGEN divider
        register (reviewed clkgen-config source
        OPEN_CFW_CLKGEN_CONFIG_DIVIDER; stock loaders 0x00426CE6/
        0x00426D1E sit in overwritten redirect spans) */
    open_cfw_bl006_u32 disable_target; /* 0x40004050: register written
        by the reviewed CLKGEN disable service; stock loader
        0x00426CF6 sits in an overwritten redirect span */
};

__attribute__((used, section(".rodata.bl006_pool_426d2c")))
const struct open_cfw_bl006_pool_426d2c open_cfw_bootloader_bl006_pool_426d2c = {
    0x00000000u, 0x40004044u, 0x40004020u, 0x40004030u, 0x4000404Cu,
    0x40004048u, 0x40004050u
};
