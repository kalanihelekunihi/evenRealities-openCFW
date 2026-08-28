/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded source replacements for the G2 2.2.6.10 LVGL theme cluster:
 *
 *   0x00482F74...0x00482F89  resolve an object's active theme
 *   0x00482F8A...0x00482FA9  remove styles and apply the active theme
 *   0x00482FAA...0x00482FCD  return the active primary color
 *
 * All target pointers are 32-bit values. RGB888 values use the LVGL byte
 * order blue, green, red and are three-byte AAPCS aggregates. Their fourth
 * return-register byte is padding and intentionally unspecified.
 */

typedef unsigned int open_cfw_runtime_theme_word;
typedef unsigned int open_cfw_runtime_theme_pointer;

struct open_cfw_runtime_theme_color {
    unsigned char blue;
    unsigned char green;
    unsigned char red;
};

_Static_assert(
    sizeof(open_cfw_runtime_theme_word) == 4U,
    "theme word width changed"
);
_Static_assert(
    sizeof(open_cfw_runtime_theme_pointer) == 4U,
    "theme pointer width changed"
);
_Static_assert(
    sizeof(struct open_cfw_runtime_theme_color) == 3U,
    "theme RGB888 size changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_runtime_theme_color, blue) == 0U,
    "theme blue offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_runtime_theme_color, green) == 1U,
    "theme green offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_runtime_theme_color, red) == 2U,
    "theme red offset changed"
);

enum {
    OPEN_CFW_RUNTIME_THEME_PRIMARY_COLOR_OFFSET = 0x10U,
    OPEN_CFW_RUNTIME_THEME_FALLBACK_PALETTE = 0x11U
};

#ifndef OPEN_CFW_RUNTIME_THEME_OBJECT_GET_DISPLAY
#define OPEN_CFW_RUNTIME_THEME_OBJECT_GET_DISPLAY(object) \
    (((void *(*)(void *))0x0044DC0BU)((object)))
#endif

#ifndef OPEN_CFW_RUNTIME_THEME_DISPLAY_GET_DEFAULT
#define OPEN_CFW_RUNTIME_THEME_DISPLAY_GET_DEFAULT() \
    (((void *(*)(void))0x0044FA1BU)())
#endif

#ifndef OPEN_CFW_RUNTIME_THEME_DISPLAY_GET_THEME
#define OPEN_CFW_RUNTIME_THEME_DISPLAY_GET_THEME(display) \
    (((void *(*)(void *))0x0044FE7FU)((display)))
#endif

#ifndef OPEN_CFW_RUNTIME_THEME_OBJECT_REMOVE_STYLES
#define OPEN_CFW_RUNTIME_THEME_OBJECT_REMOVE_STYLES(object) \
    (((void (*)(void *))0x0044BC3BU)((object)))
#endif

#ifndef OPEN_CFW_RUNTIME_THEME_APPLY_RECURSION
#define OPEN_CFW_RUNTIME_THEME_APPLY_RECURSION(theme, object) \
    (((void (*)(void *, void *))0x00482FF3U)( \
        (void *)(__UINTPTR_TYPE__)(theme), \
        (object) \
    ))
#endif

#ifndef OPEN_CFW_RUNTIME_THEME_POINTER_TO_BYTES
#define OPEN_CFW_RUNTIME_THEME_POINTER_TO_BYTES(value) \
    ((const unsigned char *)(__UINTPTR_TYPE__)(value))
#endif

#ifndef OPEN_CFW_RUNTIME_THEME_COPY
#define OPEN_CFW_RUNTIME_THEME_COPY(destination, source, size) \
    (((void *(*)(void *, const void *, unsigned int))0x00439BE5U)( \
        (destination), (source), (size) \
    ))
#endif

#ifndef OPEN_CFW_RUNTIME_THEME_PALETTE_MAIN
#define OPEN_CFW_RUNTIME_THEME_PALETTE_MAIN(index) \
    (((struct open_cfw_runtime_theme_color (*)(unsigned int)) \
        0x00488291U)((index)))
#endif

__attribute__((used, noinline))
open_cfw_runtime_theme_pointer open_cfw_runtime_theme_get_from_object(
    void *object
)
{
    void *display;
    void *theme;

    if (object != (void *)0) {
        display = OPEN_CFW_RUNTIME_THEME_OBJECT_GET_DISPLAY(object);
    }
    else {
        display = OPEN_CFW_RUNTIME_THEME_DISPLAY_GET_DEFAULT();
    }
    theme = OPEN_CFW_RUNTIME_THEME_DISPLAY_GET_THEME(display);
    return (open_cfw_runtime_theme_pointer)(__UINTPTR_TYPE__)theme;
}

__attribute__((used, noinline))
void open_cfw_runtime_theme_apply(void *object)
{
    open_cfw_runtime_theme_pointer theme =
        open_cfw_runtime_theme_get_from_object(object);

    if (theme == 0U) {
        return;
    }
    OPEN_CFW_RUNTIME_THEME_OBJECT_REMOVE_STYLES(object);
    OPEN_CFW_RUNTIME_THEME_APPLY_RECURSION(theme, object);
}

__attribute__((used, noinline))
struct open_cfw_runtime_theme_color
open_cfw_runtime_theme_get_primary_color(void *object)
{
    open_cfw_runtime_theme_pointer theme =
        open_cfw_runtime_theme_get_from_object(object);
    struct open_cfw_runtime_theme_color color;

    if (theme != 0U) {
        const unsigned char *theme_bytes =
            OPEN_CFW_RUNTIME_THEME_POINTER_TO_BYTES(theme);

        (void)OPEN_CFW_RUNTIME_THEME_COPY(
            &color,
            theme_bytes + OPEN_CFW_RUNTIME_THEME_PRIMARY_COLOR_OFFSET,
            sizeof(color)
        );
        return color;
    }
    return OPEN_CFW_RUNTIME_THEME_PALETTE_MAIN(
        OPEN_CFW_RUNTIME_THEME_FALLBACK_PALETTE
    );
}

#undef OPEN_CFW_RUNTIME_THEME_OBJECT_GET_DISPLAY
#undef OPEN_CFW_RUNTIME_THEME_DISPLAY_GET_DEFAULT
#undef OPEN_CFW_RUNTIME_THEME_DISPLAY_GET_THEME
#undef OPEN_CFW_RUNTIME_THEME_OBJECT_REMOVE_STYLES
#undef OPEN_CFW_RUNTIME_THEME_APPLY_RECURSION
#undef OPEN_CFW_RUNTIME_THEME_POINTER_TO_BYTES
#undef OPEN_CFW_RUNTIME_THEME_COPY
#undef OPEN_CFW_RUNTIME_THEME_PALETTE_MAIN
