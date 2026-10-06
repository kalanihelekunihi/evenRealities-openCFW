/* SPDX-License-Identifier: MIT. Offline fixture-only leaf providers. */
#include <stdint.h>
#define WORD(a) (*(volatile uint32_t *)(uintptr_t)(a))
void opencfw_bl_scheduler_suspend(void) {}
uint32_t opencfw_bl_scheduler_resume(void) { return 1u; }
uint32_t opencfw_bl_remove_event_waiter(uint32_t *list) { (void)list; return 0u; }
uintptr_t opencfw_bl_rtos_allocate(uint32_t bytes) { (void)bytes; return 0u; }
void opencfw_bl_rtos_free(uintptr_t address)
{
    WORD(0x20030ff0) = (uint32_t)address;
    WORD(0x20030ff4)++;
}
void opencfw_bl_timer_rollover(void) {}
void opencfw_bl_timer_expire(uint32_t expiry, uint32_t now)
{ (void)expiry; (void)now; }
void opencfw_bl_missed_yield(void) {}
uint32_t opencfw_bl_malloc_failed(void) { return 0u; }
