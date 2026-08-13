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
 * Altered, production-excluded source candidate for nanopb read_raw_value().
 * The selected compatibility baseline is authenticated nanopb 0.4.9 commit
 * 98bf4db69897b53434f3d0ba72e0a3ab1a902824. The complete recovered G2 body
 * occupies [0x0048F6EA, 0x0048F77E) and calls only source-owned pb_read.
 */

#include "runtime_nanopb_read_raw_value_candidate.h"

static const char open_cfw_nanopb_raw_varint_overflow_error[] =
    "varint overflow";
static const char open_cfw_nanopb_raw_invalid_wire_type_error[] =
    "invalid wire_type";

static bool open_cfw_nanopb_raw_error(
    struct open_cfw_nanopb_istream *stream,
    const char *error
)
{
    if (stream->errmsg == NULL) {
        stream->errmsg = error;
    }

    return false;
}

bool open_cfw_nanopb_read_raw_value_candidate(
    struct open_cfw_nanopb_istream *stream,
    uint8_t wire_type,
    uint8_t *buffer,
    size_t *size
)
{
    const size_t maximum_size = *size;

    switch (wire_type) {
    case OPEN_CFW_NANOPB_RAW_WT_VARINT:
        *size = 0U;
        do {
            *size += 1U;
            if (*size > maximum_size) {
                return open_cfw_nanopb_raw_error(
                    stream,
                    open_cfw_nanopb_raw_varint_overflow_error
                );
            }
            if (!open_cfw_nanopb_read(stream, buffer, 1U)) {
                return false;
            }
        } while ((*buffer++ & 0x80U) != 0U);
        return true;

    case OPEN_CFW_NANOPB_RAW_WT_64BIT:
        *size = 8U;
        return open_cfw_nanopb_read(stream, buffer, 8U);

    case OPEN_CFW_NANOPB_RAW_WT_32BIT:
        *size = 4U;
        return open_cfw_nanopb_read(stream, buffer, 4U);

    case OPEN_CFW_NANOPB_RAW_WT_STRING:
    default:
        return open_cfw_nanopb_raw_error(
            stream,
            open_cfw_nanopb_raw_invalid_wire_type_error
        );
    }
}
