/*
 * SPDX-License-Identifier: Zlib
 *
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
 * Altered production source for nanopb's private pb_decode_inner(). The
 * compatibility baseline is authenticated nanopb 0.4.9 commit
 * 98bf4db69897b53434f3d0ba72e0a3ab1a902824. The recovered G2 body occupies
 * [0x0048FE98, 0x00490112). Its iterator, defaults, field/extension dispatch,
 * pb_decode_tag, and pb_skip_field dependencies are now source-owned.
 */

#include "runtime_nanopb_decode_inner.h"

enum {
    OPEN_CFW_NANOPB_DECODE_NOINIT = 0x01U,
    OPEN_CFW_NANOPB_DECODE_NULLTERMINATED = 0x04U,
    OPEN_CFW_NANOPB_LTYPE_MASK = 0x0FU,
    OPEN_CFW_NANOPB_LTYPE_EXTENSION = 0x0AU,
    OPEN_CFW_NANOPB_HTYPE_MASK = 0x30U,
    OPEN_CFW_NANOPB_HTYPE_REQUIRED = 0x00U,
    OPEN_CFW_NANOPB_HTYPE_REPEATED = 0x20U,
    OPEN_CFW_NANOPB_MAX_REQUIRED_FIELDS = 64U
};

enum {
    OPEN_CFW_NANOPB_DEFAULTS_ERROR_OFFSET = 0U,
    OPEN_CFW_NANOPB_ZERO_TAG_ERROR_OFFSET = 23U,
    OPEN_CFW_NANOPB_FIXED_COUNT_ERROR_OFFSET = 32U,
    OPEN_CFW_NANOPB_REQUIRED_ERROR_OFFSET = 65U
};

static const char open_cfw_nanopb_decode_inner_errors[] =
    "failed to set defaults\0"
    "zero tag\0"
    "wrong size for fixed count field\0"
    "missing required field";

static bool open_cfw_nanopb_decode_inner_fail(
    struct open_cfw_nanopb_istream *stream,
    const char *message
)
{
    if (stream->errmsg == NULL) {
        stream->errmsg = message;
    }
    return false;
}

bool open_cfw_nanopb_decode_inner(
    struct open_cfw_nanopb_istream *stream,
    const void *fields,
    void *destination,
    unsigned int flags
)
{
    uint32_t extension_range_start = 0U;
    void *extensions = NULL;
    uint16_t fixed_count_field = UINT16_MAX;
    uint16_t fixed_count_size = 0U;
    uint16_t fixed_count_total_size = 0U;
    uint32_t fields_seen[2] = {0U, 0U};
    struct open_cfw_nanopb_field_iter iter;

    if (open_cfw_nanopb_field_iter_begin(
            &iter,
            (const struct open_cfw_nanopb_msgdesc *)fields,
            destination)
        && (flags & OPEN_CFW_NANOPB_DECODE_NOINIT) == 0U
        && !open_cfw_nanopb_message_set_to_defaults(&iter)) {
        return open_cfw_nanopb_decode_inner_fail(
            stream,
            open_cfw_nanopb_decode_inner_errors
                + OPEN_CFW_NANOPB_DEFAULTS_ERROR_OFFSET
        );
    }

    while (stream->bytes_left != 0U) {
        uint32_t tag;
        uint8_t wire_type;
        bool eof;

        if (!open_cfw_nanopb_decode_tag(stream, &wire_type, &tag, &eof)) {
            if (eof) {
                break;
            }
            return false;
        }

        if (tag == 0U) {
            if ((flags & OPEN_CFW_NANOPB_DECODE_NULLTERMINATED) != 0U) {
                break;
            }
            return open_cfw_nanopb_decode_inner_fail(
                stream,
                open_cfw_nanopb_decode_inner_errors
                    + OPEN_CFW_NANOPB_ZERO_TAG_ERROR_OFFSET
            );
        }

        if (!open_cfw_nanopb_field_iter_find(&iter, tag)
            || (iter.type & OPEN_CFW_NANOPB_LTYPE_MASK)
                == OPEN_CFW_NANOPB_LTYPE_EXTENSION) {
            if (extension_range_start == 0U) {
                if (open_cfw_nanopb_field_iter_find_extension(&iter)) {
                    extensions = *(void *const *)iter.data;
                    extension_range_start = iter.tag;
                }
                if (extensions == NULL) {
                    extension_range_start = UINT32_MAX;
                }
            }

            if (tag >= extension_range_start) {
                size_t position = stream->bytes_left;
                if (!open_cfw_nanopb_decode_extension(
                        stream, tag, wire_type, extensions)) {
                    return false;
                }
                if (position != stream->bytes_left) {
                    continue;
                }
            }

            if (!open_cfw_nanopb_skip_field(stream, (uint8_t)wire_type)) {
                return false;
            }
            continue;
        }

        if ((iter.type & OPEN_CFW_NANOPB_HTYPE_MASK)
                == OPEN_CFW_NANOPB_HTYPE_REPEATED
            && iter.size == &iter.array_size) {
            if (fixed_count_field != iter.index) {
                if (fixed_count_field != UINT16_MAX
                    && fixed_count_size != fixed_count_total_size) {
                    return open_cfw_nanopb_decode_inner_fail(
                        stream,
                        open_cfw_nanopb_decode_inner_errors
                            + OPEN_CFW_NANOPB_FIXED_COUNT_ERROR_OFFSET
                    );
                }
                fixed_count_field = iter.index;
                fixed_count_size = 0U;
                fixed_count_total_size = iter.array_size;
            }
            iter.size = &fixed_count_size;
        }

        if ((iter.type & OPEN_CFW_NANOPB_HTYPE_MASK)
                == OPEN_CFW_NANOPB_HTYPE_REQUIRED
            && iter.required_field_index
                < OPEN_CFW_NANOPB_MAX_REQUIRED_FIELDS) {
            fields_seen[iter.required_field_index >> 5]
                |= (uint32_t)1U << (iter.required_field_index & 31U);
        }

        if (!open_cfw_nanopb_decode_field(stream, wire_type, &iter)) {
            return false;
        }
    }

    if (fixed_count_field != UINT16_MAX
        && fixed_count_size != fixed_count_total_size) {
        return open_cfw_nanopb_decode_inner_fail(
            stream,
            open_cfw_nanopb_decode_inner_errors
                + OPEN_CFW_NANOPB_FIXED_COUNT_ERROR_OFFSET
        );
    }

    {
        uint16_t required =
            ((const struct open_cfw_nanopb_msgdesc *)iter.descriptor)
                ->required_field_count;
        uint16_t index;

        if (required > OPEN_CFW_NANOPB_MAX_REQUIRED_FIELDS) {
            required = OPEN_CFW_NANOPB_MAX_REQUIRED_FIELDS;
        }
        for (index = 0U; index < (required >> 5); ++index) {
            if (fields_seen[index] != UINT32_MAX) {
                return open_cfw_nanopb_decode_inner_fail(
                    stream,
                    open_cfw_nanopb_decode_inner_errors
                        + OPEN_CFW_NANOPB_REQUIRED_ERROR_OFFSET
                );
            }
        }
        if ((required & 31U) != 0U
            && fields_seen[required >> 5]
                != (UINT32_MAX >> (32U - (required & 31U)))) {
            return open_cfw_nanopb_decode_inner_fail(
                stream,
                open_cfw_nanopb_decode_inner_errors
                    + OPEN_CFW_NANOPB_REQUIRED_ERROR_OFFSET
            );
        }
    }

    return true;
}
