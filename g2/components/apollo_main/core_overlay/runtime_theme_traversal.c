/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded source replacements for the G2 2.2.6.10 LVGL theme traversal:
 *   0x00482FCE...0x00482FF1  parent-first theme callback chain
 *   0x00482FF2...0x00483027  inheritable class recursion
 *
 * Only stock-observed fields are modeled. A theme stores its apply callback
 * at +0 and parent at +4. An object's class pointer is at +0. A class stores
 * its base-class pointer at +0 and the theme-inheritable flag at bit 20 of
 * the word at +32.
 */

typedef unsigned int open_cfw_runtime_theme_traversal_word;
typedef unsigned int open_cfw_runtime_theme_traversal_pointer;

struct open_cfw_runtime_theme_traversal_theme {
    open_cfw_runtime_theme_traversal_pointer apply_callback;
    open_cfw_runtime_theme_traversal_pointer parent;
};

struct open_cfw_runtime_theme_traversal_object {
    open_cfw_runtime_theme_traversal_pointer class_pointer;
};

struct open_cfw_runtime_theme_traversal_class {
    open_cfw_runtime_theme_traversal_pointer base_class;
    open_cfw_runtime_theme_traversal_word reserved_04[7];
    open_cfw_runtime_theme_traversal_word flags_20;
};

_Static_assert(
    sizeof(struct open_cfw_runtime_theme_traversal_theme) == 8U,
    "theme traversal theme prefix size changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_runtime_theme_traversal_theme,
        parent
    ) == 4U,
    "theme traversal parent offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_runtime_theme_traversal_class,
        flags_20
    ) == 32U,
    "theme traversal class-flags offset changed"
);

enum {
    OPEN_CFW_RUNTIME_THEME_INHERITABLE = 1U << 20U
};

#ifndef OPEN_CFW_RUNTIME_THEME_POINTER_TO_THEME
#define OPEN_CFW_RUNTIME_THEME_POINTER_TO_THEME(value) \
    ((const struct open_cfw_runtime_theme_traversal_theme *) \
        (__UINTPTR_TYPE__)(value))
#endif

#ifndef OPEN_CFW_RUNTIME_THEME_POINTER_TO_CLASS
#define OPEN_CFW_RUNTIME_THEME_POINTER_TO_CLASS(value) \
    ((const struct open_cfw_runtime_theme_traversal_class *) \
        (__UINTPTR_TYPE__)(value))
#endif

#ifndef OPEN_CFW_RUNTIME_THEME_INVOKE_APPLY
typedef void (*open_cfw_runtime_theme_traversal_apply_fn)(
    open_cfw_runtime_theme_traversal_pointer,
    struct open_cfw_runtime_theme_traversal_object *,
    open_cfw_runtime_theme_traversal_pointer
);
#define OPEN_CFW_RUNTIME_THEME_INVOKE_APPLY( \
    callback, theme, object \
) \
    (((open_cfw_runtime_theme_traversal_apply_fn) \
        (__UINTPTR_TYPE__)(callback))( \
            (theme), (object), (callback) \
    ))
#endif

__attribute__((used, noinline))
void open_cfw_runtime_theme_apply_chain(
    open_cfw_runtime_theme_traversal_pointer theme_pointer,
    struct open_cfw_runtime_theme_traversal_object *object
)
{
    const struct open_cfw_runtime_theme_traversal_theme *theme =
        OPEN_CFW_RUNTIME_THEME_POINTER_TO_THEME(theme_pointer);

    if (theme->parent != 0U) {
        open_cfw_runtime_theme_apply_chain(theme->parent, object);
    }
    if (theme->apply_callback != 0U) {
        OPEN_CFW_RUNTIME_THEME_INVOKE_APPLY(
            theme->apply_callback,
            theme_pointer,
            object
        );
    }
}

__attribute__((used, noinline))
void open_cfw_runtime_theme_apply_recursion(
    open_cfw_runtime_theme_traversal_pointer theme_pointer,
    struct open_cfw_runtime_theme_traversal_object *object
)
{
    open_cfw_runtime_theme_traversal_pointer original_class =
        object->class_pointer;
    const struct open_cfw_runtime_theme_traversal_class *object_class =
        OPEN_CFW_RUNTIME_THEME_POINTER_TO_CLASS(original_class);

    if (
        object_class->base_class != 0U
        && (
            object_class->flags_20
            & OPEN_CFW_RUNTIME_THEME_INHERITABLE
        ) != 0U
    ) {
        object->class_pointer = object_class->base_class;
        open_cfw_runtime_theme_apply_recursion(theme_pointer, object);
    }

    object->class_pointer = original_class;
    open_cfw_runtime_theme_apply_chain(theme_pointer, object);
}

#undef OPEN_CFW_RUNTIME_THEME_POINTER_TO_THEME
#undef OPEN_CFW_RUNTIME_THEME_POINTER_TO_CLASS
#undef OPEN_CFW_RUNTIME_THEME_INVOKE_APPLY
