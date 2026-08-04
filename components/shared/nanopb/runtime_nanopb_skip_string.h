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
 * Altered production compatibility ABI for nanopb's private pb_skip_string().
 * The selected nanopb 0.4.9 snapshot is a compatibility baseline, not proof
 * of the vendor's historical nanopb point release.
 */

#ifndef OPEN_CFW_RUNTIME_NANOPB_SKIP_STRING_H
#define OPEN_CFW_RUNTIME_NANOPB_SKIP_STRING_H

#include "runtime_nanopb_decode_varint32.h"
#include "runtime_nanopb_read.h"

bool open_cfw_nanopb_skip_string(
    struct open_cfw_nanopb_istream *stream
);

#if __SIZEOF_POINTER__ == 4
_Static_assert(sizeof(size_t) == 4U, "G2 nanopb size_t width");
_Static_assert(sizeof(uint32_t) == 4U, "G2 nanopb uint32_t width");
_Static_assert(
    sizeof(size_t) == sizeof(uint32_t),
    "G2 skip-string length conversion is lossless"
);
#endif

#endif /* OPEN_CFW_RUNTIME_NANOPB_SKIP_STRING_H */
