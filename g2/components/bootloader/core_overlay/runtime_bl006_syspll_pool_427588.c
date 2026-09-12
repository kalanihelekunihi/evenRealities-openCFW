/* SPDX-License-Identifier: MIT */
/* Clean-room in-place data: the System-PLL literal pool at
 * 0x00427588..0x004275C4 and the range-error cell word at
 * 0x004275E4..0x004275E8.
 *
 * The pool follows the replaced System-PLL lock-wait tail (the stock
 * body ends with `bl 0x0041D246; pop {r1, pc}` at 0x00427582/
 * 0x00427586) and precedes the two range-error setter prologues at
 * 0x004275C4/0x004275D2. Every slot below names its reviewed
 * spelling:
 *
 * - 0x00989680 (10000000U) and 0x000F4240 (1000000U) are the
 *   megahertz scaling constants spelled in
 *   runtime_syspll_min_fvco_427040.c (`reference_hz / 10000000U`,
 *   `(float)output_hz / 1000000.0f`, `fraction_mode == 0U ?
 *   10000000U : 1000000U`), with 1000000U also spelled in
 *   runtime_syspll_postdiv_427160.c (`reference_hz / 1000000U`,
 *   `output_mhz /= 1000000U`).
 * - 0x03938700 (60000000U) is the low minimum-VCO bound
 *   spelled in runtime_syspll_postdiv_427160.c (the first
 *   `open_cfw_bootloader_syspll_min_fvco_427040` call).
 * - 0x00431E70 is the post-divider table base spelled in
 *   runtime_syspll_min_fvco_427040.c (`OPEN_CFW_SYSPLL_POSTDIV_TABLE`
 *   as 0x00431E70U).
 * - 0x0E4E1C00 (240000000U) is the minimum-VCO bound spelled in
 *   runtime_syspll_postdiv_427160.c (the `240000000U` argument
 *   forwarded to the min-FVCO service).
 * - 0x00433CC8/0x00433CB8 are the PTS_B/PTS_A tables spelled in
 *   runtime_syspll_postdiv_427160.c (`OPEN_CFW_SYSPLL_PTS_B` as
 *   0x00433CC8U, `OPEN_CFW_SYSPLL_PTS_A` as 0x00433CB8U).
 * - 0x20027010 is the SYSPLL state-array literal documented in
 *   docs/research/g2-bootloader-syspll-initialize-4272ac-source-closure.md.
 * - 0x00504C30 is the handle-magic literal documented in the same
 *   closure; 0x01504C30 is the tagged-handle magic documented in
 *   docs/research/g2-bootloader-syspll-lock-wait-427522-source-closure.md.
 * - 0x40020060 is the VRCTRL register spelled in
 *   runtime_syspll_enable_427360.c (`OPEN_CFW_SYSPLL_ENABLE_VRCTRL`
 *   as 0x40020060U).
 * - 0x400204D8/0x400204DC/0x400204E0/0x400204E4 are PLLCTL0/PLLDIV0/
 *   PLLDIV1/PLLSTAT spelled in runtime_syspll_configure_42740c.c and
 *   runtime_syspll_lock_wait_427522.c.
 *
 * Loader PCs were verified by bounded Capstone decode of the routed
 * spans (see docs/research/g2-bootloader-bl006-cluster-427588-
 * syspll-pool-source-closure.md): every loader sits in a replaced
 * stock span whose shipped replacement carries only
 * R_ARM_THM_CALL relocations (stale by construction), or in an
 * explicitly listed retained dead span. No loader sits in any
 * byte-exact shipped body. A whole-image linear sweep misses
 * 32-bit `ldr.w` loaders through desync, so every span is decoded
 * anchored at its own start with operand-based literal-target
 * recovery.
 *
 * The word at 0x004275E4 (0x20027194) is the range-error status
 * cell: the stock setter tails at 0x004275C4/0x004275D2 load it and
 * publish 0x21/0x22 to it on the double-ldexp range-error paths
 * (see runtime_double_range_error_4275d2.c). It is reproduced here
 * as a named layout word, not as claimed live traffic.
 */

typedef __UINT32_TYPE__ open_cfw_bl006_u32;

/* Pool at 0x00427588: System-PLL scaling constants, table
 * pointers, register addresses, and one reserved word. */
struct __attribute__((packed)) open_cfw_bl006_pool_427588 {
    open_cfw_bl006_u32 ten_mhz; /* 0x00989680: 10000000U
        megahertz scaling (reviewed
        runtime_syspll_min_fvco_427040.c). */
    open_cfw_bl006_u32 postdiv_table; /* 0x00431E70:
        post-divider table base (reviewed
        runtime_syspll_min_fvco_427040.c
        OPEN_CFW_SYSPLL_POSTDIV_TABLE). */
    open_cfw_bl006_u32 one_mhz; /* 0x000F4240: 1000000U
        megahertz scaling (reviewed
        runtime_syspll_min_fvco_427040.c,
        runtime_syspll_postdiv_427160.c). */
    open_cfw_bl006_u32 low_min_vco_hz; /* 0x03938700:
        60000000U low minimum-VCO bound (reviewed
        runtime_syspll_postdiv_427160.c). */
    open_cfw_bl006_u32 max_vco_hz; /* 0x0E4E1C00:
        240000000U minimum-VCO bound (reviewed
        runtime_syspll_postdiv_427160.c). */
    open_cfw_bl006_u32 pts_b_table; /* 0x00433CC8: PTS_B
        table (reviewed runtime_syspll_postdiv_427160.c
        OPEN_CFW_SYSPLL_PTS_B). */
    open_cfw_bl006_u32 pts_a_table; /* 0x00433CB8: PTS_A
        table (reviewed runtime_syspll_postdiv_427160.c
        OPEN_CFW_SYSPLL_PTS_A). */
    open_cfw_bl006_u32 state_array; /* 0x20027010: SYSPLL
        state-array literal (reviewed
        g2-bootloader-syspll-initialize-4272ac-source-closure.md). */
    open_cfw_bl006_u32 handle_magic; /* 0x00504C30:
        handle magic (reviewed
        g2-bootloader-syspll-initialize-4272ac-source-closure.md). */
    open_cfw_bl006_u32 handle_magic_tagged; /* 0x01504C30:
        tagged-handle magic (reviewed
        g2-bootloader-syspll-lock-wait-427522-source-closure.md). */
    open_cfw_bl006_u32 vrctrl; /* 0x40020060: VRCTRL
        register (reviewed runtime_syspll_enable_427360.c
        OPEN_CFW_SYSPLL_ENABLE_VRCTRL). */
    open_cfw_bl006_u32 pllctl0; /* 0x400204D8: PLLCTL0
        register (reviewed runtime_syspll_configure_42740c.c,
        runtime_syspll_lock_wait_427522.c). */
    open_cfw_bl006_u32 plldiv0; /* 0x400204DC: PLLDIV0
        register (reviewed
        runtime_syspll_configure_42740c.c
        OPEN_CFW_SYSPLL_CONFIGURE_PLLDIV0). */
    open_cfw_bl006_u32 plldiv1; /* 0x400204E0: PLLDIV1
        register (reviewed runtime_syspll_configure_42740c.c,
        runtime_syspll_lock_wait_427522.c). */
    open_cfw_bl006_u32 pllstat; /* 0x400204E4: PLLSTAT
        register (reviewed
        runtime_syspll_lock_wait_427522.c
        OPEN_CFW_SYSPLL_LOCK_WAIT_PLLSTAT_ADDRESS). */
};

__attribute__((used, section(".rodata.bl006_pool_427588")))
const struct open_cfw_bl006_pool_427588 open_cfw_bootloader_bl006_pool_427588 = {
    10000000u, 0x00431E70u, 1000000u, 60000000u, 240000000u,
    0x00433CC8u, 0x00433CB8u, 0x20027010u, 0x00504C30u, 0x01504C30u,
    0x40020060u, 0x400204D8u, 0x400204DCu, 0x400204E0u, 0x400204E4u
};

/* Word at 0x004275E4: the range-error status cell published by the
 * 0x004275C4/0x004275D2 setter tails (see
 * runtime_double_range_error_4275d2.c). */
struct __attribute__((packed)) open_cfw_bl006_word_4275e4 {
    open_cfw_bl006_u32 range_error_cell; /* 0x20027194. */
};

__attribute__((used, section(".rodata.bl006_word_4275e4")))
const struct open_cfw_bl006_word_4275e4 open_cfw_bootloader_bl006_word_4275e4 = {
    0x20027194u
};
