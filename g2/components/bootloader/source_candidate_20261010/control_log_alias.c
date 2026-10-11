/* The bootloader error transaction has one fixed EasyLogger callsite. */
#include <stdint.h>

__attribute__((naked)) void opencfw_boot_control_log(uint32_t level,
                                                        uint32_t line)
{
    __asm__ volatile("b.w opencfw_control_log_native");
}
