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
 * Altered production source for nanopb's private pb_dec_bool(). The selected
 * baseline is the authenticated nanopb-0.4.9 snapshot at commit
 * 98bf4db69897b53434f3d0ba72e0a3ab1a902824. The complete G2 stock adapter is
 * [0x004901CC, 0x004901D6); production binds it directly to the source-owned
 * public Boolean decoder.
 */

#include "runtime_nanopb_dec_bool.h"

bool open_cfw_nanopb_dec_bool(
    struct open_cfw_nanopb_istream *stream,
    const struct open_cfw_nanopb_field_iter *field
)
{
    return open_cfw_nanopb_decode_bool(stream, (bool *)field->data);
}
