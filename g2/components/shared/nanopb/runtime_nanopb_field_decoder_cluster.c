/*
 * Copyright (c) 2011 Petteri Aimonen <jpa at nanopb.mail.kapsi.fi>
 *
 * This software is provided 'as-is', without any express or implied warranty.
 * Permission is granted to use, alter, and redistribute this software subject
 * to the nanopb Zlib license requirements.
 *
 * Altered production source for nanopb's private decode_basic_field(),
 * decode_static_field(), no-malloc decode_pointer_field(),
 * decode_callback_field(), and pb_dec_fixed_length_bytes(). The selected
 * compatibility baseline is authenticated nanopb 0.4.9 commit
 * 98bf4db69897b53434f3d0ba72e0a3ab1a902824. The recovered G2 field cluster
 * occupies [0x0048F7F4,0x0048FBE4); the fixed-length leaf occupies
 * [0x0049053C,0x004905A8). All fixed executable dependencies are separately
 * source-owned. Dynamic field callbacks remain application/schema ABI.
 */

#include <stddef.h>
#include <stdint.h>

#include "runtime_nanopb_field_decoder_cluster.h"
#include "runtime_nanopb_close_string_substream.h"
#include "runtime_nanopb_dec_bytes.h"
#include "runtime_nanopb_dec_string.h"
#include "runtime_nanopb_dec_varint.h"
#include "runtime_nanopb_decode_fixed32.h"
#include "runtime_nanopb_decode_fixed64.h"
#include "runtime_nanopb_defaults_pair.h"
#include "runtime_nanopb_istream_from_buffer.h"
#include "runtime_nanopb_make_string_substream.h"
#include "runtime_nanopb_read_raw_value.h"

bool open_cfw_nanopb_dec_submessage(
    struct open_cfw_nanopb_istream *stream,
    const struct open_cfw_nanopb_field_iter *field
);

#ifndef OPEN_CFW_NANOPB_FIELD_DECODER_SELECTION
#define OPEN_CFW_NANOPB_FIELD_DECODER_SELECTION 5
#endif

enum {
    OPEN_CFW_FIELD_LTYPE_MASK = 0x0FU,
    OPEN_CFW_FIELD_LTYPE_BOOL = 0x00U,
    OPEN_CFW_FIELD_LTYPE_VARINT = 0x01U,
    OPEN_CFW_FIELD_LTYPE_UVARINT = 0x02U,
    OPEN_CFW_FIELD_LTYPE_SVARINT = 0x03U,
    OPEN_CFW_FIELD_LTYPE_FIXED32 = 0x04U,
    OPEN_CFW_FIELD_LTYPE_FIXED64 = 0x05U,
    OPEN_CFW_FIELD_LTYPE_BYTES = 0x06U,
    OPEN_CFW_FIELD_LTYPE_STRING = 0x07U,
    OPEN_CFW_FIELD_LTYPE_SUBMESSAGE = 0x08U,
    OPEN_CFW_FIELD_LTYPE_SUBMSG_W_CB = 0x09U,
    OPEN_CFW_FIELD_LTYPE_FIXED_LENGTH_BYTES = 0x0BU,
    OPEN_CFW_FIELD_LTYPE_LAST_PACKABLE = 0x05U,
    OPEN_CFW_FIELD_HTYPE_MASK = 0x30U,
    OPEN_CFW_FIELD_HTYPE_REQUIRED = 0x00U,
    OPEN_CFW_FIELD_HTYPE_OPTIONAL = 0x10U,
    OPEN_CFW_FIELD_HTYPE_REPEATED = 0x20U,
    OPEN_CFW_FIELD_HTYPE_ONEOF = 0x30U,
    OPEN_CFW_FIELD_WT_VARINT = 0x00U,
    OPEN_CFW_FIELD_WT_64BIT = 0x01U,
    OPEN_CFW_FIELD_WT_STRING = 0x02U,
    OPEN_CFW_FIELD_WT_32BIT = 0x05U,
    OPEN_CFW_FIELD_WT_PACKED = 0xFFU
};

#if OPEN_CFW_NANOPB_FIELD_DECODER_SELECTION == 0 \
    || OPEN_CFW_NANOPB_FIELD_DECODER_SELECTION == 1 \
    || OPEN_CFW_NANOPB_FIELD_DECODER_SELECTION == 2 \
    || OPEN_CFW_NANOPB_FIELD_DECODER_SELECTION == 3 \
    || OPEN_CFW_NANOPB_FIELD_DECODER_SELECTION == 4 \
    || OPEN_CFW_NANOPB_FIELD_DECODER_SELECTION == 5
static bool open_cfw_nanopb_field_decoder_fail(
    struct open_cfw_nanopb_istream *stream,
    const char *message
)
{
    if (stream->errmsg == NULL) {
        stream->errmsg = message;
    }
    return false;
}
#endif

#if OPEN_CFW_NANOPB_FIELD_DECODER_SELECTION == 1 \
    || OPEN_CFW_NANOPB_FIELD_DECODER_SELECTION == 4 \
    || OPEN_CFW_NANOPB_FIELD_DECODER_SELECTION == 5
static void open_cfw_nanopb_field_decoder_zero(
    void *destination,
    size_t count
)
{
    uint8_t *cursor = (uint8_t *)destination;
    while (count != 0U) {
        *cursor++ = 0U;
        --count;
    }
}
#endif

#if OPEN_CFW_NANOPB_FIELD_DECODER_SELECTION == 0 \
    || OPEN_CFW_NANOPB_FIELD_DECODER_SELECTION == 5
bool open_cfw_nanopb_decode_basic_field(
    struct open_cfw_nanopb_istream *stream,
    unsigned int wire_type,
    struct open_cfw_nanopb_field_iter *field
)
{
    unsigned int logical_type = field->type & OPEN_CFW_FIELD_LTYPE_MASK;

    switch (logical_type) {
    case OPEN_CFW_FIELD_LTYPE_BOOL:
        if (wire_type != OPEN_CFW_FIELD_WT_VARINT
            && wire_type != OPEN_CFW_FIELD_WT_PACKED) {
            return open_cfw_nanopb_field_decoder_fail(
                stream, "wrong wire type");
        }
        return open_cfw_nanopb_dec_bool(stream, field);

    case OPEN_CFW_FIELD_LTYPE_VARINT:
    case OPEN_CFW_FIELD_LTYPE_UVARINT:
    case OPEN_CFW_FIELD_LTYPE_SVARINT:
        if (wire_type != OPEN_CFW_FIELD_WT_VARINT
            && wire_type != OPEN_CFW_FIELD_WT_PACKED) {
            return open_cfw_nanopb_field_decoder_fail(
                stream, "wrong wire type");
        }
        return open_cfw_nanopb_dec_varint(stream, field);

    case OPEN_CFW_FIELD_LTYPE_FIXED32:
        if (wire_type != OPEN_CFW_FIELD_WT_32BIT
            && wire_type != OPEN_CFW_FIELD_WT_PACKED) {
            return open_cfw_nanopb_field_decoder_fail(
                stream, "wrong wire type");
        }
        return open_cfw_nanopb_decode_fixed32(stream, field->data);

    case OPEN_CFW_FIELD_LTYPE_FIXED64:
        if (wire_type != OPEN_CFW_FIELD_WT_64BIT
            && wire_type != OPEN_CFW_FIELD_WT_PACKED) {
            return open_cfw_nanopb_field_decoder_fail(
                stream, "wrong wire type");
        }
        return open_cfw_nanopb_decode_fixed64(stream, field->data);

    case OPEN_CFW_FIELD_LTYPE_BYTES:
        if (wire_type != OPEN_CFW_FIELD_WT_STRING) {
            return open_cfw_nanopb_field_decoder_fail(
                stream, "wrong wire type");
        }
        return open_cfw_nanopb_dec_bytes(stream, field);

    case OPEN_CFW_FIELD_LTYPE_STRING:
        if (wire_type != OPEN_CFW_FIELD_WT_STRING) {
            return open_cfw_nanopb_field_decoder_fail(
                stream, "wrong wire type");
        }
        return open_cfw_nanopb_dec_string(stream, field);

    case OPEN_CFW_FIELD_LTYPE_SUBMESSAGE:
    case OPEN_CFW_FIELD_LTYPE_SUBMSG_W_CB:
        if (wire_type != OPEN_CFW_FIELD_WT_STRING) {
            return open_cfw_nanopb_field_decoder_fail(
                stream, "wrong wire type");
        }
        return open_cfw_nanopb_dec_submessage(stream, field);

    case OPEN_CFW_FIELD_LTYPE_FIXED_LENGTH_BYTES:
        if (wire_type != OPEN_CFW_FIELD_WT_STRING) {
            return open_cfw_nanopb_field_decoder_fail(
                stream, "wrong wire type");
        }
        return open_cfw_nanopb_dec_fixed_length_bytes(stream, field);

    default:
        return open_cfw_nanopb_field_decoder_fail(
            stream, "invalid field type");
    }
}
#endif

#if OPEN_CFW_NANOPB_FIELD_DECODER_SELECTION == 1 \
    || OPEN_CFW_NANOPB_FIELD_DECODER_SELECTION == 5
bool open_cfw_nanopb_decode_static_field(
    struct open_cfw_nanopb_istream *stream,
    unsigned int wire_type,
    struct open_cfw_nanopb_field_iter *field
)
{
    unsigned int high_type = field->type & OPEN_CFW_FIELD_HTYPE_MASK;

    switch (high_type) {
    case OPEN_CFW_FIELD_HTYPE_REQUIRED:
        return open_cfw_nanopb_decode_basic_field(
            stream, wire_type, field);

    case OPEN_CFW_FIELD_HTYPE_OPTIONAL:
        if (field->size != NULL) {
            *(bool *)field->size = true;
        }
        return open_cfw_nanopb_decode_basic_field(
            stream, wire_type, field);

    case OPEN_CFW_FIELD_HTYPE_REPEATED:
        if (wire_type == OPEN_CFW_FIELD_WT_STRING
            && (field->type & OPEN_CFW_FIELD_LTYPE_MASK)
                <= OPEN_CFW_FIELD_LTYPE_LAST_PACKABLE) {
            bool status = true;
            uint16_t *size = (uint16_t *)field->size;
            struct open_cfw_nanopb_istream substream;

            field->data = (uint8_t *)field->field
                + (size_t)field->data_size * *size;
            if (!open_cfw_nanopb_make_string_substream(
                    stream, &substream)) {
                return false;
            }
            while (substream.bytes_left > 0U && *size < field->array_size) {
                if (!open_cfw_nanopb_decode_basic_field(
                        &substream, OPEN_CFW_FIELD_WT_PACKED, field)) {
                    status = false;
                    break;
                }
                ++*size;
                field->data = (uint8_t *)field->data + field->data_size;
            }
            if (substream.bytes_left != 0U) {
                return open_cfw_nanopb_field_decoder_fail(
                    stream, "array overflow");
            }
            if (!open_cfw_nanopb_close_string_substream(
                    stream, &substream)) {
                return false;
            }
            return status;
        } else {
            uint16_t *size = (uint16_t *)field->size;
            field->data = (uint8_t *)field->field
                + (size_t)field->data_size * *size;
            if ((*size)++ >= field->array_size) {
                return open_cfw_nanopb_field_decoder_fail(
                    stream, "array overflow");
            }
            return open_cfw_nanopb_decode_basic_field(
                stream, wire_type, field);
        }

    case OPEN_CFW_FIELD_HTYPE_ONEOF:
        if (((field->type & OPEN_CFW_FIELD_LTYPE_MASK)
                == OPEN_CFW_FIELD_LTYPE_SUBMESSAGE
             || (field->type & OPEN_CFW_FIELD_LTYPE_MASK)
                == OPEN_CFW_FIELD_LTYPE_SUBMSG_W_CB)
            && *(uint16_t *)field->size != field->tag) {
            const struct open_cfw_nanopb_msgdesc *submessage =
                (const struct open_cfw_nanopb_msgdesc *)
                    field->submessage_descriptor;

            open_cfw_nanopb_field_decoder_zero(
                field->data, field->data_size);
            if (submessage->default_value != NULL
                || submessage->field_callback != NULL
                || submessage->submessage_info[0] != NULL) {
                struct open_cfw_nanopb_field_iter submessage_iter;
                if (open_cfw_nanopb_field_iter_begin(
                        &submessage_iter, submessage, field->data)
                    && !open_cfw_nanopb_message_set_to_defaults(
                        &submessage_iter)) {
                    return open_cfw_nanopb_field_decoder_fail(
                        stream, "failed to set defaults");
                }
            }
        }
        *(uint16_t *)field->size = field->tag;
        return open_cfw_nanopb_decode_basic_field(
            stream, wire_type, field);

    default:
        return open_cfw_nanopb_field_decoder_fail(
            stream, "invalid field type");
    }
}
#endif

#if OPEN_CFW_NANOPB_FIELD_DECODER_SELECTION == 2 \
    || OPEN_CFW_NANOPB_FIELD_DECODER_SELECTION == 5
bool open_cfw_nanopb_decode_pointer_field(
    struct open_cfw_nanopb_istream *stream,
    unsigned int wire_type,
    struct open_cfw_nanopb_field_iter *field
)
{
    (void)wire_type;
    (void)field;
    return open_cfw_nanopb_field_decoder_fail(
        stream, "no malloc support");
}
#endif

#if OPEN_CFW_NANOPB_FIELD_DECODER_SELECTION == 3 \
    || OPEN_CFW_NANOPB_FIELD_DECODER_SELECTION == 5
typedef bool (*open_cfw_nanopb_dynamic_field_callback)(
    struct open_cfw_nanopb_istream *istream,
    void *ostream,
    const struct open_cfw_nanopb_field_iter *field
);

static open_cfw_nanopb_dynamic_field_callback
open_cfw_nanopb_get_dynamic_field_callback(
    const struct open_cfw_nanopb_msgdesc *descriptor
)
{
    union {
        bool (*generic)(void);
        open_cfw_nanopb_dynamic_field_callback callback;
    } conversion;
    conversion.generic = descriptor->field_callback;
    return conversion.callback;
}

bool open_cfw_nanopb_decode_callback_field(
    struct open_cfw_nanopb_istream *stream,
    unsigned int wire_type,
    struct open_cfw_nanopb_field_iter *field
)
{
    const struct open_cfw_nanopb_msgdesc *descriptor =
        (const struct open_cfw_nanopb_msgdesc *)field->descriptor;
    open_cfw_nanopb_dynamic_field_callback callback =
        open_cfw_nanopb_get_dynamic_field_callback(descriptor);

    if (callback == NULL) {
        return open_cfw_nanopb_skip_field(stream, (uint8_t)wire_type);
    }

    if (wire_type == OPEN_CFW_FIELD_WT_STRING) {
        struct open_cfw_nanopb_istream substream;
        size_t previous_bytes_left;

        if (!open_cfw_nanopb_make_string_substream(stream, &substream)) {
            return false;
        }
        do {
            previous_bytes_left = substream.bytes_left;
            if (!callback(&substream, NULL, field)) {
                const char *message = substream.errmsg != NULL
                    ? substream.errmsg : "callback failed";
                return open_cfw_nanopb_field_decoder_fail(stream, message);
            }
        } while (substream.bytes_left > 0U
                 && substream.bytes_left < previous_bytes_left);

        if (!open_cfw_nanopb_close_string_substream(
                stream, &substream)) {
            return false;
        }
        return true;
    } else {
        uint8_t buffer[10];
        size_t size = sizeof(buffer);
        struct open_cfw_nanopb_istream substream;

        if (!open_cfw_nanopb_read_raw_value(
                stream, (uint8_t)wire_type, buffer, &size)) {
            return false;
        }
        substream = open_cfw_nanopb_istream_from_buffer(buffer, size);
        return callback(&substream, NULL, field);
    }
}
#endif

#if OPEN_CFW_NANOPB_FIELD_DECODER_SELECTION == 4 \
    || OPEN_CFW_NANOPB_FIELD_DECODER_SELECTION == 5
bool open_cfw_nanopb_dec_fixed_length_bytes(
    struct open_cfw_nanopb_istream *stream,
    const struct open_cfw_nanopb_field_iter *field
)
{
    uint32_t size;

    if (!open_cfw_nanopb_decode_varint32(stream, &size)) {
        return false;
    }
    if (size > UINT16_MAX) {
        return open_cfw_nanopb_field_decoder_fail(
            stream, "bytes overflow");
    }
    if (size == 0U) {
        open_cfw_nanopb_field_decoder_zero(
            field->data, field->data_size);
        return true;
    }
    if (size != field->data_size) {
        return open_cfw_nanopb_field_decoder_fail(
            stream, "incorrect fixed length bytes size");
    }
    return open_cfw_nanopb_read(
        stream, (uint8_t *)field->data, field->data_size);
}
#endif
