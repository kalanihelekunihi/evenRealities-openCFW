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
 * Production compatibility ABI for nanopb's private pb_decode_inner().
 */

#ifndef OPEN_CFW_RUNTIME_NANOPB_DECODE_INNER_H
#define OPEN_CFW_RUNTIME_NANOPB_DECODE_INNER_H

#include "runtime_nanopb_dec_bool.h"
#include "runtime_nanopb_decode_tag.h"
#include "runtime_nanopb_skip_field.h"

struct open_cfw_nanopb_msgdesc {
    const uint32_t *field_info;
    const struct open_cfw_nanopb_msgdesc *const *submessage_info;
    const uint8_t *default_value;
    bool (*field_callback)(void);
    uint16_t field_count;
    uint16_t required_field_count;
    uint16_t largest_tag;
};

bool open_cfw_nanopb_field_iter_begin(
    struct open_cfw_nanopb_field_iter *iter,
    const struct open_cfw_nanopb_msgdesc *fields,
    void *destination
);

bool open_cfw_nanopb_message_set_to_defaults(
    struct open_cfw_nanopb_field_iter *iter
);

bool open_cfw_nanopb_field_iter_find(
    struct open_cfw_nanopb_field_iter *iter,
    uint32_t tag
);

bool open_cfw_nanopb_field_iter_find_extension(
    struct open_cfw_nanopb_field_iter *iter
);

bool open_cfw_nanopb_decode_extension(
    struct open_cfw_nanopb_istream *stream,
    uint32_t tag,
    unsigned int wire_type,
    void *extensions
);

bool open_cfw_nanopb_decode_field(
    struct open_cfw_nanopb_istream *stream,
    unsigned int wire_type,
    struct open_cfw_nanopb_field_iter *iter
);

bool open_cfw_nanopb_decode_inner(
    struct open_cfw_nanopb_istream *stream,
    const void *fields,
    void *destination,
    unsigned int flags
);

#if __SIZEOF_POINTER__ == 4
_Static_assert(offsetof(struct open_cfw_nanopb_msgdesc, required_field_count) == 0x12U,
               "G2 required-field-count offset");
_Static_assert(sizeof(struct open_cfw_nanopb_msgdesc) == 0x18U,
               "G2 message descriptor size");
#endif

#endif /* OPEN_CFW_RUNTIME_NANOPB_DECODE_INNER_H */
