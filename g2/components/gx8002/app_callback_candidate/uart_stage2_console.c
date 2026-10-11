/* SPDX-License-Identifier: MIT
 * Stage-2 console format/output at native 0x100061a4.
 * The formatter at 0x10006fa4 and byte sink at 0x10002a84 remain typed
 * source obligations; this owns their outer varargs and output loop.
 */
#include <stdarg.h>
#include <stdint.h>

extern int32_t gx8002_uart_stage2_format_engine_6b40(char *buffer,
                                                       const char *format,
                                                       va_list arguments);
extern void gx8002_uart_stage2_console_putc_2a84(uint32_t character);

int32_t gx8002_uart_stage2_format_6fa4(char *buffer, const char *format,
                                         va_list arguments)
{
    return gx8002_uart_stage2_format_engine_6b40(buffer, format, arguments);
}

int32_t gx8002_uart_stage2_launch_61a4(const char *format, ...)
{
    char buffer[256];
    va_list arguments;
    va_start(arguments, format);
    const int32_t result = gx8002_uart_stage2_format_6fa4(buffer, format,
                                                             arguments);
    va_end(arguments);
    for (const char *p = buffer; *p != '\0'; ++p)
        gx8002_uart_stage2_console_putc_2a84((uint8_t)*p);
    return result;
}
