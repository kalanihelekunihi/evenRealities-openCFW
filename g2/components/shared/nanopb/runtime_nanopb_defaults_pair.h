/*
 * Copyright (c) 2011 Petteri Aimonen <jpa at nanopb.mail.kapsi.fi>
 *
 * This software is provided 'as-is', without any express or implied warranty.
 * In no event will the authors be held liable for any damages arising from
 * its use. Permission is granted to use, alter, and redistribute this
 * software subject to the nanopb Zlib license requirements.
 *
 * Production compatibility ABI for nanopb's private defaults pair.
 */

#ifndef OPEN_CFW_RUNTIME_NANOPB_DEFAULTS_PAIR_H
#define OPEN_CFW_RUNTIME_NANOPB_DEFAULTS_PAIR_H

#include "runtime_nanopb_istream_from_buffer.h"
#include "runtime_nanopb_iterator_cluster.h"

bool open_cfw_nanopb_field_set_to_default(
    struct open_cfw_nanopb_field_iter *field
);

bool open_cfw_nanopb_message_set_to_defaults(
    struct open_cfw_nanopb_field_iter *iter
);

#endif /* OPEN_CFW_RUNTIME_NANOPB_DEFAULTS_PAIR_H */
