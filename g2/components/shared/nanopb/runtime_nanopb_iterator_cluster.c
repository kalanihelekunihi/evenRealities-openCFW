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
 * Altered production source for the G2 nanopb iterator cluster. The
 * compatibility baseline is authenticated nanopb 0.4.9 commit
 * 98bf4db69897b53434f3d0ba72e0a3ab1a902824. The upstream common-file bytes
 * are identical in official 0.4.4 through 0.4.9.1. A private byte loop removes
 * the released nonstandard memory-fill ABI from the source closure.
 */

#include "runtime_nanopb_iterator_cluster.h"

enum {
    OPEN_CFW_NANOPB_LTYPE_MASK = 0x0FU,
    OPEN_CFW_NANOPB_LTYPE_SUBMESSAGE = 0x08U,
    OPEN_CFW_NANOPB_LTYPE_SUBMSG_W_CB = 0x09U,
    OPEN_CFW_NANOPB_LTYPE_EXTENSION = 0x0AU,
    OPEN_CFW_NANOPB_HTYPE_MASK = 0x30U,
    OPEN_CFW_NANOPB_HTYPE_REQUIRED = 0x00U,
    OPEN_CFW_NANOPB_HTYPE_REPEATED = 0x20U,
    OPEN_CFW_NANOPB_ATYPE_MASK = 0xC0U,
    OPEN_CFW_NANOPB_ATYPE_STATIC = 0x00U,
    OPEN_CFW_NANOPB_ATYPE_POINTER = 0x80U
};

#if !defined(OPEN_CFW_NANOPB_ITERATOR_SELECTION) \
    || OPEN_CFW_NANOPB_ITERATOR_SELECTION == 0 \
    || OPEN_CFW_NANOPB_ITERATOR_SELECTION == 3 \
    || OPEN_CFW_NANOPB_ITERATOR_SELECTION == 4 \
    || OPEN_CFW_NANOPB_ITERATOR_SELECTION == 5
static bool open_cfw_nanopb_ltype_is_submessage(uint8_t type)
{
    uint8_t ltype = type & OPEN_CFW_NANOPB_LTYPE_MASK;
    return ltype == OPEN_CFW_NANOPB_LTYPE_SUBMESSAGE
        || ltype == OPEN_CFW_NANOPB_LTYPE_SUBMSG_W_CB;
}
#endif

#if !defined(OPEN_CFW_NANOPB_ITERATOR_SELECTION) \
    || OPEN_CFW_NANOPB_ITERATOR_SELECTION == 0
bool open_cfw_nanopb_load_descriptor_values(
    struct open_cfw_nanopb_field_iter *iter
)
{
    const struct open_cfw_nanopb_msgdesc *descriptor = iter->descriptor;
    uint32_t word0;
    uint32_t data_offset;
    int8_t size_offset;

    if (iter->index >= descriptor->field_count) {
        return false;
    }

    word0 = descriptor->field_info[iter->field_info_index];
    iter->type = (uint8_t)((word0 >> 8) & 0xFFU);

    switch (word0 & 3U) {
    case 0U:
        iter->array_size = 1U;
        iter->tag = (uint16_t)((word0 >> 2) & 0x3FU);
        size_offset = (int8_t)((word0 >> 24) & 0x0FU);
        data_offset = (word0 >> 16) & 0xFFU;
        iter->data_size = (uint16_t)((word0 >> 28) & 0x0FU);
        break;

    case 1U: {
        uint32_t word1 = descriptor->field_info[iter->field_info_index + 1U];
        iter->array_size = (uint16_t)((word0 >> 16) & 0x0FFFU);
        iter->tag = (uint16_t)(((word0 >> 2) & 0x3FU) | ((word1 >> 28) << 6));
        size_offset = (int8_t)((word0 >> 28) & 0x0FU);
        data_offset = word1 & 0xFFFFU;
        iter->data_size = (uint16_t)((word1 >> 16) & 0x0FFFU);
        break;
    }

    case 2U: {
        uint32_t word1 = descriptor->field_info[iter->field_info_index + 1U];
        uint32_t word2 = descriptor->field_info[iter->field_info_index + 2U];
        uint32_t word3 = descriptor->field_info[iter->field_info_index + 3U];
        iter->array_size = (uint16_t)(word0 >> 16);
        iter->tag = (uint16_t)(((word0 >> 2) & 0x3FU) | ((word1 >> 8) << 6));
        size_offset = (int8_t)(word1 & 0xFFU);
        data_offset = word2;
        iter->data_size = (uint16_t)word3;
        break;
    }

    default: {
        uint32_t word1 = descriptor->field_info[iter->field_info_index + 1U];
        uint32_t word2 = descriptor->field_info[iter->field_info_index + 2U];
        uint32_t word3 = descriptor->field_info[iter->field_info_index + 3U];
        uint32_t word4 = descriptor->field_info[iter->field_info_index + 4U];
        iter->array_size = (uint16_t)word4;
        iter->tag = (uint16_t)(((word0 >> 2) & 0x3FU) | ((word1 >> 8) << 6));
        size_offset = (int8_t)(word1 & 0xFFU);
        data_offset = word2;
        iter->data_size = (uint16_t)word3;
        break;
    }
    }

    if (iter->message == NULL) {
        iter->field = NULL;
        iter->size = NULL;
    } else {
        iter->field = (uint8_t *)iter->message + data_offset;
        if (size_offset != 0) {
            iter->size = (uint8_t *)iter->field - size_offset;
        } else if ((iter->type & OPEN_CFW_NANOPB_HTYPE_MASK)
                       == OPEN_CFW_NANOPB_HTYPE_REPEATED
                   && ((iter->type & OPEN_CFW_NANOPB_ATYPE_MASK)
                           == OPEN_CFW_NANOPB_ATYPE_STATIC
                       || (iter->type & OPEN_CFW_NANOPB_ATYPE_MASK)
                           == OPEN_CFW_NANOPB_ATYPE_POINTER)) {
            iter->size = &iter->array_size;
        } else {
            iter->size = NULL;
        }

        if ((iter->type & OPEN_CFW_NANOPB_ATYPE_MASK)
                == OPEN_CFW_NANOPB_ATYPE_POINTER
            && iter->field != NULL) {
            iter->data = *(void **)iter->field;
        } else {
            iter->data = iter->field;
        }
    }

    if (open_cfw_nanopb_ltype_is_submessage(iter->type)) {
        iter->submessage_descriptor =
            descriptor->submessage_info[iter->submessage_index];
    } else {
        iter->submessage_descriptor = NULL;
    }
    return true;
}
#endif

#if !defined(OPEN_CFW_NANOPB_ITERATOR_SELECTION) \
    || OPEN_CFW_NANOPB_ITERATOR_SELECTION == 3 \
    || OPEN_CFW_NANOPB_ITERATOR_SELECTION == 4 \
    || OPEN_CFW_NANOPB_ITERATOR_SELECTION == 5
static void open_cfw_nanopb_advance_iterator(
    struct open_cfw_nanopb_field_iter *iter
)
{
    const struct open_cfw_nanopb_msgdesc *descriptor = iter->descriptor;
    ++iter->index;

    if (iter->index >= descriptor->field_count) {
        iter->index = 0U;
        iter->field_info_index = 0U;
        iter->submessage_index = 0U;
        iter->required_field_index = 0U;
    } else {
        uint32_t previous = descriptor->field_info[iter->field_info_index];
        uint8_t previous_type = (uint8_t)((previous >> 8) & 0xFFU);
        uint16_t descriptor_length = (uint16_t)(1U << (previous & 3U));
        iter->field_info_index =
            (uint16_t)(iter->field_info_index + descriptor_length);
        iter->required_field_index = (uint16_t)(
            iter->required_field_index
            + ((previous_type & OPEN_CFW_NANOPB_HTYPE_MASK)
                == OPEN_CFW_NANOPB_HTYPE_REQUIRED)
        );
        iter->submessage_index = (uint16_t)(
            iter->submessage_index
            + open_cfw_nanopb_ltype_is_submessage(previous_type)
        );
    }
}
#endif

#if !defined(OPEN_CFW_NANOPB_ITERATOR_SELECTION) \
    || OPEN_CFW_NANOPB_ITERATOR_SELECTION == 1 \
    || OPEN_CFW_NANOPB_ITERATOR_SELECTION == 2 \
    || OPEN_CFW_NANOPB_ITERATOR_SELECTION == 6 \
    || OPEN_CFW_NANOPB_ITERATOR_SELECTION == 7
static bool open_cfw_nanopb_field_iter_begin_impl(
    struct open_cfw_nanopb_field_iter *iter,
    const struct open_cfw_nanopb_msgdesc *descriptor,
    void *message
)
{
    uint8_t *cursor = (uint8_t *)iter;
    size_t remaining = sizeof(*iter);
    while (remaining-- != 0U) {
        *cursor++ = 0U;
    }
    iter->descriptor = descriptor;
    iter->message = message;
    return open_cfw_nanopb_load_descriptor_values(iter);
}
#endif

#if !defined(OPEN_CFW_NANOPB_ITERATOR_SELECTION) \
    || OPEN_CFW_NANOPB_ITERATOR_SELECTION == 1
bool open_cfw_nanopb_field_iter_begin(
    struct open_cfw_nanopb_field_iter *iter,
    const struct open_cfw_nanopb_msgdesc *descriptor,
    void *message
)
{
    return open_cfw_nanopb_field_iter_begin_impl(iter, descriptor, message);
}
#endif

#if !defined(OPEN_CFW_NANOPB_ITERATOR_SELECTION) \
    || OPEN_CFW_NANOPB_ITERATOR_SELECTION == 2 \
    || OPEN_CFW_NANOPB_ITERATOR_SELECTION == 7
static bool open_cfw_nanopb_field_iter_begin_extension_impl(
    struct open_cfw_nanopb_field_iter *iter,
    struct open_cfw_nanopb_extension *extension
)
{
    const struct open_cfw_nanopb_msgdesc *message = extension->type->argument;
    uint32_t word0 = message->field_info[0];
    bool status;

    if (((word0 >> 8) & OPEN_CFW_NANOPB_ATYPE_MASK)
            == OPEN_CFW_NANOPB_ATYPE_POINTER) {
        status = open_cfw_nanopb_field_iter_begin_impl(
            iter, message, &extension->destination
        );
    } else {
        status = open_cfw_nanopb_field_iter_begin_impl(
            iter, message, extension->destination
        );
    }
    iter->size = &extension->found;
    return status;
}
#endif

#if !defined(OPEN_CFW_NANOPB_ITERATOR_SELECTION) \
    || OPEN_CFW_NANOPB_ITERATOR_SELECTION == 2
bool open_cfw_nanopb_field_iter_begin_extension(
    struct open_cfw_nanopb_field_iter *iter,
    struct open_cfw_nanopb_extension *extension
)
{
    return open_cfw_nanopb_field_iter_begin_extension_impl(iter, extension);
}
#endif

#if !defined(OPEN_CFW_NANOPB_ITERATOR_SELECTION) \
    || OPEN_CFW_NANOPB_ITERATOR_SELECTION == 3
bool open_cfw_nanopb_field_iter_next(
    struct open_cfw_nanopb_field_iter *iter
)
{
    open_cfw_nanopb_advance_iterator(iter);
    (void)open_cfw_nanopb_load_descriptor_values(iter);
    return iter->index != 0U;
}
#endif

#if !defined(OPEN_CFW_NANOPB_ITERATOR_SELECTION) \
    || OPEN_CFW_NANOPB_ITERATOR_SELECTION == 4
bool open_cfw_nanopb_field_iter_find(
    struct open_cfw_nanopb_field_iter *iter,
    uint32_t tag
)
{
    const struct open_cfw_nanopb_msgdesc *descriptor = iter->descriptor;
    if (iter->tag == tag) {
        return true;
    }
    if (tag > descriptor->largest_tag) {
        return false;
    }

    {
        uint16_t start = iter->index;
        if (tag < iter->tag) {
            iter->index = descriptor->field_count;
        }
        do {
            uint32_t field_info;
            open_cfw_nanopb_advance_iterator(iter);
            field_info = descriptor->field_info[iter->field_info_index];
            if (((field_info >> 2) & 0x3FU) == (tag & 0x3FU)) {
                (void)open_cfw_nanopb_load_descriptor_values(iter);
                if (iter->tag == tag
                    && (iter->type & OPEN_CFW_NANOPB_LTYPE_MASK)
                        != OPEN_CFW_NANOPB_LTYPE_EXTENSION) {
                    return true;
                }
            }
        } while (iter->index != start);
    }
    (void)open_cfw_nanopb_load_descriptor_values(iter);
    return false;
}
#endif

#if !defined(OPEN_CFW_NANOPB_ITERATOR_SELECTION) \
    || OPEN_CFW_NANOPB_ITERATOR_SELECTION == 5
bool open_cfw_nanopb_field_iter_find_extension(
    struct open_cfw_nanopb_field_iter *iter
)
{
    const struct open_cfw_nanopb_msgdesc *descriptor = iter->descriptor;
    if ((iter->type & OPEN_CFW_NANOPB_LTYPE_MASK)
            == OPEN_CFW_NANOPB_LTYPE_EXTENSION) {
        return true;
    }

    {
        uint16_t start = iter->index;
        do {
            uint32_t field_info;
            open_cfw_nanopb_advance_iterator(iter);
            field_info = descriptor->field_info[iter->field_info_index];
            if (((field_info >> 8) & OPEN_CFW_NANOPB_LTYPE_MASK)
                    == OPEN_CFW_NANOPB_LTYPE_EXTENSION) {
                return open_cfw_nanopb_load_descriptor_values(iter);
            }
        } while (iter->index != start);
    }
    (void)open_cfw_nanopb_load_descriptor_values(iter);
    return false;
}
#endif

#if !defined(OPEN_CFW_NANOPB_ITERATOR_SELECTION) \
    || OPEN_CFW_NANOPB_ITERATOR_SELECTION == 6 \
    || OPEN_CFW_NANOPB_ITERATOR_SELECTION == 7
static void *open_cfw_nanopb_const_cast(const void *pointer)
{
    union {
        void *mutable_pointer;
        const void *const_pointer;
    } value;
    value.const_pointer = pointer;
    return value.mutable_pointer;
}
#endif

#if !defined(OPEN_CFW_NANOPB_ITERATOR_SELECTION) \
    || OPEN_CFW_NANOPB_ITERATOR_SELECTION == 6
bool open_cfw_nanopb_field_iter_begin_const(
    struct open_cfw_nanopb_field_iter *iter,
    const struct open_cfw_nanopb_msgdesc *descriptor,
    const void *message
)
{
    return open_cfw_nanopb_field_iter_begin_impl(
        iter, descriptor, open_cfw_nanopb_const_cast(message)
    );
}
#endif

#if !defined(OPEN_CFW_NANOPB_ITERATOR_SELECTION) \
    || OPEN_CFW_NANOPB_ITERATOR_SELECTION == 7
bool open_cfw_nanopb_field_iter_begin_extension_const(
    struct open_cfw_nanopb_field_iter *iter,
    const struct open_cfw_nanopb_extension *extension
)
{
    return open_cfw_nanopb_field_iter_begin_extension_impl(
        iter,
        (struct open_cfw_nanopb_extension *)open_cfw_nanopb_const_cast(extension)
    );
}
#endif

#if !defined(OPEN_CFW_NANOPB_ITERATOR_SELECTION) \
    || OPEN_CFW_NANOPB_ITERATOR_SELECTION == 8
bool open_cfw_nanopb_default_field_callback(
    struct open_cfw_nanopb_istream *istream,
    struct open_cfw_nanopb_ostream *ostream,
    const struct open_cfw_nanopb_field_iter *field
)
{
    if (field->data_size == sizeof(struct open_cfw_nanopb_callback)) {
        struct open_cfw_nanopb_callback *callback = field->data;
        if (callback != NULL) {
            if (istream != NULL && callback->functions.decode != NULL) {
                return callback->functions.decode(
                    istream, field, &callback->argument
                );
            }
            if (ostream != NULL && callback->functions.encode != NULL) {
                return callback->functions.encode(
                    ostream, field, &callback->argument
                );
            }
        }
    }
    return true;
}
#endif
