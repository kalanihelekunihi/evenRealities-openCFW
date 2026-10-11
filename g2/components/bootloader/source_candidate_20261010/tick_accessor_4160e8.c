/* SPDX-License-Identifier: MIT
 * Stock 0x4160e8..0x4160fe, authenticated body SHA-256
 * 4fe35d35c5f61f5683c7ddd34f424d7f51d8a9276a0249c71b8473811dc7890a.
 * Its two original getters at 0x41835a and 0x418362 both read the same
 * 0x20027148 word; the guard call still occurs on both paths. The stock
 * pop {r1,pc} returns incoming R7 in R1, represented by a 64-bit C return.
 */
#include <stdint.h>

extern uint32_t opencfw_bl_context_guard(void);

uint64_t opencfw_provider_4160e8(void)
{
    uint32_t saved_r7;
    __asm__ volatile("mov %0, r7" : "=r"(saved_r7));
    (void)opencfw_bl_context_guard();
    const uint32_t tick = *(volatile const uint32_t *)(uintptr_t)0x20027148u;
    return ((uint64_t)saved_r7 << 32) | tick;
}
