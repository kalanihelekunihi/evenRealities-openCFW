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
 * Production compatibility ABI for nanopb's private pb_dec_varint().
 */

#ifndef OPEN_CFW_RUNTIME_NANOPB_DEC_VARINT_H
#define OPEN_CFW_RUNTIME_NANOPB_DEC_VARINT_H

#include <stdbool.h>
#include <stdint.h>

#include "runtime_nanopb_dec_bool.h"
#include "runtime_nanopb_decode_svarint.h"

enum open_cfw_nanopb_ltype {
    OPEN_CFW_NANOPB_LTYPE_VARINT = 0x01U,
    OPEN_CFW_NANOPB_LTYPE_UVARINT = 0x02U,
    OPEN_CFW_NANOPB_LTYPE_SVARINT = 0x03U,
    OPEN_CFW_NANOPB_LTYPE_MASK = 0x0FU
};

bool open_cfw_nanopb_dec_varint(
    struct open_cfw_nanopb_istream *stream,
    const struct open_cfw_nanopb_field_iter *field
);

_Static_assert(sizeof(uint64_t) == 8U, "G2 nanopb uint64 width");
_Static_assert(sizeof(int64_t) == 8U, "G2 nanopb int64 width");
_Static_assert(sizeof(uint32_t) == 4U, "G2 nanopb uint32 width");
_Static_assert(sizeof(int32_t) == 4U, "G2 nanopb int32 width");
_Static_assert(sizeof(uint16_t) == 2U, "G2 nanopb uint16 width");
_Static_assert(sizeof(int16_t) == 2U, "G2 nanopb int16 width");
_Static_assert(sizeof(uint8_t) == 1U, "G2 nanopb uint8 width");
_Static_assert(sizeof(int8_t) == 1U, "G2 nanopb int8 width");

#endif /* OPEN_CFW_RUNTIME_NANOPB_DEC_VARINT_H */
