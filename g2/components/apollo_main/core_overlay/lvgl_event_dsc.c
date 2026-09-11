/*
 * SPDX-License-Identifier: MIT
 *
 * Source replacement for the G2 2.2.6.10 LVGL event-descriptor cluster at
 * 0x004501D2...0x0045028E and 0x004502E0...0x00450390 (link-order
 * interleaved with the animation cluster in `lvgl_anim_core.c`).
 *
 * Upstream identity: LVGL `src/misc/lv_event.c`, authenticated openCFW
 * compatibility-ceiling commit `344c7c318047b7348e1be8572a9fd4260c251cfa`
 * (blob `472fc081a5e4ff391f4f92a214da8b4d27f5592801739e00c4064d2acc8d3160`,
 * `third_party/lvgl/PROVENANCE.json`). License: MIT
 * (`third_party/lvgl/LICENCE.txt`).
 *
 * Every G2 struct offset below is independently proven by the authenticated
 * public headers `third_party/lvgl/src/misc/lv_array.h` and
 * `third_party/lvgl/src/misc/lv_event.h` (`lv_event_private.h`), which are
 * part of the same authenticated snapshot, and cross-checked against every
 * call site's decompiled field access in
 * `research/corpus/apollo-main/ghidra/decomp/bundles/apollo-decomp-01.c`.
 * See `docs/research/g2-lvgl-event-anim-area-recovery.md` for the full
 * per-function evidence table.
 *
 * The still-retained callees (`lv_event_get_dsc`, `lv_array_size`,
 * `lv_array_at`, `lv_array_deinit`, `lv_array_resize`, `lv_free`, and the
 * shared LVGL log/assert entry point) are invoked at their exact G2 2.2.6.10
 * addresses, matching the fixed-address calling convention already used by
 * `lv_global.c`, `lv_init.c`, and the `runtime_linked_list_*.c` leaves in
 * this directory. Each of the ten functions below is redirected in place
 * from its own original stock entry address, so intra-cluster calls use
 * those same original addresses: after admission, every one of them is a
 * `b.w` trampoline into this reviewed implementation.
 */

#include <stdbool.h>
#include <stdint.h>

typedef struct open_cfw_lv_array {
    uint8_t *data;
    uint32_t size;
    uint32_t capacity;
    uint32_t element_size;
    uint8_t inner_alloc;
    uint8_t reserved[3];
} open_cfw_lv_array;

typedef struct open_cfw_lv_event_list {
    open_cfw_lv_array array;
    uint8_t flags; /* bit0: is_traversing, bit1: has_marked_deleting */
} open_cfw_lv_event_list;

typedef struct open_cfw_lv_event_dsc {
    void *cb;
    void *user_data;
    uint32_t filter;
} open_cfw_lv_event_dsc;

typedef struct open_cfw_lv_event {
    void *current_target;
    void *original_target;
    uint32_t code;
    void *user_data;
    void *param;
    struct open_cfw_lv_event *prev;
    uint8_t flags; /* bit0: deleted */
} open_cfw_lv_event;

_Static_assert(sizeof(open_cfw_lv_array) == 0x14U, "lv_array_t size changed");
_Static_assert(
    __builtin_offsetof(open_cfw_lv_event_list, flags) == 0x14U,
    "lv_event_list_t flag-byte offset changed"
);
_Static_assert(
    __builtin_offsetof(open_cfw_lv_event_dsc, filter) == 0x08U,
    "lv_event_dsc_t filter offset changed"
);
_Static_assert(
    __builtin_offsetof(open_cfw_lv_event, code) == 0x08U,
    "lv_event_t code offset changed"
);
_Static_assert(
    __builtin_offsetof(open_cfw_lv_event, prev) == 0x14U,
    "lv_event_t prev offset changed"
);

#define OPEN_CFW_LVGL_EVENT_PREPROCESS 0x8000U
#define OPEN_CFW_LVGL_EVENT_MARKED_DELETING 0x10000U
#define OPEN_CFW_LVGL_EVENT_FLAG_TRAVERSING 0x01U
#define OPEN_CFW_LVGL_EVENT_FLAG_MARKED_DELETING 0x02U
#define OPEN_CFW_LVGL_EVENT_FLAG_DELETED 0x01U

/* `LV_GLOBAL_DEFAULT()` resolves to the fixed G2 `lv_global_t` object at
 * 0x2006F548; `event_header` is proven at offset 0x6C from the same
 * decompiled reference used by `lv_event_mark_deleted`. */
#define OPEN_CFW_LVGL_EVENT_GLOBAL_BASE ((unsigned char *)(void *)0x2006F548U)
#define OPEN_CFW_LVGL_EVENT_HEAD \
    (*(open_cfw_lv_event **)(void *)(OPEN_CFW_LVGL_EVENT_GLOBAL_BASE + 0x6CU))

typedef open_cfw_lv_event_dsc *(*open_cfw_lvgl_event_get_dsc_fn)(
    open_cfw_lv_event_list *, uint32_t
);
#define OPEN_CFW_LVGL_EVENT_GET_DSC(list, index) \
    (((open_cfw_lvgl_event_get_dsc_fn)0x00450191U)((list), (index)))

typedef uint32_t (*open_cfw_lvgl_event_array_size_raw_fn)(const open_cfw_lv_array *);
#define OPEN_CFW_LVGL_EVENT_ARRAY_SIZE_RAW(array) \
    (((open_cfw_lvgl_event_array_size_raw_fn)0x0044FFCDU)((array)))

typedef void *(*open_cfw_lvgl_event_array_at_raw_fn)(const open_cfw_lv_array *, uint32_t);
#define OPEN_CFW_LVGL_EVENT_ARRAY_AT_RAW(array, index) \
    (((open_cfw_lvgl_event_array_at_raw_fn)0x00488579U)((array), (index)))

typedef void (*open_cfw_lvgl_event_array_deinit_fn)(open_cfw_lv_array *);
#define OPEN_CFW_LVGL_EVENT_ARRAY_DEINIT(array) \
    (((open_cfw_lvgl_event_array_deinit_fn)0x00488479U)((array)))

typedef unsigned char (*open_cfw_lvgl_event_array_resize_fn)(open_cfw_lv_array *, uint32_t);
#define OPEN_CFW_LVGL_EVENT_ARRAY_RESIZE(array, capacity) \
    (((open_cfw_lvgl_event_array_resize_fn)0x0048849DU)((array), (capacity)))

typedef void (*open_cfw_lvgl_event_free_fn)(void *);
#define OPEN_CFW_LVGL_EVENT_FREE(pointer) \
    (((open_cfw_lvgl_event_free_fn)0x0044F759U)((pointer)))

typedef bool (*open_cfw_lvgl_event_is_marked_deleting_fn)(open_cfw_lv_event_dsc *);
#define OPEN_CFW_LVGL_EVENT_IS_MARKED_DELETING(dsc) \
    (((open_cfw_lvgl_event_is_marked_deleting_fn)0x0045037FU)((dsc)))

typedef void (*open_cfw_lvgl_event_cleanup_core_fn)(open_cfw_lv_array *);
#define OPEN_CFW_LVGL_EVENT_CLEANUP_CORE(array) \
    (((open_cfw_lvgl_event_cleanup_core_fn)0x004502E1U)((array)))

typedef void (*open_cfw_lvgl_event_cleanup_fn)(open_cfw_lv_event_list *);
#define OPEN_CFW_LVGL_EVENT_CLEANUP(list) \
    (((open_cfw_lvgl_event_cleanup_fn)0x00450347U)((list)))

typedef void (*open_cfw_lvgl_event_mark_deleting_fn)(
    open_cfw_lv_event_list *, open_cfw_lv_event_dsc *
);
#define OPEN_CFW_LVGL_EVENT_MARK_DELETING(list, dsc) \
    (((open_cfw_lvgl_event_mark_deleting_fn)0x0045036DU)((list), (dsc)))

typedef uint32_t (*open_cfw_lvgl_event_array_size_fn)(open_cfw_lv_event_list *);
#define OPEN_CFW_LVGL_EVENT_ARRAY_SIZE(list) \
    (((open_cfw_lvgl_event_array_size_fn)0x00450389U)((list)))

typedef open_cfw_lv_event_dsc **(*open_cfw_lvgl_event_array_at_fn)(
    open_cfw_lv_event_list *, uint32_t
);
#define OPEN_CFW_LVGL_EVENT_ARRAY_AT(list, index) \
    (((open_cfw_lvgl_event_array_at_fn)0x00450391U)((list), (index)))

typedef void (*open_cfw_lvgl_event_log_fn)(
    unsigned int level,
    const void *file,
    unsigned int line,
    const void *function,
    ...
);
#define OPEN_CFW_LVGL_EVENT_LOG ((open_cfw_lvgl_event_log_fn)0x0044D25DU)

#define OPEN_CFW_LVGL_EVENT_FATAL() \
    do { \
        for (;;) { \
            *(volatile unsigned int *)(void *)0xFFFFFFFFU = 0U; \
        } \
    } while (0)

/* Opaque `LV_ASSERT_NULL(list)` diagnostic operands, read verbatim from the
 * G2 2.2.6.10 image at the two call sites; their text is not decoded, only
 * forwarded, matching the `lv_global.c`/`lv_init.c` precedent. */
#define OPEN_CFW_LVGL_EVENT_FILE ((const void *)0x006E8644U)
#define OPEN_CFW_LVGL_EVENT_ASSERTED_LIST ((const void *)0x00760E30U)
#define OPEN_CFW_LVGL_EVENT_EXPR_LIST ((const void *)0x007868A0U)
#define OPEN_CFW_LVGL_EVENT_NULLPTR_TEXT ((const void *)0x00786890U)
#define OPEN_CFW_LVGL_EVENT_FN_REMOVE ((const void *)0x007868B0U)
#define OPEN_CFW_LVGL_EVENT_FN_REMOVE_ALL ((const void *)0x0077FFF4U)

#if defined(OPEN_CFW_LVGL_EVENT_GET_CODE_ONLY) || defined(OPEN_CFW_LVGL_EVENT_BUILD_ALL)
__attribute__((used, noinline))
uint32_t open_cfw_lv_event_get_code(open_cfw_lv_event *e)
{
    return e->code & ~(uint32_t)OPEN_CFW_LVGL_EVENT_PREPROCESS;
}
#endif

#if defined(OPEN_CFW_LVGL_EVENT_MARK_DELETED_ONLY) || defined(OPEN_CFW_LVGL_EVENT_BUILD_ALL)
__attribute__((used, noinline))
void open_cfw_lv_event_mark_deleted(void *target)
{
    open_cfw_lv_event *e = OPEN_CFW_LVGL_EVENT_HEAD;

    while (e != (open_cfw_lv_event *)0) {
        if (e->original_target == target || e->current_target == target) {
            e->flags |= OPEN_CFW_LVGL_EVENT_FLAG_DELETED;
        }
        e = e->prev;
    }
}
#endif

#if defined(OPEN_CFW_LVGL_EVENT_ARRAY_SIZE_ONLY) || defined(OPEN_CFW_LVGL_EVENT_BUILD_ALL)
__attribute__((used, noinline))
uint32_t open_cfw_event_array_size(open_cfw_lv_event_list *list)
{
    return OPEN_CFW_LVGL_EVENT_ARRAY_SIZE_RAW(&list->array);
}
#endif

#if defined(OPEN_CFW_LVGL_EVENT_ARRAY_AT_ONLY) || defined(OPEN_CFW_LVGL_EVENT_BUILD_ALL)
__attribute__((used, noinline))
open_cfw_lv_event_dsc **open_cfw_event_array_at(
    open_cfw_lv_event_list *list, uint32_t index
)
{
    return (open_cfw_lv_event_dsc **)
        OPEN_CFW_LVGL_EVENT_ARRAY_AT_RAW(&list->array, index);
}
#endif

#if defined(OPEN_CFW_LVGL_EVENT_IS_MARKED_DELETING_ONLY) || \
    defined(OPEN_CFW_LVGL_EVENT_BUILD_ALL)
__attribute__((used, noinline))
bool open_cfw_event_is_marked_deleting(open_cfw_lv_event_dsc *dsc)
{
    return (dsc->filter & OPEN_CFW_LVGL_EVENT_MARKED_DELETING) != 0U;
}
#endif

#if defined(OPEN_CFW_LVGL_EVENT_MARK_DELETING_ONLY) || defined(OPEN_CFW_LVGL_EVENT_BUILD_ALL)
__attribute__((used, noinline))
void open_cfw_event_mark_deleting(
    open_cfw_lv_event_list *list, open_cfw_lv_event_dsc *dsc
)
{
    list->flags |= OPEN_CFW_LVGL_EVENT_FLAG_MARKED_DELETING;
    dsc->filter |= OPEN_CFW_LVGL_EVENT_MARKED_DELETING;
}
#endif

#if defined(OPEN_CFW_LVGL_EVENT_CLEANUP_CORE_ONLY) || defined(OPEN_CFW_LVGL_EVENT_BUILD_ALL)
__attribute__((used, noinline))
void open_cfw_cleanup_event_list_core(open_cfw_lv_array *array)
{
    uint32_t size = OPEN_CFW_LVGL_EVENT_ARRAY_SIZE_RAW(array);
    uint32_t kept_count = 0U;
    uint32_t index;

    for (index = 0U; index < size; ++index) {
        open_cfw_lv_event_dsc **dsc_i = (open_cfw_lv_event_dsc **)
            OPEN_CFW_LVGL_EVENT_ARRAY_AT_RAW(array, index);
        open_cfw_lv_event_dsc **dsc_kept = (open_cfw_lv_event_dsc **)
            OPEN_CFW_LVGL_EVENT_ARRAY_AT_RAW(array, kept_count);

        if (OPEN_CFW_LVGL_EVENT_IS_MARKED_DELETING(*dsc_i)) {
            OPEN_CFW_LVGL_EVENT_FREE(*dsc_i);
        } else {
            *dsc_kept = *dsc_i;
            kept_count += 1U;
        }
    }

    if (kept_count == 0U) {
        OPEN_CFW_LVGL_EVENT_ARRAY_DEINIT(array);
    } else {
        OPEN_CFW_LVGL_EVENT_ARRAY_RESIZE(array, kept_count);
    }
}
#endif

#if defined(OPEN_CFW_LVGL_EVENT_CLEANUP_ONLY) || defined(OPEN_CFW_LVGL_EVENT_BUILD_ALL)
__attribute__((used, noinline))
void open_cfw_cleanup_event_list(open_cfw_lv_event_list *list)
{
    if ((list->flags & OPEN_CFW_LVGL_EVENT_FLAG_TRAVERSING) != 0U) {
        return;
    }
    if ((list->flags & OPEN_CFW_LVGL_EVENT_FLAG_MARKED_DELETING) == 0U) {
        return;
    }

    OPEN_CFW_LVGL_EVENT_CLEANUP_CORE(&list->array);
    list->flags = (uint8_t)(list->flags & ~OPEN_CFW_LVGL_EVENT_FLAG_MARKED_DELETING);
}
#endif

#if defined(OPEN_CFW_LVGL_EVENT_REMOVE_ONLY) || defined(OPEN_CFW_LVGL_EVENT_BUILD_ALL)
__attribute__((used, noinline))
bool open_cfw_lv_event_remove(open_cfw_lv_event_list *list, uint32_t index)
{
    open_cfw_lv_event_dsc *dsc;

    if (list == (open_cfw_lv_event_list *)0) {
        OPEN_CFW_LVGL_EVENT_LOG(
            3U, OPEN_CFW_LVGL_EVENT_FILE, 0xB9U, OPEN_CFW_LVGL_EVENT_FN_REMOVE,
            OPEN_CFW_LVGL_EVENT_ASSERTED_LIST, OPEN_CFW_LVGL_EVENT_EXPR_LIST,
            OPEN_CFW_LVGL_EVENT_NULLPTR_TEXT, index
        );
        OPEN_CFW_LVGL_EVENT_FATAL();
    }

    dsc = OPEN_CFW_LVGL_EVENT_GET_DSC(list, index);
    if (dsc == (open_cfw_lv_event_dsc *)0) {
        return false;
    }
    OPEN_CFW_LVGL_EVENT_MARK_DELETING(list, dsc);
    OPEN_CFW_LVGL_EVENT_CLEANUP(list);
    return true;
}
#endif

#if defined(OPEN_CFW_LVGL_EVENT_REMOVE_ALL_ONLY) || defined(OPEN_CFW_LVGL_EVENT_BUILD_ALL)
__attribute__((used, noinline))
void open_cfw_lv_event_remove_all(open_cfw_lv_event_list *list)
{
    uint32_t size;
    uint32_t index;

    if (list == (open_cfw_lv_event_list *)0) {
        OPEN_CFW_LVGL_EVENT_LOG(
            3U, OPEN_CFW_LVGL_EVENT_FILE, 0xC3U, OPEN_CFW_LVGL_EVENT_FN_REMOVE_ALL,
            OPEN_CFW_LVGL_EVENT_ASSERTED_LIST, OPEN_CFW_LVGL_EVENT_EXPR_LIST,
            OPEN_CFW_LVGL_EVENT_NULLPTR_TEXT, (uint32_t)0U
        );
        OPEN_CFW_LVGL_EVENT_FATAL();
    }

    size = OPEN_CFW_LVGL_EVENT_ARRAY_SIZE(list);
    for (index = 0U; index < size; ++index) {
        OPEN_CFW_LVGL_EVENT_MARK_DELETING(
            list, *OPEN_CFW_LVGL_EVENT_ARRAY_AT(list, index)
        );
    }
    OPEN_CFW_LVGL_EVENT_CLEANUP(list);
}
#endif
