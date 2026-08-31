/*
 * SPDX-License-Identifier: FTL
 *
 * Maintained G2 lifecycle boundary for the authenticated FreeType
 * 2.9.1 source snapshot.  Upstream source files remain unmodified.
 * See third_party/freetype/LICENSE for the FreeType Project License.
 */

#include "runtime_freetype_base.h"

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
_Static_assert(sizeof(struct open_cfw_freetype_base_state) == 32U,
    "G2 FreeType base state ABI changed");
#endif

static struct open_cfw_freetype_base_state *
open_cfw_freetype_state_from_memory(FT_Memory memory)
{
    return (struct open_cfw_freetype_base_state *)memory->user;
}

static void *open_cfw_freetype_alloc(FT_Memory memory, long size)
{
    struct open_cfw_freetype_base_state *state;

    if (memory == NULL || size <= 0) {
        return NULL;
    }
    state = open_cfw_freetype_state_from_memory(memory);
    return state->ports.allocate(
        (size_t)size,
        state->ports.context
    );
}

static void *open_cfw_freetype_realloc(
    FT_Memory memory,
    long current_size,
    long new_size,
    void *block
)
{
    struct open_cfw_freetype_base_state *state;

    if (memory == NULL || current_size < 0 || new_size <= 0) {
        return NULL;
    }
    state = open_cfw_freetype_state_from_memory(memory);
    return state->ports.reallocate(
        block,
        (size_t)current_size,
        (size_t)new_size,
        state->ports.context
    );
}

static void open_cfw_freetype_free(FT_Memory memory, void *block)
{
    struct open_cfw_freetype_base_state *state;

    if (memory == NULL || block == NULL) {
        return;
    }
    state = open_cfw_freetype_state_from_memory(memory);
    state->ports.release(block, state->ports.context);
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
    struct open_cfw_freetype_base_state *state,
    const struct open_cfw_freetype_ports *ports
)
{
    FT_Error error;

    if (state == NULL || ports == NULL || ports->allocate == NULL ||
        ports->reallocate == NULL || ports->release == NULL) {
        return OPEN_CFW_FREETYPE_INVALID_ARGUMENT;
    }
    if (state->active == OPEN_CFW_FREETYPE_ACTIVE_MAGIC) {
        return OPEN_CFW_FREETYPE_BUSY;
    }

    state->memory = NULL;
    state->library = NULL;
    state->ports = *ports;
    state->last_freetype_error = FT_Err_Ok;
    state->active = 0U;

    state->memory = (FT_Memory)ports->allocate(
        sizeof(struct FT_MemoryRec_),
        ports->context
    );
    if (state->memory == NULL) {
        return OPEN_CFW_FREETYPE_OUT_OF_MEMORY;
    }
    state->memory->user = state;
    state->memory->alloc = open_cfw_freetype_alloc;
    state->memory->free = open_cfw_freetype_free;
    state->memory->realloc = open_cfw_freetype_realloc;

    error = FT_New_Library(state->memory, &state->library);
    state->last_freetype_error = error;
    if (error != FT_Err_Ok) {
        ports->release(state->memory, ports->context);
        state->memory = NULL;
        return OPEN_CFW_FREETYPE_LIBRARY_ERROR;
    }

    FT_Add_Default_Modules(state->library);
    if (!open_cfw_freetype_modules_are_complete(state->library)) {
        (void)FT_Done_Library(state->library);
        state->library = NULL;
        ports->release(state->memory, ports->context);
        state->memory = NULL;
        return OPEN_CFW_FREETYPE_MODULE_ERROR;
    }

    state->active = OPEN_CFW_FREETYPE_ACTIVE_MAGIC;
    return OPEN_CFW_FREETYPE_OK;
}

int open_cfw_freetype_base_done(
    struct open_cfw_freetype_base_state *state
)
{
    FT_Error error;

    if (state == NULL ||
        state->active != OPEN_CFW_FREETYPE_ACTIVE_MAGIC ||
        state->memory == NULL || state->library == NULL) {
        return OPEN_CFW_FREETYPE_INVALID_ARGUMENT;
    }
    error = FT_Done_Library(state->library);
    state->last_freetype_error = error;
    if (error != FT_Err_Ok) {
        return OPEN_CFW_FREETYPE_LIBRARY_ERROR;
    }
    state->library = NULL;
    state->ports.release(state->memory, state->ports.context);
    state->memory = NULL;
    state->active = 0U;
    return OPEN_CFW_FREETYPE_OK;
}

FT_Library open_cfw_freetype_base_library(
    const struct open_cfw_freetype_base_state *state
)
{
    if (state == NULL ||
        state->active != OPEN_CFW_FREETYPE_ACTIVE_MAGIC) {
        return NULL;
    }
    return state->library;
}

FT_Error open_cfw_freetype_base_last_error(
    const struct open_cfw_freetype_base_state *state
)
{
    return state == NULL ? FT_Err_Invalid_Argument :
        state->last_freetype_error;
}
