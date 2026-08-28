/* SPDX-License-Identifier: MIT */

#ifndef OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT
extern unsigned int open_cfw_bootloader_critical_context(void);
#define OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() \
    open_cfw_bootloader_critical_context()
#endif

#ifndef OPEN_CFW_BOOTLOADER_NORMAL_CONTEXT_VALUE
extern unsigned int open_cfw_bootloader_normal_context_value(void);
#define OPEN_CFW_BOOTLOADER_NORMAL_CONTEXT_VALUE() \
    open_cfw_bootloader_normal_context_value()
#endif

#ifndef OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT_VALUE
extern unsigned int open_cfw_bootloader_critical_context_value(void);
#define OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT_VALUE() \
    open_cfw_bootloader_critical_context_value()
#endif

__attribute__((used, noinline))
unsigned int open_cfw_bootloader_context_value(void)
{
    if (OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() != 0U) {
        return OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT_VALUE();
    }
    return OPEN_CFW_BOOTLOADER_NORMAL_CONTEXT_VALUE();
}
