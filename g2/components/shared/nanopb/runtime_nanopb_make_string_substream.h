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
 * Production compatibility ABI for nanopb pb_make_string_substream().
 */

#ifndef OPEN_CFW_RUNTIME_NANOPB_MAKE_STRING_SUBSTREAM_H
#define OPEN_CFW_RUNTIME_NANOPB_MAKE_STRING_SUBSTREAM_H

#include "runtime_nanopb_decode_varint32.h"

bool open_cfw_nanopb_make_string_substream(
    struct open_cfw_nanopb_istream *stream,
    struct open_cfw_nanopb_istream *substream
);

#if __SIZEOF_POINTER__ == 4
_Static_assert(sizeof(size_t) == 4U, "G2 nanopb size_t width");
_Static_assert(sizeof(struct open_cfw_nanopb_istream) == 16U, "G2 stream ABI");
#endif

#endif /* OPEN_CFW_RUNTIME_NANOPB_MAKE_STRING_SUBSTREAM_H */
