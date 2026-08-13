/*
 * Copyright (c) 2011 Petteri Aimonen <jpa at nanopb.mail.kapsi.fi>
 *
 * This software is provided 'as-is', without any express or implied warranty.
 * In no event will the authors be held liable for any damages arising from
 * the use of this software.
 *
 * Permission is granted to anyone to use this software for any purpose,
 * including commercial applications, and to alter it and redistribute it
 * freely, subject to the restrictions in the nanopb Zlib license.
 *
 * Altered production source for nanopb's private pb_dec_submessage(). The
 * selected compatibility baseline is authenticated nanopb 0.4.9 commit
 * 98bf4db69897b53434f3d0ba72e0a3ab1a902824. The recovered G2 body occupies
 * [0x0049048C, 0x00490538). pb_decode_inner remains an explicit stock seam at
 * 0x0048FE98 until that larger decoder is independently reconstructed.
 */

#include <stdint.h>

#include "runtime_nanopb_dec_submessage.h"

enum {
    OPEN_CFW_NANOPB_LTYPE_MASK = 0x0FU,
    OPEN_CFW_NANOPB_LTYPE_SUBMSG_W_CB = 0x09U,
    OPEN_CFW_NANOPB_HTYPE_MASK = 0x30U,
    OPEN_CFW_NANOPB_HTYPE_REPEATED = 0x20U,
    OPEN_CFW_NANOPB_DECODE_NOINIT = 0x01U
};

static const char open_cfw_nanopb_dec_submessage_error[] =
    "invalid field descriptor";

static bool open_cfw_nanopb_dec_submessage_fail(
    struct open_cfw_nanopb_istream *stream
)
{
    if (stream->errmsg == NULL) {
        stream->errmsg = open_cfw_nanopb_dec_submessage_error;
    }
    return false;
}

bool open_cfw_nanopb_dec_submessage(
    struct open_cfw_nanopb_istream *stream,
    const struct open_cfw_nanopb_field_iter *field
)
{
    bool status = true;
    bool submessage_consumed = false;
    struct open_cfw_nanopb_istream substream;

    if (!open_cfw_nanopb_make_string_substream(stream, &substream)) {
        return false;
    }

    if (field->submessage_descriptor == NULL) {
        return open_cfw_nanopb_dec_submessage_fail(stream);
    }

    if ((field->type & OPEN_CFW_NANOPB_LTYPE_MASK)
            == OPEN_CFW_NANOPB_LTYPE_SUBMSG_W_CB
        && field->size != NULL) {
        struct open_cfw_nanopb_callback *callback =
            (struct open_cfw_nanopb_callback *)field->size - 1;
        if (callback->decode != NULL) {
            status = callback->decode(&substream, field, &callback->argument);
            if (substream.bytes_left == 0U) {
                submessage_consumed = true;
            }
        }
    }

    if (status && !submessage_consumed) {
        unsigned int flags = 0U;
        if ((field->type & OPEN_CFW_NANOPB_ATYPE_MASK) == 0U
            && (field->type & OPEN_CFW_NANOPB_HTYPE_MASK)
                != OPEN_CFW_NANOPB_HTYPE_REPEATED) {
            flags = OPEN_CFW_NANOPB_DECODE_NOINIT;
        }
        status = open_cfw_nanopb_decode_inner(
            &substream,
            field->submessage_descriptor,
            field->data,
            flags
        );
    }

    if (!open_cfw_nanopb_close_string_substream(stream, &substream)) {
        return false;
    }

    return status;
}
