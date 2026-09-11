/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room realization of thirteen authenticated Apollo510 SPOT-manager
 * shared-literal pools retained between [0x0042A078,0x0042B6B8). Each pool
 * is the constant data that the already source-owned SPOT-manager leaves in
 * this file (runtime_spotmgr_*.c) reach with `ldr rX, [pc, #imm]`; the pools
 * themselves were left as untouched stock bytes because no prior admission
 * covered the gaps between adjacent function bodies. This file gives every
 * word an identified role and places it back at its authenticated address so
 * nothing in the bootloader still depends on unexplained retained bytes.
 *
 * Every four-byte word is decoded against the vendored Apollo510 CMSIS
 * register map (third_party/ambiqsuite-apollo510/CMSIS/AmbiqMicro/Include/
 * apollo510.h, offsets verified with offsetof()), against the ARMv8.1-M
 * SCB->CCR system-control-register address, and against the SRAM state
 * names already established by the sibling closure documents in
 * docs/research/g2-bootloader-spotmgr-*.md (cited per pool below). A few
 * SRAM cells and one packed configuration word are consumed by state
 * machines documented in those files without an independently re-derived
 * bit-level breakdown; those are called out explicitly rather than claimed
 * as fully understood register fields.
 *
 * Two-byte 0x0000 halfwords preceding a pool are the authenticated Thumb
 * alignment padding the compiler leaves before a word-aligned literal pool;
 * they carry no data of their own.
 */

typedef __UINT32_TYPE__ open_cfw_spotmgr_literal_u32;

#if defined(__arm__) || defined(__thumb__)

/*
 * Gap between the SPOT-manager Ton-trim selector's fixed-address callers
 * and the SIMOBUCK deep-sleep classifier. See
 * docs/research/g2-bootloader-spotmgr-buck-deepsleep-42a08c-source-closure.md
 * and runtime_dual_switch_426c8c.c for the first cell.
 */
__attribute__((used, noinline, naked, visibility("default")))
void open_cfw_bootloader_spotmgr_shared_literals_42a078(void)
{
    __asm volatile(
        ".word 0x40004030\n" /* CLKGEN CLOCKENSTAT; polled as the dual-switch
                                 status pointer in runtime_dual_switch_426c8c.c */
        ".word 0x200270b4\n" /* SPOT-manager "new VDDF trim" SRAM cell, named
                                 in g2-bootloader-spotmgr-transition-428378 */
        ".word 0x40020048\n" /* MCUCTRL VREFGEN3 */
        ".word 0x20026ba0\n" /* SPOT-manager factory-trim table base (SRAM),
                                 named in runtime_spotmgr_factory_trims_429da4.c */
        ".word 0x400083e0\n" /* TIMER CTRL15 */
    );
}

/*
 * Gap immediately before the SPOT-manager internal-domain marker.
 */
__attribute__((used, noinline, naked, visibility("default")))
void open_cfw_bootloader_spotmgr_shared_literals_42a1b2(void)
{
    __asm volatile(
        ".short 0x0000\n"    /* alignment */
        ".word 0x40008064\n" /* TIMER INTSTAT */
        ".word 0x200270c0\n" /* SPOT-manager trim/state SRAM cell adjacent to
                                 the core-LDO trim cluster (see 0x42a2a4 pool) */
    );
}

/*
 * Gap between the Ton-trim selector and the state-transition sequence
 * selector: the four-cell core-LDO/VDDC trim cluster named in
 * docs/research/g2-bootloader-spotmgr-transition-428378-source-closure.md.
 */
__attribute__((used, noinline, naked, visibility("default")))
void open_cfw_bootloader_spotmgr_shared_literals_42a2a4(void)
{
    __asm volatile(
        ".word 0x200270c4\n" /* SPOT-manager trim/state SRAM cell adjacent to
                                 the named VDDC/VDDF/core-LDO trim cluster */
        ".word 0x200270b8\n" /* "core-LDO active trim" */
        ".word 0x200270bc\n" /* "core-LDO temperature trim" */
        ".word 0x200270b0\n" /* "new VDDC trim" */
    );
}

/*
 * Gap between the trim router and the power-state classifier.
 */
__attribute__((used, noinline, naked, visibility("default")))
void open_cfw_bootloader_spotmgr_shared_literals_42a546(void)
{
    __asm volatile(
        ".short 0x0000\n"    /* alignment */
        ".word 0x40020080\n" /* MCUCTRL LDOREG1 */
        ".word 0x200271bc\n" /* SPOT-manager "ready byte", named in
                                 runtime_spotmgr_factory_trims_429da4.c */
    );
}

/*
 * Gap before the power-state stimulus update entry: the ARM core-control
 * register and the five MMIO cells the transition_7b/factory-trim leaves
 * document explicitly by address.
 */
__attribute__((used, noinline, naked, visibility("default")))
void open_cfw_bootloader_spotmgr_shared_literals_42a85e(void)
{
    __asm volatile(
        ".short 0x0000\n"    /* alignment */
        ".word 0xe000ed14\n" /* ARMv8.1-M SCB->CCR (Configuration and
                                 Control Register) */
        ".word 0x4002037c\n" /* "PWRSW0", named in
                                 g2-bootloader-spotmgr-transition-428378 */
        ".word 0x20000150\n" /* SPOT-manager "trim index" SRAM cell */
        ".word 0x40020044\n" /* MCUCTRL VREFGEN2 */
        ".word 0x4002004c\n" /* MCUCTRL VREFGEN4 */
        ".word 0x400204d8\n" /* MCUCTRL PLLCTL0 (SYSPLL control), matches
                                 runtime_syspll_configure_42740c.c */
    );
}

/*
 * Gap between the power-state stimulus update and profile-apply entries:
 * the three STIMER/TIMER cells the deep-sleep scan closure names.
 */
__attribute__((used, noinline, naked, visibility("default")))
void open_cfw_bootloader_spotmgr_shared_literals_42ab6e(void)
{
    __asm volatile(
        ".short 0x0000\n"    /* alignment */
        ".word 0x40008800\n" /* STIMER_BASE ("STIMER configuration") */
        ".word 0x40008000\n" /* TIMER CTRL, timer instance base */
        ".word 0x40008010\n" /* TIMER GLOBEN, timer global enable */
    );
}

/*
 * Gap between the profile-apply and initialization entries.
 */
__attribute__((used, noinline, naked, visibility("default")))
void open_cfw_bootloader_spotmgr_shared_literals_42abb2(void)
{
    __asm volatile(
        ".short 0x0000\n"    /* alignment */
        ".word 0x2000055a\n" /* SPOT-manager "ongoing-sequence byte" */
        ".word 0x200271c0\n" /* SPOT-manager "result byte" (deep-sleep scan) */
    );
}

/*
 * Gap between the initialization and temperature-monitor entries.
 */
__attribute__((used, noinline, naked, visibility("default")))
void open_cfw_bootloader_spotmgr_shared_literals_42ac4e(void)
{
    __asm volatile(
        ".short 0x0000\n"    /* alignment */
        ".word 0x20026ba0\n" /* SPOT-manager factory-trim table base (SRAM) */
    );
}

/*
 * Four-byte literal/alignment gap before the second SPOT-manager deep-sleep
 * eligibility scan: the -273.0f temperature-classifier lower bound, one of
 * the five bounds named in
 * g2-bootloader-spotmgr-temperature-range-42ad40-source-closure.md.
 */
__attribute__((used, noinline, naked, visibility("default")))
void open_cfw_bootloader_spotmgr_shared_literals_42aeec(void)
{
    __asm volatile(".word 0xc3888000\n" /* float -273.0f */);
}

/*
 * Four-byte gap before the state-transition side-effect leaf: the 50.0f
 * temperature-classifier bound.
 */
__attribute__((used, noinline, naked, visibility("default")))
void open_cfw_bootloader_spotmgr_shared_literals_42b010(void)
{
    __asm volatile(".word 0x42480000\n" /* float 50.0f */);
}

/*
 * Four-byte gap before the power-transition trim transaction: the 1000.0f
 * temperature-classifier bound.
 */
__attribute__((used, noinline, naked, visibility("default")))
void open_cfw_bootloader_spotmgr_shared_literals_42b068(void)
{
    __asm volatile(".word 0x447a0000\n" /* float 1000.0f */);
}

/*
 * Twenty-eight-byte gap before the hardware-state decoder: MCUCTRL/SRAM
 * cells already named by the memory-select and trim closures, plus two
 * further MCUCTRL registers and one SPOT-manager SRAM cell.
 */
__attribute__((used, noinline, naked, visibility("default")))
void open_cfw_bootloader_spotmgr_shared_literals_42b69c(void)
{
    __asm volatile(
        ".word 0x400201b0\n" /* MCUCTRL product-specific register outside the
                                 public CMSIS map; same cluster as
                                 OPEN_CFW_MEMORY_SELECT_CONTROL in
                                 runtime_memory_select_copy_4213e6.c */
        ".word 0x40020088\n" /* MCUCTRL LDOREG2 */
        ".word 0x20026ba0\n" /* SPOT-manager factory-trim table base (SRAM) */
        ".word 0x40020080\n" /* MCUCTRL LDOREG1 */
        ".word 0x200271ae\n" /* SPOT-manager SRAM cell adjacent to the named
                                 HP-to-deep-sleep flag (0x200271B0) */
        ".word 0x40020044\n" /* MCUCTRL VREFGEN2 */
        ".word 0x200270a8\n" /* SPOT-manager SRAM cell adjacent to the named
                                 VDDC/VDDF trim cluster */
    );
}

#else

/* Host builds have no PC-relative literal pool to place; nothing to model. */
typedef open_cfw_spotmgr_literal_u32 open_cfw_spotmgr_literal_unused;

#endif
