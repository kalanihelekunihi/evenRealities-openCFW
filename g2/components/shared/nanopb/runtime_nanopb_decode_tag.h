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
 * Production compatibility ABI for nanopb pb_decode_tag(). G2 uses a
 * one-byte pb_wire_type_t, consistent with the recovered short-enum ABI.
 */

#ifndef OPEN_CFW_RUNTIME_NANOPB_DECODE_TAG_H
#define OPEN_CFW_RUNTIME_NANOPB_DECODE_TAG_H

#include "runtime_nanopb_decode_varint32.h"

bool open_cfw_nanopb_decode_tag(
    struct open_cfw_nanopb_istream *stream,
    uint8_t *wire_type,
    uint32_t *tag,
    bool *eof
);

_Static_assert(sizeof(bool) == 1U, "G2 nanopb bool width");
_Static_assert(sizeof(uint8_t) == 1U, "G2 nanopb wire-type width");

#endif /* OPEN_CFW_RUNTIME_NANOPB_DECODE_TAG_H */
