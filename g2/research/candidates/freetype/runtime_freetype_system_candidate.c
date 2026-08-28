/*
 * SPDX-License-Identifier: FTL
 *
 * Target replacement for the allocator and stdio portions of upstream
 * ftsystem.c.  Upstream FreeType sources remain unmodified.
 */

#include "runtime_freetype_system_candidate.h"

#include <limits.h>
#include <stdint.h>

#include <ft2build.h>
#include FT_CONFIG_CONFIG_H
#include FT_ERRORS_H
#include FT_INTERNAL_DEBUG_H
#include FT_INTERNAL_STREAM_H
#include FT_INTERNAL_OBJECTS_H

enum {
    OPEN_CFW_FREETYPE_SYSTEM_MAGIC = 0x46545359U
};

struct open_cfw_freetype_system_memory {
    struct FT_MemoryRec_ memory;
    struct open_cfw_freetype_system_ports ports;
    uint32_t magic;
};

struct open_cfw_freetype_system_stream {
    FT_Memory memory;
    const unsigned char *data;
    size_t size;
    void *token;
    open_cfw_freetype_system_release_view_fn release_view;
    void *context;
};

static struct open_cfw_freetype_system_ports open_cfw_freetype_system_ports;
static uint32_t open_cfw_freetype_system_configured;

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(struct FT_MemoryRec_) == 16U,
    "recovered G2 FT_MemoryRec size changed");
_Static_assert(offsetof(struct open_cfw_freetype_system_memory, memory) == 0U,
    "FT_Memory must address the system owner record");
#endif

static struct open_cfw_freetype_system_memory *
open_cfw_freetype_system_owner(FT_Memory memory)
{
    struct open_cfw_freetype_system_memory *owner =
        (struct open_cfw_freetype_system_memory *)memory;
    if (owner == NULL || owner->magic != OPEN_CFW_FREETYPE_SYSTEM_MAGIC)
        return NULL;
    return owner;
}

static void *open_cfw_freetype_system_alloc(FT_Memory memory, long size)
{
    struct open_cfw_freetype_system_memory *owner =
        open_cfw_freetype_system_owner(memory);
    if (owner == NULL || size <= 0)
        return NULL;
    return owner->ports.allocate((size_t)size, owner->ports.context);
}

static void *open_cfw_freetype_system_realloc(
    FT_Memory memory,
    long current_size,
    long new_size,
    void *block
)
{
    struct open_cfw_freetype_system_memory *owner =
        open_cfw_freetype_system_owner(memory);
    if (owner == NULL || current_size < 0 || new_size <= 0)
        return NULL;
    return owner->ports.reallocate(
        block,
        (size_t)current_size,
        (size_t)new_size,
        owner->ports.context
    );
}

static void open_cfw_freetype_system_free(FT_Memory memory, void *block)
{
    struct open_cfw_freetype_system_memory *owner =
        open_cfw_freetype_system_owner(memory);
    if (owner != NULL && block != NULL)
        owner->ports.release(block, owner->ports.context);
}

int open_cfw_freetype_system_configure(
    const struct open_cfw_freetype_system_ports *ports
)
{
    if (ports == NULL || ports->allocate == NULL ||
        ports->reallocate == NULL || ports->release == NULL ||
        ports->resolve_view == NULL || ports->release_view == NULL)
        return OPEN_CFW_FREETYPE_SYSTEM_INVALID_ARGUMENT;
    if (open_cfw_freetype_system_configured != 0U)
        return OPEN_CFW_FREETYPE_SYSTEM_ALREADY_CONFIGURED;
    open_cfw_freetype_system_ports = *ports;
    open_cfw_freetype_system_configured = OPEN_CFW_FREETYPE_SYSTEM_MAGIC;
    return OPEN_CFW_FREETYPE_SYSTEM_OK;
}

FT_BASE_DEF(FT_Memory)
FT_New_Memory(void)
{
    struct open_cfw_freetype_system_memory *owner;
    if (open_cfw_freetype_system_configured !=
        OPEN_CFW_FREETYPE_SYSTEM_MAGIC)
        return NULL;
    owner = (struct open_cfw_freetype_system_memory *)
        open_cfw_freetype_system_ports.allocate(
            sizeof(*owner), open_cfw_freetype_system_ports.context
        );
    if (owner == NULL)
        return NULL;
    owner->ports = open_cfw_freetype_system_ports;
    owner->magic = OPEN_CFW_FREETYPE_SYSTEM_MAGIC;
    owner->memory.user = owner;
    owner->memory.alloc = open_cfw_freetype_system_alloc;
    owner->memory.realloc = open_cfw_freetype_system_realloc;
    owner->memory.free = open_cfw_freetype_system_free;
    return &owner->memory;
}

FT_BASE_DEF(void)
FT_Done_Memory(FT_Memory memory)
{
    struct open_cfw_freetype_system_memory *owner =
        open_cfw_freetype_system_owner(memory);
    struct open_cfw_freetype_system_ports ports;
    if (owner == NULL)
        return;
    ports = owner->ports;
    owner->magic = 0U;
    ports.release(owner, ports.context);
}

static void open_cfw_freetype_system_stream_close(FT_Stream stream)
{
    struct open_cfw_freetype_system_stream *record;
    if (stream == NULL)
        return;
    record = (struct open_cfw_freetype_system_stream *)
        stream->descriptor.pointer;
    if (record != NULL) {
        record->release_view(
            record->token, record->data, record->size, record->context
        );
        record->memory->free(record->memory, record);
    }
    stream->base = NULL;
    stream->size = 0U;
    stream->pos = 0U;
    stream->descriptor.pointer = NULL;
    stream->read = NULL;
    stream->close = NULL;
}

FT_BASE_DEF(FT_Error)
FT_Stream_Open(FT_Stream stream, const char *pathname)
{
    struct open_cfw_freetype_system_stream *record;
    const unsigned char *data = NULL;
    size_t size = 0U;
    void *token = NULL;

    if (stream == NULL)
        return FT_THROW(Invalid_Stream_Handle);
    stream->descriptor.pointer = NULL;
    stream->pathname.pointer = (char *)pathname;
    stream->base = NULL;
    stream->size = 0U;
    stream->pos = 0U;
    stream->read = NULL;
    stream->close = NULL;
    if (pathname == NULL || stream->memory == NULL ||
        open_cfw_freetype_system_configured !=
            OPEN_CFW_FREETYPE_SYSTEM_MAGIC)
        return FT_THROW(Cannot_Open_Resource);
    if (open_cfw_freetype_system_ports.resolve_view(
            pathname, &data, &size, &token,
            open_cfw_freetype_system_ports.context
        ) != 0 || data == NULL || size == 0U || size > (size_t)ULONG_MAX) {
        if (data != NULL)
            open_cfw_freetype_system_ports.release_view(
                token, data, size, open_cfw_freetype_system_ports.context
            );
        return FT_THROW(Cannot_Open_Resource);
    }
    record = (struct open_cfw_freetype_system_stream *)
        stream->memory->alloc(stream->memory, (long)sizeof(*record));
    if (record == NULL) {
        open_cfw_freetype_system_ports.release_view(
            token, data, size, open_cfw_freetype_system_ports.context
        );
        return FT_THROW(Out_Of_Memory);
    }
    record->memory = stream->memory;
    record->data = data;
    record->size = size;
    record->token = token;
    record->release_view = open_cfw_freetype_system_ports.release_view;
    record->context = open_cfw_freetype_system_ports.context;
    stream->descriptor.pointer = record;
    stream->base = (unsigned char *)data;
    stream->size = (unsigned long)size;
    stream->close = open_cfw_freetype_system_stream_close;
    return FT_Err_Ok;
}
