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
 * Production openCFW compatibility ABI for nanopb's pb_decode_bool(). This is
 * altered source selected against the authenticated nanopb-0.4.9 snapshot;
 * it is not proof of the vendor's historical nanopb checkout.
 */

#ifndef OPEN_CFW_RUNTIME_NANOPB_DECODE_BOOL_H
#define OPEN_CFW_RUNTIME_NANOPB_DECODE_BOOL_H

#include <stdbool.h>
#include <stdint.h>

#include "runtime_nanopb_decode_varint32.h"

bool open_cfw_nanopb_decode_bool(
    struct open_cfw_nanopb_istream *stream,
    bool *destination
);

_Static_assert(sizeof(bool) == 1U, "G2 nanopb Boolean width");
_Static_assert(sizeof(uint32_t) == 4U, "G2 nanopb Boolean wire width");

#endif /* OPEN_CFW_RUNTIME_NANOPB_DECODE_BOOL_H */
