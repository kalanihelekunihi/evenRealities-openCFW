/* AmbiqSuite am_util_stdio bounded formatters, reconstructed from the
 * 2.2.6.10 disassembly (AmbiqSuite SDK, BSD-3-Clause).
 *
 * Stock ranges:
 *   0x0047341a..0x0047344d  am_util_stdio_vsnprintf (log_vsnprintf_47341a)
 *   0x0047344e..0x0047345b  am_util_stdio_snprintf  (log_snprintf_47344e)
 *   literal 0x473470 = RAM 0x2006b930 (g_prfbuf), in the pool shared with
 *   am_util_stdio_printf 0x4733ee.
 *
 * The text is formatted unbounded into the 1024-byte g_prfbuf by
 * am_util_stdio_vsprintf 0x473036 and copied out only when it fits: size >= 1024
 * or a result of size or more characters returns 0 and leaves dst untouched.
 * The copy does not append a NUL. Profile g2-apollo-main-2. */
#include <stdint.h>
#include <stdarg.h>

#define AM_PRINTF_BUFSIZE 1024u

extern uint32_t audio_heap_formatter(char *out, const char *format, va_list args); /* 0x473036 am_util_stdio_vsprintf */
extern uint8_t g2_flashdb_print_buffer[AM_PRINTF_BUFSIZE];                       /* RAM 0x2006b930 g_prfbuf */

int32_t log_vsnprintf_47341a(char *dst, uint32_t size, const char *format, va_list args);
int32_t log_snprintf_47344e(char *dst, uint32_t size, const char *format, ...);

/* Stock 0x0047341a (am_util_stdio_vsnprintf) */
int32_t log_vsnprintf_47341a(char *dst, uint32_t size, const char *format, va_list args)
{
    uint32_t count;

    if (size >= AM_PRINTF_BUFSIZE)
        return 0;
    count = audio_heap_formatter((char *)g2_flashdb_print_buffer, format, args);
    if (count >= size)
        return 0;
    for (uint32_t i = 0u; i < count; i++)
        dst[i] = (char)g2_flashdb_print_buffer[i];
    return (int32_t)count;
}

/* Stock 0x0047344e (am_util_stdio_snprintf) */
int32_t log_snprintf_47344e(char *dst, uint32_t size, const char *format, ...)
{
    va_list args;
    int32_t count;

    va_start(args, format);
    count = log_vsnprintf_47341a(dst, size, format, args);
    va_end(args);
    return count;
}
