/* SPDX-License-Identifier: GPL-3.0-or-later */

#include "runtime_string_spans.h"

__attribute__((used, noinline))
open_cfw_bootloader_span_size open_cfw_bootloader_strspn(
    const char *string,
    const char *accept
)
{
    const char *cursor = string;
    while (*cursor != '\0') {
        const char *candidate = accept;
        while (*candidate != '\0' && *cursor != *candidate) {
            ++candidate;
        }
        if (*candidate == '\0') {
            break;
        }
        ++cursor;
    }
    return (open_cfw_bootloader_span_size)(cursor - string);
}
