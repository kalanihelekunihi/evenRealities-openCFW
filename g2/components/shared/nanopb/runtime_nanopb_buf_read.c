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
 * Altered production source adaptation of nanopb's private buf_read(). The
 * authenticated nanopb-0.4.9 compatibility baseline is commit
 * 98bf4db69897b53434f3d0ba72e0a3ab1a902824; this does not prove the vendor's
 * historical point release. Stock entry [0x0048F3A4,0x0048F3BE) redirects
 * here while preserving canonical Thumb callback identity 0x0048F3A5.
 */

#include "runtime_nanopb_private_read_pair.h"

bool open_cfw_nanopb_buf_read(
    struct open_cfw_nanopb_istream *stream,
    uint8_t *buffer,
    size_t count
)
{
    const uint8_t *source = (const uint8_t *)stream->state;

    stream->state = (uint8_t *)stream->state + count;

    if (buffer != NULL) {
        __aeabi_memcpy(buffer, source, count);
    }

    return true;
}
