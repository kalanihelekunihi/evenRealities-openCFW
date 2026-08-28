/* SPDX-License-Identifier: MIT */

typedef unsigned int open_cfw_bootloader_u32;

#ifndef OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT
extern open_cfw_bootloader_u32 open_cfw_bootloader_critical_context(void);
#define OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() \
    open_cfw_bootloader_critical_context()
#endif

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_CALL_41806E
extern void open_cfw_bootloader_runtime_call_41806e(
    open_cfw_bootloader_u32 argument_0,
    open_cfw_bootloader_u32 argument_1
);
#define OPEN_CFW_BOOTLOADER_RUNTIME_CALL_41806E(...) \
    open_cfw_bootloader_runtime_call_41806e(__VA_ARGS__)
#endif

__attribute__((used, noinline))
int open_cfw_bootloader_runtime_call_4161ce(
    open_cfw_bootloader_u32 argument_0,
    open_cfw_bootloader_u32 argument_1
)
{
    if (OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() != 0U) {
        return -6;
    }
    if (argument_0 == 0U || argument_1 == 0U || argument_1 >= 0x39U) {
        return -4;
    }

    OPEN_CFW_BOOTLOADER_RUNTIME_CALL_41806E(argument_0, argument_1);
    return 0;
}
