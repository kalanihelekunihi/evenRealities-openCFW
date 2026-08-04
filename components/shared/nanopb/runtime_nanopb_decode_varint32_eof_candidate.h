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
 * Production-excluded compatibility ABI for nanopb's private
 * pb_decode_varint32_eof(). This is altered source, not proof of the vendor's
 * historical checkout.
 */

#ifndef OPEN_CFW_RUNTIME_NANOPB_DECODE_VARINT32_EOF_CANDIDATE_H
#define OPEN_CFW_RUNTIME_NANOPB_DECODE_VARINT32_EOF_CANDIDATE_H

#include "runtime_nanopb_decode_varint.h"

enum {
    OPEN_CFW_NANOPB_DECODE_VARINT32_EOF_STOCK_ADDRESS = 0x0048F4B8U,
    OPEN_CFW_NANOPB_DECODE_VARINT32_EOF_READBYTE_ADDRESS = 0x0048F454U,
    OPEN_CFW_NANOPB_VARINT_OVERFLOW_STRING_ADDRESS = 0x00787C80U
};

bool open_cfw_nanopb_decode_varint32_eof_source_candidate(
    struct open_cfw_nanopb_istream *stream,
    uint32_t *destination,
    bool *eof
);

#if __SIZEOF_POINTER__ == 4
_Static_assert(sizeof(bool) == 1U, "G2 nanopb bool width");
_Static_assert(sizeof(uint8_t) == 1U, "G2 nanopb byte width");
_Static_assert(sizeof(uint32_t) == 4U, "G2 nanopb uint32_t width");
_Static_assert(sizeof(uint_fast8_t) >= 1U, "nanopb bit-position width");
#endif

#endif /* OPEN_CFW_RUNTIME_NANOPB_DECODE_VARINT32_EOF_CANDIDATE_H */
