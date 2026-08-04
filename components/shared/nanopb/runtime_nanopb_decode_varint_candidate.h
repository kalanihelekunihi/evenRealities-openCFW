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
 * Production-excluded openCFW compatibility-candidate ABI for nanopb's
 * pb_decode_varint(). This is an altered source adaptation, not pristine
 * upstream source and not proof of the vendor's historical point release.
 */

#ifndef OPEN_CFW_RUNTIME_NANOPB_DECODE_VARINT_CANDIDATE_H
#define OPEN_CFW_RUNTIME_NANOPB_DECODE_VARINT_CANDIDATE_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

struct open_cfw_nanopb_istream_candidate;

typedef bool (*open_cfw_nanopb_read_callback_candidate)(
    struct open_cfw_nanopb_istream_candidate *stream,
    uint8_t *buffer,
    size_t count
);

/* Recovered callback-stream, error-enabled nanopb pb_istream_t ABI. */
struct open_cfw_nanopb_istream_candidate {
    open_cfw_nanopb_read_callback_candidate callback;
    void *state;
    size_t bytes_left;
    const char *errmsg;
};

/*
 * Production integration would bind this seam to the reviewed pb_readbyte()
 * provider at 0x0048F454. The candidate deliberately leaves it unresolved.
 */
bool open_cfw_nanopb_readbyte_candidate(
    struct open_cfw_nanopb_istream_candidate *stream,
    uint8_t *byte
);

bool open_cfw_nanopb_decode_varint_candidate(
    struct open_cfw_nanopb_istream_candidate *stream,
    uint64_t *destination
);

#if __SIZEOF_POINTER__ == 4
_Static_assert(
    offsetof(struct open_cfw_nanopb_istream_candidate, callback) == 0U,
    "G2 pb_istream_t callback offset"
);
_Static_assert(
    offsetof(struct open_cfw_nanopb_istream_candidate, state) == 4U,
    "G2 pb_istream_t state offset"
);
_Static_assert(
    offsetof(struct open_cfw_nanopb_istream_candidate, bytes_left) == 8U,
    "G2 pb_istream_t bytes_left offset"
);
_Static_assert(
    offsetof(struct open_cfw_nanopb_istream_candidate, errmsg) == 12U,
    "G2 pb_istream_t errmsg offset"
);
_Static_assert(
    sizeof(struct open_cfw_nanopb_istream_candidate) == 16U,
    "G2 pb_istream_t size"
);
#endif

#endif
