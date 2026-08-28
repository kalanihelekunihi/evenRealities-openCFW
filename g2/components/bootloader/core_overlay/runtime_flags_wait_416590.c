/* SPDX-License-Identifier: MIT */

typedef __UINTPTR_TYPE__ open_cfw_bootloader_word;

#ifndef OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT
extern open_cfw_bootloader_word open_cfw_bootloader_critical_context(void);
#define OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() \
    open_cfw_bootloader_critical_context()
#endif

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_FLAGS_WAIT_4199DC
extern open_cfw_bootloader_word open_cfw_bootloader_runtime_flags_wait_4199dc(
    open_cfw_bootloader_word object,
    open_cfw_bootloader_word flags,
    open_cfw_bootloader_word clear_on_exit,
    open_cfw_bootloader_word wait_all,
    open_cfw_bootloader_word timeout
);
#define OPEN_CFW_BOOTLOADER_RUNTIME_FLAGS_WAIT_4199DC( \
    object, flags, clear_on_exit, wait_all, timeout) \
    open_cfw_bootloader_runtime_flags_wait_4199dc( \
        object, flags, clear_on_exit, wait_all, timeout)
#endif

__attribute__((used, noinline))
open_cfw_bootloader_word open_cfw_bootloader_runtime_flags_wait_416590(
    open_cfw_bootloader_word object,
    open_cfw_bootloader_word flags,
    open_cfw_bootloader_word options,
    open_cfw_bootloader_word timeout
)
{
    open_cfw_bootloader_word result;
    open_cfw_bootloader_word wait_all;
    open_cfw_bootloader_word clear_on_exit;
    open_cfw_bootloader_word satisfied;

    if (object == 0U || (flags & 0xFF000000U) != 0U) {
        return ~(open_cfw_bootloader_word)3U;
    }
    if (OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() != 0U) {
        return timeout == 0U
            ? ~(open_cfw_bootloader_word)5U
            : ~(open_cfw_bootloader_word)3U;
    }

    wait_all = (options & 1U) != 0U ? 1U : 0U;
    clear_on_exit = (options & 2U) != 0U ? 0U : 1U;
    result = OPEN_CFW_BOOTLOADER_RUNTIME_FLAGS_WAIT_4199DC(
        object,
        flags,
        clear_on_exit,
        wait_all,
        timeout
    );
    if (wait_all != 0U) {
        satisfied = (result & flags) == flags ? 1U : 0U;
    } else {
        satisfied = (result & flags) != 0U ? 1U : 0U;
    }
    if (satisfied != 0U) {
        return result;
    }
    return timeout != 0U
        ? ~(open_cfw_bootloader_word)1U
        : ~(open_cfw_bootloader_word)2U;
}
