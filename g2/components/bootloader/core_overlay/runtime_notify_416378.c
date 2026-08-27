/* SPDX-License-Identifier: GPL-3.0-or-later */

typedef unsigned int open_cfw_bootloader_u32;

#ifndef OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT
extern open_cfw_bootloader_u32 open_cfw_bootloader_critical_context(void);
#define OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() \
    open_cfw_bootloader_critical_context()
#endif

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_NOTIFY_417FA8
extern void open_cfw_bootloader_runtime_notify_417fa8(
    open_cfw_bootloader_u32 argument
);
#define OPEN_CFW_BOOTLOADER_RUNTIME_NOTIFY_417FA8(argument) \
    open_cfw_bootloader_runtime_notify_417fa8(argument)
#endif

__attribute__((used, noinline))
int open_cfw_bootloader_runtime_notify_416378(open_cfw_bootloader_u32 argument)
{
    if (OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() != 0U) {
        return -6;
    }
    if (argument != 0U) {
        OPEN_CFW_BOOTLOADER_RUNTIME_NOTIFY_417FA8(argument);
    }
    return 0;
}
