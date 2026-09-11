/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room reconstruction of the authenticated G2 bootloader
 * master-interrupt-enable primitive at 0x0041B8E0. This is a G2-specific
 * compiled leaf; no upstream identity is claimed even though the observed
 * behavior matches the common Cortex-M "read PRIMASK, then CPSIE" idiom.
 *
 * The sole stock caller, the MSPI low-level initializer at 0x00420254, holds
 * this entry's absolute address as a literal function-pointer constant
 * (0x0041B8E1) rather than a linked symbol, so this leaf's production route
 * is the in-place byte replacement at its original address; no caller-side
 * change is required.
 */

#ifndef OPEN_CFW_BOOTLOADER_READ_PRIMASK_MIE
static __attribute__((always_inline)) inline unsigned int
open_cfw_bootloader_read_primask_mie(void)
{
    unsigned int value;

    __asm__ volatile ("mrs %0, primask" : "=r" (value));
    return value;
}
#define OPEN_CFW_BOOTLOADER_READ_PRIMASK_MIE() open_cfw_bootloader_read_primask_mie()
#endif

#ifndef OPEN_CFW_BOOTLOADER_CPSIE_MIE
static __attribute__((always_inline)) inline void
open_cfw_bootloader_cpsie_mie(void)
{
    __asm__ volatile ("cpsie i" ::: "memory");
}
#define OPEN_CFW_BOOTLOADER_CPSIE_MIE() open_cfw_bootloader_cpsie_mie()
#endif

__attribute__((used, noinline))
unsigned int open_cfw_bootloader_master_interrupt_enable_41b8e0(void)
{
    unsigned int primask = OPEN_CFW_BOOTLOADER_READ_PRIMASK_MIE();

    OPEN_CFW_BOOTLOADER_CPSIE_MIE();
    return primask;
}
