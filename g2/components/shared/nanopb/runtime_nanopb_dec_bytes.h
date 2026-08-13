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
 * Production compatibility ABI for nanopb's private pb_dec_bytes().
 */

#ifndef OPEN_CFW_RUNTIME_NANOPB_DEC_BYTES_H
#define OPEN_CFW_RUNTIME_NANOPB_DEC_BYTES_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "runtime_nanopb_dec_bool.h"
#include "runtime_nanopb_decode_varint32.h"
#include "runtime_nanopb_read.h"

enum {
    OPEN_CFW_NANOPB_ATYPE_POINTER = 0x80U,
    OPEN_CFW_NANOPB_ATYPE_MASK = 0xC0U,
    OPEN_CFW_NANOPB_SIZE_MAX = UINT16_MAX
};

struct open_cfw_nanopb_bytes_array {
    uint16_t size;
    uint8_t bytes[];
};

bool open_cfw_nanopb_dec_bytes(
    struct open_cfw_nanopb_istream *stream,
    const struct open_cfw_nanopb_field_iter *field
);

_Static_assert(
    offsetof(struct open_cfw_nanopb_bytes_array, bytes) == 2U,
    "G2 nanopb bytes-array payload offset"
);

#endif /* OPEN_CFW_RUNTIME_NANOPB_DEC_BYTES_H */
