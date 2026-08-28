/*
 * SPDX-License-Identifier: MIT
 *
 * Host substitutions for the source-owned G2 LVGL theme cluster.
 */

static void *open_cfw_test_runtime_theme_object_get_display(void *object);
static void *open_cfw_test_runtime_theme_display_get_default(void);
static void *open_cfw_test_runtime_theme_display_get_theme(void *display);
static void open_cfw_test_runtime_theme_object_remove_styles(void *object);
static void open_cfw_test_runtime_theme_apply_recursion(
    unsigned int theme,
    void *object
);
static const unsigned char *open_cfw_test_runtime_theme_pointer_to_bytes(
    unsigned int value
);
static void *open_cfw_test_runtime_theme_copy(
    void *destination,
    const void *source,
    unsigned int size
);
struct open_cfw_runtime_theme_color;
static struct open_cfw_runtime_theme_color
open_cfw_test_runtime_theme_palette_main(unsigned int index);

#define OPEN_CFW_RUNTIME_THEME_OBJECT_GET_DISPLAY(object) \
    open_cfw_test_runtime_theme_object_get_display((object))
#define OPEN_CFW_RUNTIME_THEME_DISPLAY_GET_DEFAULT() \
    open_cfw_test_runtime_theme_display_get_default()
#define OPEN_CFW_RUNTIME_THEME_DISPLAY_GET_THEME(display) \
    open_cfw_test_runtime_theme_display_get_theme((display))
#define OPEN_CFW_RUNTIME_THEME_OBJECT_REMOVE_STYLES(object) \
    open_cfw_test_runtime_theme_object_remove_styles((object))
#define OPEN_CFW_RUNTIME_THEME_APPLY_RECURSION(theme, object) \
    open_cfw_test_runtime_theme_apply_recursion((theme), (object))
#define OPEN_CFW_RUNTIME_THEME_POINTER_TO_BYTES(value) \
    open_cfw_test_runtime_theme_pointer_to_bytes((value))
#define OPEN_CFW_RUNTIME_THEME_COPY(destination, source, size) \
    open_cfw_test_runtime_theme_copy((destination), (source), (size))
#define OPEN_CFW_RUNTIME_THEME_PALETTE_MAIN(index) \
    open_cfw_test_runtime_theme_palette_main((index))

#include "../../components/apollo_main/core_overlay/runtime_theme.c"

enum {
    OPEN_CFW_TEST_RUNTIME_THEME_STORAGE_SIZE = 1024U,
    OPEN_CFW_TEST_RUNTIME_THEME_EVENT_CAPACITY = 16U,
    OPEN_CFW_TEST_RUNTIME_THEME_OBJECT_GET_DISPLAY = 1U,
    OPEN_CFW_TEST_RUNTIME_THEME_DISPLAY_GET_DEFAULT = 2U,
    OPEN_CFW_TEST_RUNTIME_THEME_DISPLAY_GET_THEME = 3U,
    OPEN_CFW_TEST_RUNTIME_THEME_OBJECT_REMOVE_STYLES = 4U,
    OPEN_CFW_TEST_RUNTIME_THEME_APPLY_RECURSION = 5U,
    OPEN_CFW_TEST_RUNTIME_THEME_COPY = 6U,
    OPEN_CFW_TEST_RUNTIME_THEME_PALETTE_MAIN = 7U
};

unsigned char open_cfw_test_runtime_theme_storage[
    OPEN_CFW_TEST_RUNTIME_THEME_STORAGE_SIZE
];
unsigned int open_cfw_test_runtime_theme_object_display;
unsigned int open_cfw_test_runtime_theme_default_display;
unsigned int open_cfw_test_runtime_theme_resolved_theme;
struct open_cfw_runtime_theme_color
    open_cfw_test_runtime_theme_fallback_color;
unsigned int open_cfw_test_runtime_theme_event_count;
unsigned int open_cfw_test_runtime_theme_event_kind[
    OPEN_CFW_TEST_RUNTIME_THEME_EVENT_CAPACITY
];
unsigned int open_cfw_test_runtime_theme_event_first[
    OPEN_CFW_TEST_RUNTIME_THEME_EVENT_CAPACITY
];
unsigned int open_cfw_test_runtime_theme_event_second[
    OPEN_CFW_TEST_RUNTIME_THEME_EVENT_CAPACITY
];
unsigned int open_cfw_test_runtime_theme_event_third[
    OPEN_CFW_TEST_RUNTIME_THEME_EVENT_CAPACITY
];

static void open_cfw_test_runtime_theme_record(
    unsigned int kind,
    unsigned int first,
    unsigned int second,
    unsigned int third
)
{
    unsigned int index = open_cfw_test_runtime_theme_event_count;

    if (index < OPEN_CFW_TEST_RUNTIME_THEME_EVENT_CAPACITY) {
        open_cfw_test_runtime_theme_event_kind[index] = kind;
        open_cfw_test_runtime_theme_event_first[index] = first;
        open_cfw_test_runtime_theme_event_second[index] = second;
        open_cfw_test_runtime_theme_event_third[index] = third;
    }
    open_cfw_test_runtime_theme_event_count = index + 1U;
}

static void *open_cfw_test_runtime_theme_object_get_display(void *object)
{
    open_cfw_test_runtime_theme_record(
        OPEN_CFW_TEST_RUNTIME_THEME_OBJECT_GET_DISPLAY,
        (unsigned int)(__UINTPTR_TYPE__)object,
        open_cfw_test_runtime_theme_object_display,
        0U
    );
    return (void *)(__UINTPTR_TYPE__)
        open_cfw_test_runtime_theme_object_display;
}

static void *open_cfw_test_runtime_theme_display_get_default(void)
{
    open_cfw_test_runtime_theme_record(
        OPEN_CFW_TEST_RUNTIME_THEME_DISPLAY_GET_DEFAULT,
        open_cfw_test_runtime_theme_default_display,
        0U,
        0U
    );
    return (void *)(__UINTPTR_TYPE__)
        open_cfw_test_runtime_theme_default_display;
}

static void *open_cfw_test_runtime_theme_display_get_theme(void *display)
{
    open_cfw_test_runtime_theme_record(
        OPEN_CFW_TEST_RUNTIME_THEME_DISPLAY_GET_THEME,
        (unsigned int)(__UINTPTR_TYPE__)display,
        open_cfw_test_runtime_theme_resolved_theme,
        0U
    );
    return (void *)(__UINTPTR_TYPE__)
        open_cfw_test_runtime_theme_resolved_theme;
}

static void open_cfw_test_runtime_theme_object_remove_styles(void *object)
{
    open_cfw_test_runtime_theme_record(
        OPEN_CFW_TEST_RUNTIME_THEME_OBJECT_REMOVE_STYLES,
        (unsigned int)(__UINTPTR_TYPE__)object,
        0U,
        0U
    );
}

static void open_cfw_test_runtime_theme_apply_recursion(
    unsigned int theme,
    void *object
)
{
    open_cfw_test_runtime_theme_record(
        OPEN_CFW_TEST_RUNTIME_THEME_APPLY_RECURSION,
        theme,
        (unsigned int)(__UINTPTR_TYPE__)object,
        0U
    );
}

static const unsigned char *open_cfw_test_runtime_theme_pointer_to_bytes(
    unsigned int value
)
{
    return open_cfw_test_runtime_theme_storage + value;
}

static void *open_cfw_test_runtime_theme_copy(
    void *destination,
    const void *source,
    unsigned int size
)
{
    unsigned char *destination_bytes = (unsigned char *)destination;
    const unsigned char *source_bytes = (const unsigned char *)source;
    unsigned int source_offset = (unsigned int)(
        source_bytes - open_cfw_test_runtime_theme_storage
    );
    unsigned int index;

    open_cfw_test_runtime_theme_record(
        OPEN_CFW_TEST_RUNTIME_THEME_COPY,
        source_offset,
        size,
        0U
    );
    for (index = 0U; index < size; index += 1U) {
        destination_bytes[index] = source_bytes[index];
    }
    return destination;
}

static struct open_cfw_runtime_theme_color
open_cfw_test_runtime_theme_palette_main(unsigned int index)
{
    open_cfw_test_runtime_theme_record(
        OPEN_CFW_TEST_RUNTIME_THEME_PALETTE_MAIN,
        index,
        0U,
        0U
    );
    return open_cfw_test_runtime_theme_fallback_color;
}

void open_cfw_test_runtime_theme_reset(
    unsigned int object_display,
    unsigned int default_display,
    unsigned int theme,
    unsigned int fallback_color
)
{
    unsigned int index;

    for (
        index = 0U;
        index < OPEN_CFW_TEST_RUNTIME_THEME_STORAGE_SIZE;
        index += 1U
    ) {
        open_cfw_test_runtime_theme_storage[index] = 0xCCU;
    }
    open_cfw_test_runtime_theme_object_display = object_display;
    open_cfw_test_runtime_theme_default_display = default_display;
    open_cfw_test_runtime_theme_resolved_theme = theme;
    open_cfw_test_runtime_theme_fallback_color.blue =
        (unsigned char)fallback_color;
    open_cfw_test_runtime_theme_fallback_color.green =
        (unsigned char)(fallback_color >> 8U);
    open_cfw_test_runtime_theme_fallback_color.red =
        (unsigned char)(fallback_color >> 16U);
    open_cfw_test_runtime_theme_event_count = 0U;
    for (
        index = 0U;
        index < OPEN_CFW_TEST_RUNTIME_THEME_EVENT_CAPACITY;
        index += 1U
    ) {
        open_cfw_test_runtime_theme_event_kind[index] = 0U;
        open_cfw_test_runtime_theme_event_first[index] = 0U;
        open_cfw_test_runtime_theme_event_second[index] = 0U;
        open_cfw_test_runtime_theme_event_third[index] = 0U;
    }
}

void open_cfw_test_runtime_theme_set_primary_color(unsigned int color)
{
    unsigned int offset =
        open_cfw_test_runtime_theme_resolved_theme
        + OPEN_CFW_RUNTIME_THEME_PRIMARY_COLOR_OFFSET;

    open_cfw_test_runtime_theme_storage[offset] = (unsigned char)color;
    open_cfw_test_runtime_theme_storage[offset + 1U] =
        (unsigned char)(color >> 8U);
    open_cfw_test_runtime_theme_storage[offset + 2U] =
        (unsigned char)(color >> 16U);
}

unsigned int open_cfw_test_runtime_theme_execute_get(unsigned int object)
{
    return open_cfw_runtime_theme_get_from_object(
        (void *)(__UINTPTR_TYPE__)object
    );
}

void open_cfw_test_runtime_theme_execute_apply(unsigned int object)
{
    open_cfw_runtime_theme_apply((void *)(__UINTPTR_TYPE__)object);
}

unsigned int open_cfw_test_runtime_theme_execute_primary(
    unsigned int object,
    unsigned int padding_carrier
)
{
    struct open_cfw_runtime_theme_color color =
        open_cfw_runtime_theme_get_primary_color(
            (void *)(__UINTPTR_TYPE__)object
        );
    unsigned int packed = padding_carrier & 0xFF000000U;

    packed |= (unsigned int)color.blue;
    packed |= (unsigned int)color.green << 8U;
    packed |= (unsigned int)color.red << 16U;
    return packed;
}
