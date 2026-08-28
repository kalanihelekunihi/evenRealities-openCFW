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
 * Altered production source adaptation of nanopb pb_decode_fixed64(). The
 * selected compatibility baseline is the
 * authenticated nanopb-0.4.9 snapshot at commit
 * 98bf4db69897b53434f3d0ba72e0a3ab1a902824. The complete definition is
 * byte-identical in pristine nanopb 0.4.7, 0.4.8, and 0.4.9; this does not
 * prove the vendor's historical point release or checkout.
 *
 * The G2 stock body occupies [0x004901AC, 0x004901CC). The Apollo-main
 * overlay redirects that complete span to this leaf. Its sole runtime
 * dependency remains the authenticated stock pb_read() provider at
 * 0x0048F3BE; this file does not claim source ownership of that provider.
 */

#include "runtime_nanopb_decode_fixed64.h"

bool open_cfw_nanopb_decode_fixed64(
    struct open_cfw_nanopb_istream *stream,
    void *destination
)
{
    union {
        uint64_t fixed64;
        uint8_t bytes[8];
    } value;

    if (!open_cfw_nanopb_read(stream, value.bytes, sizeof(value.bytes))) {
        return false;
    }

    /* Recovered G2 configuration selects nanopb's little-endian fast path. */
    *(uint64_t *)destination = value.fixed64;
    return true;
}
