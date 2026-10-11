/* SPDX-License-Identifier: MIT
 * Stock 0x416378 CMSIS delay alias for NOR polling callers.
 * The stock wrapper returns its incoming R3 in R1 after the status in R0.
 */
#include <stdint.h>

__attribute__((naked)) uint32_t opencfw_bl_task_delay(uint32_t ticks)
{
    __asm__ volatile("push {r3, lr}\n"
                     "bl opencfw_cmsis_delay\n"
                     "pop {r1, pc}");
}
