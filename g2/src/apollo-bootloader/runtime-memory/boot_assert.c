/* SPDX-License-Identifier: MIT
 * Native Boot assertion reporter, 0x415734 -> 0x417c28 -> 0x41b298.
 * The semihosting BKPT and the failure loop are architectural source behavior:
 * operation 0x18 with the {file, line, condition} block, then on a zero result
 * an endless SYS_EXIT(ADP_Stopped_ApplicationExit) request.
 */
#include <stdint.h>

/* One ARM semihosting request: BKPT 0xAB with the operation in r0 and its
 * operands in r1/r2; the host's result comes back in r0. */
static inline uint32_t boot_semihost(uint32_t operation, uint32_t r1_value,
                                     const void *r2_value)
{
    register uint32_t r0 __asm__("r0") = operation;
    register uint32_t r1 __asm__("r1") = r1_value;
    register const void *r2 __asm__("r2") = r2_value;

    __asm__ volatile("bkpt #0xab" : "+r"(r0) : "r"(r1), "r"(r2) : "memory");
    return r0;
}

__attribute__((noreturn)) void opencfw_boot_semihost_exit_loop(void)
{
    for (;;)
        (void)boot_semihost(0x18u, 0x00020026u, (const void *)0x00020026u);
}

__attribute__((noreturn)) void opencfw_boot_assert_abort(void)
{
    opencfw_boot_semihost_exit_loop();
}

void opencfw_boot_assert_report(const char *condition, const char *file,
                                unsigned line)
{
    const uint32_t block[3] = {
        (uint32_t)(uintptr_t)file, line, (uint32_t)(uintptr_t)condition,
    };

    if (boot_semihost(0x18u, 0x00021010u, block) == 0u)
        opencfw_boot_assert_abort();
}
