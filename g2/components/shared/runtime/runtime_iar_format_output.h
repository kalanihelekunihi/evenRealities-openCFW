/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_RUNTIME_IAR_FORMAT_OUTPUT_H
#define OPEN_CFW_RUNTIME_IAR_FORMAT_OUTPUT_H

#include <stdarg.h>

typedef void *(*open_cfw_runtime_iar_format_writer_fn)(
    void *state,
    unsigned int character
);

int open_cfw_runtime_iar_vformat(
    open_cfw_runtime_iar_format_writer_fn writer,
    void *state,
    const unsigned char *format,
    va_list arguments,
    int secure
);

#if defined(__arm__) || defined(__thumb__)
__attribute__((pcs("aapcs")))
int open_cfw_runtime_iar_printf_core(
    open_cfw_runtime_iar_format_writer_fn writer,
    void *state,
    const unsigned char *format,
    void **argument_cursor,
    int secure
);
#endif

#endif
