/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded source recovery of LVGL 9.3's `lv_obj_style.c` static
 * `update_obj_state` helper at 0x0043EBEC...0x0043EE2C in G2 firmware
 * 2.2.6.10.
 *
 * Identity is direct, not inferred: the stock null-guard assert embeds the
 * literal function-name string "update_obj_state" (read from the official
 * image at 0x0043EE4C -> 0x00780EB8) together with the LVGL source path
 * "LVGL/src/core/lv_obj.c" (0x0043EE50 -> 0x006E8890), the assert format
 * "Asserted at expression: %s (%s)" (0x0043EE48), and "obj != NULL" /
 * "NULL pointer" (0x0043EE44 / 0x0043EE40).
 *
 * This is the property-0x68 (== LV_STYLE_TRANSITION, confirmed against the
 * official LVGL 9.3-dev interval 60d976c..344c7c src/misc/lv_style.h) style
 * transition collector reached from `lv_obj_set_state`. Reviewed against
 * the decompilation in
 * ../../../research/corpus/apollo-main/ghidra/decomp/bundles/apollo-decomp-00.c
 * (`FUN_0043ebec`) line by line:
 *
 *  1. If `obj->state` already equals `new_state`, the stock caller
 *     (`lv_obj_set_state`, outside this recovered span) never reaches this
 *     helper; the observed entry guard is therefore preserved only for a
 *     defensive re-check, not exercised by any known caller.
 *  2. `open_cfw_runtime_style_state_cmp` (FUN_0044C178) classifies how the
 *     object's rendered style differs between the old and new state. Its
 *     result is reused, untouched, as the low half of the running
 *     candidate-priority word for the whole function -- this is why the
 *     final dispatch switches on the *same* value the entry guard read.
 *  3. When the classification is not "no visible difference", the object
 *     is invalidated, `obj->state` is committed, the object is invalidated
 *     again, and every local/cascaded style attached to the object that
 *     carries a non-local `LV_STYLE_TRANSITION` descriptor whose guard
 *     state is satisfied by `new_state` contributes at most one
 *     transition candidate per (property, part), the highest-state-
 *     specificity candidate winning ties. Each surviving candidate then
 *     starts a transition via `open_cfw_runtime_start_transition`
 *     (FUN_0044BFAE).
 *  4. Finally, "redraw" and "layout" classifications refresh the object's
 *     extended draw size; "draw pad" classification instead invalidates
 *     and refreshes layout through a second pair of stock hooks.
 *
 * Field roles inside the per-candidate 20-byte scratch record and the
 * `lv_style_transition_dsc_t`-shaped source record are copied opaquely by
 * word/half/byte exactly as the decompilation copies them; only the time
 * and delay half-words and the property-id byte are interpreted by this
 * file; the remaining two pointer-sized fields are forwarded unread to the
 * stock transition starter.
 */

typedef unsigned int open_cfw_runtime_obj_pointer;
typedef unsigned int open_cfw_runtime_style_pointer;

struct open_cfw_runtime_obj_state_view {
    unsigned char reserved_00[0x0C];
    open_cfw_runtime_obj_pointer style_list;
    unsigned char reserved_10[0x28 - 0x10];
    unsigned short state;
    unsigned short style_count_packed;
};

_Static_assert(
    __builtin_offsetof(struct open_cfw_runtime_obj_state_view, style_list)
        == 0x0CU,
    "lv_obj_t style-list offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_runtime_obj_state_view, state)
        == 0x28U,
    "lv_obj_t state offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_runtime_obj_state_view,
        style_count_packed
    ) == 0x2AU,
    "lv_obj_t style-count offset changed"
);

struct open_cfw_runtime_style_list_entry {
    open_cfw_runtime_style_pointer style;
    unsigned int selector;
};

_Static_assert(
    sizeof(struct open_cfw_runtime_style_list_entry) == 8U,
    "lv_obj_t style-list entry size changed"
);

struct open_cfw_runtime_transition_source {
    unsigned int properties;
    unsigned int field_a;
    unsigned int field_b;
    unsigned int time;
    unsigned int delay;
};

struct open_cfw_runtime_transition_candidate {
    unsigned short time;
    unsigned short delay;
    unsigned int selector;
    unsigned char property;
    unsigned char reserved[3];
    unsigned int field_b;
    unsigned int field_a;
};

_Static_assert(
    sizeof(struct open_cfw_runtime_transition_candidate) == 0x14U,
    "transition candidate record size changed"
);

enum {
    OPEN_CFW_RUNTIME_STATE_TRANSITION_MAX_CANDIDATES = 0x20U,
    OPEN_CFW_RUNTIME_STATE_TRANSITION_LV_STYLE_TRANSITION = 0x68U,
    OPEN_CFW_RUNTIME_STATE_TRANSITION_STYLE_CMP_SAME = 0U,
    OPEN_CFW_RUNTIME_STATE_TRANSITION_STYLE_CMP_DIFF_REDRAW = 1U,
    OPEN_CFW_RUNTIME_STATE_TRANSITION_STYLE_CMP_DIFF_DRAW_PAD = 2U,
    OPEN_CFW_RUNTIME_STATE_TRANSITION_STYLE_CMP_DIFF_LAYOUT = 3U,
    OPEN_CFW_RUNTIME_STATE_TRANSITION_PROP_FOUND = 1,
    OPEN_CFW_RUNTIME_STATE_TRANSITION_LOG_LEVEL = 3U,
    OPEN_CFW_RUNTIME_STATE_TRANSITION_LOG_FILE = 0x006E8890U,
    OPEN_CFW_RUNTIME_STATE_TRANSITION_LOG_FUNCTION = 0x00780EB8U,
    OPEN_CFW_RUNTIME_STATE_TRANSITION_ASSERT_FORMAT = 0x00761CB0U,
    OPEN_CFW_RUNTIME_STATE_TRANSITION_NULL_LINE = 0x0000038FU,
    OPEN_CFW_RUNTIME_STATE_TRANSITION_NULL_EXPRESSION = 0x0078B3F0U,
    OPEN_CFW_RUNTIME_STATE_TRANSITION_NULL_MESSAGE = 0x00787610U
};

#ifndef OPEN_CFW_RUNTIME_STATE_TRANSITION_LOG_ASSERT
#define OPEN_CFW_RUNTIME_STATE_TRANSITION_LOG_ASSERT( \
    level, file, line, function, format, expression, message \
) \
    (((void (*)( \
        unsigned int, \
        unsigned int, \
        unsigned int, \
        unsigned int, \
        unsigned int, \
        unsigned int, \
        unsigned int \
    ))0x0044D25DU)( \
        (level), (file), (line), (function), (format), (expression), (message) \
    ))
#endif

#ifndef OPEN_CFW_RUNTIME_STATE_TRANSITION_FATAL
#define OPEN_CFW_RUNTIME_STATE_TRANSITION_FATAL() \
    do { \
        for (;;) { \
            *(volatile unsigned int *)(__UINTPTR_TYPE__)0xFFFFFFFFU = 0U; \
        } \
    } while (0)
#endif

#ifndef OPEN_CFW_RUNTIME_STATE_TRANSITION_STYLE_STATE_CMP
typedef unsigned int (*open_cfw_runtime_style_state_cmp_fn)(
    open_cfw_runtime_obj_pointer obj,
    unsigned int old_state,
    unsigned int new_state
);
#define OPEN_CFW_RUNTIME_STATE_TRANSITION_STYLE_STATE_CMP( \
    obj, old_state, new_state \
) \
    (((open_cfw_runtime_style_state_cmp_fn)(__UINTPTR_TYPE__)0x0044C179U)( \
        (obj), (old_state), (new_state) \
    ))
#endif

#ifndef OPEN_CFW_RUNTIME_STATE_TRANSITION_PRE_HOOK
typedef void (*open_cfw_runtime_obj_hook_fn)(open_cfw_runtime_obj_pointer obj);
#define OPEN_CFW_RUNTIME_STATE_TRANSITION_PRE_HOOK(obj) \
    (((open_cfw_runtime_obj_hook_fn)(__UINTPTR_TYPE__)0x00440657U)((obj)))
#endif

#ifndef OPEN_CFW_RUNTIME_STATE_TRANSITION_POST_HOOK
#define OPEN_CFW_RUNTIME_STATE_TRANSITION_POST_HOOK(obj) \
    (((open_cfw_runtime_obj_hook_fn)(__UINTPTR_TYPE__)0x0044C50FU)((obj)))
#endif

#ifndef OPEN_CFW_RUNTIME_STATE_TRANSITION_LAYOUT_REFRESH
#define OPEN_CFW_RUNTIME_STATE_TRANSITION_LAYOUT_REFRESH(obj) \
    (((open_cfw_runtime_obj_hook_fn)(__UINTPTR_TYPE__)0x00452D43U)((obj)))
#endif

#ifndef OPEN_CFW_RUNTIME_STATE_TRANSITION_ALLOCATE
typedef unsigned int (*open_cfw_runtime_allocate_fn)(unsigned int size);
#define OPEN_CFW_RUNTIME_STATE_TRANSITION_ALLOCATE(size) \
    (((open_cfw_runtime_allocate_fn)(__UINTPTR_TYPE__)0x0044F731U)((size)))
#endif

#ifndef OPEN_CFW_RUNTIME_STATE_TRANSITION_FREE
typedef void (*open_cfw_runtime_free_fn)(unsigned int allocation);
#define OPEN_CFW_RUNTIME_STATE_TRANSITION_FREE(allocation) \
    (((open_cfw_runtime_free_fn)(__UINTPTR_TYPE__)0x0044F759U)((allocation)))
#endif

#ifndef OPEN_CFW_RUNTIME_STATE_TRANSITION_SELECTOR_STATE
typedef unsigned int (*open_cfw_runtime_selector_extract_fn)(
    unsigned int selector
);
#define OPEN_CFW_RUNTIME_STATE_TRANSITION_SELECTOR_STATE(selector) \
    (((open_cfw_runtime_selector_extract_fn)(__UINTPTR_TYPE__)0x0043DD49U)( \
        (selector) \
    ))
#endif

#ifndef OPEN_CFW_RUNTIME_STATE_TRANSITION_SELECTOR_PART
#define OPEN_CFW_RUNTIME_STATE_TRANSITION_SELECTOR_PART(selector) \
    (((open_cfw_runtime_selector_extract_fn)(__UINTPTR_TYPE__)0x0043DD4DU)( \
        (selector) \
    ))
#endif

#ifndef OPEN_CFW_RUNTIME_STATE_TRANSITION_GET_TRANSITION_DSC
typedef int (*open_cfw_runtime_style_get_prop_fn)(
    open_cfw_runtime_style_pointer style,
    unsigned int property,
    struct open_cfw_runtime_transition_source **out_value
);
#define OPEN_CFW_RUNTIME_STATE_TRANSITION_GET_TRANSITION_DSC( \
    style, out_value \
) \
    (((open_cfw_runtime_style_get_prop_fn)(__UINTPTR_TYPE__)0x0043DCE1U)( \
        (style), \
        OPEN_CFW_RUNTIME_STATE_TRANSITION_LV_STYLE_TRANSITION, \
        (out_value) \
    ))
#endif

#ifndef OPEN_CFW_RUNTIME_STATE_TRANSITION_START
typedef void (*open_cfw_runtime_start_transition_fn)(
    open_cfw_runtime_obj_pointer obj,
    unsigned int part,
    unsigned int old_state,
    unsigned int new_state,
    struct open_cfw_runtime_transition_candidate *candidate
);
#define OPEN_CFW_RUNTIME_STATE_TRANSITION_START( \
    obj, part, old_state, new_state, candidate \
) \
    (((open_cfw_runtime_start_transition_fn)(__UINTPTR_TYPE__)0x0044BFAFU)( \
        (obj), (part), (old_state), (new_state), (candidate) \
    ))
#endif

#ifndef OPEN_CFW_RUNTIME_STATE_TRANSITION_REFRESH_EXT_DRAW
typedef void (*open_cfw_runtime_refresh_fn)(
    open_cfw_runtime_obj_pointer obj,
    unsigned int mask,
    unsigned int selector
);
#define OPEN_CFW_RUNTIME_STATE_TRANSITION_REFRESH_EXT_DRAW(obj) \
    (((open_cfw_runtime_refresh_fn)(__UINTPTR_TYPE__)0x0044BC8DU)( \
        (obj), 0xF0000U, 0xFFU \
    ))
#endif

/*
 * The three macros below turn a plain 32-bit word (the stock target's
 * native pointer width) into a dereferenceable view. They default to a
 * raw reinterpret cast, which is exactly correct on the real 32-bit ARM
 * target; a host test overrides them with a bounded lookup instead of
 * reinterpreting an arbitrary 32-bit test value as a live host pointer.
 */
#ifndef OPEN_CFW_RUNTIME_STATE_TRANSITION_STYLE_LIST_VIEW
#define OPEN_CFW_RUNTIME_STATE_TRANSITION_STYLE_LIST_VIEW(handle) \
    ((struct open_cfw_runtime_style_list_entry *)(__UINTPTR_TYPE__)(handle))
#endif

#ifndef OPEN_CFW_RUNTIME_STATE_TRANSITION_PROPERTIES_VIEW
#define OPEN_CFW_RUNTIME_STATE_TRANSITION_PROPERTIES_VIEW(handle) \
    ((unsigned char *)(__UINTPTR_TYPE__)(handle))
#endif

#ifndef OPEN_CFW_RUNTIME_STATE_TRANSITION_CANDIDATES_VIEW
#define OPEN_CFW_RUNTIME_STATE_TRANSITION_CANDIDATES_VIEW(handle) \
    ((struct open_cfw_runtime_transition_candidate *)(__UINTPTR_TYPE__)( \
        handle \
    ))
#endif

__attribute__((used, noinline))
void open_cfw_runtime_update_obj_state(
    struct open_cfw_runtime_obj_state_view *obj,
    unsigned int new_state
)
{
    struct open_cfw_runtime_transition_candidate *candidates;
    unsigned int candidates_allocation;
    unsigned int old_state;
    unsigned int classification;
    unsigned int style_index;
    unsigned int candidate_count;

    if ((unsigned short)new_state == obj->state) {
        return;
    }

    if (obj == (struct open_cfw_runtime_obj_state_view *)0) {
        OPEN_CFW_RUNTIME_STATE_TRANSITION_LOG_ASSERT(
            OPEN_CFW_RUNTIME_STATE_TRANSITION_LOG_LEVEL,
            OPEN_CFW_RUNTIME_STATE_TRANSITION_LOG_FILE,
            OPEN_CFW_RUNTIME_STATE_TRANSITION_NULL_LINE,
            OPEN_CFW_RUNTIME_STATE_TRANSITION_LOG_FUNCTION,
            OPEN_CFW_RUNTIME_STATE_TRANSITION_ASSERT_FORMAT,
            OPEN_CFW_RUNTIME_STATE_TRANSITION_NULL_EXPRESSION,
            OPEN_CFW_RUNTIME_STATE_TRANSITION_NULL_MESSAGE
        );
        OPEN_CFW_RUNTIME_STATE_TRANSITION_FATAL();
        return;
    }

    old_state = obj->state;
    classification = OPEN_CFW_RUNTIME_STATE_TRANSITION_STYLE_STATE_CMP(
        (open_cfw_runtime_obj_pointer)(__UINTPTR_TYPE__)obj,
        old_state,
        new_state & 0xFFFFU
    );
    if (classification == OPEN_CFW_RUNTIME_STATE_TRANSITION_STYLE_CMP_SAME) {
        obj->state = (unsigned short)new_state;
        return;
    }

    OPEN_CFW_RUNTIME_STATE_TRANSITION_PRE_HOOK(
        (open_cfw_runtime_obj_pointer)(__UINTPTR_TYPE__)obj
    );
    obj->state = (unsigned short)new_state;
    OPEN_CFW_RUNTIME_STATE_TRANSITION_POST_HOOK(
        (open_cfw_runtime_obj_pointer)(__UINTPTR_TYPE__)obj
    );

    candidates_allocation = OPEN_CFW_RUNTIME_STATE_TRANSITION_ALLOCATE(
        OPEN_CFW_RUNTIME_STATE_TRANSITION_MAX_CANDIDATES
            * (unsigned int)sizeof(
                struct open_cfw_runtime_transition_candidate
            )
    );
    candidates = OPEN_CFW_RUNTIME_STATE_TRANSITION_CANDIDATES_VIEW(
        candidates_allocation
    );
    candidate_count = 0U;
    style_index = 0U;
    /*
     * The stock loop re-reads the packed style-count halfword from the
     * object on every iteration rather than caching it once; nothing in
     * this loop body writes that field, but the read is kept live here to
     * match the decompiled loop guard exactly.
     */
    while (
        style_index < ((obj->style_count_packed & 0x3FFU) >> 4)
        && candidate_count
            < OPEN_CFW_RUNTIME_STATE_TRANSITION_MAX_CANDIDATES
    ) {
        struct open_cfw_runtime_style_list_entry *entry =
            OPEN_CFW_RUNTIME_STATE_TRANSITION_STYLE_LIST_VIEW(
                obj->style_list
            ) + style_index;
        unsigned int guard_selector = entry->selector & 0xFFFFFFU;
        unsigned int guard_state =
            OPEN_CFW_RUNTIME_STATE_TRANSITION_SELECTOR_STATE(
                guard_selector
            );
        unsigned int part =
            OPEN_CFW_RUNTIME_STATE_TRANSITION_SELECTOR_PART(guard_selector);
        int is_non_local = (int)(entry->selector << 6) >= 0;

        if (
            (guard_state & ~new_state & 0xFFFFU) == 0U
            && is_non_local
        ) {
            struct open_cfw_runtime_transition_source *source;
            int found = OPEN_CFW_RUNTIME_STATE_TRANSITION_GET_TRANSITION_DSC(
                entry->style,
                &source
            );
            if (
                found
                == OPEN_CFW_RUNTIME_STATE_TRANSITION_PROP_FOUND
            ) {
                unsigned char *properties =
                    OPEN_CFW_RUNTIME_STATE_TRANSITION_PROPERTIES_VIEW(
                        source->properties
                    );
                unsigned int property_index = 0U;

                while (
                    properties[property_index] != 0U
                    && candidate_count
                        < OPEN_CFW_RUNTIME_STATE_TRANSITION_MAX_CANDIDATES
                ) {
                    unsigned int existing;
                    unsigned char property = properties[property_index];

                    for (existing = 0U; existing < candidate_count; existing++) {
                        unsigned int existing_selector =
                            candidates[existing].selector;
                        unsigned int existing_state =
                            OPEN_CFW_RUNTIME_STATE_TRANSITION_SELECTOR_STATE(
                                existing_selector
                            );
                        unsigned int existing_part =
                            OPEN_CFW_RUNTIME_STATE_TRANSITION_SELECTOR_PART(
                                existing_selector
                            );
                        if (
                            candidates[existing].property == property
                            && existing_part == part
                            && guard_state <= (existing_state & 0xFFFFU)
                        ) {
                            break;
                        }
                    }

                    if (existing == candidate_count) {
                        struct open_cfw_runtime_transition_candidate *slot =
                            &candidates[candidate_count];
                        slot->time = (unsigned short)source->time;
                        slot->delay = (unsigned short)source->delay;
                        slot->field_a = source->field_a;
                        slot->property = property;
                        slot->field_b = source->field_b;
                        slot->selector = entry->selector & 0xFFFFFFU;
                        candidate_count++;
                    }
                    property_index++;
                }
            }
        }
        style_index++;
    }

    for (style_index = 0U; style_index < candidate_count; style_index++) {
        unsigned int part =
            OPEN_CFW_RUNTIME_STATE_TRANSITION_SELECTOR_PART(
                candidates[style_index].selector
            );
        OPEN_CFW_RUNTIME_STATE_TRANSITION_START(
            (open_cfw_runtime_obj_pointer)(__UINTPTR_TYPE__)obj,
            part,
            old_state & 0xFFFFU,
            new_state & 0xFFFFU,
            &candidates[style_index]
        );
    }

    OPEN_CFW_RUNTIME_STATE_TRANSITION_FREE(candidates_allocation);

    if (
        classification
            == OPEN_CFW_RUNTIME_STATE_TRANSITION_STYLE_CMP_DIFF_REDRAW
        || classification
            == OPEN_CFW_RUNTIME_STATE_TRANSITION_STYLE_CMP_DIFF_LAYOUT
    ) {
        OPEN_CFW_RUNTIME_STATE_TRANSITION_REFRESH_EXT_DRAW(
            (open_cfw_runtime_obj_pointer)(__UINTPTR_TYPE__)obj
        );
    } else if (
        classification
            == OPEN_CFW_RUNTIME_STATE_TRANSITION_STYLE_CMP_DIFF_DRAW_PAD
    ) {
        OPEN_CFW_RUNTIME_STATE_TRANSITION_PRE_HOOK(
            (open_cfw_runtime_obj_pointer)(__UINTPTR_TYPE__)obj
        );
        OPEN_CFW_RUNTIME_STATE_TRANSITION_LAYOUT_REFRESH(
            (open_cfw_runtime_obj_pointer)(__UINTPTR_TYPE__)obj
        );
    }
}

#undef OPEN_CFW_RUNTIME_STATE_TRANSITION_LOG_ASSERT
#undef OPEN_CFW_RUNTIME_STATE_TRANSITION_FATAL
#undef OPEN_CFW_RUNTIME_STATE_TRANSITION_STYLE_STATE_CMP
#undef OPEN_CFW_RUNTIME_STATE_TRANSITION_PRE_HOOK
#undef OPEN_CFW_RUNTIME_STATE_TRANSITION_POST_HOOK
#undef OPEN_CFW_RUNTIME_STATE_TRANSITION_LAYOUT_REFRESH
#undef OPEN_CFW_RUNTIME_STATE_TRANSITION_ALLOCATE
#undef OPEN_CFW_RUNTIME_STATE_TRANSITION_FREE
#undef OPEN_CFW_RUNTIME_STATE_TRANSITION_SELECTOR_STATE
#undef OPEN_CFW_RUNTIME_STATE_TRANSITION_SELECTOR_PART
#undef OPEN_CFW_RUNTIME_STATE_TRANSITION_GET_TRANSITION_DSC
#undef OPEN_CFW_RUNTIME_STATE_TRANSITION_START
#undef OPEN_CFW_RUNTIME_STATE_TRANSITION_REFRESH_EXT_DRAW
#undef OPEN_CFW_RUNTIME_STATE_TRANSITION_STYLE_LIST_VIEW
#undef OPEN_CFW_RUNTIME_STATE_TRANSITION_PROPERTIES_VIEW
#undef OPEN_CFW_RUNTIME_STATE_TRANSITION_CANDIDATES_VIEW
