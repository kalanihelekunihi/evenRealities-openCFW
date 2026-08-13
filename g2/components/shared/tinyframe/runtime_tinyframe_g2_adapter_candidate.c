/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Production-excluded G2 object/port adapter around the byte-authenticated
 * MightyPork/TinyFrame core. The upstream files remain unmodified.
 *
 * TinyFrame.c must be compiled with these three symbol renames so its dynamic
 * constructor cannot collide with this reviewed allocation boundary:
 *
 *   -DTF_Init=open_cfw_tinyframe_upstream_init
 *   -DTF_InitStatic=open_cfw_tinyframe_upstream_init_static
 *   -DTF_DeInit=open_cfw_tinyframe_upstream_deinit
 */

#include "runtime_tinyframe_g2_adapter_candidate.h"

#include <string.h>

struct open_cfw_tinyframe_g2_allocation {
    uint32_t prefix_magic;
    TinyFrame core;
    uint32_t suffix_magic;
};

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(
    sizeof(TinyFrame) == 0x7158U,
    "recovered G2 TinyFrame core size changed"
);
_Static_assert(
    offsetof(struct open_cfw_tinyframe_g2_allocation, core) == 0x4U,
    "G2 TinyFrame prefix offset changed"
);
_Static_assert(
    offsetof(struct open_cfw_tinyframe_g2_allocation, suffix_magic) == 0x715CU,
    "G2 TinyFrame suffix offset changed"
);
_Static_assert(
    sizeof(struct open_cfw_tinyframe_g2_allocation) == 0x7160U,
    "G2 TinyFrame allocation size changed"
);
#endif

extern bool open_cfw_tinyframe_upstream_init_static(
    TinyFrame *tf,
    TF_Peer peer_bit
);

static struct open_cfw_tinyframe_g2_ports open_cfw_tinyframe_g2_active_ports;

static struct open_cfw_tinyframe_g2_allocation *
open_cfw_tinyframe_g2_allocation_from_core(const TinyFrame *tf)
{
    uintptr_t address = (uintptr_t)(const void *)tf;
    address -= offsetof(struct open_cfw_tinyframe_g2_allocation, core);
    return (struct open_cfw_tinyframe_g2_allocation *)(void *)address;
}

void open_cfw_tinyframe_g2_configure(
    const struct open_cfw_tinyframe_g2_ports *ports
)
{
    if (ports == (const struct open_cfw_tinyframe_g2_ports *)0) {
        memset(
            &open_cfw_tinyframe_g2_active_ports,
            0,
            sizeof(open_cfw_tinyframe_g2_active_ports)
        );
        return;
    }
    open_cfw_tinyframe_g2_active_ports = *ports;
}

TinyFrame *open_cfw_tinyframe_g2_init(TF_Peer peer_bit)
{
    struct open_cfw_tinyframe_g2_allocation *allocation;
    struct open_cfw_tinyframe_g2_ports *ports =
        &open_cfw_tinyframe_g2_active_ports;

    if (ports->allocate == (open_cfw_tinyframe_g2_alloc_fn)0) {
        return (TinyFrame *)0;
    }
    allocation = (struct open_cfw_tinyframe_g2_allocation *)ports->allocate(
        sizeof(*allocation),
        ports->context
    );
    if (allocation == (struct open_cfw_tinyframe_g2_allocation *)0) {
        return (TinyFrame *)0;
    }

    memset(allocation, 0, sizeof(*allocation));
    allocation->prefix_magic = OPEN_CFW_TINYFRAME_G2_PREFIX_MAGIC;
    allocation->suffix_magic = OPEN_CFW_TINYFRAME_G2_SUFFIX_MAGIC;
    if (!open_cfw_tinyframe_upstream_init_static(&allocation->core, peer_bit)) {
        if (ports->release != (open_cfw_tinyframe_g2_free_fn)0) {
            ports->release(allocation, ports->context);
        }
        return (TinyFrame *)0;
    }

    /* Keep the non-upstream sentinels explicit and outside the pristine core. */
    allocation->prefix_magic = OPEN_CFW_TINYFRAME_G2_PREFIX_MAGIC;
    allocation->suffix_magic = OPEN_CFW_TINYFRAME_G2_SUFFIX_MAGIC;
    return &allocation->core;
}

void open_cfw_tinyframe_g2_deinit(TinyFrame *tf)
{
    struct open_cfw_tinyframe_g2_ports *ports =
        &open_cfw_tinyframe_g2_active_ports;

    if (
        tf != (TinyFrame *)0 &&
        ports->release != (open_cfw_tinyframe_g2_free_fn)0
    ) {
        ports->release(
            open_cfw_tinyframe_g2_allocation_from_core(tf),
            ports->context
        );
    }
}

uint32_t open_cfw_tinyframe_g2_prefix(const TinyFrame *tf)
{
    return open_cfw_tinyframe_g2_allocation_from_core(tf)->prefix_magic;
}

uint32_t open_cfw_tinyframe_g2_suffix(const TinyFrame *tf)
{
    return open_cfw_tinyframe_g2_allocation_from_core(tf)->suffix_magic;
}

size_t open_cfw_tinyframe_g2_core_offset(void)
{
    return offsetof(struct open_cfw_tinyframe_g2_allocation, core);
}

size_t open_cfw_tinyframe_g2_storage_size(void)
{
    return sizeof(struct open_cfw_tinyframe_g2_allocation);
}

void TF_WriteImpl(TinyFrame *tf, const uint8_t *buffer, uint32_t length)
{
    struct open_cfw_tinyframe_g2_ports *ports =
        &open_cfw_tinyframe_g2_active_ports;
    (void)tf;
    if (ports->write != (open_cfw_tinyframe_g2_write_fn)0) {
        ports->write(
            buffer,
            length,
            OPEN_CFW_TINYFRAME_G2_WRITE_TIMEOUT,
            ports->context
        );
    }
}

void open_cfw_tinyframe_error(const char *format, ...)
{
    struct open_cfw_tinyframe_g2_ports *ports =
        &open_cfw_tinyframe_g2_active_ports;
    va_list arguments;

    if (ports->vlog == (open_cfw_tinyframe_g2_vlog_fn)0) {
        return;
    }
    va_start(arguments, format);
    ports->vlog(format, arguments, ports->context);
    va_end(arguments);
}
