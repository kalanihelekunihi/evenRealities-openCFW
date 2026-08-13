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
 * Altered production source adaptation for nanopb
 * pb_decode_fixed32(). The selected source baseline is the authenticated
 * nanopb-0.4.9 snapshot at commit
 * 98bf4db69897b53434f3d0ba72e0a3ab1a902824. Exact definition evidence is
 * identical in pristine nanopb 0.4.7, 0.4.8, and 0.4.9; this compatibility
 * range is not proof of the vendor's historical point release.
 *
 * The G2 stock body occupies [0x00490190, 0x004901AC). Production integration
 * binds the single retained read seam to reviewed stock pb_read().
 */

#include "runtime_nanopb_decode_fixed32.h"

bool open_cfw_nanopb_decode_fixed32(
    struct open_cfw_nanopb_istream *stream,
    void *destination
)
{
    uint8_t bytes[4];
    uint32_t value;

    if (!open_cfw_nanopb_read(stream, bytes, sizeof(bytes))) {
        return false;
    }

    value = ((uint32_t)bytes[0] << 0U) |
            ((uint32_t)bytes[1] << 8U) |
            ((uint32_t)bytes[2] << 16U) |
            ((uint32_t)bytes[3] << 24U);
    *(uint32_t *)destination = value;
    return true;
}
