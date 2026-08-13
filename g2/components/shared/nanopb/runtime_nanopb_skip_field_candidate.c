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
 * Altered, production-excluded source candidate for nanopb pb_skip_field().
 * The selected baseline is authenticated nanopb 0.4.9 commit
 * 98bf4db69897b53434f3d0ba72e0a3ab1a902824. Existing binary evidence only
 * narrows the vendor runtime to the source-equivalent 0.4.7--0.4.9 interval.
 *
 * The complete stock body occupies [0x0048F6A0, 0x0048F6EA). Its three
 * executable dependencies are already source-owned. This file remains absent
 * from every production overlay and manifest until a separate promotion pass
 * pins target output, relocation closure, placement, and ownership accounting.
 */

#include "runtime_nanopb_skip_field_candidate.h"

static const char open_cfw_nanopb_invalid_wire_type_error[] =
    "invalid wire_type";

static bool open_cfw_nanopb_skip_field_error(
    struct open_cfw_nanopb_istream *stream
)
{
    if (stream->errmsg == NULL) {
        stream->errmsg = open_cfw_nanopb_invalid_wire_type_error;
    }

    return false;
}

bool open_cfw_nanopb_skip_field_candidate(
    struct open_cfw_nanopb_istream *stream,
    uint8_t wire_type
)
{
    switch (wire_type) {
    case OPEN_CFW_NANOPB_WT_VARINT:
        return open_cfw_nanopb_skip_varint(stream);
    case OPEN_CFW_NANOPB_WT_64BIT:
        return open_cfw_nanopb_read(stream, NULL, 8U);
    case OPEN_CFW_NANOPB_WT_STRING:
        return open_cfw_nanopb_skip_string(stream);
    case OPEN_CFW_NANOPB_WT_32BIT:
        return open_cfw_nanopb_read(stream, NULL, 4U);
    default:
        return open_cfw_nanopb_skip_field_error(stream);
    }
}
