/*
 * SPDX-License-Identifier: Zlib
 *
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
 * Altered production source for nanopb's private decode_field(),
 * default_extension_decoder(), and decode_extension(). The selected baseline
 * is authenticated nanopb 0.4.9 commit
 * 98bf4db69897b53434f3d0ba72e0a3ab1a902824. The recovered G2 stock cluster
 * occupies [0x0048FBE4,0x0048FCE2). Iterator operations are source-owned;
 * static, pointer, and callback field decoders remain explicit executable
 * seams until their adjacent source cluster is promoted.
 */

#include "runtime_nanopb_dispatch_extension.h"

#ifndef OPEN_CFW_NANOPB_DISPATCH_SELECTION
#define OPEN_CFW_NANOPB_DISPATCH_SELECTION 3
#endif

enum {
    OPEN_CFW_NANOPB_ATYPE_MASK = 0xC0U,
    OPEN_CFW_NANOPB_ATYPE_STATIC = 0x00U,
    OPEN_CFW_NANOPB_ATYPE_CALLBACK = 0x40U,
    OPEN_CFW_NANOPB_ATYPE_POINTER = 0x80U
};

#if OPEN_CFW_NANOPB_DISPATCH_SELECTION == 0 \
    || OPEN_CFW_NANOPB_DISPATCH_SELECTION == 1 \
    || OPEN_CFW_NANOPB_DISPATCH_SELECTION == 3
static bool open_cfw_nanopb_dispatch_fail(
    struct open_cfw_nanopb_istream *stream,
    const char *message
)
{
    if (stream->errmsg == NULL) {
        stream->errmsg = message;
    }
    return false;
}
#endif

#if OPEN_CFW_NANOPB_DISPATCH_SELECTION == 0 \
    || OPEN_CFW_NANOPB_DISPATCH_SELECTION == 3
bool open_cfw_nanopb_decode_field(
    struct open_cfw_nanopb_istream *stream,
    unsigned int wire_type,
    struct open_cfw_nanopb_field_iter *field
)
{
    switch (field->type & OPEN_CFW_NANOPB_ATYPE_MASK) {
    case OPEN_CFW_NANOPB_ATYPE_STATIC:
        return open_cfw_nanopb_decode_static_field(stream, wire_type, field);
    case OPEN_CFW_NANOPB_ATYPE_POINTER:
        return open_cfw_nanopb_decode_pointer_field(stream, wire_type, field);
    case OPEN_CFW_NANOPB_ATYPE_CALLBACK:
        return open_cfw_nanopb_decode_callback_field(stream, wire_type, field);
    default:
        return open_cfw_nanopb_dispatch_fail(stream, "invalid field type");
    }
}
#endif

#if OPEN_CFW_NANOPB_DISPATCH_SELECTION == 1 \
    || OPEN_CFW_NANOPB_DISPATCH_SELECTION == 3
bool open_cfw_nanopb_default_extension_decoder(
    struct open_cfw_nanopb_istream *stream,
    struct open_cfw_nanopb_extension *extension,
    uint32_t tag,
    unsigned int wire_type
)
{
    struct open_cfw_nanopb_field_iter iter;

    if (!open_cfw_nanopb_field_iter_begin_extension(&iter, extension)) {
        return open_cfw_nanopb_dispatch_fail(stream, "invalid extension");
    }
    if (iter.tag != tag || iter.descriptor == NULL) {
        return true;
    }
    extension->found = true;
    return open_cfw_nanopb_decode_field(stream, wire_type, &iter);
}
#endif

#if OPEN_CFW_NANOPB_DISPATCH_SELECTION == 2 \
    || OPEN_CFW_NANOPB_DISPATCH_SELECTION == 3
bool open_cfw_nanopb_decode_extension(
    struct open_cfw_nanopb_istream *stream,
    uint32_t tag,
    unsigned int wire_type,
    void *extensions
)
{
    struct open_cfw_nanopb_extension *extension =
        (struct open_cfw_nanopb_extension *)extensions;
    size_t position = stream->bytes_left;

    while (extension != NULL && position == stream->bytes_left) {
        bool status;
        if (extension->type->decode != NULL) {
            status = extension->type->decode(
                stream, extension, tag, (uint8_t)wire_type
            );
        } else {
            status = open_cfw_nanopb_default_extension_decoder(
                stream, extension, tag, wire_type
            );
        }
        if (!status) {
            return false;
        }
        extension = extension->next;
    }
    return true;
}
#endif
