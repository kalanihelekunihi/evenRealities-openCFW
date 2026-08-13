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
 * Production openCFW compatibility ABI for nanopb's
 * pb_decode_fixed32(). This altered source adaptation shares the recovered G2
 * pb_istream_t contract with the qualified nanopb production leaves. It is not
 * pristine upstream source or proof of the vendor's historical point release.
 */

#ifndef OPEN_CFW_RUNTIME_NANOPB_DECODE_FIXED32_H
#define OPEN_CFW_RUNTIME_NANOPB_DECODE_FIXED32_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "runtime_nanopb_decode_varint.h"

/*
 * Bound by the production overlay to reviewed stock pb_read() at 0x0048F3BE.
 */
bool open_cfw_nanopb_read(
    struct open_cfw_nanopb_istream *stream,
    uint8_t *buffer,
    size_t count
);

bool open_cfw_nanopb_decode_fixed32(
    struct open_cfw_nanopb_istream *stream,
    void *destination
);

#endif
