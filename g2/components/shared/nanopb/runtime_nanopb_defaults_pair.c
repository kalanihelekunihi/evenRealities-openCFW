/*
 * Copyright (c) 2011 Petteri Aimonen <jpa at nanopb.mail.kapsi.fi>
 *
 * This software is provided 'as-is', without any express or implied warranty.
 * In no event will the authors be held liable for any damages arising from
 * its use. Permission is granted to use, alter, and redistribute this
 * software subject to the nanopb Zlib license requirements.
 *
 * Altered production source for nanopb's private pb_field_set_to_default()
 * and pb_message_set_to_defaults(). The selected compatibility baseline is
 * authenticated nanopb 0.4.9 commit
 * 98bf4db69897b53434f3d0ba72e0a3ab1a902824. The recovered G2 stock bodies
 * occupy [0x0048FCE2,0x0048FE98). A local byte loop replaces the released
 * memory-fill helper. Iterator operations bind to separately reviewed source
 * leaves; decode_field now binds to the separately reviewed relocated source
 * dispatcher.
 */

#include <stddef.h>
#include <stdint.h>

#include "runtime_nanopb_defaults_pair.h"

#ifndef OPEN_CFW_NANOPB_DEFAULTS_SELECTION
#define OPEN_CFW_NANOPB_DEFAULTS_SELECTION 2
#endif

enum {
    OPEN_CFW_NANOPB_LTYPE_MASK = 0x0FU,
    OPEN_CFW_NANOPB_LTYPE_SUBMESSAGE = 0x08U,
    OPEN_CFW_NANOPB_LTYPE_SUBMSG_W_CB = 0x09U,
    OPEN_CFW_NANOPB_LTYPE_EXTENSION = 0x0AU,
    OPEN_CFW_NANOPB_HTYPE_MASK = 0x30U,
    OPEN_CFW_NANOPB_HTYPE_OPTIONAL = 0x10U,
    OPEN_CFW_NANOPB_HTYPE_REPEATED = 0x20U,
    OPEN_CFW_NANOPB_HTYPE_ONEOF = 0x30U,
    OPEN_CFW_NANOPB_ATYPE_MASK = 0xC0U,
    OPEN_CFW_NANOPB_ATYPE_STATIC = 0x00U,
    OPEN_CFW_NANOPB_ATYPE_CALLBACK = 0x40U,
    OPEN_CFW_NANOPB_ATYPE_POINTER = 0x80U
};

#if OPEN_CFW_NANOPB_DEFAULTS_SELECTION != 1
static void open_cfw_nanopb_defaults_zero(void *destination, size_t count)
{
    uint8_t *cursor = (uint8_t *)destination;
    while (count != 0U) {
        *cursor++ = 0U;
        --count;
    }
}

bool open_cfw_nanopb_field_set_to_default(
    struct open_cfw_nanopb_field_iter *field
)
{
    uint8_t type = field->type;

    if ((type & OPEN_CFW_NANOPB_LTYPE_MASK)
            == OPEN_CFW_NANOPB_LTYPE_EXTENSION) {
        struct open_cfw_nanopb_extension *extension =
            *(struct open_cfw_nanopb_extension **)field->data;
        while (extension != NULL) {
            struct open_cfw_nanopb_field_iter extension_iter;
            if (open_cfw_nanopb_field_iter_begin_extension(
                    &extension_iter, extension)) {
                extension->found = false;
                if (!open_cfw_nanopb_message_set_to_defaults(
                        &extension_iter)) {
                    return false;
                }
            }
            extension = extension->next;
        }
    } else if ((type & OPEN_CFW_NANOPB_ATYPE_MASK)
            == OPEN_CFW_NANOPB_ATYPE_STATIC) {
        bool initialize_data = true;
        uint8_t htype = type & OPEN_CFW_NANOPB_HTYPE_MASK;

        if (htype == OPEN_CFW_NANOPB_HTYPE_OPTIONAL
            && field->size != NULL) {
            *(bool *)field->size = false;
        } else if (htype == OPEN_CFW_NANOPB_HTYPE_REPEATED
                   || htype == OPEN_CFW_NANOPB_HTYPE_ONEOF) {
            *(uint16_t *)field->size = 0U;
            initialize_data = false;
        }

        if (initialize_data) {
            uint8_t ltype = type & OPEN_CFW_NANOPB_LTYPE_MASK;
            const struct open_cfw_nanopb_msgdesc *submessage =
                (const struct open_cfw_nanopb_msgdesc *)
                    field->submessage_descriptor;
            bool is_submessage =
                ltype == OPEN_CFW_NANOPB_LTYPE_SUBMESSAGE
                || ltype == OPEN_CFW_NANOPB_LTYPE_SUBMSG_W_CB;

            if (is_submessage
                && (submessage->default_value != NULL
                    || submessage->field_callback != NULL
                    || submessage->submessage_info[0] != NULL)) {
                struct open_cfw_nanopb_field_iter submessage_iter;
                if (open_cfw_nanopb_field_iter_begin(
                        &submessage_iter, submessage, field->data)
                    && !open_cfw_nanopb_message_set_to_defaults(
                        &submessage_iter)) {
                    return false;
                }
            } else {
                open_cfw_nanopb_defaults_zero(
                    field->data, (size_t)field->data_size);
            }
        }
    } else if ((type & OPEN_CFW_NANOPB_ATYPE_MASK)
            == OPEN_CFW_NANOPB_ATYPE_POINTER) {
        *(void **)field->field = NULL;
        if ((type & OPEN_CFW_NANOPB_HTYPE_MASK)
                == OPEN_CFW_NANOPB_HTYPE_REPEATED
            || (type & OPEN_CFW_NANOPB_HTYPE_MASK)
                == OPEN_CFW_NANOPB_HTYPE_ONEOF) {
            *(uint16_t *)field->size = 0U;
        }
    } else if ((type & OPEN_CFW_NANOPB_ATYPE_MASK)
            == OPEN_CFW_NANOPB_ATYPE_CALLBACK) {
        /* Application-owned callback state is intentionally preserved. */
    }

    return true;
}
#endif

#if OPEN_CFW_NANOPB_DEFAULTS_SELECTION != 0
bool open_cfw_nanopb_message_set_to_defaults(
    struct open_cfw_nanopb_field_iter *iter
)
{
    struct open_cfw_nanopb_istream default_stream = {
        NULL, NULL, 0U, NULL
    };
    uint32_t tag = 0U;
    uint8_t wire_type = OPEN_CFW_NANOPB_WT_VARINT;
    bool eof;
    const struct open_cfw_nanopb_msgdesc *descriptor =
        (const struct open_cfw_nanopb_msgdesc *)iter->descriptor;

    if (descriptor->default_value != NULL) {
        default_stream = open_cfw_nanopb_istream_from_buffer(
            descriptor->default_value, (size_t)-1);
        if (!open_cfw_nanopb_decode_tag(
                &default_stream, &wire_type, &tag, &eof)) {
            return false;
        }
    }

    do {
        if (!open_cfw_nanopb_field_set_to_default(iter)) {
            return false;
        }

        if (tag != 0U && iter->tag == tag) {
            if (!open_cfw_nanopb_decode_field(
                    &default_stream, wire_type, iter)) {
                return false;
            }
            if (!open_cfw_nanopb_decode_tag(
                    &default_stream, &wire_type, &tag, &eof)) {
                return false;
            }
            if (iter->size != NULL) {
                *(bool *)iter->size = false;
            }
        }
    } while (open_cfw_nanopb_field_iter_next(iter));

    return true;
}
#endif
