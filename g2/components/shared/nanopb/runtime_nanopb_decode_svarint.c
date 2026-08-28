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
 * Altered production source for nanopb pb_decode_svarint(). The selected
 * compatibility baseline is the
 * authenticated nanopb-0.4.9 snapshot at commit
 * 98bf4db69897b53434f3d0ba72e0a3ab1a902824. Controlled reference builds
 * cannot distinguish pristine nanopb 0.4.7, 0.4.8, and 0.4.9 on the G2
 * target, so this selection is not proof of the vendor's historical point
 * release or checkout.
 *
 * The G2 stock body occupies [0x00490150, 0x00490190). The production overlay
 * binds its unsigned-varint call directly to the source-owned decoder.
 */

#include "runtime_nanopb_decode_svarint.h"

bool open_cfw_nanopb_decode_svarint(
    struct open_cfw_nanopb_istream *stream,
    int64_t *destination
)
{
    uint64_t value;

    if (!open_cfw_nanopb_decode_varint(stream, &value)) {
        return false;
    }

    if ((value & UINT64_C(1)) != UINT64_C(0)) {
        *destination = (int64_t)(~(value >> 1U));
    } else {
        *destination = (int64_t)(value >> 1U);
    }

    return true;
}
