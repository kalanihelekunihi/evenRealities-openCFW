/* SPDX-License-Identifier: MIT */
/* Bounded reconstruction of stock 0x4420bc; requests PendSV, not a switch. */
#include "resume.h"
void opencfw_resume_yield_request(void)
{
    *(volatile uint32_t *)(uintptr_t)0xe000ed04u = 0x10000000u;
    __asm__ volatile("dsb\nisb" ::: "memory");
}
