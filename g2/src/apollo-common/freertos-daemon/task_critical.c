/* SPDX-License-Identifier: MIT */
/* Reconstructed stock port critical helpers, separate from WSF and Ambiq. */
#include "daemon.h"
#define NEST (*(volatile uint32_t *)(uintptr_t)0x2000309cu)
void opencfw_daemon_critical_enter(void)
{
    (void)opencfw_queue_mask_set();NEST++;
    __asm__ volatile("dsb sy\nisb sy":::"memory");
}
void opencfw_daemon_critical_exit(void)
{
    if(NEST==0)opencfw_event_group_assert_failure();
    NEST--;
    if(NEST==0)opencfw_queue_mask_restore(0);
}
void opencfw_daemon_yield(void)
{
    *(volatile uint32_t *)(uintptr_t)0xe000ed04u=0x10000000u;
    __asm__ volatile("dsb sy\nisb sy":::"memory");
}
