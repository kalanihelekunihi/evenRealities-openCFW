/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_RUNTIME_FORMAT_SCAN_H
#define OPEN_CFW_RUNTIME_FORMAT_SCAN_H

#include <stdarg.h>

#ifdef __cplusplus
extern "C" {
#endif

double open_cfw_runtime_strtod(const char *input, const char **end);
double open_cfw_runtime_strtod_bounded(
    const char *input,
    unsigned int maximum,
    const char **end
);
int open_cfw_runtime_vsscanf(
    const char *input,
    const char *format,
    va_list arguments
);
int open_cfw_runtime_sscanf(const char *input, const char *format, ...);
int open_cfw_runtime_scanset_match(
    const unsigned char *table,
    unsigned int table_bytes,
    unsigned int character
);

#if defined(__arm__) || defined(__thumb__)
typedef unsigned int (*open_cfw_runtime_iar_scan_reader_fn)(
    const unsigned char **cursor,
    unsigned int value,
    int read
);
__attribute__((pcs("aapcs")))
int open_cfw_runtime_iar_scanf_core(
    open_cfw_runtime_iar_scan_reader_fn reader,
    const unsigned char **cursor,
    const char *format,
    void **argument_cursor,
    int secure
);
#endif

#ifdef __cplusplus
}
#endif

#endif
