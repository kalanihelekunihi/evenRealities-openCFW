/* openCFW compatibility header (Compat, not a stock file): the subset of
 * <stdio.h> that EasyLogger a596b264 elog.c uses, for freestanding builds.
 * Stock links IAR DLIB snprintf 0x44b728 and vsnprintf 0x44b76c. */
#ifndef G2_EASYLOGGER_STDIO_H
#define G2_EASYLOGGER_STDIO_H
#include <stdarg.h>
#include <stddef.h>
int snprintf(char *s, size_t n, const char *format, ...);
int vsnprintf(char *s, size_t n, const char *format, va_list ap);
#endif
