/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded source recovery of LVGL 9.3's public `lv_obj_is_valid` at
 * 0x0043E2EA...0x0043E33E and its static recursive helper (LVGL upstream
 * names it `obj_valid_child`) at 0x0043EE54...0x0043EE94, both in
 * `LVGL/src/core/lv_obj.c`, in G2 firmware 2.2.6.10.
 *
 * `lv_obj_is_valid` walks every display's screen list (the display's
 * `screens` pointer array and `screen_cnt`, at +0x2B8/+0x2D4 of the
 * display struct reached by the display iterator at 0x0044FA22, already
 * anchored to `LVGL/src/core/lv_obj.c` by call-topology census evidence)
 * looking for the exact pointer, recursing into each screen's children
 * through the same `lv_obj_spec_attr_t` children array and count used by
 * `open_cfw_runtime_obj_allocate_spec_attr`
 * (runtime_obj_spec_attr.c) and by `update_obj_state`'s style-list walk.
 *
 * Every field that stores a stock 32-bit pointer is kept as an explicit
 * 32-bit word (not a native pointer) so the struct layouts below pin the
 * *real* hardware byte offsets regardless of host pointer width; turning
 * such a word into a dereferenceable view goes through one of the
 * `#ifndef`-guarded `_VIEW` macros below so a host test can substitute a
 * bounded lookup instead of reinterpreting an arbitrary 32-bit value as a
 * live pointer.
 */

typedef unsigned int open_cfw_runtime_tree_pointer;

struct open_cfw_runtime_display_view {
    unsigned char reserved_00[0x2B8];
    open_cfw_runtime_tree_pointer screens;
    unsigned char reserved_2bc[0x2D4 - 0x2BC];
    unsigned int screen_cnt;
};

_Static_assert(
    __builtin_offsetof(struct open_cfw_runtime_display_view, screens)
        == 0x2B8U,
    "lv_display_t screens offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_runtime_display_view, screen_cnt)
        == 0x2D4U,
    "lv_display_t screen_cnt offset changed"
);

struct open_cfw_runtime_obj_children_view {
    unsigned char reserved_00[0x08];
    open_cfw_runtime_tree_pointer spec_attr;
};

_Static_assert(
    __builtin_offsetof(
        struct open_cfw_runtime_obj_children_view,
        spec_attr
    ) == 0x08U,
    "lv_obj_t spec_attr offset changed"
);

struct open_cfw_runtime_obj_children_spec_attr_view {
    open_cfw_runtime_tree_pointer children;
    unsigned char reserved_04[0x30 - 0x04];
    unsigned short child_cnt;
};

_Static_assert(
    __builtin_offsetof(
        struct open_cfw_runtime_obj_children_spec_attr_view,
        child_cnt
    ) == 0x30U,
    "lv_obj_spec_attr_t child_cnt offset changed"
);

#ifndef OPEN_CFW_RUNTIME_TREE_SEARCH_DISPLAY_NEXT
typedef open_cfw_runtime_tree_pointer (*open_cfw_runtime_display_next_fn)(
    open_cfw_runtime_tree_pointer display
);
#define OPEN_CFW_RUNTIME_TREE_SEARCH_DISPLAY_NEXT(display) \
    (((open_cfw_runtime_display_next_fn)(__UINTPTR_TYPE__)0x0044FA23U)( \
        (display) \
    ))
#endif

#ifndef OPEN_CFW_RUNTIME_TREE_SEARCH_DISPLAY_VIEW
#define OPEN_CFW_RUNTIME_TREE_SEARCH_DISPLAY_VIEW(handle) \
    ((struct open_cfw_runtime_display_view *)(__UINTPTR_TYPE__)(handle))
#endif

#ifndef OPEN_CFW_RUNTIME_TREE_SEARCH_OBJ_VIEW
#define OPEN_CFW_RUNTIME_TREE_SEARCH_OBJ_VIEW(handle) \
    ((struct open_cfw_runtime_obj_children_view *)(__UINTPTR_TYPE__)(handle))
#endif

#ifndef OPEN_CFW_RUNTIME_TREE_SEARCH_SPEC_ATTR_VIEW
#define OPEN_CFW_RUNTIME_TREE_SEARCH_SPEC_ATTR_VIEW(handle) \
    ((struct open_cfw_runtime_obj_children_spec_attr_view *) \
        (__UINTPTR_TYPE__)(handle))
#endif

#ifndef OPEN_CFW_RUNTIME_TREE_SEARCH_POINTER_ARRAY
#define OPEN_CFW_RUNTIME_TREE_SEARCH_POINTER_ARRAY(handle) \
    ((open_cfw_runtime_tree_pointer *)(__UINTPTR_TYPE__)(handle))
#endif

__attribute__((used, noinline))
int open_cfw_runtime_obj_valid_child(
    open_cfw_runtime_tree_pointer parent,
    open_cfw_runtime_tree_pointer target
)
{
    struct open_cfw_runtime_obj_children_view *parent_view =
        OPEN_CFW_RUNTIME_TREE_SEARCH_OBJ_VIEW(parent);
    struct open_cfw_runtime_obj_children_spec_attr_view *spec_attr;
    unsigned int child_count;
    unsigned int index;

    child_count = 0U;
    spec_attr =
        (struct open_cfw_runtime_obj_children_spec_attr_view *)0;
    if (parent_view->spec_attr != 0U) {
        spec_attr = OPEN_CFW_RUNTIME_TREE_SEARCH_SPEC_ATTR_VIEW(
            parent_view->spec_attr
        );
        child_count = spec_attr->child_cnt;
    }

    for (index = 0U; index < child_count; index++) {
        open_cfw_runtime_tree_pointer child =
            OPEN_CFW_RUNTIME_TREE_SEARCH_POINTER_ARRAY(
                spec_attr->children
            )[index];
        if (child == target) {
            return 1;
        }
        if (open_cfw_runtime_obj_valid_child(child, target)) {
            return 1;
        }
    }
    return 0;
}

__attribute__((used, noinline))
int open_cfw_runtime_obj_is_valid(open_cfw_runtime_tree_pointer obj)
{
    open_cfw_runtime_tree_pointer display =
        OPEN_CFW_RUNTIME_TREE_SEARCH_DISPLAY_NEXT(0U);

    while (display != 0U) {
        struct open_cfw_runtime_display_view *view =
            OPEN_CFW_RUNTIME_TREE_SEARCH_DISPLAY_VIEW(display);
        unsigned int index;

        for (index = 0U; index < view->screen_cnt; index++) {
            open_cfw_runtime_tree_pointer screen =
                OPEN_CFW_RUNTIME_TREE_SEARCH_POINTER_ARRAY(
                    view->screens
                )[index];
            if (screen == obj) {
                return 1;
            }
            if (open_cfw_runtime_obj_valid_child(screen, obj)) {
                return 1;
            }
        }
        display = OPEN_CFW_RUNTIME_TREE_SEARCH_DISPLAY_NEXT(display);
    }
    return 0;
}

#undef OPEN_CFW_RUNTIME_TREE_SEARCH_DISPLAY_NEXT
#undef OPEN_CFW_RUNTIME_TREE_SEARCH_DISPLAY_VIEW
#undef OPEN_CFW_RUNTIME_TREE_SEARCH_OBJ_VIEW
#undef OPEN_CFW_RUNTIME_TREE_SEARCH_SPEC_ATTR_VIEW
#undef OPEN_CFW_RUNTIME_TREE_SEARCH_POINTER_ARRAY
