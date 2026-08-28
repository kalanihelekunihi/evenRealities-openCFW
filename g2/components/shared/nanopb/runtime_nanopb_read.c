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
 * Altered production source adaptation of nanopb pb_read(). The selected
 * compatibility baseline is the authenticated nanopb-0.4.9 snapshot at commit
 * 98bf4db69897b53434f3d0ba72e0a3ab1a902824. The definition is byte-identical
 * in pristine nanopb 0.4.7, 0.4.8, and 0.4.9. The private buffer callback now
 * retains its canonical stock-entry identity through a source trampoline;
 * the two error strings remain authenticated stock data seams.
 */

#include "runtime_nanopb_read.h"

static bool open_cfw_nanopb_read_error(
    struct open_cfw_nanopb_istream *stream,
    const char *message
)
{
    if (stream->errmsg == NULL) {
        stream->errmsg = message;
    }

    return false;
}

bool open_cfw_nanopb_read(
    struct open_cfw_nanopb_istream *stream,
    uint8_t *buffer,
    size_t count
)
{
    if (count == 0U) {
        return true;
    }

    if (
        buffer == NULL &&
        stream->callback != open_cfw_nanopb_stock_buffer_read_identity
    ) {
        /* Preserve upstream's contract for callbacks that reject NULL. */
        uint8_t temporary[16];

        while (count > sizeof(temporary)) {
            if (!open_cfw_nanopb_read(
                    stream,
                    temporary,
                    sizeof(temporary)
                )) {
                return false;
            }

            count -= sizeof(temporary);
        }

        return open_cfw_nanopb_read(stream, temporary, count);
    }

    if (stream->bytes_left < count) {
        return open_cfw_nanopb_read_error(
            stream,
            open_cfw_nanopb_end_of_stream_error
        );
    }

    if (!stream->callback(stream, buffer, count)) {
        return open_cfw_nanopb_read_error(
            stream,
            open_cfw_nanopb_io_error
        );
    }

    /* The callback may alter bytes_left; reload it before accounting. */
    if (stream->bytes_left < count) {
        stream->bytes_left = 0U;
    } else {
        stream->bytes_left -= count;
    }

    return true;
}
