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
 * Production altered source adaptation of nanopb 0.4.9 private
 * pb_decode_varint32_eof() and public pb_decode_varint32(). The formerly
 * private provider has a production link symbol and uses openCFW's shared
 * recovered stream ABI and explicit source-owned readbyte seam.
 */

#include "runtime_nanopb_decode_varint32.h"

#if !defined(OPENCFW_NANOPB_VARINT32_PUBLIC_LEAF_ONLY)
static const char open_cfw_nanopb_varint32_overflow_error[] =
    "varint overflow";

static bool open_cfw_nanopb_varint32_error(
    struct open_cfw_nanopb_istream *stream
)
{
    if (stream->errmsg == NULL) {
        stream->errmsg = open_cfw_nanopb_varint32_overflow_error;
    }

    return false;
}

bool open_cfw_nanopb_decode_varint32_eof(
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

    if ((byte & UINT8_C(0x80)) == 0U) {
        result = byte;
    } else {
        uint8_t bit_position = 7U;

        result = byte & UINT8_C(0x7F);
        do {
            if (!open_cfw_nanopb_readbyte(stream, &byte)) {
                return false;
            }

            if (bit_position >= 32U) {
                uint8_t sign_extension =
                    bit_position < 63U ? UINT8_C(0xFF) : UINT8_C(0x01);
                bool valid_extension =
                    (byte & UINT8_C(0x7F)) == 0U ||
                    ((result >> 31U) != 0U && byte == sign_extension);

                if (bit_position >= 64U || !valid_extension) {
                    return open_cfw_nanopb_varint32_error(stream);
                }
            } else if (bit_position == 28U) {
                if (
                    (byte & UINT8_C(0x70)) != 0U &&
                    (byte & UINT8_C(0x78)) != UINT8_C(0x78)
                ) {
                    return open_cfw_nanopb_varint32_error(stream);
                }
                result |= (uint32_t)(byte & UINT8_C(0x0F)) << bit_position;
            } else {
                result |= (uint32_t)(byte & UINT8_C(0x7F)) << bit_position;
            }
            bit_position = (uint8_t)(bit_position + 7U);
        } while ((byte & UINT8_C(0x80)) != 0U);
    }

    *destination = result;
    return true;
}

#endif

#if !defined(OPENCFW_NANOPB_VARINT32_PRIVATE_LEAF_ONLY)
__attribute__((disable_tail_calls))
bool open_cfw_nanopb_decode_varint32(
    struct open_cfw_nanopb_istream *stream,
    uint32_t *destination
)
{
    return open_cfw_nanopb_decode_varint32_eof(
        stream, destination, NULL
    );
}

#endif
