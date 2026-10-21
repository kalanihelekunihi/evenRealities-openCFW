/* Update-core callers use the canonical EasyLogger variadic ABI. */
#include <stdint.h>

__attribute__((naked)) void opencfw_boot_log(uint32_t level,
                                             const char *tag,
                                             const char *file,
                                             const char *function,
                                             uint32_t line,
                                             const char *format, ...)
{
    __asm__ volatile("b.w opencfw_boot_elog_output");
}
