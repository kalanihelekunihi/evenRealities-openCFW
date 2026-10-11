/* SPDX-License-Identifier: MIT
 * Native XIP 0x10206c24..0x10206c41 is the target's tinyprintf
 * variadic wrapper. Pinned NationalChip utility/libc/tinyprintf.c
 * printf_ source confirms a va_start/format/va_end call. The formatting
 * engine and console sink remain separate actual source bodies.
 */
#include <stdarg.h>
#include <stdint.h>

extern uint32_t gx8002_xip_tfp_format_10206a84(
    void *stream, const char *format, va_list args);

uint32_t gx8002_xip_tws_publish_10206c24(const char *format, ...)
{
    va_list args;
    va_start(args, format);
    uint32_t written = gx8002_xip_tfp_format_10206a84(0, format, args);
    va_end(args);
    return written;
}
