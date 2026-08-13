/* SPDX-License-Identifier: GPL-3.0-only */

/*
 * Production-excluded concrete port binding for the authenticated TinyFrame
 * core and G2 bookended-layout adapter.  It deliberately retains the complete
 * first-party sync transport wrapper rather than recreating its hardware
 * provider, and uses the already source-owned FreeRTOS heap_4 boundary.
 */

#include "runtime_tinyframe_g2_adapter_candidate.h"

typedef __UINT32_TYPE__ open_cfw_tinyframe_g2_port_uint32;
typedef __INT32_TYPE__ open_cfw_tinyframe_g2_port_int32;

extern void *open_cfw_freertos_heap4_malloc(
    open_cfw_tinyframe_g2_port_uint32 size
);
extern void open_cfw_freertos_heap4_free(void *allocation);
extern open_cfw_tinyframe_g2_port_int32
open_cfw_retained_sync_transport_write(
    const uint8_t *buffer,
    open_cfw_tinyframe_g2_port_uint32 length,
    open_cfw_tinyframe_g2_port_uint32 timeout
);

static void *open_cfw_tinyframe_g2_production_allocate(
    size_t size,
    void *context
)
{
    (void)context;
    if (size > 0xFFFFFFFFU) {
        return (void *)0;
    }
    return open_cfw_freertos_heap4_malloc(
        (open_cfw_tinyframe_g2_port_uint32)size
    );
}

static void open_cfw_tinyframe_g2_production_release(
    void *allocation,
    void *context
)
{
    (void)context;
    open_cfw_freertos_heap4_free(allocation);
}

static void open_cfw_tinyframe_g2_production_write(
    const uint8_t *buffer,
    uint32_t length,
    uint32_t timeout,
    void *context
)
{
    (void)context;
    (void)open_cfw_retained_sync_transport_write(buffer, length, timeout);
}

static void open_cfw_tinyframe_g2_production_vlog(
    const char *format,
    va_list arguments,
    void *context
)
{
    /* Logging is non-functional policy; avoid guessing a retained vararg ABI. */
    (void)format;
    (void)arguments;
    (void)context;
}

__attribute__((used,noinline))
TinyFrame *open_cfw_tinyframe_g2_init_production(TF_Peer peer_bit)
{
    static const struct open_cfw_tinyframe_g2_ports ports = {
        open_cfw_tinyframe_g2_production_allocate,
        open_cfw_tinyframe_g2_production_release,
        open_cfw_tinyframe_g2_production_write,
        open_cfw_tinyframe_g2_production_vlog,
        (void *)0
    };

    open_cfw_tinyframe_g2_configure(&ports);
    return open_cfw_tinyframe_g2_init(peer_bit);
}
