/* Test-only architectural readback, not stock firmware reconstruction. */
#include <stdint.h>

uint32_t opencfw_test_read_psplim(void)
{
    uint32_t limit;

    __asm__ volatile("mrs %0, psplim" : "=r"(limit));
    return limit;
}

void opencfw_test_set_stack_limits(uint32_t psplim, uint32_t psp)
{
    __asm__ volatile("msr psplim, %0" : : "r"(psplim) : "memory");
    __asm__ volatile("msr psp, %0" : : "r"(psp) : "memory");
}
