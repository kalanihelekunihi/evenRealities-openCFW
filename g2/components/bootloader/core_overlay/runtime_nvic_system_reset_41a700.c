/*
 * Copyright (c) 2026, openCFW contributors
 * SPDX-License-Identifier: MIT
 *
 * Clean-room reconstruction of two tiny, independently callable Even
 * Realities G2 S200 bootloader leaves that request a system reset.
 *
 * `open_cfw_bootloader_nvic_system_reset_41a700` reproduces the stock body
 * at `[0x0041A700,0x0041A71E)`: a DSB, a read-modify-write of SCB->AIRCR that
 * preserves the PRIGROUP field while writing VECTKEY 0x5FA and SYSRESETREQ,
 * a second DSB, and an infinite NOP spin while the reset takes effect.  This
 * is the architectural Cortex-M "request a system reset" sequence described
 * for AIRCR in the ARMv8-M Architecture Reference Manual and is structurally
 * identical to the well-known CMSIS-Core `NVIC_SystemReset()` helper shipped
 * with every Cortex-M CMSIS-Core package (including the vendored
 * `g2/third_party/ambiqsuite-apollo510/CMSIS` snapshot).  It is written here
 * independently from the public architecture description of AIRCR, not
 * copied from any vendor source file, so it carries no vendor license.
 *
 * `open_cfw_bootloader_reset_now_41ac8a` reproduces the stock body at
 * `[0x0041AC8A,0x0041AC92)`: a trivial wrapper that calls the reset entry
 * above and formally returns (unreachable in practice, matching stock,
 * which also emits a normal epilogue after its call).
 *
 * See docs/research/g2-bootloader-nvic-system-reset-41a700-source-closure.md
 * for the authenticated stock boundaries and caller census.
 */

typedef unsigned int open_cfw_bootloader_reset_u32;
typedef __UINTPTR_TYPE__ open_cfw_bootloader_reset_uintptr;

enum {
    OPEN_CFW_BOOTLOADER_SCB_AIRCR_ADDRESS = 0xE000ED0CU,
    OPEN_CFW_BOOTLOADER_SCB_AIRCR_PRIGROUP_MASK = 0x00000700U,
    OPEN_CFW_BOOTLOADER_SCB_AIRCR_RESET_REQUEST = 0x05FA0004U
};

__attribute__((used, noinline))
void open_cfw_bootloader_nvic_system_reset_41a700(void)
{
    volatile open_cfw_bootloader_reset_u32 *const aircr =
        (volatile open_cfw_bootloader_reset_u32 *)
            (open_cfw_bootloader_reset_uintptr)
                OPEN_CFW_BOOTLOADER_SCB_AIRCR_ADDRESS;
    open_cfw_bootloader_reset_u32 value;

    __asm__ volatile ("dsb sy" ::: "memory");
    value = *aircr;
    value &= OPEN_CFW_BOOTLOADER_SCB_AIRCR_PRIGROUP_MASK;
    value |= OPEN_CFW_BOOTLOADER_SCB_AIRCR_RESET_REQUEST;
    *aircr = value;
    __asm__ volatile ("dsb sy" ::: "memory");

    for (;;) {
        __asm__ volatile ("nop");
    }
}

__attribute__((used, noinline))
void open_cfw_bootloader_reset_now_41ac8a(void)
{
    open_cfw_bootloader_nvic_system_reset_41a700();
}
