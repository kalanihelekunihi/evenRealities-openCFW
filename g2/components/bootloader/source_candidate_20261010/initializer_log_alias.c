/* Initializer callers place tag, file, then function in R1-R3. */
#include <stdint.h>

__attribute__((naked)) void opencfw_bl_logger_output(uint32_t level,
                                                      const char *tag,
                                                      const char *file,
                                                      const char *function,
                                                      uint32_t line,
                                                      const char *format, ...)
{
    __asm__ volatile("b.w opencfw_boot_elog_output");
}
