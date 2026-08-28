/*
 * SPDX-License-Identifier: FTL
 *
 * Production-excluded G2 lifecycle boundary for FreeType 2.9.1.
 * See third_party/freetype/LICENSE for the FreeType Project License.
 */

#ifndef OPEN_CFW_RUNTIME_FREETYPE_BASE_CANDIDATE_H
#define OPEN_CFW_RUNTIME_FREETYPE_BASE_CANDIDATE_H

#include <stddef.h>
#include <stdint.h>

#include <ft2build.h>
#include FT_FREETYPE_H
#include FT_MODULE_H
#include FT_SYSTEM_H

enum open_cfw_freetype_status {
    OPEN_CFW_FREETYPE_OK = 0,
    OPEN_CFW_FREETYPE_INVALID_ARGUMENT = -1,
    OPEN_CFW_FREETYPE_OUT_OF_MEMORY = -2,
    OPEN_CFW_FREETYPE_LIBRARY_ERROR = -3,
    OPEN_CFW_FREETYPE_MODULE_ERROR = -4,
    OPEN_CFW_FREETYPE_BUSY = -5
};

typedef void *(*open_cfw_freetype_allocate_fn)(
    size_t size,
    void *context
);
typedef void *(*open_cfw_freetype_reallocate_fn)(
    void *block,
    size_t current_size,
    size_t new_size,
    void *context
);
typedef void (*open_cfw_freetype_release_fn)(
    void *block,
    void *context
);

struct open_cfw_freetype_ports {
    open_cfw_freetype_allocate_fn allocate;
    open_cfw_freetype_reallocate_fn reallocate;
    open_cfw_freetype_release_fn release;
    void *context;
};

struct open_cfw_freetype_base_candidate {
    FT_Memory memory;
    FT_Library library;
    struct open_cfw_freetype_ports ports;
    FT_Error last_freetype_error;
    uint32_t active;
};

#define OPEN_CFW_FREETYPE_BASE_CANDIDATE_INIT { 0 }

/*
 * Recreates the recovered G2 sequence.  candidate must be initialized with
 * OPEN_CFW_FREETYPE_BASE_CANDIDATE_INIT before its first call:
 *   allocate FT_MemoryRec -> FT_New_Library -> FT_Add_Default_Modules.
 * The memory record and every FreeType allocation use the supplied ports.
 */
int open_cfw_freetype_base_init(
    struct open_cfw_freetype_base_candidate *candidate,
    const struct open_cfw_freetype_ports *ports
);

/*
 * Symmetric community-firmware teardown.  Stock has no safely assignable
 * FT_Done_FreeType entry; this candidate deliberately uses FT_Done_Library
 * before releasing the separately allocated 16-byte G2 memory record.  The
 * returned library is borrowed; callers must not increment its reference.
 */
int open_cfw_freetype_base_done(
    struct open_cfw_freetype_base_candidate *candidate
);

FT_Library open_cfw_freetype_base_library(
    const struct open_cfw_freetype_base_candidate *candidate
);

FT_Error open_cfw_freetype_base_last_error(
    const struct open_cfw_freetype_base_candidate *candidate
);

#endif
