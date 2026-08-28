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
 * Altered production source for nanopb
 * pb_close_string_substream(). The selected source baseline is the
 * authenticated nanopb-0.4.9 snapshot at commit
 * 98bf4db69897b53434f3d0ba72e0a3ab1a902824. Authenticated evidence only
 * establishes pristine-runtime compatibility with nanopb 0.4.7 through
 * 0.4.9; this baseline is not proof of the vendor's historical point release.
 *
 * The G2 stock body occupies [0x0048F7CA, 0x0048F7F4). The production overlay
 * binds its complete three-argument read seam to the separately reviewed
 * stock pb_read at 0x0048F3BE.
 */

#include "runtime_nanopb_close_string_substream.h"

__attribute__((used, noinline))
bool open_cfw_nanopb_close_string_substream(
    struct open_cfw_nanopb_istream *stream,
    struct open_cfw_nanopb_istream *substream
)
{
    if (substream->bytes_left != 0U) {
        if (!open_cfw_nanopb_read(
                substream,
                (uint8_t *)0,
                substream->bytes_left
            )) {
            return false;
        }
    }

    stream->state = substream->state;
    stream->errmsg = substream->errmsg;
    return true;
}
