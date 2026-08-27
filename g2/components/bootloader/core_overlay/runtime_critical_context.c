/* SPDX-License-Identifier: GPL-3.0-or-later */

#ifndef OPEN_CFW_BOOTLOADER_READ_IPSR
static unsigned int open_cfw_bootloader_read_ipsr(void)
{
    unsigned int value;

    __asm__ volatile ("mrs %0, ipsr" : "=r" (value));
    return value;
}
#define OPEN_CFW_BOOTLOADER_READ_IPSR() open_cfw_bootloader_read_ipsr()
#endif

#ifndef OPEN_CFW_BOOTLOADER_READ_PRIMASK
static unsigned int open_cfw_bootloader_read_primask(void)
{
    unsigned int value;

    __asm__ volatile ("mrs %0, primask" : "=r" (value));
    return value;
}
#define OPEN_CFW_BOOTLOADER_READ_PRIMASK() open_cfw_bootloader_read_primask()
#endif

#ifndef OPEN_CFW_BOOTLOADER_READ_BASEPRI
static unsigned int open_cfw_bootloader_read_basepri(void)
{
    unsigned int value;

    __asm__ volatile ("mrs %0, basepri" : "=r" (value));
    return value;
}
#define OPEN_CFW_BOOTLOADER_READ_BASEPRI() open_cfw_bootloader_read_basepri()
#endif

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_STATE
extern unsigned int open_cfw_bootloader_runtime_state_query(void);
#define OPEN_CFW_BOOTLOADER_RUNTIME_STATE() \
    open_cfw_bootloader_runtime_state_query()
#endif

__attribute__((used, noinline))
unsigned int open_cfw_bootloader_critical_context(void)
{
    if (OPEN_CFW_BOOTLOADER_READ_IPSR() != 0U) {
        return 1U;
    }
    if (OPEN_CFW_BOOTLOADER_RUNTIME_STATE() == 1U) {
        return 0U;
    }
    if (OPEN_CFW_BOOTLOADER_READ_PRIMASK() != 0U) {
        return 1U;
    }
    return OPEN_CFW_BOOTLOADER_READ_BASEPRI() != 0U ? 1U : 0U;
}
