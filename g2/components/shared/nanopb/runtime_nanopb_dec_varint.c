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
 * Altered production source for nanopb's private pb_dec_varint(). The selected
 * compatibility baseline is authenticated nanopb 0.4.9 commit
 * 98bf4db69897b53434f3d0ba72e0a3ab1a902824. The complete recovered G2 body
 * occupies [0x004901D6, 0x00490352). Its executable dependencies are the
 * separately source-owned public unsigned- and signed-varint decoders.
 */

#include "runtime_nanopb_dec_varint.h"

#include <stddef.h>

static const struct {
    char invalid_data_size[18];
    char integer_too_large[18];
} open_cfw_nanopb_dec_varint_errors = {
    "invalid data_size",
    "integer too large"
};

static bool open_cfw_nanopb_dec_varint_error(
    struct open_cfw_nanopb_istream *stream,
    const char *error
)
{
    if (stream->errmsg == NULL) {
        stream->errmsg = error;
    }
    return false;
}

bool open_cfw_nanopb_dec_varint(
    struct open_cfw_nanopb_istream *stream,
    const struct open_cfw_nanopb_field_iter *field
)
{
    const uint8_t ltype =
        (uint8_t)(field->type & OPEN_CFW_NANOPB_LTYPE_MASK);

    if (ltype == OPEN_CFW_NANOPB_LTYPE_UVARINT) {
        uint64_t value;
        uint64_t clamped;

        if (!open_cfw_nanopb_decode_varint(stream, &value)) {
            return false;
        }

        if (field->data_size == sizeof(uint64_t)) {
            clamped = *(uint64_t *)field->data = value;
        } else if (field->data_size == sizeof(uint32_t)) {
            clamped = *(uint32_t *)field->data = (uint32_t)value;
        } else if (field->data_size == sizeof(uint16_t)) {
            clamped = *(uint16_t *)field->data = (uint16_t)value;
        } else if (field->data_size == sizeof(uint8_t)) {
            clamped = *(uint8_t *)field->data = (uint8_t)value;
        } else {
            return open_cfw_nanopb_dec_varint_error(
                stream,
                open_cfw_nanopb_dec_varint_errors.invalid_data_size
            );
        }

        if (clamped != value) {
            return open_cfw_nanopb_dec_varint_error(
                stream,
                open_cfw_nanopb_dec_varint_errors.integer_too_large
            );
        }
        return true;
    }

    {
        uint64_t value;
        int64_t signed_value;
        int64_t clamped;

        if (ltype == OPEN_CFW_NANOPB_LTYPE_SVARINT) {
            if (!open_cfw_nanopb_decode_svarint(stream, &signed_value)) {
                return false;
            }
        } else {
            if (!open_cfw_nanopb_decode_varint(stream, &value)) {
                return false;
            }

            if (field->data_size == sizeof(int64_t)) {
                signed_value = (int64_t)value;
            } else {
                signed_value = (int32_t)value;
            }
        }

        if (field->data_size == sizeof(int64_t)) {
            clamped = *(int64_t *)field->data = signed_value;
        } else if (field->data_size == sizeof(int32_t)) {
            clamped = *(int32_t *)field->data = (int32_t)signed_value;
        } else if (field->data_size == sizeof(int16_t)) {
            clamped = *(int16_t *)field->data = (int16_t)signed_value;
        } else if (field->data_size == sizeof(int8_t)) {
            clamped = *(int8_t *)field->data = (int8_t)signed_value;
        } else {
            return open_cfw_nanopb_dec_varint_error(
                stream,
                open_cfw_nanopb_dec_varint_errors.invalid_data_size
            );
        }

        if (clamped != signed_value) {
            return open_cfw_nanopb_dec_varint_error(
                stream,
                open_cfw_nanopb_dec_varint_errors.integer_too_large
            );
        }
        return true;
    }
}
