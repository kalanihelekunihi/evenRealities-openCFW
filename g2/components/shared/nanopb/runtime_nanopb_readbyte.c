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
 * Altered production source adaptation of nanopb's private pb_readbyte(). The
 * authenticated nanopb-0.4.9 compatibility baseline is commit
 * 98bf4db69897b53434f3d0ba72e0a3ab1a902824; this does not prove the vendor's
 * historical point release. Complete stock entry [0x0048F454,0x0048F49C)
 * redirects here while retaining the two authenticated stock error strings.
 */

#include "runtime_nanopb_private_read_pair.h"

static bool open_cfw_nanopb_private_read_error(
    struct open_cfw_nanopb_istream *stream,
    const char *message
)
{
    if (stream->errmsg == NULL) {
        stream->errmsg = message;
    }

    return false;
}

bool open_cfw_nanopb_readbyte(
    struct open_cfw_nanopb_istream *stream,
    uint8_t *byte
)
{
    if (stream->bytes_left == 0U) {
        return open_cfw_nanopb_private_read_error(
            stream,
            open_cfw_nanopb_end_of_stream_error
        );
    }

    if (!stream->callback(stream, byte, 1U)) {
        return open_cfw_nanopb_private_read_error(
            stream,
            open_cfw_nanopb_io_error
        );
    }

    stream->bytes_left--;
    return true;
}
