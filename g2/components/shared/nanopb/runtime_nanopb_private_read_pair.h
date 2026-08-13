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
 * Production openCFW compatibility ABI for nanopb's private buf_read() and
 * pb_readbyte() helpers. This is altered source, not pristine upstream source
 * and not proof of the vendor's historical checkout.
 */

#ifndef OPEN_CFW_RUNTIME_NANOPB_PRIVATE_READ_PAIR_H
#define OPEN_CFW_RUNTIME_NANOPB_PRIVATE_READ_PAIR_H

#include "runtime_nanopb_decode_varint.h"

/* Retained void-EABI copy seam, bound to stock entry 0x00439BE4. */
void __aeabi_memcpy(void *destination, const void *source, size_t count);

/* Authenticated stock error-string providers, including terminating NUL. */
extern const char open_cfw_nanopb_end_of_stream_error[];
extern const char open_cfw_nanopb_io_error[];

/*
 * Stock entry 0x0048F3A4 redirects here while retaining canonical odd Thumb
 * callback identity 0x0048F3A5 for buffer streams and pb_read().
 */
bool open_cfw_nanopb_buf_read(
    struct open_cfw_nanopb_istream *stream,
    uint8_t *buffer,
    size_t count
);

bool open_cfw_nanopb_readbyte(
    struct open_cfw_nanopb_istream *stream,
    uint8_t *byte
);

#endif /* OPEN_CFW_RUNTIME_NANOPB_PRIVATE_READ_PAIR_H */
