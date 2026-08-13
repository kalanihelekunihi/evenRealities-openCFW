/* SPDX-License-Identifier: GPL-3.0-only */

/*
 * Production-excluded stateless G2 boundary for an atomic TinyFrame routing
 * set.  TinyFrame.c is compiled separately with TF_Init/TF_InitStatic renamed
 * to the open_cfw_tinyframe_upstream_* names documented below.  This file has
 * no writable port table: heap allocation is source-owned and the complete
 * authenticated first-party sync-write wrapper remains at its fixed address.
 */

#include "runtime_tinyframe_g2_adapter_candidate.h"

typedef __UINT32_TYPE__ open_cfw_tinyframe_g2_atomic_u32;
typedef __INT32_TYPE__ open_cfw_tinyframe_g2_atomic_i32;
typedef __UINTPTR_TYPE__ open_cfw_tinyframe_g2_atomic_uintptr;

struct open_cfw_tinyframe_g2_atomic_allocation {
    uint32_t prefix_magic;
    TinyFrame core;
    uint32_t suffix_magic;
};

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(TinyFrame) == 0x7158U, "G2 TinyFrame core size changed");
_Static_assert(
    offsetof(struct open_cfw_tinyframe_g2_atomic_allocation, core) == 0x4U,
    "G2 TinyFrame core offset changed"
);
_Static_assert(
    sizeof(struct open_cfw_tinyframe_g2_atomic_allocation) == 0x7160U,
    "G2 TinyFrame allocation size changed"
);
#endif

extern void *open_cfw_freertos_heap4_malloc(open_cfw_tinyframe_g2_atomic_u32);
extern void open_cfw_freertos_heap4_free(void *);
extern bool open_cfw_tinyframe_upstream_init_static(TinyFrame *, TF_Peer);

typedef open_cfw_tinyframe_g2_atomic_i32
(*open_cfw_tinyframe_g2_atomic_write_fn)(
    const uint8_t *,
    open_cfw_tinyframe_g2_atomic_u32,
    open_cfw_tinyframe_g2_atomic_u32
);

#ifndef OPEN_CFW_TINYFRAME_G2_SYNC_WRITE
#define OPEN_CFW_TINYFRAME_G2_SYNC_WRITE(buffer, length, timeout) \
    (((open_cfw_tinyframe_g2_atomic_write_fn) \
        (open_cfw_tinyframe_g2_atomic_uintptr)0x00541791U)( \
            (buffer), (length), (timeout)))
#endif

void *open_cfw_tinyframe_g2_memory_set(
    void *destination,
    int value,
    size_t count
)
{
    uint8_t *cursor = (uint8_t *)destination;
    while (count != 0U) {
        *cursor++ = (uint8_t)value;
        --count;
    }
    return destination;
}

void open_cfw_tinyframe_error(const char *format, ...)
{
    /* Logging is deliberately non-functional policy for this candidate. */
    (void)format;
}

void TF_WriteImpl(TinyFrame *tf, const uint8_t *buffer, uint32_t length)
{
    (void)tf;
    (void)OPEN_CFW_TINYFRAME_G2_SYNC_WRITE(
        buffer,
        length,
        OPEN_CFW_TINYFRAME_G2_WRITE_TIMEOUT
    );
}

TinyFrame *TF_Init(TF_Peer peer_bit)
{
    struct open_cfw_tinyframe_g2_atomic_allocation *allocation =
        (struct open_cfw_tinyframe_g2_atomic_allocation *)
            open_cfw_freertos_heap4_malloc(
                (open_cfw_tinyframe_g2_atomic_u32)sizeof(*allocation)
            );
    if (allocation == (struct open_cfw_tinyframe_g2_atomic_allocation *)0) {
        return (TinyFrame *)0;
    }
    allocation->prefix_magic = OPEN_CFW_TINYFRAME_G2_PREFIX_MAGIC;
    allocation->suffix_magic = OPEN_CFW_TINYFRAME_G2_SUFFIX_MAGIC;
    if (!open_cfw_tinyframe_upstream_init_static(&allocation->core, peer_bit)) {
        open_cfw_freertos_heap4_free(allocation);
        return (TinyFrame *)0;
    }
    allocation->prefix_magic = OPEN_CFW_TINYFRAME_G2_PREFIX_MAGIC;
    allocation->suffix_magic = OPEN_CFW_TINYFRAME_G2_SUFFIX_MAGIC;
    return &allocation->core;
}
