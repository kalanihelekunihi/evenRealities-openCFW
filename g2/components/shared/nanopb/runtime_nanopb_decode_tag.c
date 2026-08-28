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
 * Altered production source for nanopb pb_decode_tag(). The authenticated
 * compatibility baseline is nanopb 0.4.9 commit
 * 98bf4db69897b53434f3d0ba72e0a3ab1a902824. The recovered G2 body occupies
 * [0x0048F66C, 0x0048F6A0) and calls the source-owned varint32/eof decoder.
 */

#include "runtime_nanopb_decode_tag.h"

bool open_cfw_nanopb_decode_tag(
    struct open_cfw_nanopb_istream *stream,
    uint8_t *wire_type,
    uint32_t *tag,
    bool *eof
)
{
    uint32_t temporary;

    *eof = false;
    *wire_type = 0U;
    *tag = 0U;

    if (!open_cfw_nanopb_decode_varint32_eof(
            stream, &temporary, eof)) {
        return false;
    }

    *tag = temporary >> 3;
    *wire_type = (uint8_t)(temporary & 7U);
    return true;
}
