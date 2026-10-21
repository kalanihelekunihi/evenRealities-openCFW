/* The selected NOR helpers use the stock EasyLogger argument order. */
#include <stdint.h>

__attribute__((naked)) void opencfw_bl_log(uint32_t level,
                                            const char *tag,
                                            const char *file,
                                            const char *function,
                                            uint32_t line,
                                            const char *format, ...)
{
    __asm__ volatile("b.w opencfw_boot_elog_output");
}
