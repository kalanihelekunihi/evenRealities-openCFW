/* SPDX-License-Identifier: GPL-3.0-or-later */

typedef __UINTPTR_TYPE__ open_cfw_bootloader_word;

#ifndef OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT
extern open_cfw_bootloader_word open_cfw_bootloader_critical_context(void);
#define OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() \
    open_cfw_bootloader_critical_context()
#endif

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_FLAGS_SET_ISR_419BD2
extern open_cfw_bootloader_word open_cfw_bootloader_runtime_flags_set_isr_419bd2(
    open_cfw_bootloader_word object,
    open_cfw_bootloader_word flags,
    open_cfw_bootloader_word *wake_required
);
#define OPEN_CFW_BOOTLOADER_RUNTIME_FLAGS_SET_ISR_419BD2( \
    object, flags, wake_required) \
    open_cfw_bootloader_runtime_flags_set_isr_419bd2( \
        object, flags, wake_required)
#endif

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_FLAGS_GET_ISR_419AF4
extern open_cfw_bootloader_word open_cfw_bootloader_runtime_flags_get_isr_419af4(
    open_cfw_bootloader_word object
);
#define OPEN_CFW_BOOTLOADER_RUNTIME_FLAGS_GET_ISR_419AF4(object) \
    open_cfw_bootloader_runtime_flags_get_isr_419af4(object)
#endif

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_FLAGS_SET_TASK_419B06
extern open_cfw_bootloader_word open_cfw_bootloader_runtime_flags_set_task_419b06(
    open_cfw_bootloader_word object,
    open_cfw_bootloader_word flags
);
#define OPEN_CFW_BOOTLOADER_RUNTIME_FLAGS_SET_TASK_419B06(object, flags) \
    open_cfw_bootloader_runtime_flags_set_task_419b06(object, flags)
#endif

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_REQUEST_PENDSV
#define OPEN_CFW_BOOTLOADER_RUNTIME_REQUEST_PENDSV() \
    (*(volatile open_cfw_bootloader_word *)0xE000ED04U = 0x10000000U)
#endif

__attribute__((used, noinline))
open_cfw_bootloader_word open_cfw_bootloader_runtime_flags_set_41652e(
    open_cfw_bootloader_word object,
    open_cfw_bootloader_word flags
)
{
    open_cfw_bootloader_word wake_required = 0U;
    open_cfw_bootloader_word result;

    if (object == 0U || (flags & 0xFF000000U) != 0U) {
        return ~(open_cfw_bootloader_word)3U;
    }

    if (OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() == 0U) {
        return OPEN_CFW_BOOTLOADER_RUNTIME_FLAGS_SET_TASK_419B06(object, flags);
    }

    if (OPEN_CFW_BOOTLOADER_RUNTIME_FLAGS_SET_ISR_419BD2(
            object, flags, &wake_required) == 0U) {
        return ~(open_cfw_bootloader_word)2U;
    }
    result = flags | OPEN_CFW_BOOTLOADER_RUNTIME_FLAGS_GET_ISR_419AF4(object);
    if (wake_required != 0U) {
        OPEN_CFW_BOOTLOADER_RUNTIME_REQUEST_PENDSV();
    }
    return result;
}
