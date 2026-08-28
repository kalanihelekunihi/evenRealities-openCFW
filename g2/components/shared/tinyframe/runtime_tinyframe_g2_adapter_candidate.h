/*
 * SPDX-License-Identifier: MIT
 *
 * Production-excluded G2 boundary for the authenticated MIT TinyFrame core.
 */

#ifndef OPEN_CFW_RUNTIME_TINYFRAME_G2_ADAPTER_CANDIDATE_H
#define OPEN_CFW_RUNTIME_TINYFRAME_G2_ADAPTER_CANDIDATE_H

#include <stdarg.h>
#include <stddef.h>
#include <stdint.h>

#include "TinyFrame.h"

enum {
    OPEN_CFW_TINYFRAME_G2_PREFIX_MAGIC = 0xA5A5A5A5U,
    OPEN_CFW_TINYFRAME_G2_SUFFIX_MAGIC = 0x5A5A5A5AU,
    OPEN_CFW_TINYFRAME_G2_WRITE_TIMEOUT = 100U
};

typedef void *(*open_cfw_tinyframe_g2_alloc_fn)(size_t size, void *context);
typedef void (*open_cfw_tinyframe_g2_free_fn)(void *pointer, void *context);
typedef void (*open_cfw_tinyframe_g2_write_fn)(
    const uint8_t *buffer,
    uint32_t length,
    uint32_t timeout,
    void *context
);
typedef void (*open_cfw_tinyframe_g2_vlog_fn)(
    const char *format,
    va_list arguments,
    void *context
);

struct open_cfw_tinyframe_g2_ports {
    open_cfw_tinyframe_g2_alloc_fn allocate;
    open_cfw_tinyframe_g2_free_fn release;
    open_cfw_tinyframe_g2_write_fn write;
    open_cfw_tinyframe_g2_vlog_fn vlog;
    void *context;
};

/* Configure before constructing the one Sync Framework TinyFrame instance. */
void open_cfw_tinyframe_g2_configure(
    const struct open_cfw_tinyframe_g2_ports *ports
);

/*
 * Returns the pristine core pointer, four bytes after the G2 allocation base
 * on the 32-bit target. Stock application code treats this pointer as opaque;
 * the admission audit proves every use reaches a TinyFrame public API.
 */
TinyFrame *open_cfw_tinyframe_g2_init(TF_Peer peer_bit);
void open_cfw_tinyframe_g2_deinit(TinyFrame *tf);

uint32_t open_cfw_tinyframe_g2_prefix(const TinyFrame *tf);
uint32_t open_cfw_tinyframe_g2_suffix(const TinyFrame *tf);
size_t open_cfw_tinyframe_g2_core_offset(void);
size_t open_cfw_tinyframe_g2_storage_size(void);

#endif
