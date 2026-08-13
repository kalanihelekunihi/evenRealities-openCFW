/*
 * Copyright (c) 2011 Petteri Aimonen <jpa at nanopb.mail.kapsi.fi>
 *
 * This software is provided 'as-is', without any express or implied warranty.
 * In no event will the authors be held liable for any damages arising from
 * the use of this software.
 *
 * Permission is granted to anyone to use this software for any purpose,
 * including commercial applications, and to alter it and redistribute it
 * freely, subject to the following restrictions:
 *
 * 1. The origin of this software must not be misrepresented; you must not
 *    claim that you wrote the original software. If you use this software in
 *    a product, an acknowledgment in the product documentation would be
 *    appreciated but is not required.
 * 2. Altered source versions must be plainly marked as such, and must not be
 *    misrepresented as being the original software.
 * 3. This notice may not be removed or altered from any source distribution.
 *
 * Altered production source for nanopb's private pb_dec_string(). The selected
 * compatibility baseline is authenticated nanopb 0.4.9 commit
 * 98bf4db69897b53434f3d0ba72e0a3ab1a902824. The recovered G2 body occupies
 * [0x004903EA, 0x00490488), uses 32-bit size_t and has PB_ENABLE_MALLOC and
 * PB_VALIDATE_UTF8 disabled. Its executable dependencies are source-owned.
 */

#include <stdint.h>

#include "runtime_nanopb_dec_string.h"

static const struct {
    char size_too_large[15];
    char no_malloc_support[18];
    char string_overflow[16];
} open_cfw_nanopb_dec_string_errors = {
    "size too large",
    "no malloc support",
    "string overflow"
};

static bool open_cfw_nanopb_dec_string_error(
    struct open_cfw_nanopb_istream *stream,
    const char *error
)
{
    if (stream->errmsg == NULL) {
        stream->errmsg = error;
    }
    return false;
}

bool open_cfw_nanopb_dec_string(
    struct open_cfw_nanopb_istream *stream,
    const struct open_cfw_nanopb_field_iter *field
)
{
    uint32_t size;
    size_t allocation_size;
    uint8_t *destination = (uint8_t *)field->data;

    if (!open_cfw_nanopb_decode_varint32(stream, &size)) {
        return false;
    }

    if (size == UINT32_MAX) {
        return open_cfw_nanopb_dec_string_error(
            stream,
            open_cfw_nanopb_dec_string_errors.size_too_large
        );
    }

    allocation_size = (size_t)(size + 1U);
    if (allocation_size < size) {
        return open_cfw_nanopb_dec_string_error(
            stream,
            open_cfw_nanopb_dec_string_errors.size_too_large
        );
    }

    if ((field->type & OPEN_CFW_NANOPB_ATYPE_MASK)
        == OPEN_CFW_NANOPB_ATYPE_POINTER) {
        return open_cfw_nanopb_dec_string_error(
            stream,
            open_cfw_nanopb_dec_string_errors.no_malloc_support
        );
    }

    if (allocation_size > field->data_size) {
        return open_cfw_nanopb_dec_string_error(
            stream,
            open_cfw_nanopb_dec_string_errors.string_overflow
        );
    }

    destination[size] = 0U;
    if (!open_cfw_nanopb_read(stream, destination, size)) {
        return false;
    }

    return true;
}
