/* SPDX-License-Identifier: MIT */
/* Variadic logging wrapper; formatter/output dependencies remain unqualified. */
#include <stdarg.h>
extern int open_cfw_gx8002_tfp_format(void *, const char *, va_list);
int open_cfw_gx8002_printf(const char *format, ...)
{
    va_list args;
    va_start(args, format);
    int result = open_cfw_gx8002_tfp_format((void *)0, format, args);
    va_end(args);
    return result;
}
