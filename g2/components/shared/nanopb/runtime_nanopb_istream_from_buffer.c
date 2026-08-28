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
 * Altered production adaptation of nanopb 0.4.9
 * pb_istream_from_buffer(). The authenticated definition is byte-identical in
 * pristine nanopb 0.4.7 through 0.4.9. It deliberately retains canonical
 * stock callback identity 0x0048F3A5 rather than naming an appended leaf.
 */

#include "runtime_nanopb_istream_from_buffer.h"

struct open_cfw_nanopb_istream
open_cfw_nanopb_istream_from_buffer(
    const uint8_t *buffer,
    size_t message_length
)
{
    struct open_cfw_nanopb_istream stream;
    union {
        void *state;
        const void *constant_state;
    } state;

    stream.callback = open_cfw_nanopb_stock_buffer_read_identity;
    state.constant_state = buffer;
    stream.state = state.state;
    stream.bytes_left = message_length;
    stream.errmsg = NULL;

    return stream;
}
