/* SPDX-License-Identifier: MIT */
/* Clean-room in-place data: the MSPI state-literal island at
 * 0x00424AEA..0x00424AF0 and the MSPI state-literal pool at
 * 0x00424BD4..0x00424BE4.
 *
 * The island pads the replaced MSPI initialize tail (the stock body
 * ends with `pop {r4, r5}; bx lr` at 0x00424AE6/0x00424AE8, so the
 * halfword at 0x00424AEA restores word alignment) and carries the
 * MSPI init state-table base word at 0x00424AEC. That word is live:
 * the byte-exact command-queue initializer loads it at 0x00423F36
 * and the byte-exact command-queue terminator loads it at
 * 0x00423F5C (its source names the load explicitly as
 * "Fixed literal load from 0x00423F5C to 0x00424AEC").
 *
 * The pool follows the replaced MSPI configure tail (stock body ends
 * with `pop {r4, r5, r6}; bx lr` at 0x00424BD0/0x00424BD2, already
 * word-aligned, so no pad is needed). Slots 0x00424BD4 and
 * 0x00424BD8 are live: the byte-exact command-queue pause body loads
 * both (0x00423FBE/0x00423FC4), and the byte-exact DMA-program and
 * high-priority-schedule adapters load the base word (0x00424070,
 * 0x004240DE). Slots 0x00424BDC/0x00424BE0 are layout-preserving:
 * their only stock-decode loaders sit inside the functionally
 * replaced device-configure span, whose shipped replacement carries
 * zero data relocations (constants materialized internally), and
 * 0x00424BE0 has no loader in any routed span at all.
 *
 * Every value below names its reviewed spelling: 0x2001CAA0 is the
 * MSPI init state-table base (`0x2001caa0U + module * 0x8d0U +
 * 0x828U` in runtime_mspi_cq_init_423f28.c); 100000U is the pause
 * poll timeout (`remaining = 100000U` in
 * runtime_mspi_cq_pause_423fb8.c); 0x40060000U is MSPI0_BASE
 * (vendored CMSIS `apollo510.h`, `MSPI0_BASE 0x40060000UL`, and
 * `base = 0x40060000U + instance->module * 0x1000U` in
 * runtime_mspi_cq_pause_423fb8.c); 0x80000013U/0x8000001fU are the
 * pad-configuration words spelled in
 * runtime_mspi_device_configure_424120.c. Loader PCs were verified
 * by bounded Capstone decode of the routed spans; see
 * docs/research/g2-bootloader-bl006-cluster-424aea-424be4-source-closure.md.
 */

typedef __UINT16_TYPE__ open_cfw_bl006_u16;
typedef __UINT32_TYPE__ open_cfw_bl006_u32;

/* Island at 0x00424AEA: alignment pad plus the MSPI init
 * state-table base word. */
struct __attribute__((packed)) open_cfw_bl006_island_424aea {
    open_cfw_bl006_u16 align_pad; /* 0x0000: pads the replaced
        initialize tail (ends 0x00424AEA) so the state-base word is
        word-aligned; no loader. */
    open_cfw_bl006_u32 state_table_base; /* 0x2001CAA0: MSPI init
        state-table base (reviewed
        runtime_mspi_cq_init_423f28.c `0x2001caa0U + module * 0x8d0U
        + 0x828U`; live loaders in byte-exact bodies 0x00423F36 and
        0x00423F5C). */
};

__attribute__((used, section(".rodata.bl006_island_424aea")))
const struct open_cfw_bl006_island_424aea open_cfw_bootloader_bl006_island_424aea = {
    0x0000u, 0x2001CAA0u
};

/* Pool at 0x00424BD4: pause timeout, MSPI register base, and two
 * pad-configuration words following the replaced configure tail. */
struct __attribute__((packed)) open_cfw_bl006_pool_424bd4 {
    open_cfw_bl006_u32 pause_timeout; /* 0x000186A0: 100000U pause
        poll timeout (reviewed runtime_mspi_cq_pause_423fb8.c
        `remaining = 100000U`; live loader in the byte-exact pause
        body at 0x00423FBE). */
    open_cfw_bl006_u32 mspi_base; /* 0x40060000: MSPI0_BASE
        (vendored CMSIS apollo510.h; reviewed
        runtime_mspi_cq_pause_423fb8.c `base = 0x40060000U +
        instance->module * 0x1000U`; live loaders in byte-exact
        bodies 0x00423FC4, 0x00424070, 0x004240DE; one stale loader
        in the replaced configure span at 0x00424B1A, dead by
        construction). */
    open_cfw_bl006_u32 pad_config_a; /* 0x80000013: pad-configuration
        word spelled in the replaced
        runtime_mspi_device_configure_424120.c; stock-decode loaders
        only at 0x004241E0/0x00424228 inside that replaced span,
        whose shipped replacement carries zero data relocations --
        reproduced as a named layout constant, not as claimed live
        data. */
    open_cfw_bl006_u32 pad_config_b; /* 0x8000001F: pad-configuration
        word spelled in the replaced
        runtime_mspi_device_configure_424120.c; no loader in any
        routed span -- reproduced as a named layout constant, not
        as claimed live data. */
};

__attribute__((used, section(".rodata.bl006_pool_424bd4")))
const struct open_cfw_bl006_pool_424bd4 open_cfw_bootloader_bl006_pool_424bd4 = {
    0x000186A0u, 0x40060000u, 0x80000013u, 0x8000001Fu
};
