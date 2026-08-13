#ifndef OPEN_CFW_AM_UTIL_STDIO_SHIM_H
#define OPEN_CFW_AM_UTIL_STDIO_SHIM_H

#include <stdarg.h>
#include <stdint.h>

#ifndef AM_PRINTF_BUFSIZE
#define AM_PRINTF_BUFSIZE 1024
#endif

uint32_t am_util_stdio_vsprintf(char *buffer, const char *format, va_list args);
uint32_t am_util_stdio_printf(const char *format, ...);

#endif
