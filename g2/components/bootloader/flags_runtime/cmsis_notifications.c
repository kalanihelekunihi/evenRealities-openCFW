/* SPDX-License-Identifier: MIT. Readable source for stock 0x41623a/0x4162c4. */
#include "flags_runtime.h"
#include "../../bootloader/thread_creation/thread_notifications.h"
#include <stddef.h>

extern uint32_t opencfw_provider_41602a(void);
extern uint32_t opencfw_boot_tick_get(void);
/* Stock ISR-only path remains an injected provider; it is not needed by the
 * manager task path and is not emulated as a thread-context operation. */
extern void opencfw_boot_isr_thread_notify(uint32_t *thread, uint32_t index,
    uint32_t value, uint32_t action, uint32_t stack_arg4, uint32_t stack_arg5);

uint32_t opencfw_provider_41623a(uint32_t *thread, int32_t flags)
{
    if (thread == NULL || flags < 0)
        return UINT32_C(0xfffffffc);

    uint32_t result = UINT32_MAX;
    if (opencfw_provider_41602a() == 0u) {
        (void)opencfw_boot_thread_notify(thread, 0u, (uint32_t)flags, 1u,
                                         NULL);
        (void)opencfw_boot_thread_notify(thread, 0u, 0u, 0u, &result);
    } else {
        uint32_t transferred = 0u;
        opencfw_boot_isr_thread_notify(thread, 0u, (uint32_t)flags, 1u,
                                       0u, (uint32_t)(uintptr_t)&transferred);
        opencfw_boot_isr_thread_notify(thread, 0u, 0u, 0u,
                                       (uint32_t)(uintptr_t)&result, 0u);
        if (transferred != 0u)
            *(volatile uint32_t *)(uintptr_t)UINT32_C(0xe000ed04) =
                UINT32_C(0x10000000);
    }
    return result;
}

/* Stock returns a 64-bit pair: low word is the flag/status result and high
 * word is the remaining raw timeout. The public manager caller consumes only
 * the low word. */
uint64_t opencfw_provider_4162c4(uint32_t mask, uint32_t options,
                                uint32_t timeout_ticks, uint32_t opaque)
{
    (void)opaque;
    if (opencfw_provider_41602a() != 0u)
        return (uint64_t)options << 32 | UINT32_C(0xfffffffa);
    if ((int32_t)mask < 0)
        return (uint64_t)options << 32 | UINT32_C(0xfffffffc);

    const uint32_t wait_mask = (options & 2u) != 0u
        ? 0u : mask;
    uint32_t result = 0u;
    uint32_t received = 0u;
    uint32_t remaining = timeout_ticks;
    const uint32_t start = opencfw_boot_tick_get();
    uint32_t woke;
    do {
        woke = opencfw_boot_thread_notify_wait(0u, 0u, wait_mask, &received,
                                                remaining);
        if (woke == 1u) {
            result = received | (result & mask);
            if ((options & 1u) != 0u) {
                if ((result & mask) == mask)
                    break;
                if (timeout_ticks == 0u) {
                    result = UINT32_C(0xfffffffd);
                    break;
                }
            } else {
                if ((mask & result) != 0u)
                    break;
                if (timeout_ticks == 0u) {
                    result = UINT32_C(0xfffffffd);
                    break;
                }
            }
            const uint32_t elapsed = opencfw_boot_tick_get() - start;
            remaining = timeout_ticks < elapsed ? 0u : timeout_ticks - elapsed;
        } else {
            result = timeout_ticks == 0u ? UINT32_C(0xfffffffd)
                                         : UINT32_C(0xfffffffe);
        }
    } while (woke != 0u);
    return (uint64_t)remaining << 32 | result;
}
