/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Host substitutions for the source-owned G2 LVGL theme traversal.
 */

static const void *open_cfw_test_runtime_theme_pointer_to_theme(
    unsigned int value
);
static const void *open_cfw_test_runtime_theme_pointer_to_class(
    unsigned int value
);
static void open_cfw_test_runtime_theme_invoke_apply(
    unsigned int callback,
    unsigned int theme,
    void *object
);

#define OPEN_CFW_RUNTIME_THEME_POINTER_TO_THEME(value) \
    ((const struct open_cfw_runtime_theme_traversal_theme *) \
        open_cfw_test_runtime_theme_pointer_to_theme((value)))
#define OPEN_CFW_RUNTIME_THEME_POINTER_TO_CLASS(value) \
    ((const struct open_cfw_runtime_theme_traversal_class *) \
        open_cfw_test_runtime_theme_pointer_to_class((value)))
#define OPEN_CFW_RUNTIME_THEME_INVOKE_APPLY(callback, theme, object) \
    open_cfw_test_runtime_theme_invoke_apply( \
        (callback), (theme), (object) \
    )

#include "../../components/apollo_main/core_overlay/runtime_theme_traversal.c"

enum {
    OPEN_CFW_TEST_RUNTIME_THEME_STORAGE_SIZE = 32768U,
    OPEN_CFW_TEST_RUNTIME_THEME_BASE = 128U,
    OPEN_CFW_TEST_RUNTIME_THEME_STRIDE = 64U,
    OPEN_CFW_TEST_RUNTIME_CLASS_BASE = 16384U,
    OPEN_CFW_TEST_RUNTIME_CLASS_STRIDE = 64U,
    OPEN_CFW_TEST_RUNTIME_THEME_MAX_RECORDS = 4096U
};

unsigned char open_cfw_test_runtime_theme_storage[
    OPEN_CFW_TEST_RUNTIME_THEME_STORAGE_SIZE
];
struct open_cfw_runtime_theme_traversal_object
    open_cfw_test_runtime_theme_object;
unsigned int open_cfw_test_runtime_theme_record_count;
unsigned int open_cfw_test_runtime_theme_record_callback[
    OPEN_CFW_TEST_RUNTIME_THEME_MAX_RECORDS
];
unsigned int open_cfw_test_runtime_theme_record_callback_r2[
    OPEN_CFW_TEST_RUNTIME_THEME_MAX_RECORDS
];
unsigned int open_cfw_test_runtime_theme_record_theme[
    OPEN_CFW_TEST_RUNTIME_THEME_MAX_RECORDS
];
unsigned int open_cfw_test_runtime_theme_record_class[
    OPEN_CFW_TEST_RUNTIME_THEME_MAX_RECORDS
];
unsigned int open_cfw_test_runtime_theme_mutating_callback;
unsigned int open_cfw_test_runtime_theme_mutated_class;
unsigned int open_cfw_test_runtime_theme_theme_resolutions;
unsigned int open_cfw_test_runtime_theme_class_resolutions;

static unsigned int open_cfw_test_runtime_theme_handle(unsigned int index)
{
    return (
        OPEN_CFW_TEST_RUNTIME_THEME_BASE
        + index * OPEN_CFW_TEST_RUNTIME_THEME_STRIDE
    );
}

static unsigned int open_cfw_test_runtime_class_handle(unsigned int index)
{
    return (
        OPEN_CFW_TEST_RUNTIME_CLASS_BASE
        + index * OPEN_CFW_TEST_RUNTIME_CLASS_STRIDE
    );
}

static void open_cfw_test_runtime_theme_store_word(
    unsigned int offset,
    unsigned int value
)
{
    open_cfw_test_runtime_theme_storage[offset] = (unsigned char)value;
    open_cfw_test_runtime_theme_storage[offset + 1U] =
        (unsigned char)(value >> 8U);
    open_cfw_test_runtime_theme_storage[offset + 2U] =
        (unsigned char)(value >> 16U);
    open_cfw_test_runtime_theme_storage[offset + 3U] =
        (unsigned char)(value >> 24U);
}

static const void *open_cfw_test_runtime_theme_pointer_to_theme(
    unsigned int value
)
{
    open_cfw_test_runtime_theme_theme_resolutions += 1U;
    return open_cfw_test_runtime_theme_storage + value;
}

static const void *open_cfw_test_runtime_theme_pointer_to_class(
    unsigned int value
)
{
    open_cfw_test_runtime_theme_class_resolutions += 1U;
    return open_cfw_test_runtime_theme_storage + value;
}

static void open_cfw_test_runtime_theme_invoke_apply(
    unsigned int callback,
    unsigned int theme,
    void *object_pointer
)
{
    struct open_cfw_runtime_theme_traversal_object *object =
        (struct open_cfw_runtime_theme_traversal_object *)object_pointer;
    unsigned int index = open_cfw_test_runtime_theme_record_count;

    if (index < OPEN_CFW_TEST_RUNTIME_THEME_MAX_RECORDS) {
        open_cfw_test_runtime_theme_record_callback[index] = callback;
        open_cfw_test_runtime_theme_record_callback_r2[index] = callback;
        open_cfw_test_runtime_theme_record_theme[index] = theme;
        open_cfw_test_runtime_theme_record_class[index] =
            object->class_pointer;
    }
    open_cfw_test_runtime_theme_record_count = index + 1U;
    if (callback == open_cfw_test_runtime_theme_mutating_callback) {
        object->class_pointer = open_cfw_test_runtime_theme_mutated_class;
    }
}

void open_cfw_test_runtime_theme_reset(
    unsigned int theme_count,
    unsigned int class_count
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
    for (
        index = 0U;
        index < OPEN_CFW_TEST_RUNTIME_THEME_MAX_RECORDS;
        index += 1U
    ) {
        open_cfw_test_runtime_theme_record_callback[index] = 0U;
        open_cfw_test_runtime_theme_record_callback_r2[index] = 0U;
        open_cfw_test_runtime_theme_record_theme[index] = 0U;
        open_cfw_test_runtime_theme_record_class[index] = 0U;
    }

    for (index = 0U; index < theme_count; index += 1U) {
        unsigned int theme = open_cfw_test_runtime_theme_handle(index);
        unsigned int parent =
            index == 0U
            ? 0U
            : open_cfw_test_runtime_theme_handle(index - 1U);

        open_cfw_test_runtime_theme_store_word(theme, index + 1U);
        open_cfw_test_runtime_theme_store_word(theme + 4U, parent);
    }
    for (index = 0U; index < class_count; index += 1U) {
        unsigned int object_class =
            open_cfw_test_runtime_class_handle(index);
        unsigned int base_class =
            index == 0U
            ? 0U
            : open_cfw_test_runtime_class_handle(index - 1U);

        open_cfw_test_runtime_theme_store_word(
            object_class,
            base_class
        );
        open_cfw_test_runtime_theme_store_word(
            object_class + 32U,
            1U << 20U
        );
    }

    open_cfw_test_runtime_theme_object.class_pointer =
        class_count == 0U
        ? 0U
        : open_cfw_test_runtime_class_handle(class_count - 1U);
    open_cfw_test_runtime_theme_record_count = 0U;
    open_cfw_test_runtime_theme_mutating_callback = 0U;
    open_cfw_test_runtime_theme_mutated_class = 0U;
    open_cfw_test_runtime_theme_theme_resolutions = 0U;
    open_cfw_test_runtime_theme_class_resolutions = 0U;
}

unsigned int open_cfw_test_runtime_theme_at(unsigned int index)
{
    return open_cfw_test_runtime_theme_handle(index);
}

unsigned int open_cfw_test_runtime_class_at(unsigned int index)
{
    return open_cfw_test_runtime_class_handle(index);
}

void open_cfw_test_runtime_theme_set_callback(
    unsigned int index,
    unsigned int callback
)
{
    open_cfw_test_runtime_theme_store_word(
        open_cfw_test_runtime_theme_handle(index),
        callback
    );
}

void open_cfw_test_runtime_theme_set_parent(
    unsigned int index,
    unsigned int parent
)
{
    open_cfw_test_runtime_theme_store_word(
        open_cfw_test_runtime_theme_handle(index) + 4U,
        parent
    );
}

void open_cfw_test_runtime_class_set_base(
    unsigned int index,
    unsigned int base_class
)
{
    open_cfw_test_runtime_theme_store_word(
        open_cfw_test_runtime_class_handle(index),
        base_class
    );
}

void open_cfw_test_runtime_class_set_flags(
    unsigned int index,
    unsigned int flags
)
{
    open_cfw_test_runtime_theme_store_word(
        open_cfw_test_runtime_class_handle(index) + 32U,
        flags
    );
}

void open_cfw_test_runtime_theme_set_mutation(
    unsigned int callback,
    unsigned int object_class
)
{
    open_cfw_test_runtime_theme_mutating_callback = callback;
    open_cfw_test_runtime_theme_mutated_class = object_class;
}

void open_cfw_test_runtime_theme_execute_chain(unsigned int theme)
{
    open_cfw_runtime_theme_apply_chain(
        theme,
        &open_cfw_test_runtime_theme_object
    );
}

void open_cfw_test_runtime_theme_execute_recursion(unsigned int theme)
{
    open_cfw_runtime_theme_apply_recursion(
        theme,
        &open_cfw_test_runtime_theme_object
    );
}
