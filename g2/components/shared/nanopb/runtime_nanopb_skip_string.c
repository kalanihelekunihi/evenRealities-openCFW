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
 * Altered production adaptation of nanopb 0.4.9 pb_skip_string(). The
 * authenticated definition is byte-identical in pristine nanopb 0.4.7 through
 * 0.4.9; this compatibility baseline is not proof of the vendor's historical
 * nanopb point release. On the G2 ABI size_t and uint32_t are both 32 bits, so
 * upstream's length-conversion guard is tautologically false. Both surviving
 * calls bind directly to already source-owned openCFW providers.
 */

#include "runtime_nanopb_skip_string.h"

bool open_cfw_nanopb_skip_string(struct open_cfw_nanopb_istream *stream)
{
    uint32_t length;

    if (!open_cfw_nanopb_decode_varint32(stream, &length)) {
        return false;
    }

    return open_cfw_nanopb_read(stream, NULL, (size_t)length);
}
