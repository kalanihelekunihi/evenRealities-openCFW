/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded source recovery of LVGL 9.3 `lv_obj_allocate_spec_attr` at
 * 0x0043E1FA...0x0043E282 in G2 firmware 2.2.6.10.
 *
 * Identity is direct, not inferred: the stock assert-log call embeds the
 * literal function-name string "lv_obj_allocate_spec_attr" (read from the
 * official image at 0x0043EE34 -> 0x0076DC7C) together with the LVGL
 * source path "LVGL/src/core/lv_obj.c" (0x0043E298 -> 0x006E8890), the
 * assert message "Asserted at expression: %s (%s)" (0x0043E290), and the
 * two guarded expressions "obj != NULL" / "NULL pointer" (first assert,
 * 0x0043E28C/0x0043E288) and "obj->spec_attr != NULL" / "Out of memory"
 * (second assert, 0x0043EE3C/0x0043EE38).
 *
 * Machine ABI: r0 obj. The stock epilogue echoes the incoming r0/r1 back
 * out (CONCAT44(param_2, obj) in the decompilation); the real LVGL
 * function is void and every direct caller discards the return value, so
 * this port declares it void.
 *
 * lv_obj_spec_attr_t is only touched at two fields here: the trailing
 * bitfield word at +0x32 (an allocation of size 0x34 leaves everything
 * else at the zero-fill the allocator already guarantees, matching
 * upstream's `lv_malloc_zeroed` call and its subsequent explicit
 * `scroll_dir = LV_DIR_ALL; scrollbar_mode = LV_SCROLLBAR_MODE_AUTO;`
 * assignments).
 */

typedef unsigned int open_cfw_runtime_spec_attr_pointer;

struct open_cfw_runtime_obj_spec_attr_view {
    unsigned char reserved_00[0x32];
    unsigned short scroll_and_bar_bits;
};

_Static_assert(
    sizeof(struct open_cfw_runtime_obj_spec_attr_view) == 0x34U,
    "lv_obj_spec_attr_t size changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_runtime_obj_spec_attr_view,
        scroll_and_bar_bits
    ) == 0x32U,
    "lv_obj_spec_attr_t scroll/scrollbar bitfield offset changed"
);

struct open_cfw_runtime_obj_view {
    unsigned char reserved_00[0x08];
    open_cfw_runtime_spec_attr_pointer spec_attr;
};

_Static_assert(
    __builtin_offsetof(struct open_cfw_runtime_obj_view, spec_attr) == 0x08U,
    "lv_obj_t spec_attr offset changed"
);

enum {
    OPEN_CFW_RUNTIME_SPEC_ATTR_SIZE = 0x34U,
    OPEN_CFW_RUNTIME_SPEC_ATTR_SCROLL_DIR_ALL = 0x3C0U,
    OPEN_CFW_RUNTIME_SPEC_ATTR_SCROLLBAR_MODE_AUTO = 0x03U,
    OPEN_CFW_RUNTIME_SPEC_ATTR_LOG_LEVEL = 3U,
    OPEN_CFW_RUNTIME_SPEC_ATTR_LOG_FILE = 0x006E8890U,
    OPEN_CFW_RUNTIME_SPEC_ATTR_LOG_FUNCTION = 0x0076DC7CU,
    OPEN_CFW_RUNTIME_SPEC_ATTR_ASSERT_FORMAT = 0x00761CB0U,
    OPEN_CFW_RUNTIME_SPEC_ATTR_NULL_LINE = 0x00000178U,
    OPEN_CFW_RUNTIME_SPEC_ATTR_NULL_EXPRESSION = 0x0078B3F0U,
    OPEN_CFW_RUNTIME_SPEC_ATTR_NULL_MESSAGE = 0x00787610U,
    OPEN_CFW_RUNTIME_SPEC_ATTR_ALLOC_LINE = 0x0000017CU,
    OPEN_CFW_RUNTIME_SPEC_ATTR_ALLOC_EXPRESSION = 0x007791FCU,
    OPEN_CFW_RUNTIME_SPEC_ATTR_OOM_MESSAGE = 0x00787640U
};

#ifndef OPEN_CFW_RUNTIME_SPEC_ATTR_ALLOCATE_ZEROED
typedef open_cfw_runtime_spec_attr_pointer
(*open_cfw_runtime_spec_attr_allocate_fn)(unsigned int size);
#define OPEN_CFW_RUNTIME_SPEC_ATTR_ALLOCATE_ZEROED(size) \
    (((open_cfw_runtime_spec_attr_allocate_fn) \
        (__UINTPTR_TYPE__)0x0044F731U)((size)))
#endif

#ifndef OPEN_CFW_RUNTIME_SPEC_ATTR_LOG_ASSERT
#define OPEN_CFW_RUNTIME_SPEC_ATTR_LOG_ASSERT( \
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

#ifndef OPEN_CFW_RUNTIME_SPEC_ATTR_FATAL
#define OPEN_CFW_RUNTIME_SPEC_ATTR_FATAL() \
    do { \
        for (;;) { \
            *(volatile unsigned int *)(__UINTPTR_TYPE__)0xFFFFFFFFU = 0U; \
        } \
    } while (0)
#endif

#ifndef OPEN_CFW_RUNTIME_SPEC_ATTR_FROM_POINTER
#define OPEN_CFW_RUNTIME_SPEC_ATTR_FROM_POINTER(pointer) \
    ((struct open_cfw_runtime_obj_spec_attr_view *) \
        (__UINTPTR_TYPE__)(pointer))
#endif

__attribute__((used, noinline))
void open_cfw_runtime_obj_allocate_spec_attr(
    struct open_cfw_runtime_obj_view *obj
)
{
    open_cfw_runtime_spec_attr_pointer allocation;
    struct open_cfw_runtime_obj_spec_attr_view *spec_attr;

    if (obj == (struct open_cfw_runtime_obj_view *)0) {
        OPEN_CFW_RUNTIME_SPEC_ATTR_LOG_ASSERT(
            OPEN_CFW_RUNTIME_SPEC_ATTR_LOG_LEVEL,
            OPEN_CFW_RUNTIME_SPEC_ATTR_LOG_FILE,
            OPEN_CFW_RUNTIME_SPEC_ATTR_NULL_LINE,
            OPEN_CFW_RUNTIME_SPEC_ATTR_LOG_FUNCTION,
            OPEN_CFW_RUNTIME_SPEC_ATTR_ASSERT_FORMAT,
            OPEN_CFW_RUNTIME_SPEC_ATTR_NULL_EXPRESSION,
            OPEN_CFW_RUNTIME_SPEC_ATTR_NULL_MESSAGE
        );
        OPEN_CFW_RUNTIME_SPEC_ATTR_FATAL();
        return;
    }

    if (obj->spec_attr != 0U) {
        return;
    }

    allocation = OPEN_CFW_RUNTIME_SPEC_ATTR_ALLOCATE_ZEROED(
        OPEN_CFW_RUNTIME_SPEC_ATTR_SIZE
    );
    obj->spec_attr = allocation;
    if (allocation == 0U) {
        OPEN_CFW_RUNTIME_SPEC_ATTR_LOG_ASSERT(
            OPEN_CFW_RUNTIME_SPEC_ATTR_LOG_LEVEL,
            OPEN_CFW_RUNTIME_SPEC_ATTR_LOG_FILE,
            OPEN_CFW_RUNTIME_SPEC_ATTR_ALLOC_LINE,
            OPEN_CFW_RUNTIME_SPEC_ATTR_LOG_FUNCTION,
            OPEN_CFW_RUNTIME_SPEC_ATTR_ASSERT_FORMAT,
            OPEN_CFW_RUNTIME_SPEC_ATTR_ALLOC_EXPRESSION,
            OPEN_CFW_RUNTIME_SPEC_ATTR_OOM_MESSAGE
        );
        OPEN_CFW_RUNTIME_SPEC_ATTR_FATAL();
        return;
    }

    spec_attr = OPEN_CFW_RUNTIME_SPEC_ATTR_FROM_POINTER(allocation);
    spec_attr->scroll_and_bar_bits |=
        (unsigned short)OPEN_CFW_RUNTIME_SPEC_ATTR_SCROLL_DIR_ALL;
    spec_attr->scroll_and_bar_bits |=
        (unsigned short)OPEN_CFW_RUNTIME_SPEC_ATTR_SCROLLBAR_MODE_AUTO;
}

#undef OPEN_CFW_RUNTIME_SPEC_ATTR_ALLOCATE_ZEROED
#undef OPEN_CFW_RUNTIME_SPEC_ATTR_LOG_ASSERT
#undef OPEN_CFW_RUNTIME_SPEC_ATTR_FATAL
#undef OPEN_CFW_RUNTIME_SPEC_ATTR_FROM_POINTER
