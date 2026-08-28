/* SPDX-License-Identifier: MIT */

typedef __UINTPTR_TYPE__ open_cfw_bootloader_word;

#ifndef OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT
extern open_cfw_bootloader_word open_cfw_bootloader_critical_context(void);
#define OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() \
    open_cfw_bootloader_critical_context()
#endif

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_SUBMIT_41937C
extern open_cfw_bootloader_word open_cfw_bootloader_runtime_submit_41937c(
    open_cfw_bootloader_word owner,
    open_cfw_bootloader_word kind,
    open_cfw_bootloader_word argument,
    open_cfw_bootloader_word option,
    open_cfw_bootloader_word reserved
);
#define OPEN_CFW_BOOTLOADER_RUNTIME_SUBMIT_41937C( \
    owner, kind, argument, option, reserved) \
    open_cfw_bootloader_runtime_submit_41937c( \
        owner, kind, argument, option, reserved)
#endif

__attribute__((used, noinline))
int open_cfw_bootloader_runtime_submit_41649a(
    open_cfw_bootloader_word owner,
    open_cfw_bootloader_word argument
)
{
    open_cfw_bootloader_word result;

    if (OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() != 0U) {
        return -6;
    }
    if (owner == 0U || argument == 0U) {
        return -4;
    }

    result = OPEN_CFW_BOOTLOADER_RUNTIME_SUBMIT_41937C(
        owner,
        4U,
        argument,
        0U,
        0U
    );
    return result == 1U ? 0 : -3;
}
