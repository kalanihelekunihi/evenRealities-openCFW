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
 * Production compatibility ABI for nanopb's private pb_dec_submessage().
 */

#ifndef OPEN_CFW_RUNTIME_NANOPB_DEC_SUBMESSAGE_H
#define OPEN_CFW_RUNTIME_NANOPB_DEC_SUBMESSAGE_H

#include "runtime_nanopb_dec_string.h"
#include "runtime_nanopb_make_string_substream.h"
#include "runtime_nanopb_close_string_substream.h"

typedef bool (*open_cfw_nanopb_message_decode_callback)(
    struct open_cfw_nanopb_istream *stream,
    const struct open_cfw_nanopb_field_iter *field,
    void **argument
);

struct open_cfw_nanopb_callback {
    open_cfw_nanopb_message_decode_callback decode;
    void *argument;
};

bool open_cfw_nanopb_decode_inner(
    struct open_cfw_nanopb_istream *stream,
    const void *fields,
    void *destination,
    unsigned int flags
);

bool open_cfw_nanopb_dec_submessage(
    struct open_cfw_nanopb_istream *stream,
    const struct open_cfw_nanopb_field_iter *field
);

#if __SIZEOF_POINTER__ == 4
_Static_assert(sizeof(struct open_cfw_nanopb_callback) == 8U, "G2 callback ABI");
_Static_assert(offsetof(struct open_cfw_nanopb_field_iter, size) == 0x20U, "G2 pSize offset");
_Static_assert(offsetof(struct open_cfw_nanopb_field_iter, submessage_descriptor) == 0x24U,
               "G2 submessage descriptor offset");
#endif

#endif
