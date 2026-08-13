/*
 * Copyright (c) 2014 Petteri Aimonen <jpa@kapsi.fi>
 *
 * This software is provided 'as-is', without any express or implied warranty.
 * In no event will the authors be liable for any damages arising from its use.
 * Permission is granted to use, alter, and redistribute this software subject
 * to the nanopb Zlib license requirements.
 *
 * Production compatibility ABI for the nanopb field iterator cluster.
 */

#ifndef OPEN_CFW_RUNTIME_NANOPB_ITERATOR_CLUSTER_H
#define OPEN_CFW_RUNTIME_NANOPB_ITERATOR_CLUSTER_H

#include "runtime_nanopb_decode_inner.h"

struct open_cfw_nanopb_ostream;
struct open_cfw_nanopb_extension;

struct open_cfw_nanopb_extension_type {
    bool (*decode)(
        struct open_cfw_nanopb_istream *stream,
        struct open_cfw_nanopb_extension *extension,
        uint32_t tag,
        uint8_t wire_type
    );
    bool (*encode)(
        struct open_cfw_nanopb_ostream *stream,
        const struct open_cfw_nanopb_extension *extension
    );
    const void *argument;
};

struct open_cfw_nanopb_extension {
    const struct open_cfw_nanopb_extension_type *type;
    void *destination;
    struct open_cfw_nanopb_extension *next;
    bool found;
};

struct open_cfw_nanopb_callback {
    union {
        bool (*decode)(
            struct open_cfw_nanopb_istream *stream,
            const struct open_cfw_nanopb_field_iter *field,
            void **argument
        );
        bool (*encode)(
            struct open_cfw_nanopb_ostream *stream,
            const struct open_cfw_nanopb_field_iter *field,
            void *const *argument
        );
    } functions;
    void *argument;
};

/* Overlay-private provider placed before each public iterator leaf. */
bool open_cfw_nanopb_load_descriptor_values(
    struct open_cfw_nanopb_field_iter *iter
);

bool open_cfw_nanopb_field_iter_begin_extension(
    struct open_cfw_nanopb_field_iter *iter,
    struct open_cfw_nanopb_extension *extension
);

bool open_cfw_nanopb_field_iter_next(
    struct open_cfw_nanopb_field_iter *iter
);

bool open_cfw_nanopb_field_iter_begin_const(
    struct open_cfw_nanopb_field_iter *iter,
    const struct open_cfw_nanopb_msgdesc *descriptor,
    const void *message
);

bool open_cfw_nanopb_field_iter_begin_extension_const(
    struct open_cfw_nanopb_field_iter *iter,
    const struct open_cfw_nanopb_extension *extension
);

bool open_cfw_nanopb_default_field_callback(
    struct open_cfw_nanopb_istream *istream,
    struct open_cfw_nanopb_ostream *ostream,
    const struct open_cfw_nanopb_field_iter *field
);

#if __SIZEOF_POINTER__ == 4
_Static_assert(sizeof(struct open_cfw_nanopb_extension_type) == 0x0CU,
               "G2 nanopb extension-type size");
_Static_assert(offsetof(struct open_cfw_nanopb_extension, found) == 0x0CU,
               "G2 nanopb extension found offset");
_Static_assert(sizeof(struct open_cfw_nanopb_callback) == 0x08U,
               "G2 nanopb callback size");
#endif

#endif /* OPEN_CFW_RUNTIME_NANOPB_ITERATOR_CLUSTER_H */
