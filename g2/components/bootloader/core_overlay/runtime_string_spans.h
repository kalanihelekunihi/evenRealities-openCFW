/* SPDX-License-Identifier: GPL-3.0-or-later */
#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_STRING_SPANS_H
#define OPEN_CFW_BOOTLOADER_RUNTIME_STRING_SPANS_H

typedef unsigned int open_cfw_bootloader_span_size;

open_cfw_bootloader_span_size open_cfw_bootloader_strcspn(
    const char *string,
    const char *reject
);
open_cfw_bootloader_span_size open_cfw_bootloader_strspn(
    const char *string,
    const char *accept
);

#endif
