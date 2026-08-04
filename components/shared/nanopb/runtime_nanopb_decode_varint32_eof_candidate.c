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
 * Altered, production-excluded adaptation of nanopb 0.4.9 private
 * pb_decode_varint32_eof(). The authenticated definition is byte-identical in
 * pristine nanopb 0.4.7 through 0.4.9. The identified stock overflow string
 * is emitted from source; the only external code seam is pb_readbyte().
 */

#include "runtime_nanopb_decode_varint32_eof_candidate.h"

static const char open_cfw_nanopb_varint32_overflow_error[] =
    "varint overflow";

static bool open_cfw_nanopb_varint32_overflow(
    struct open_cfw_nanopb_istream *stream
)
{
    if (stream->errmsg == NULL) {
        stream->errmsg = open_cfw_nanopb_varint32_overflow_error;
    }
    return false;
}

bool open_cfw_nanopb_decode_varint32_eof_source_candidate(
    struct open_cfw_nanopb_istream *stream,
    uint32_t *destination,
    bool *eof
)
{
    uint8_t byte;
    uint32_t result;

    if (!open_cfw_nanopb_readbyte(stream, &byte)) {
        if (stream->bytes_left == 0U && eof != NULL) {
            *eof = true;
        }
        return false;
    }

    if ((byte & 0x80U) == 0U) {
        result = byte;
    } else {
        uint_fast8_t bit_position = 7U;
        result = byte & 0x7FU;

        do {
            uint8_t sign_extension;
            bool valid_extension;

            if (!open_cfw_nanopb_readbyte(stream, &byte)) {
                return false;
            }

            if (bit_position >= 32U) {
                sign_extension = bit_position < 63U ? 0xFFU : 0x01U;
                valid_extension = (
                    (byte & 0x7FU) == 0U ||
                    ((result >> 31) != 0U && byte == sign_extension)
                );
                if (bit_position >= 64U || !valid_extension) {
                    return open_cfw_nanopb_varint32_overflow(stream);
                }
            } else if (bit_position == 28U) {
                if (
                    (byte & 0x70U) != 0U &&
                    (byte & 0x78U) != 0x78U
                ) {
                    return open_cfw_nanopb_varint32_overflow(stream);
                }
                result |= (uint32_t)(byte & 0x0FU) << bit_position;
            } else {
                result |= (uint32_t)(byte & 0x7FU) << bit_position;
            }

            bit_position = (uint_fast8_t)(bit_position + 7U);
        } while ((byte & 0x80U) != 0U);
    }

    *destination = result;
    return true;
}
