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
 * Production-excluded compatibility ABI for nanopb read_raw_value().
 */

#ifndef OPEN_CFW_RUNTIME_NANOPB_READ_RAW_VALUE_CANDIDATE_H
#define OPEN_CFW_RUNTIME_NANOPB_READ_RAW_VALUE_CANDIDATE_H

#include "runtime_nanopb_read.h"

enum open_cfw_nanopb_raw_wire_type {
    OPEN_CFW_NANOPB_RAW_WT_VARINT = 0,
    OPEN_CFW_NANOPB_RAW_WT_64BIT = 1,
    OPEN_CFW_NANOPB_RAW_WT_STRING = 2,
    OPEN_CFW_NANOPB_RAW_WT_32BIT = 5
};

bool open_cfw_nanopb_read_raw_value_candidate(
    struct open_cfw_nanopb_istream *stream,
    uint8_t wire_type,
    uint8_t *buffer,
    size_t *size
);

#if __SIZEOF_POINTER__ == 4
_Static_assert(sizeof(size_t) == 4U, "G2 nanopb size_t width");
_Static_assert(sizeof(struct open_cfw_nanopb_istream) == 16U, "G2 stream ABI");
#endif

#endif /* OPEN_CFW_RUNTIME_NANOPB_READ_RAW_VALUE_CANDIDATE_H */
