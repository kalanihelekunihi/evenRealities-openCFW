/* SPDX-License-Identifier: MIT
 * Stock 0x4160e8..0x4160fe, authenticated body SHA-256
 * 4fe35d35c5f61f5683c7ddd34f424d7f51d8a9276a0249c71b8473811dc7890a.
 * Its two original getters at 0x41835a and 0x418362 both read the same
 * 0x20027148 word; the guard call still occurs on both paths. The stock
 * pop {r1,pc} returns incoming R7 in R1. Every caller (manager_task.c,
 * event_dispatch.c) declares a uint32_t return and reads only R0, so the
 * ambient R7 is not reproduced: the upper word of the 64-bit return is 0.
 */
#include <stdint.h>

extern uint32_t opencfw_bl_context_guard(void);

uint64_t opencfw_provider_4160e8(void)
{
    (void)opencfw_bl_context_guard();
    const uint32_t tick = *(volatile const uint32_t *)(uintptr_t)0x20027148u;
    return (uint64_t)tick;
}
