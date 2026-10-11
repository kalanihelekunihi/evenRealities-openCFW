/* Stock 0x41b600 RTOS stack-overflow hook. */
#include <stdint.h>

__attribute__((naked, noreturn)) void opencfw_bl_stack_overflow(uint32_t *tcb,
                                                                  const char *name)
{
    __asm__ volatile("b.w opencfw_stack_overflow_native");
}
