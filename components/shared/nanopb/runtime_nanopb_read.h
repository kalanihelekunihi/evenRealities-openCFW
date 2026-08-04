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
 * Production openCFW compatibility ABI for nanopb's pb_read(). This altered
 * source preserves the recovered G2 callback-stream contract, the canonical
 * buffer-callback identity, and two stock data seams. It is not proof of the vendor's
 * historical nanopb checkout.
 */

#ifndef OPEN_CFW_RUNTIME_NANOPB_READ_H
#define OPEN_CFW_RUNTIME_NANOPB_READ_H

#include "runtime_nanopb_decode_varint.h"

/*
 * Canonical identity seam for nanopb's private buf_read(). The production
 * overlay binds this symbol to stock Thumb entry 0x0048F3A5, whose complete
 * body now redirects to the separately reviewed source leaf.
 */
bool open_cfw_nanopb_stock_buffer_read_identity(
    struct open_cfw_nanopb_istream *stream,
    uint8_t *buffer,
    size_t count
);

/* Authenticated stock string-data seams, including their terminating NUL. */
extern const char open_cfw_nanopb_end_of_stream_error[];
extern const char open_cfw_nanopb_io_error[];

bool open_cfw_nanopb_read(
    struct open_cfw_nanopb_istream *stream,
    uint8_t *buffer,
    size_t count
);

#endif /* OPEN_CFW_RUNTIME_NANOPB_READ_H */
