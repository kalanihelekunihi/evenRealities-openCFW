/* Fixed DFU log lines use the selected source metadata adapter. */
#include <stdint.h>

__attribute__((naked)) void opencfw_boot_dfu_log(uint32_t level,
                                                 uint32_t line)
{
    __asm__ volatile("b.w opencfw_dfu_log_native");
}
