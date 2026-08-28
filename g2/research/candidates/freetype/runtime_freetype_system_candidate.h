/*
 * SPDX-License-Identifier: FTL
 *
 * Production-excluded target system boundary for FreeType 2.9.1.
 * See third_party/freetype/LICENSE.
 */

#ifndef OPEN_CFW_RUNTIME_FREETYPE_SYSTEM_CANDIDATE_H
#define OPEN_CFW_RUNTIME_FREETYPE_SYSTEM_CANDIDATE_H

#include <stddef.h>

#include <ft2build.h>
#include FT_FREETYPE_H
#include FT_SYSTEM_H

enum open_cfw_freetype_system_status {
    OPEN_CFW_FREETYPE_SYSTEM_OK = 0,
    OPEN_CFW_FREETYPE_SYSTEM_INVALID_ARGUMENT = -1,
    OPEN_CFW_FREETYPE_SYSTEM_ALREADY_CONFIGURED = -2
};

typedef void *(*open_cfw_freetype_system_allocate_fn)(
    size_t size,
    void *context
);
typedef void *(*open_cfw_freetype_system_reallocate_fn)(
    void *block,
    size_t current_size,
    size_t new_size,
    void *context
);
typedef void (*open_cfw_freetype_system_release_fn)(
    void *block,
    void *context
);

/*
 * A successful resolver returns an immutable, non-empty byte view and an
 * optional provider token.  The view remains valid until release_view.
 */
typedef int (*open_cfw_freetype_system_resolve_view_fn)(
    const char *pathname,
    const unsigned char **data,
    size_t *size,
    void **token,
    void *context
);
typedef void (*open_cfw_freetype_system_release_view_fn)(
    void *token,
    const unsigned char *data,
    size_t size,
    void *context
);

struct open_cfw_freetype_system_ports {
    open_cfw_freetype_system_allocate_fn allocate;
    open_cfw_freetype_system_reallocate_fn reallocate;
    open_cfw_freetype_system_release_fn release;
    open_cfw_freetype_system_resolve_view_fn resolve_view;
    open_cfw_freetype_system_release_view_fn release_view;
    void *context;
};

/*
 * Configure once during single-threaded boot, before any FreeType call.
 * Configuration is intentionally immutable because conventional FreeType
 * libraries and opened path streams can outlive their immediate caller.
 */
int open_cfw_freetype_system_configure(
    const struct open_cfw_freetype_system_ports *ports
);

#endif
