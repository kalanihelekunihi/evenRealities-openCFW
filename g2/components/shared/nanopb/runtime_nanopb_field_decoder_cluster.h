/*
 * Copyright (c) 2011 Petteri Aimonen <jpa at nanopb.mail.kapsi.fi>
 *
 * This software is provided 'as-is', without any express or implied warranty.
 * Permission is granted to use, alter, and redistribute this software subject
 * to the nanopb Zlib license requirements.
 *
 * Production compatibility ABI for nanopb's private field decoder cluster.
 */

#ifndef OPEN_CFW_RUNTIME_NANOPB_FIELD_DECODER_CLUSTER_H
#define OPEN_CFW_RUNTIME_NANOPB_FIELD_DECODER_CLUSTER_H

#include "runtime_nanopb_dispatch_extension.h"

bool open_cfw_nanopb_decode_basic_field(
    struct open_cfw_nanopb_istream *stream,
    unsigned int wire_type,
    struct open_cfw_nanopb_field_iter *field
);

bool open_cfw_nanopb_dec_fixed_length_bytes(
    struct open_cfw_nanopb_istream *stream,
    const struct open_cfw_nanopb_field_iter *field
);

#endif /* OPEN_CFW_RUNTIME_NANOPB_FIELD_DECODER_CLUSTER_H */
