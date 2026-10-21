/* The allocator's sole call passes source line 19 to the fixed metadata adapter. */
#include <stdint.h>

__attribute__((naked)) void opencfw_boot_allocator_log(uint32_t line)
{
    __asm__ volatile("b.w opencfw_allocator_log_native");
}
