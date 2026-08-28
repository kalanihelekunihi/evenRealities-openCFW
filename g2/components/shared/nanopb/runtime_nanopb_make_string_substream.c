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
 * Altered production source for nanopb pb_make_string_substream(). The
 * selected baseline is authenticated nanopb 0.4.9 commit
 * 98bf4db69897b53434f3d0ba72e0a3ab1a902824. Existing binary evidence narrows
 * the vendor runtime only to the source-equivalent 0.4.7--0.4.9 interval.
 *
 * The complete stock body occupies [0x0048F77E, 0x0048F7CA). Stock copies the
 * recovered 16-byte stream through an aligned interior __aeabi_memcpy entry.
 * This source closes that compiler-runtime seam with four named ABI-field
 * assignments and calls only the separately source-owned varint32 decoder.
 */

#include "runtime_nanopb_make_string_substream.h"

static const char open_cfw_nanopb_parent_too_short_error[] =
    "parent stream too short";

static bool open_cfw_nanopb_substream_error(
    struct open_cfw_nanopb_istream *stream
)
{
    if (stream->errmsg == NULL) {
        stream->errmsg = open_cfw_nanopb_parent_too_short_error;
    }

    return false;
}

static void open_cfw_nanopb_copy_stream(
    struct open_cfw_nanopb_istream *destination,
    const struct open_cfw_nanopb_istream *source
)
{
    destination->callback = source->callback;
    destination->state = source->state;
    destination->bytes_left = source->bytes_left;
    destination->errmsg = source->errmsg;
}

bool open_cfw_nanopb_make_string_substream(
    struct open_cfw_nanopb_istream *stream,
    struct open_cfw_nanopb_istream *substream
)
{
    uint32_t size;

    if (!open_cfw_nanopb_decode_varint32(stream, &size)) {
        return false;
    }

    open_cfw_nanopb_copy_stream(substream, stream);
    if (substream->bytes_left < (size_t)size) {
        return open_cfw_nanopb_substream_error(stream);
    }

    substream->bytes_left = (size_t)size;
    stream->bytes_left -= (size_t)size;
    return true;
}
