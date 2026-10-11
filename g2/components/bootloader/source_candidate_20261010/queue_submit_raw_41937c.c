/* SPDX-License-Identifier: MIT
 * Source reconstruction of the stock queue envelope at 0x41937c..0x4193de.
 * AAPCS: R0 event, R1 class, R2 payload, R3 ISR wake flag pointer;
 * caller's fifth word is the blocking timeout.
 */
#include <stdint.h>

extern uint32_t opencfw_bl_queue_runtime_mode(void);
extern uint32_t opencfw_bl_kernel_queue_put_blocking(uint32_t *queue,
                                                       const void *message,
                                                       uint32_t timeout,
                                                       uint32_t mode);
extern uint32_t opencfw_bl_kernel_queue_put_from_isr(uint32_t *queue,
                                                       const void *message,
                                                       uint32_t *woken,
                                                       uint32_t mode);
extern uint32_t opencfw_bl_mask_interrupts(void);

__attribute__((noreturn)) static void invalid_event(void)
{
    (void)opencfw_bl_mask_interrupts();
    *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0u;
    for (;;) __asm__ volatile("b ." ::: "memory");
}

uint32_t opencfw_boot_queue_submit_raw(uint32_t event, int32_t event_class,
                                        uint32_t payload, uint32_t *woken,
                                        uint32_t timeout)
{
    if (event == 0u) invalid_event();
    uint32_t *queue = *(uint32_t * volatile *)(uintptr_t)0x20027180u;
    if (queue == 0) return 0u;

    uint32_t envelope[3] = {(uint32_t)event_class, payload, event};
    if (event_class < 6) {
        uint32_t wait = opencfw_bl_queue_runtime_mode() == 2u ? timeout : 0u;
        return opencfw_bl_kernel_queue_put_blocking(queue, envelope, wait, 0u);
    }
    return opencfw_bl_kernel_queue_put_from_isr(queue, envelope, woken, 0u);
}
