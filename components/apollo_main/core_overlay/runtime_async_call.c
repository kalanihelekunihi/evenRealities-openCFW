/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded source recovery of LVGL 9.3 lv_async_call at
 * 0x00484014...0x00484051, lv_async_call_cancel at
 * 0x00484052...0x004840A9, and lv_async_timer_cb at
 * 0x004840AC...0x004840C5 in G2 firmware 2.2.6.10.
 */

typedef unsigned int open_cfw_runtime_async_pointer;

struct open_cfw_runtime_async_info {
    open_cfw_runtime_async_pointer callback;
    open_cfw_runtime_async_pointer user_data;
};

struct open_cfw_runtime_async_timer_view {
    open_cfw_runtime_async_pointer period;
    open_cfw_runtime_async_pointer last_run;
    open_cfw_runtime_async_pointer callback;
    open_cfw_runtime_async_pointer user_data;
};

_Static_assert(
    sizeof(struct open_cfw_runtime_async_info) == 8U,
    "async info ABI changed"
);
_Static_assert(
    sizeof(struct open_cfw_runtime_async_timer_view) == 16U,
    "async timer prefix ABI changed"
);

#ifndef OPEN_CFW_RUNTIME_ASYNC_ALLOCATE
typedef open_cfw_runtime_async_pointer
(*open_cfw_runtime_async_allocate_fn)(
    unsigned int size
);
#define OPEN_CFW_RUNTIME_ASYNC_ALLOCATE(size) \
    (((open_cfw_runtime_async_allocate_fn) \
        (__UINTPTR_TYPE__)0x0044F719U)((size)))
#endif

#ifndef OPEN_CFW_RUNTIME_ASYNC_FREE
typedef void (*open_cfw_runtime_async_free_fn)(
    open_cfw_runtime_async_pointer allocation
);
#define OPEN_CFW_RUNTIME_ASYNC_FREE(allocation) \
    (((open_cfw_runtime_async_free_fn) \
        (__UINTPTR_TYPE__)0x0044F759U)((allocation)))
#endif

#ifndef OPEN_CFW_RUNTIME_ASYNC_TIMER_CREATE
typedef open_cfw_runtime_async_pointer
(*open_cfw_runtime_async_timer_create_fn)(
    open_cfw_runtime_async_pointer callback,
    unsigned int period,
    open_cfw_runtime_async_pointer user_data
);
#define OPEN_CFW_RUNTIME_ASYNC_TIMER_CREATE(callback, period, user_data) \
    (((open_cfw_runtime_async_timer_create_fn) \
        (__UINTPTR_TYPE__)0x00464467U)( \
            (callback), (period), (user_data) \
        ))
#endif

#ifndef OPEN_CFW_RUNTIME_ASYNC_TIMER_SET_REPEAT
typedef void (*open_cfw_runtime_async_timer_set_repeat_fn)(
    open_cfw_runtime_async_pointer timer,
    int repeat_count
);
#define OPEN_CFW_RUNTIME_ASYNC_TIMER_SET_REPEAT(timer, repeat_count) \
    (((open_cfw_runtime_async_timer_set_repeat_fn) \
        (__UINTPTR_TYPE__)0x004645ADU)((timer), (repeat_count)))
#endif

#ifndef OPEN_CFW_RUNTIME_ASYNC_TIMER_DELETE
typedef void (*open_cfw_runtime_async_timer_delete_fn)(
    open_cfw_runtime_async_pointer timer
);
#define OPEN_CFW_RUNTIME_ASYNC_TIMER_DELETE(timer) \
    (((open_cfw_runtime_async_timer_delete_fn) \
        (__UINTPTR_TYPE__)0x004644EFU)((timer)))
#endif

#ifndef OPEN_CFW_RUNTIME_ASYNC_TIMER_GET_NEXT
typedef open_cfw_runtime_async_pointer
(*open_cfw_runtime_async_timer_get_next_fn)(
    open_cfw_runtime_async_pointer timer
);
#define OPEN_CFW_RUNTIME_ASYNC_TIMER_GET_NEXT(timer) \
    (((open_cfw_runtime_async_timer_get_next_fn) \
        (__UINTPTR_TYPE__)0x004645EDU)((timer)))
#endif

#ifndef OPEN_CFW_RUNTIME_ASYNC_INFO_FROM_POINTER
#define OPEN_CFW_RUNTIME_ASYNC_INFO_FROM_POINTER(pointer) \
    ((struct open_cfw_runtime_async_info *)(__UINTPTR_TYPE__)(pointer))
#endif

#ifndef OPEN_CFW_RUNTIME_ASYNC_TIMER_FROM_POINTER
#define OPEN_CFW_RUNTIME_ASYNC_TIMER_FROM_POINTER(pointer) \
    ((struct open_cfw_runtime_async_timer_view *) \
        (__UINTPTR_TYPE__)(pointer))
#endif

#ifndef OPEN_CFW_RUNTIME_ASYNC_TIMER_USER_DATA
#define OPEN_CFW_RUNTIME_ASYNC_TIMER_USER_DATA(timer) \
    (OPEN_CFW_RUNTIME_ASYNC_TIMER_FROM_POINTER((timer))->user_data)
#endif

#ifndef OPEN_CFW_RUNTIME_ASYNC_INVOKE
typedef void (*open_cfw_runtime_async_callback_fn)(
    open_cfw_runtime_async_pointer user_data
);
#define OPEN_CFW_RUNTIME_ASYNC_INVOKE(callback, user_data) \
    (((open_cfw_runtime_async_callback_fn) \
        (__UINTPTR_TYPE__)(callback))((user_data)))
#endif

#ifndef OPEN_CFW_RUNTIME_ASYNC_TIMER_CALLBACK
/*
 * Keep the stock Thumb identity while lv_async_call_cancel remains stock.
 * Its callback comparison at 0x00484070 resolves to the same address.
 */
#define OPEN_CFW_RUNTIME_ASYNC_TIMER_CALLBACK 0x004840ADU
#endif

enum {
    OPEN_CFW_RUNTIME_ASYNC_RESULT_INVALID = 0U,
    OPEN_CFW_RUNTIME_ASYNC_RESULT_OK = 1U
};

__attribute__((used, noinline))
unsigned int open_cfw_runtime_async_call(
    open_cfw_runtime_async_pointer callback,
    open_cfw_runtime_async_pointer user_data
)
{
    open_cfw_runtime_async_pointer allocation =
        OPEN_CFW_RUNTIME_ASYNC_ALLOCATE(
            sizeof(struct open_cfw_runtime_async_info)
        );
    struct open_cfw_runtime_async_info *info;
    open_cfw_runtime_async_pointer timer;

    if (allocation == 0U) {
        return OPEN_CFW_RUNTIME_ASYNC_RESULT_INVALID;
    }

    timer = OPEN_CFW_RUNTIME_ASYNC_TIMER_CREATE(
        OPEN_CFW_RUNTIME_ASYNC_TIMER_CALLBACK,
        0U,
        allocation
    );
    if (timer == 0U) {
        OPEN_CFW_RUNTIME_ASYNC_FREE(allocation);
        return OPEN_CFW_RUNTIME_ASYNC_RESULT_INVALID;
    }

    info = OPEN_CFW_RUNTIME_ASYNC_INFO_FROM_POINTER(allocation);
    info->callback = callback;
    info->user_data = user_data;
    OPEN_CFW_RUNTIME_ASYNC_TIMER_SET_REPEAT(timer, 1);
    return OPEN_CFW_RUNTIME_ASYNC_RESULT_OK;
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_async_call_cancel(
    open_cfw_runtime_async_pointer callback,
    open_cfw_runtime_async_pointer user_data
)
{
    open_cfw_runtime_async_pointer timer =
        OPEN_CFW_RUNTIME_ASYNC_TIMER_GET_NEXT(0U);
    unsigned int result = OPEN_CFW_RUNTIME_ASYNC_RESULT_INVALID;

    while (timer != 0U) {
        open_cfw_runtime_async_pointer next =
            OPEN_CFW_RUNTIME_ASYNC_TIMER_GET_NEXT(timer);
        struct open_cfw_runtime_async_timer_view *timer_view =
            OPEN_CFW_RUNTIME_ASYNC_TIMER_FROM_POINTER(timer);

        if (
            timer_view->callback
            == OPEN_CFW_RUNTIME_ASYNC_TIMER_CALLBACK
        ) {
            open_cfw_runtime_async_pointer allocation =
                timer_view->user_data;
            struct open_cfw_runtime_async_info *info =
                OPEN_CFW_RUNTIME_ASYNC_INFO_FROM_POINTER(allocation);

            if (
                info->callback == callback
                && info->user_data == user_data
            ) {
                OPEN_CFW_RUNTIME_ASYNC_TIMER_DELETE(timer);
                OPEN_CFW_RUNTIME_ASYNC_FREE(allocation);
                result = OPEN_CFW_RUNTIME_ASYNC_RESULT_OK;
            }
        }

        timer = next;
    }

    return result;
}

__attribute__((used, noinline))
void open_cfw_runtime_async_timer_callback(
    open_cfw_runtime_async_pointer timer
)
{
    open_cfw_runtime_async_pointer allocation =
        OPEN_CFW_RUNTIME_ASYNC_TIMER_USER_DATA(timer);
    struct open_cfw_runtime_async_info *info =
        OPEN_CFW_RUNTIME_ASYNC_INFO_FROM_POINTER(allocation);
    open_cfw_runtime_async_pointer callback = info->callback;
    open_cfw_runtime_async_pointer user_data = info->user_data;

    OPEN_CFW_RUNTIME_ASYNC_TIMER_DELETE(timer);
    OPEN_CFW_RUNTIME_ASYNC_FREE(allocation);
    OPEN_CFW_RUNTIME_ASYNC_INVOKE(callback, user_data);
}

#undef OPEN_CFW_RUNTIME_ASYNC_ALLOCATE
#undef OPEN_CFW_RUNTIME_ASYNC_FREE
#undef OPEN_CFW_RUNTIME_ASYNC_TIMER_CREATE
#undef OPEN_CFW_RUNTIME_ASYNC_TIMER_SET_REPEAT
#undef OPEN_CFW_RUNTIME_ASYNC_TIMER_DELETE
#undef OPEN_CFW_RUNTIME_ASYNC_TIMER_GET_NEXT
#undef OPEN_CFW_RUNTIME_ASYNC_INFO_FROM_POINTER
#undef OPEN_CFW_RUNTIME_ASYNC_TIMER_FROM_POINTER
#undef OPEN_CFW_RUNTIME_ASYNC_TIMER_USER_DATA
#undef OPEN_CFW_RUNTIME_ASYNC_INVOKE
#undef OPEN_CFW_RUNTIME_ASYNC_TIMER_CALLBACK
