/* SPDX-License-Identifier: MIT
 * Experimental C printf for TLSF's scalar diagnostic formats.
 *
 * The selected 0x415fae formatter wrapper uses this buffer, callback slot,
 * and opencfw_boot_plain_vsprintf. This source expresses that same route as a
 * C varargs function. It is excluded from archive admission until the TLSF
 * printf import is authenticated against a stock call target and its %p/%x/%u
 * domain is compared with the original output path.
 */
#include <stdarg.h>
#include <stdint.h>

extern uint32_t opencfw_boot_plain_vsprintf(char *dst,
                                           const char *format,
                                           va_list arguments);

typedef void (*opencfw_boot_print_sink_t)(const char *line);

int printf(const char *format, ...)
{
    opencfw_boot_print_sink_t sink =
        *(volatile opencfw_boot_print_sink_t *)(uintptr_t)0x200270ccu;
    if (sink == (opencfw_boot_print_sink_t)0)
        return 0;

    va_list arguments;
    va_start(arguments, format);
    char *const buffer = (char *)(uintptr_t)0x20024cd0u;
    uint32_t count = opencfw_boot_plain_vsprintf(buffer, format, arguments);
    va_end(arguments);
    sink(buffer);
    return (int)count;
}
