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
 * Altered production compatibility ABI for nanopb pb_skip_field(). The
 * selected nanopb 0.4.9 source is a maintained compatibility baseline for the
 * recovered G2 0.4.7--0.4.9 runtime interval, not proof of the vendor checkout.
 */

#ifndef OPEN_CFW_RUNTIME_NANOPB_SKIP_FIELD_H
#define OPEN_CFW_RUNTIME_NANOPB_SKIP_FIELD_H

#include "runtime_nanopb_skip_string.h"
#include "runtime_nanopb_skip_varint.h"

enum open_cfw_nanopb_wire_type {
    OPEN_CFW_NANOPB_WT_VARINT = 0,
    OPEN_CFW_NANOPB_WT_64BIT = 1,
    OPEN_CFW_NANOPB_WT_STRING = 2,
    OPEN_CFW_NANOPB_WT_32BIT = 5,
    OPEN_CFW_NANOPB_WT_PACKED = 255
};

bool open_cfw_nanopb_skip_field(
    struct open_cfw_nanopb_istream *stream,
    uint8_t wire_type
);

#if __SIZEOF_POINTER__ == 4
_Static_assert(sizeof(bool) == 1U, "G2 nanopb bool width");
_Static_assert(sizeof(size_t) == 4U, "G2 nanopb size_t width");
_Static_assert(sizeof(uint8_t) == 1U, "G2 nanopb wire-type width");
_Static_assert(
    offsetof(struct open_cfw_nanopb_istream, errmsg) == 12U,
    "G2 pb_istream_t errmsg offset"
);
_Static_assert(
    sizeof(struct open_cfw_nanopb_istream) == 16U,
    "G2 pb_istream_t size"
);
#endif

#endif /* OPEN_CFW_RUNTIME_NANOPB_SKIP_FIELD_H */
