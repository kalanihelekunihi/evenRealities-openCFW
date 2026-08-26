/* SPDX-License-Identifier: GPL-3.0-or-later */

#include "runtime_string_spans.h"

__attribute__((used, noinline))
open_cfw_bootloader_span_size open_cfw_bootloader_strcspn(
    const char *string,
    const char *reject
)
{
    const char *cursor = string;
    while (*cursor != '\0') {
        const char *candidate = reject;
        while (*candidate != '\0') {
            if (*cursor == *candidate) {
                return (open_cfw_bootloader_span_size)(cursor - string);
            }
            ++candidate;
        }
        ++cursor;
    }
    return (open_cfw_bootloader_span_size)(cursor - string);
}
