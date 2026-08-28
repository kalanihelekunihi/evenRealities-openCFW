/* SPDX-License-Identifier: MIT */

typedef unsigned int open_cfw_bootloader_u32;

#ifndef OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT
extern open_cfw_bootloader_u32 open_cfw_bootloader_critical_context(void);
#define OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() \
    open_cfw_bootloader_critical_context()
#endif

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_PREDICATE_417FE4
extern open_cfw_bootloader_u32 open_cfw_bootloader_runtime_predicate_417fe4(
    open_cfw_bootloader_u32 argument_0
);
#define OPEN_CFW_BOOTLOADER_RUNTIME_PREDICATE_417FE4(argument_0) \
    open_cfw_bootloader_runtime_predicate_417fe4(argument_0)
#endif

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_ACTION_417F0A
extern void open_cfw_bootloader_runtime_action_417f0a(
    open_cfw_bootloader_u32 argument_0
);
#define OPEN_CFW_BOOTLOADER_RUNTIME_ACTION_417F0A(argument_0) \
    open_cfw_bootloader_runtime_action_417f0a(argument_0)
#endif

__attribute__((used, noinline))
int open_cfw_bootloader_runtime_action_416200(
    open_cfw_bootloader_u32 argument_0
)
{
    if (OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() != 0U) {
        return -6;
    }
    if (argument_0 == 0U) {
        return -4;
    }
    if ((unsigned char)OPEN_CFW_BOOTLOADER_RUNTIME_PREDICATE_417FE4(
            argument_0
        ) == 4U) {
        return -3;
    }

    OPEN_CFW_BOOTLOADER_RUNTIME_ACTION_417F0A(argument_0);
    return 0;
}
