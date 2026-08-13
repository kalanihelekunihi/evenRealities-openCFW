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
 * Production openCFW compatibility ABI for nanopb's pb_decode_svarint(). The
 * implementation reuses the production-qualified G2 callback-stream ABI and
 * source-owned unsigned-varint provider. It is altered source, not pristine
 * upstream source and not proof of the vendor's historical nanopb point
 * release.
 */

#ifndef OPEN_CFW_RUNTIME_NANOPB_DECODE_SVARINT_H
#define OPEN_CFW_RUNTIME_NANOPB_DECODE_SVARINT_H

#include <stdbool.h>
#include <stdint.h>

#include "runtime_nanopb_decode_varint.h"

bool open_cfw_nanopb_decode_svarint(
    struct open_cfw_nanopb_istream *stream,
    int64_t *destination
);

_Static_assert(sizeof(int64_t) == 8U, "G2 nanopb signed-varint width");
_Static_assert(sizeof(uint64_t) == 8U, "G2 nanopb unsigned-varint width");
_Static_assert(INT64_MIN == (-INT64_MAX - INT64_C(1)), "two's-complement ABI");

#endif
