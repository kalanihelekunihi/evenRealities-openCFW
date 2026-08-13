/*
 * Copyright (c) 2011 Petteri Aimonen <jpa at nanopb.mail.kapsi.fi>
 *
 * This software is provided 'as-is', without any express or implied warranty.
 * Permission is granted to use, alter, and redistribute this software subject
 * to the nanopb Zlib license requirements.
 *
 * Production compatibility ABI for nanopb field and extension dispatch.
 */

#ifndef OPEN_CFW_RUNTIME_NANOPB_DISPATCH_EXTENSION_H
#define OPEN_CFW_RUNTIME_NANOPB_DISPATCH_EXTENSION_H

#include "runtime_nanopb_iterator_cluster.h"

bool open_cfw_nanopb_decode_static_field(
    struct open_cfw_nanopb_istream *stream,
    unsigned int wire_type,
    struct open_cfw_nanopb_field_iter *field
);

bool open_cfw_nanopb_decode_pointer_field(
    struct open_cfw_nanopb_istream *stream,
    unsigned int wire_type,
    struct open_cfw_nanopb_field_iter *field
);

bool open_cfw_nanopb_decode_callback_field(
    struct open_cfw_nanopb_istream *stream,
    unsigned int wire_type,
    struct open_cfw_nanopb_field_iter *field
);

bool open_cfw_nanopb_decode_field(
    struct open_cfw_nanopb_istream *stream,
    unsigned int wire_type,
    struct open_cfw_nanopb_field_iter *field
);

bool open_cfw_nanopb_default_extension_decoder(
    struct open_cfw_nanopb_istream *stream,
    struct open_cfw_nanopb_extension *extension,
    uint32_t tag,
    unsigned int wire_type
);

bool open_cfw_nanopb_decode_extension(
    struct open_cfw_nanopb_istream *stream,
    uint32_t tag,
    unsigned int wire_type,
    void *extensions
);

#endif /* OPEN_CFW_RUNTIME_NANOPB_DISPATCH_EXTENSION_H */
