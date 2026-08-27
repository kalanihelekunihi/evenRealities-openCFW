/* SPDX-License-Identifier: GPL-3.0-or-later */

typedef __UINTPTR_TYPE__ open_cfw_bootloader_word;

#ifndef OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT
extern open_cfw_bootloader_word open_cfw_bootloader_critical_context(void);
#define OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() \
    open_cfw_bootloader_critical_context()
#endif

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_HANDLE_ACQUIRE_TAGGED_419E22
extern open_cfw_bootloader_word open_cfw_bootloader_runtime_handle_acquire_tagged_419e22(
    open_cfw_bootloader_word object,
    open_cfw_bootloader_word timeout
);
#define OPEN_CFW_BOOTLOADER_RUNTIME_HANDLE_ACQUIRE_TAGGED_419E22(object, timeout) \
    open_cfw_bootloader_runtime_handle_acquire_tagged_419e22(object, timeout)
#endif

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_HANDLE_ACQUIRE_PLAIN_41A24E
extern open_cfw_bootloader_word open_cfw_bootloader_runtime_handle_acquire_plain_41a24e(
    open_cfw_bootloader_word object,
    open_cfw_bootloader_word timeout
);
#define OPEN_CFW_BOOTLOADER_RUNTIME_HANDLE_ACQUIRE_PLAIN_41A24E(object, timeout) \
    open_cfw_bootloader_runtime_handle_acquire_plain_41a24e(object, timeout)
#endif

__attribute__((used, noinline))
open_cfw_bootloader_word open_cfw_bootloader_runtime_handle_acquire_4166aa(
    open_cfw_bootloader_word tagged_object,
    open_cfw_bootloader_word timeout
)
{
    open_cfw_bootloader_word object = tagged_object & ~(open_cfw_bootloader_word)1U;
    open_cfw_bootloader_word tagged = tagged_object & 1U;
    open_cfw_bootloader_word result;

    if (OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() != 0U) {
        return (open_cfw_bootloader_word)-6;
    }
    if (object == 0U) {
        return (open_cfw_bootloader_word)-4;
    }
    result = tagged != 0U
        ? OPEN_CFW_BOOTLOADER_RUNTIME_HANDLE_ACQUIRE_TAGGED_419E22(object, timeout)
        : OPEN_CFW_BOOTLOADER_RUNTIME_HANDLE_ACQUIRE_PLAIN_41A24E(object, timeout);
    if (result == 1U) {
        return 0U;
    }
    return timeout != 0U
        ? (open_cfw_bootloader_word)-2
        : (open_cfw_bootloader_word)-3;
}
