/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room source replacement for the G2 LVGL font manager at
 * 0x0046CAE0...0x0046D587.  External font payload bytes are deliberately not
 * embedded here; the two XIP headers remain a separately authenticated media
 * boundary.
 */

#include <stddef.h>
#include <stdint.h>

typedef struct open_cfw_font_config {
    uint8_t type;
    uint8_t reserved[3];
    const void *source;
    uint16_t size;
    uint8_t style;
    uint8_t reserved_tail;
} open_cfw_font_config;

typedef struct open_cfw_font_node {
    void *font;
    uint8_t type;
    uint8_t reserved[3];
    struct open_cfw_font_node *next;
} open_cfw_font_node;

typedef struct open_cfw_font_manager {
    void *head;
    open_cfw_font_node *nodes;
    uint8_t count;
} open_cfw_font_manager;

typedef struct open_cfw_xip_font_header {
    uint32_t magic;
    uint8_t reserved0[32];
    char name[16];
    uint32_t font_data;
    uint16_t size;
    uint16_t style;
} open_cfw_xip_font_header;

typedef struct open_cfw_xip_font_registration {
    void *loader;
    uint8_t reserved0[8];
    uint32_t size;
    uint32_t style;
    uint8_t reserved1[4];
    const void *font_data;
} open_cfw_xip_font_registration;

void *open_cfw_retained_font_manager_alloc(size_t size);
void open_cfw_retained_font_manager_free(void *pointer);
void *open_cfw_retained_font_manager_freetype_create(
    const char *name,
    uint32_t render_mode,
    uint16_t size,
    uint8_t style
);
void open_cfw_retained_font_manager_freetype_delete(void *font);
void open_cfw_retained_font_manager_mspi_lock(void);
void open_cfw_retained_font_manager_mspi_unlock(void);
void *open_cfw_retained_font_manager_memset(void *, int, size_t);
void *open_cfw_retained_font_manager_memcpy(void *, const void *, size_t);

#ifdef OPEN_CFW_FONT_MANAGER_TEST_HOST
extern open_cfw_font_config open_cfw_test_font_background_configs[4];
extern open_cfw_font_config open_cfw_test_font_foreground_configs[4];
extern open_cfw_font_manager *open_cfw_test_font_background_manager;
extern open_cfw_font_manager *open_cfw_test_font_foreground_manager;
extern void *open_cfw_test_font_background_font;
extern void *open_cfw_test_font_foreground_font;
extern uint8_t open_cfw_test_font_xip_scratch[0x5000];
extern open_cfw_xip_font_header open_cfw_test_font_background_header;
extern open_cfw_xip_font_header open_cfw_test_font_foreground_header;
extern open_cfw_xip_font_registration open_cfw_test_font_background_xip;
extern open_cfw_xip_font_registration open_cfw_test_font_foreground_xip;
extern char open_cfw_test_font_xip_name[16];
extern uint8_t open_cfw_test_font_xip_native;
int open_cfw_test_font_is_native(const void *font_data);
#define OPEN_CFW_FONT_MANAGER_BACKGROUND_CONFIGS \
    open_cfw_test_font_background_configs
#define OPEN_CFW_FONT_MANAGER_FOREGROUND_CONFIGS \
    open_cfw_test_font_foreground_configs
#define OPEN_CFW_FONT_MANAGER_BACKGROUND_MANAGER \
    open_cfw_test_font_background_manager
#define OPEN_CFW_FONT_MANAGER_FOREGROUND_MANAGER \
    open_cfw_test_font_foreground_manager
#define OPEN_CFW_FONT_MANAGER_BACKGROUND_FONT \
    open_cfw_test_font_background_font
#define OPEN_CFW_FONT_MANAGER_FOREGROUND_FONT \
    open_cfw_test_font_foreground_font
#define OPEN_CFW_FONT_MANAGER_XIP_SCRATCH open_cfw_test_font_xip_scratch
#define OPEN_CFW_FONT_MANAGER_BACKGROUND_HEADER \
    (&open_cfw_test_font_background_header)
#define OPEN_CFW_FONT_MANAGER_FOREGROUND_HEADER \
    (&open_cfw_test_font_foreground_header)
#define OPEN_CFW_FONT_MANAGER_BACKGROUND_XIP_CONFIG \
    (&open_cfw_test_font_background_xip)
#define OPEN_CFW_FONT_MANAGER_FOREGROUND_XIP_CONFIG \
    (&open_cfw_test_font_foreground_xip)
#define OPEN_CFW_FONT_MANAGER_XIP_NAME open_cfw_test_font_xip_name
#define OPEN_CFW_FONT_MANAGER_XIP_NATIVE open_cfw_test_font_xip_native
#define OPEN_CFW_FONT_MANAGER_XIP_LOADER ((void *)(uintptr_t)0x0046D239U)
#define OPEN_CFW_FONT_MANAGER_FONT_IS_NATIVE(p) \
    open_cfw_test_font_is_native((p))
#endif

#ifndef OPEN_CFW_FONT_MANAGER_ALLOC
#define OPEN_CFW_FONT_MANAGER_ALLOC(n) \
    open_cfw_retained_font_manager_alloc((n))
#endif
#ifndef OPEN_CFW_FONT_MANAGER_FREE
#define OPEN_CFW_FONT_MANAGER_FREE(p) \
    open_cfw_retained_font_manager_free((p))
#endif
#ifndef OPEN_CFW_FONT_MANAGER_FREETYPE_CREATE
#define OPEN_CFW_FONT_MANAGER_FREETYPE_CREATE(n, m, s, f) \
    open_cfw_retained_font_manager_freetype_create((n), (m), (s), (f))
#endif
#ifndef OPEN_CFW_FONT_MANAGER_FREETYPE_DELETE
#define OPEN_CFW_FONT_MANAGER_FREETYPE_DELETE(f) \
    open_cfw_retained_font_manager_freetype_delete((f))
#endif
#ifndef OPEN_CFW_FONT_MANAGER_MSPI_LOCK
#define OPEN_CFW_FONT_MANAGER_MSPI_LOCK() \
    open_cfw_retained_font_manager_mspi_lock()
#endif
#ifndef OPEN_CFW_FONT_MANAGER_MSPI_UNLOCK
#define OPEN_CFW_FONT_MANAGER_MSPI_UNLOCK() \
    open_cfw_retained_font_manager_mspi_unlock()
#endif
#ifndef OPEN_CFW_FONT_MANAGER_MEMSET
#define OPEN_CFW_FONT_MANAGER_MEMSET(p, v, n) \
    open_cfw_retained_font_manager_memset((p), (v), (n))
#endif
#ifndef OPEN_CFW_FONT_MANAGER_MEMCPY
#define OPEN_CFW_FONT_MANAGER_MEMCPY(d, s, n) \
    open_cfw_retained_font_manager_memcpy((d), (s), (n))
#endif
#ifndef OPEN_CFW_FONT_MANAGER_DIAGNOSTIC
#define OPEN_CFW_FONT_MANAGER_DIAGNOSTIC(code, value) \
    do { (void)(code); (void)(value); } while (0)
#endif

#ifndef OPEN_CFW_FONT_MANAGER_BACKGROUND_CONFIGS
#define OPEN_CFW_FONT_MANAGER_BACKGROUND_CONFIGS \
    ((const open_cfw_font_config *)(uintptr_t)0x20002C48U)
#endif
#ifndef OPEN_CFW_FONT_MANAGER_FOREGROUND_CONFIGS
#define OPEN_CFW_FONT_MANAGER_FOREGROUND_CONFIGS \
    ((const open_cfw_font_config *)(uintptr_t)0x20002C78U)
#endif
#ifndef OPEN_CFW_FONT_MANAGER_BACKGROUND_MANAGER
#define OPEN_CFW_FONT_MANAGER_BACKGROUND_MANAGER \
    (*(open_cfw_font_manager * volatile *)(uintptr_t)0x200746D4U)
#endif
#ifndef OPEN_CFW_FONT_MANAGER_FOREGROUND_MANAGER
#define OPEN_CFW_FONT_MANAGER_FOREGROUND_MANAGER \
    (*(open_cfw_font_manager * volatile *)(uintptr_t)0x200746D8U)
#endif
#ifndef OPEN_CFW_FONT_MANAGER_BACKGROUND_FONT
#define OPEN_CFW_FONT_MANAGER_BACKGROUND_FONT \
    (*(void * volatile *)(uintptr_t)0x200746DCU)
#endif
#ifndef OPEN_CFW_FONT_MANAGER_FOREGROUND_FONT
#define OPEN_CFW_FONT_MANAGER_FOREGROUND_FONT \
    (*(void * volatile *)(uintptr_t)0x200746E0U)
#endif
#ifndef OPEN_CFW_FONT_MANAGER_XIP_SCRATCH
#define OPEN_CFW_FONT_MANAGER_XIP_SCRATCH \
    ((void *)(uintptr_t)0x20324600U)
#endif
#ifndef OPEN_CFW_FONT_MANAGER_XIP_SCRATCH_SIZE
#define OPEN_CFW_FONT_MANAGER_XIP_SCRATCH_SIZE 0x5000U
#endif
#ifndef OPEN_CFW_FONT_MANAGER_BACKGROUND_HEADER
#define OPEN_CFW_FONT_MANAGER_BACKGROUND_HEADER \
    ((const volatile open_cfw_xip_font_header *)(uintptr_t)0x80100000U)
#endif
#ifndef OPEN_CFW_FONT_MANAGER_FOREGROUND_HEADER
#define OPEN_CFW_FONT_MANAGER_FOREGROUND_HEADER \
    ((const volatile open_cfw_xip_font_header *)(uintptr_t)0x80700000U)
#endif
#ifndef OPEN_CFW_FONT_MANAGER_BACKGROUND_XIP_CONFIG
#define OPEN_CFW_FONT_MANAGER_BACKGROUND_XIP_CONFIG \
    ((open_cfw_xip_font_registration *)(uintptr_t)0x20002C00U)
#endif
#ifndef OPEN_CFW_FONT_MANAGER_FOREGROUND_XIP_CONFIG
#define OPEN_CFW_FONT_MANAGER_FOREGROUND_XIP_CONFIG \
    ((open_cfw_xip_font_registration *)(uintptr_t)0x20002C24U)
#endif
#ifndef OPEN_CFW_FONT_MANAGER_XIP_NAME
#define OPEN_CFW_FONT_MANAGER_XIP_NAME \
    ((char *)(uintptr_t)0x20073E94U)
#endif
#ifndef OPEN_CFW_FONT_MANAGER_XIP_NATIVE
#define OPEN_CFW_FONT_MANAGER_XIP_NATIVE \
    (*(volatile uint8_t *)(uintptr_t)0x20074FE3U)
#endif
#ifndef OPEN_CFW_FONT_MANAGER_XIP_LOADER
#define OPEN_CFW_FONT_MANAGER_XIP_LOADER \
    ((void *)(uintptr_t)0x0046D239U)
#endif
#ifndef OPEN_CFW_FONT_MANAGER_FONT_IS_NATIVE
#define OPEN_CFW_FONT_MANAGER_FONT_IS_NATIVE(p) \
    (*(const uint32_t *)((const uint8_t *)(p) + 12U) == 0U)
#endif

#define OPEN_CFW_FONT_TYPE_NATIVE 0U
#define OPEN_CFW_FONT_TYPE_FREETYPE 1U
#define OPEN_CFW_FONT_TYPE_BINARY 2U
#define OPEN_CFW_FONT_XIP_MAGIC 0x5A5A5A5AU
#define OPEN_CFW_FONT_CONFIG_LIMIT 8U
#define OPEN_CFW_FONT_FALLBACK_OFFSET 0x1CU

open_cfw_font_manager *open_cfw_font_manager_create_chain(
    const open_cfw_font_config *configs,
    uint8_t count
);
void *open_cfw_font_manager_get_font(const open_cfw_font_manager *manager);
void *open_cfw_font_manager_create_single(const open_cfw_font_config *config);
int open_cfw_font_manager_add(
    open_cfw_font_manager *manager,
    void *font,
    uint8_t type
);
void open_cfw_font_manager_cleanup_single(void *font, uint8_t type);
int open_cfw_font_manager_configure_xip(void);
int open_cfw_font_manager_init(void);
const char *open_cfw_font_manager_xip_name(void);

#if defined(OPEN_CFW_FONT_MANAGER_CREATE_CHAIN_ONLY) || \
    defined(OPEN_CFW_FONT_MANAGER_BUILD_ALL)
static __attribute__((always_inline)) inline void
open_cfw_font_set_fallback(void *font, void *fallback)
{
    *(void **)((uint8_t *)font + OPEN_CFW_FONT_FALLBACK_OFFSET) = fallback;
}
#endif

#if defined(OPEN_CFW_FONT_MANAGER_CREATE_CHAIN_ONLY) || \
    defined(OPEN_CFW_FONT_MANAGER_BUILD_ALL)
__attribute__((used, noinline))
open_cfw_font_manager *open_cfw_font_manager_create_chain(
    const open_cfw_font_config *configs,
    uint8_t count
)
{
    open_cfw_font_manager *manager;
    void **fonts;
    void *previous = NULL;
    uint8_t valid = 0U;
    uint8_t index;

    if (configs == NULL || count == 0U || count > OPEN_CFW_FONT_CONFIG_LIMIT) {
        OPEN_CFW_FONT_MANAGER_DIAGNOSTIC(1U, count);
        return NULL;
    }
    manager = (open_cfw_font_manager *)OPEN_CFW_FONT_MANAGER_ALLOC(
        sizeof(*manager)
    );
    if (manager == NULL) {
        OPEN_CFW_FONT_MANAGER_DIAGNOSTIC(2U, count);
        return NULL;
    }
    manager->head = NULL;
    manager->nodes = NULL;
    manager->count = 0U;
    fonts = (void **)OPEN_CFW_FONT_MANAGER_ALLOC((size_t)count * sizeof(*fonts));
    if (fonts == NULL) {
        OPEN_CFW_FONT_MANAGER_FREE(manager);
        OPEN_CFW_FONT_MANAGER_DIAGNOSTIC(3U, count);
        return NULL;
    }
    for (index = 0U; index < count; ++index) {
        fonts[index] = NULL;
    }
    for (index = 0U; index < count; ++index) {
        fonts[index] = open_cfw_font_manager_create_single(&configs[index]);
        if (fonts[index] == NULL) {
            OPEN_CFW_FONT_MANAGER_DIAGNOSTIC(4U, index);
            continue;
        }
        if (open_cfw_font_manager_add(
                manager, fonts[index], configs[index].type
            ) == 0) {
            open_cfw_font_manager_cleanup_single(
                fonts[index], configs[index].type
            );
            fonts[index] = NULL;
            OPEN_CFW_FONT_MANAGER_DIAGNOSTIC(5U, index);
            continue;
        }
        ++valid;
    }
    if (valid == 0U) {
        OPEN_CFW_FONT_MANAGER_FREE(fonts);
        OPEN_CFW_FONT_MANAGER_FREE(manager);
        OPEN_CFW_FONT_MANAGER_DIAGNOSTIC(6U, 0U);
        return NULL;
    }
    for (index = 0U; index < count; ++index) {
        if (fonts[index] == NULL) {
            continue;
        }
        if (manager->head == NULL) {
            manager->head = fonts[index];
        }
        if (previous != NULL) {
            open_cfw_font_set_fallback(previous, fonts[index]);
        }
        previous = fonts[index];
    }
    open_cfw_font_set_fallback(previous, NULL);
    manager->count = valid;
    OPEN_CFW_FONT_MANAGER_FREE(fonts);
    OPEN_CFW_FONT_MANAGER_DIAGNOSTIC(7U, valid);
    return manager;
}
#endif

#if defined(OPEN_CFW_FONT_MANAGER_GET_FONT_ONLY) || \
    defined(OPEN_CFW_FONT_MANAGER_BUILD_ALL)
__attribute__((used, noinline))
void *open_cfw_font_manager_get_font(const open_cfw_font_manager *manager)
{
    if (manager == NULL) {
        OPEN_CFW_FONT_MANAGER_DIAGNOSTIC(8U, 0U);
        return NULL;
    }
    return manager->head;
}
#endif

#if defined(OPEN_CFW_FONT_MANAGER_CREATE_SINGLE_ONLY) || \
    defined(OPEN_CFW_FONT_MANAGER_BUILD_ALL)
__attribute__((used, noinline))
void *open_cfw_font_manager_create_single(const open_cfw_font_config *config)
{
    if (config == NULL) {
        return NULL;
    }
    if (config->type == OPEN_CFW_FONT_TYPE_NATIVE) {
        if (config->source == NULL) {
            OPEN_CFW_FONT_MANAGER_DIAGNOSTIC(9U, 0U);
            return NULL;
        }
        return (void *)config->source;
    }
    if (config->type == OPEN_CFW_FONT_TYPE_FREETYPE) {
        void *font;
        if (config->source == NULL) {
            OPEN_CFW_FONT_MANAGER_DIAGNOSTIC(10U, 0U);
            return NULL;
        }
        font = OPEN_CFW_FONT_MANAGER_FREETYPE_CREATE(
            (const char *)config->source, 1U, config->size, config->style
        );
        if (font == NULL) {
            OPEN_CFW_FONT_MANAGER_DIAGNOSTIC(
                11U, (uintptr_t)config->source
            );
        }
        return font;
    }
    OPEN_CFW_FONT_MANAGER_DIAGNOSTIC(12U, config->type);
    return NULL;
}
#endif

#if defined(OPEN_CFW_FONT_MANAGER_ADD_ONLY) || \
    defined(OPEN_CFW_FONT_MANAGER_BUILD_ALL)
__attribute__((used, noinline))
int open_cfw_font_manager_add(
    open_cfw_font_manager *manager,
    void *font,
    uint8_t type
)
{
    open_cfw_font_node *node;
    if (manager == NULL || font == NULL) {
        return 0;
    }
    node = (open_cfw_font_node *)OPEN_CFW_FONT_MANAGER_ALLOC(sizeof(*node));
    if (node == NULL) {
        OPEN_CFW_FONT_MANAGER_DIAGNOSTIC(13U, 0U);
        return 0;
    }
    node->font = font;
    node->type = type;
    node->next = manager->nodes;
    manager->nodes = node;
    return 1;
}
#endif

#if defined(OPEN_CFW_FONT_MANAGER_CLEANUP_SINGLE_ONLY) || \
    defined(OPEN_CFW_FONT_MANAGER_BUILD_ALL)
__attribute__((used, noinline))
void open_cfw_font_manager_cleanup_single(void *font, uint8_t type)
{
    if (font == NULL || type == OPEN_CFW_FONT_TYPE_NATIVE ||
        type == OPEN_CFW_FONT_TYPE_BINARY) {
        return;
    }
    if (type == OPEN_CFW_FONT_TYPE_FREETYPE) {
        OPEN_CFW_FONT_MANAGER_FREETYPE_DELETE(font);
        return;
    }
    OPEN_CFW_FONT_MANAGER_DIAGNOSTIC(14U, type);
}
#endif

#if defined(OPEN_CFW_FONT_MANAGER_CONFIGURE_XIP_ONLY) || \
    defined(OPEN_CFW_FONT_MANAGER_BUILD_ALL)
static __attribute__((always_inline)) inline void
open_cfw_font_apply_xip_header(
    const volatile open_cfw_xip_font_header *header,
    open_cfw_xip_font_registration *registration,
    int copy_name
)
{
    if (header->magic != OPEN_CFW_FONT_XIP_MAGIC) {
        registration->font_data = NULL;
        OPEN_CFW_FONT_MANAGER_DIAGNOSTIC(15U, (uintptr_t)header);
        return;
    }
    registration->font_data = (const void *)(uintptr_t)header->font_data;
    if (header->size != UINT16_MAX) {
        registration->size = header->size;
    }
    if (header->style != UINT16_MAX) {
        registration->style = header->style;
    }
    if (copy_name != 0) {
        OPEN_CFW_FONT_MANAGER_MEMCPY(
            OPEN_CFW_FONT_MANAGER_XIP_NAME, (const void *)header->name, 16U
        );
        OPEN_CFW_FONT_MANAGER_XIP_NATIVE =
            OPEN_CFW_FONT_MANAGER_FONT_IS_NATIVE(registration->font_data)
                ? 1U : 0U;
        registration->loader = OPEN_CFW_FONT_MANAGER_XIP_LOADER;
    }
}
#endif

#if defined(OPEN_CFW_FONT_MANAGER_CONFIGURE_XIP_ONLY) || \
    defined(OPEN_CFW_FONT_MANAGER_BUILD_ALL)
__attribute__((used, noinline))
int open_cfw_font_manager_configure_xip(void)
{
    OPEN_CFW_FONT_MANAGER_MEMSET(
        OPEN_CFW_FONT_MANAGER_XIP_SCRATCH,
        0,
        OPEN_CFW_FONT_MANAGER_XIP_SCRATCH_SIZE
    );
    OPEN_CFW_FONT_MANAGER_MSPI_LOCK();
    open_cfw_font_apply_xip_header(
        OPEN_CFW_FONT_MANAGER_BACKGROUND_HEADER,
        OPEN_CFW_FONT_MANAGER_BACKGROUND_XIP_CONFIG,
        1
    );
    open_cfw_font_apply_xip_header(
        OPEN_CFW_FONT_MANAGER_FOREGROUND_HEADER,
        OPEN_CFW_FONT_MANAGER_FOREGROUND_XIP_CONFIG,
        0
    );
    OPEN_CFW_FONT_MANAGER_MSPI_UNLOCK();
    return 1;
}
#endif

#if defined(OPEN_CFW_FONT_MANAGER_INIT_ONLY) || \
    defined(OPEN_CFW_FONT_MANAGER_BUILD_ALL)
__attribute__((used, noinline))
int open_cfw_font_manager_init(void)
{
    open_cfw_font_manager_configure_xip();
    OPEN_CFW_FONT_MANAGER_BACKGROUND_MANAGER =
        open_cfw_font_manager_create_chain(
            OPEN_CFW_FONT_MANAGER_BACKGROUND_CONFIGS, 4U
        );
    OPEN_CFW_FONT_MANAGER_BACKGROUND_FONT = open_cfw_font_manager_get_font(
        OPEN_CFW_FONT_MANAGER_BACKGROUND_MANAGER
    );
    OPEN_CFW_FONT_MANAGER_FOREGROUND_MANAGER =
        open_cfw_font_manager_create_chain(
            OPEN_CFW_FONT_MANAGER_FOREGROUND_CONFIGS, 4U
        );
    OPEN_CFW_FONT_MANAGER_FOREGROUND_FONT = open_cfw_font_manager_get_font(
        OPEN_CFW_FONT_MANAGER_FOREGROUND_MANAGER
    );
    return 0;
}
#endif

#if defined(OPEN_CFW_FONT_MANAGER_XIP_NAME_ONLY) || \
    defined(OPEN_CFW_FONT_MANAGER_BUILD_ALL)
__attribute__((used, noinline))
const char *open_cfw_font_manager_xip_name(void)
{
    return OPEN_CFW_FONT_MANAGER_XIP_NAME;
}
#endif
