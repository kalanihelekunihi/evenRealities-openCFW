/*
 * SPDX-License-Identifier: FTL
 *
 * Production-excluded G2 lifecycle boundary for the authenticated FreeType
 * 2.9.1 source snapshot.  Upstream source files remain unmodified.
 * See third_party/freetype/LICENSE for the FreeType Project License.
 */

#include "runtime_freetype_base_candidate.h"

#include <limits.h>
#include <stddef.h>
#include <stdint.h>

enum {
    OPEN_CFW_FREETYPE_G2_MODULE_COUNT = 10,
    OPEN_CFW_FREETYPE_ACTIVE_MAGIC = 0x46543239U
};

static const char *const open_cfw_freetype_g2_modules[] = {
    "autofitter",
    "truetype",
    "cff",
    "psaux",
    "psnames",
    "pshinter",
    "sfnt",
    "smooth",
    "smooth-lcd",
    "smooth-lcdv"
};

_Static_assert(
    sizeof(open_cfw_freetype_g2_modules) /
        sizeof(open_cfw_freetype_g2_modules[0]) ==
        OPEN_CFW_FREETYPE_G2_MODULE_COUNT,
    "G2 FreeType module count changed"
);
_Static_assert(sizeof(FT_Error) == 4U, "G2 FreeType error ABI changed");
_Static_assert(sizeof(long) >= 4U, "FreeType allocation size ABI changed");

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(long) == 4U, "G2 FreeType requires 32-bit long");
_Static_assert(sizeof(struct FT_MemoryRec_) == 16U,
    "recovered G2 FT_MemoryRec size changed");
_Static_assert(offsetof(struct FT_MemoryRec_, user) == 0U,
    "G2 FT_MemoryRec user offset changed");
_Static_assert(offsetof(struct FT_MemoryRec_, alloc) == 4U,
    "G2 FT_MemoryRec alloc offset changed");
_Static_assert(offsetof(struct FT_MemoryRec_, free) == 8U,
    "G2 FT_MemoryRec free offset changed");
_Static_assert(offsetof(struct FT_MemoryRec_, realloc) == 12U,
    "G2 FT_MemoryRec realloc offset changed");
_Static_assert(sizeof(struct open_cfw_freetype_base_candidate) == 32U,
    "G2 FreeType candidate state ABI changed");
#endif

static struct open_cfw_freetype_base_candidate *
open_cfw_freetype_candidate_from_memory(FT_Memory memory)
{
    return (struct open_cfw_freetype_base_candidate *)memory->user;
}

static void *open_cfw_freetype_alloc(FT_Memory memory, long size)
{
    struct open_cfw_freetype_base_candidate *candidate;

    if (memory == NULL || size <= 0) {
        return NULL;
    }
    candidate = open_cfw_freetype_candidate_from_memory(memory);
    return candidate->ports.allocate(
        (size_t)size,
        candidate->ports.context
    );
}

static void *open_cfw_freetype_realloc(
    FT_Memory memory,
    long current_size,
    long new_size,
    void *block
)
{
    struct open_cfw_freetype_base_candidate *candidate;

    if (memory == NULL || current_size < 0 || new_size <= 0) {
        return NULL;
    }
    candidate = open_cfw_freetype_candidate_from_memory(memory);
    return candidate->ports.reallocate(
        block,
        (size_t)current_size,
        (size_t)new_size,
        candidate->ports.context
    );
}

static void open_cfw_freetype_free(FT_Memory memory, void *block)
{
    struct open_cfw_freetype_base_candidate *candidate;

    if (memory == NULL || block == NULL) {
        return;
    }
    candidate = open_cfw_freetype_candidate_from_memory(memory);
    candidate->ports.release(block, candidate->ports.context);
}

static int open_cfw_freetype_modules_are_complete(FT_Library library)
{
    size_t index;

    if (library == NULL) {
        return 0;
    }
    for (index = 0U; index < OPEN_CFW_FREETYPE_G2_MODULE_COUNT; index++) {
        if (FT_Get_Module(library, open_cfw_freetype_g2_modules[index]) == NULL) {
            return 0;
        }
    }
    return 1;
}

int open_cfw_freetype_base_init(
    struct open_cfw_freetype_base_candidate *candidate,
    const struct open_cfw_freetype_ports *ports
)
{
    FT_Error error;

    if (candidate == NULL || ports == NULL || ports->allocate == NULL ||
        ports->reallocate == NULL || ports->release == NULL) {
        return OPEN_CFW_FREETYPE_INVALID_ARGUMENT;
    }
    if (candidate->active == OPEN_CFW_FREETYPE_ACTIVE_MAGIC) {
        return OPEN_CFW_FREETYPE_BUSY;
    }

    candidate->memory = NULL;
    candidate->library = NULL;
    candidate->ports = *ports;
    candidate->last_freetype_error = FT_Err_Ok;
    candidate->active = 0U;

    candidate->memory = (FT_Memory)ports->allocate(
        sizeof(struct FT_MemoryRec_),
        ports->context
    );
    if (candidate->memory == NULL) {
        return OPEN_CFW_FREETYPE_OUT_OF_MEMORY;
    }
    candidate->memory->user = candidate;
    candidate->memory->alloc = open_cfw_freetype_alloc;
    candidate->memory->free = open_cfw_freetype_free;
    candidate->memory->realloc = open_cfw_freetype_realloc;

    error = FT_New_Library(candidate->memory, &candidate->library);
    candidate->last_freetype_error = error;
    if (error != FT_Err_Ok) {
        ports->release(candidate->memory, ports->context);
        candidate->memory = NULL;
        return OPEN_CFW_FREETYPE_LIBRARY_ERROR;
    }

    FT_Add_Default_Modules(candidate->library);
    if (!open_cfw_freetype_modules_are_complete(candidate->library)) {
        (void)FT_Done_Library(candidate->library);
        candidate->library = NULL;
        ports->release(candidate->memory, ports->context);
        candidate->memory = NULL;
        return OPEN_CFW_FREETYPE_MODULE_ERROR;
    }

    candidate->active = OPEN_CFW_FREETYPE_ACTIVE_MAGIC;
    return OPEN_CFW_FREETYPE_OK;
}

int open_cfw_freetype_base_done(
    struct open_cfw_freetype_base_candidate *candidate
)
{
    FT_Error error;

    if (candidate == NULL ||
        candidate->active != OPEN_CFW_FREETYPE_ACTIVE_MAGIC ||
        candidate->memory == NULL || candidate->library == NULL) {
        return OPEN_CFW_FREETYPE_INVALID_ARGUMENT;
    }
    error = FT_Done_Library(candidate->library);
    candidate->last_freetype_error = error;
    if (error != FT_Err_Ok) {
        return OPEN_CFW_FREETYPE_LIBRARY_ERROR;
    }
    candidate->library = NULL;
    candidate->ports.release(candidate->memory, candidate->ports.context);
    candidate->memory = NULL;
    candidate->active = 0U;
    return OPEN_CFW_FREETYPE_OK;
}

FT_Library open_cfw_freetype_base_library(
    const struct open_cfw_freetype_base_candidate *candidate
)
{
    if (candidate == NULL ||
        candidate->active != OPEN_CFW_FREETYPE_ACTIVE_MAGIC) {
        return NULL;
    }
    return candidate->library;
}

FT_Error open_cfw_freetype_base_last_error(
    const struct open_cfw_freetype_base_candidate *candidate
)
{
    return candidate == NULL ? FT_Err_Invalid_Argument :
        candidate->last_freetype_error;
}
