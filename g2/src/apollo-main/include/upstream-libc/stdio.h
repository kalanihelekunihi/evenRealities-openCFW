/* SPDX-License-Identifier: MIT
 * Freestanding <stdio.h> for pinned upstream units in the G2 Apollo main
 * image. printf is the IAR DLIB entry at 0x4733EE (pushes r1-r3, formats
 * through 0x473036 into a shared buffer, then calls the output sink).
 */
#ifndef G2_UPSTREAM_LIBC_STDIO_H
#define G2_UPSTREAM_LIBC_STDIO_H
#include <stddef.h>
#include <stdarg.h>
int printf(const char *format, ...);
int sprintf(char *buffer, const char *format, ...);
int snprintf(char *buffer, size_t size, const char *format, ...);
int vsnprintf(char *buffer, size_t size, const char *format, va_list arguments);
int sscanf(const char *string, const char *format, ...);
#endif
