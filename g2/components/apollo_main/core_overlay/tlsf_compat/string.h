/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_TLSF_COMPAT_STRING_H
#define OPEN_CFW_TLSF_COMPAT_STRING_H

#include <stddef.h>

void *open_cfw_tlsf_memcpy(
    void *destination,
    const void *source,
    size_t byte_count
);

#define memcpy open_cfw_tlsf_memcpy

#endif
