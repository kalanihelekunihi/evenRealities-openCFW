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
 * Production compatibility ABI for nanopb's private pb_dec_bool() adapter.
 */

#ifndef OPEN_CFW_RUNTIME_NANOPB_DEC_BOOL_H
#define OPEN_CFW_RUNTIME_NANOPB_DEC_BOOL_H

#include <stddef.h>
#include <stdint.h>

#include "runtime_nanopb_decode_bool.h"

struct open_cfw_nanopb_field_iter {
    const void *descriptor;
    void *message;
    uint16_t index;
    uint16_t field_info_index;
    uint16_t required_field_index;
    uint16_t submessage_index;
    uint16_t tag;
    uint16_t data_size;
    uint16_t array_size;
    uint8_t type;
    uint8_t reserved;
    void *field;
    void *data;
    void *size;
    const void *submessage_descriptor;
};

bool open_cfw_nanopb_dec_bool(
    struct open_cfw_nanopb_istream *stream,
    const struct open_cfw_nanopb_field_iter *field
);

#if __SIZEOF_POINTER__ == 4
_Static_assert(
    offsetof(struct open_cfw_nanopb_field_iter, data) == 0x1CU,
    "G2 nanopb field iterator data offset"
);
_Static_assert(
    sizeof(struct open_cfw_nanopb_field_iter) == 0x28U,
    "G2 nanopb field iterator size"
);
#endif

#endif /* OPEN_CFW_RUNTIME_NANOPB_DEC_BOOL_H */
