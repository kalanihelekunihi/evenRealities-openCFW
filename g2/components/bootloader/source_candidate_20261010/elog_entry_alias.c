/* Retained stock-address name for the canonical EasyLogger call ABI. */
#include <stdint.h>

__attribute__((naked)) void opencfw_provider_4176ce(uint32_t level,
                                                     const char *tag,
                                                     const char *file,
                                                     const char *function,
                                                     uint32_t line,
                                                     const char *format, ...)
{
    __asm__ volatile("b.w opencfw_boot_elog_output");
}
