/* SPDX-License-Identifier: MIT */
/* Exact-ABI task-notification-mode LVGL thread-sync provider. */

#include "lvgl_ambiq_lvgl_thread_sync_signal_provider.h"

#include <stddef.h>
#include <stdint.h>

typedef int32_t open_cfw_base_type;
typedef uint32_t open_cfw_ubase_type;
typedef uint16_t open_cfw_stack_depth_type;

enum {
    OPEN_CFW_FALSE = 0,
    OPEN_CFW_TRUE = 1,
    OPEN_CFW_NOTIFY_INCREMENT = 2
};

#if defined(__arm__) || defined(__thumb__)
_Static_assert(sizeof(void *) == 4U, "G2 pointer ABI changed");
_Static_assert(sizeof(open_cfw_lvgl_thread_sync_result) == 1U,
               "G2 short-enum result ABI changed");
_Static_assert(sizeof(open_cfw_lvgl_thread_sync) == 12U,
               "G2 notify-mode lv_thread_sync_t ABI changed");
_Static_assert(sizeof(open_cfw_lvgl_thread_priority) == 1U,
               "G2 short-enum thread priority ABI changed");
_Static_assert(sizeof(open_cfw_lvgl_thread) == 12U,
               "G2 lv_thread_t ABI changed");
_Static_assert(offsetof(open_cfw_lvgl_thread, start_routine) == 0U,
               "G2 thread callback offset changed");
_Static_assert(offsetof(open_cfw_lvgl_thread, task_argument) == 4U,
               "G2 thread argument offset changed");
_Static_assert(offsetof(open_cfw_lvgl_thread, task_handle) == 8U,
               "G2 thread handle offset changed");
_Static_assert(offsetof(open_cfw_lvgl_thread_sync, initialized) == 0U,
               "G2 sync initialized offset changed");
_Static_assert(offsetof(open_cfw_lvgl_thread_sync, signal) == 4U,
               "G2 sync signal offset changed");
_Static_assert(offsetof(open_cfw_lvgl_thread_sync, task_to_notify) == 8U,
               "G2 sync task offset changed");
#endif

#ifndef OPEN_CFW_LVGL_THREAD_TASK_CREATE
typedef open_cfw_base_type (*open_cfw_task_create_fn)(
    void (*)(void *), const char *, open_cfw_stack_depth_type,
    void *, open_cfw_ubase_type, void **
);
#define OPEN_CFW_LVGL_THREAD_TASK_CREATE(callback, name, depth, argument, priority, handle) \
    (((open_cfw_task_create_fn)(uintptr_t)0x004548BBU)( \
        (callback), (name), (depth), (argument), (priority), (handle)))
#endif

#ifndef OPEN_CFW_LVGL_THREAD_TASK_DELETE
typedef void (*open_cfw_task_delete_fn)(void *);
#define OPEN_CFW_LVGL_THREAD_TASK_DELETE(task) \
    (((open_cfw_task_delete_fn)(uintptr_t)0x00454AAFU)((task)))
#endif

static void open_cfw_lvgl_thread_runner(void * argument)
{
    open_cfw_lvgl_thread * thread = (open_cfw_lvgl_thread *)argument;

    if(thread != NULL && thread->start_routine != NULL) {
        thread->start_routine(thread->task_argument);
    }
    OPEN_CFW_LVGL_THREAD_TASK_DELETE(NULL);
}

__attribute__((visibility("default"), used, noinline))
open_cfw_lvgl_thread_sync_result lv_thread_init(
    open_cfw_lvgl_thread * thread,
    const char * name,
    open_cfw_lvgl_thread_priority priority,
    void (*callback)(void *),
    size_t stack_size,
    void * user_data
)
{
    size_t stack_depth;
    open_cfw_base_type status;

    if(thread == NULL || name == NULL || callback == NULL) {
        return OPEN_CFW_LVGL_THREAD_SYNC_INVALID;
    }
    if((unsigned)priority > (unsigned)OPEN_CFW_LVGL_THREAD_PRIO_HIGHEST) {
        return OPEN_CFW_LVGL_THREAD_SYNC_INVALID;
    }
    stack_depth = stack_size / sizeof(uint32_t);
    if(stack_depth == 0U || stack_depth > UINT16_MAX) {
        return OPEN_CFW_LVGL_THREAD_SYNC_INVALID;
    }

    thread->task_argument = user_data;
    thread->start_routine = callback;
    status = OPEN_CFW_LVGL_THREAD_TASK_CREATE(
        open_cfw_lvgl_thread_runner,
        name,
        (open_cfw_stack_depth_type)stack_depth,
        thread,
        (open_cfw_ubase_type)priority,
        &thread->task_handle
    );
    return status == OPEN_CFW_TRUE
        ? OPEN_CFW_LVGL_THREAD_SYNC_OK
        : OPEN_CFW_LVGL_THREAD_SYNC_INVALID;
}

__attribute__((visibility("default"), used, noinline))
open_cfw_lvgl_thread_sync_result lv_thread_delete(
    open_cfw_lvgl_thread * thread
)
{
    if(thread == NULL || thread->task_handle == NULL) {
        return OPEN_CFW_LVGL_THREAD_SYNC_INVALID;
    }
    OPEN_CFW_LVGL_THREAD_TASK_DELETE(thread->task_handle);
    return OPEN_CFW_LVGL_THREAD_SYNC_OK;
}

#ifndef OPEN_CFW_LVGL_SYNC_ENTER_CRITICAL
typedef void (*open_cfw_enter_critical_fn)(void);
#define OPEN_CFW_LVGL_SYNC_ENTER_CRITICAL() \
    (((open_cfw_enter_critical_fn)(uintptr_t)0x004420D1U)())
#endif

#ifndef OPEN_CFW_LVGL_SYNC_EXIT_CRITICAL
typedef void (*open_cfw_exit_critical_fn)(void);
#define OPEN_CFW_LVGL_SYNC_EXIT_CRITICAL() \
    (((open_cfw_exit_critical_fn)(uintptr_t)0x004420E9U)())
#endif

#ifndef OPEN_CFW_LVGL_SYNC_TASK_NOTIFY
typedef open_cfw_base_type (*open_cfw_task_notify_fn)(
    void *, open_cfw_ubase_type, open_cfw_ubase_type,
    open_cfw_base_type, open_cfw_ubase_type *
);
#define OPEN_CFW_LVGL_SYNC_TASK_NOTIFY(task, index, value, action, previous) \
    (((open_cfw_task_notify_fn)(uintptr_t)0x00455C49U)( \
        (task), (index), (value), (action), (previous)))
#endif

#ifndef OPEN_CFW_LVGL_SYNC_CURRENT_TASK
typedef void * (*open_cfw_current_task_fn)(void);
#define OPEN_CFW_LVGL_SYNC_CURRENT_TASK() \
    (((open_cfw_current_task_fn)(uintptr_t)0x0045589DU)())
#endif

#ifndef OPEN_CFW_LVGL_SYNC_ADD_DELAYED
typedef void (*open_cfw_add_delayed_fn)(open_cfw_ubase_type, open_cfw_base_type);
#define OPEN_CFW_LVGL_SYNC_ADD_DELAYED(ticks, can_block) \
    (((open_cfw_add_delayed_fn)(uintptr_t)0x00455FA9U)((ticks), (can_block)))
#endif

#ifndef OPEN_CFW_LVGL_SYNC_YIELD
typedef void (*open_cfw_yield_fn)(void);
#define OPEN_CFW_LVGL_SYNC_YIELD() \
    (((open_cfw_yield_fn)(uintptr_t)0x004420BDU)())
#endif

struct open_cfw_lvgl_notify_tcb {
    uint8_t before_notification[0x68U];
    open_cfw_ubase_type notification_value;
    uint8_t notification_state;
};

static open_cfw_ubase_type open_cfw_lvgl_sync_notify_take(
    void * current_task,
    open_cfw_base_type clear_count,
    open_cfw_ubase_type ticks
)
{
    struct open_cfw_lvgl_notify_tcb * task =
        (struct open_cfw_lvgl_notify_tcb *)current_task;
    open_cfw_ubase_type result;

    OPEN_CFW_LVGL_SYNC_ENTER_CRITICAL();
    if(task->notification_value == 0U) {
        task->notification_state = 1U;
        if(ticks != 0U) {
            OPEN_CFW_LVGL_SYNC_ADD_DELAYED(ticks, OPEN_CFW_TRUE);
            OPEN_CFW_LVGL_SYNC_YIELD();
        }
    }
    OPEN_CFW_LVGL_SYNC_EXIT_CRITICAL();

    OPEN_CFW_LVGL_SYNC_ENTER_CRITICAL();
    result = task->notification_value;
    if(result != 0U) {
        task->notification_value = clear_count != OPEN_CFW_FALSE
            ? 0U : result - 1U;
    }
    task->notification_state = 0U;
    OPEN_CFW_LVGL_SYNC_EXIT_CRITICAL();
    return result;
}

static void open_cfw_lvgl_sync_initialize_if_needed(
    open_cfw_lvgl_thread_sync * sync
)
{
    if(sync->initialized != OPEN_CFW_FALSE) return;

    OPEN_CFW_LVGL_SYNC_ENTER_CRITICAL();
    if(sync->initialized == OPEN_CFW_FALSE) {
        sync->initialized = OPEN_CFW_TRUE;
        sync->signal = OPEN_CFW_FALSE;
        sync->task_to_notify = NULL;
    }
    OPEN_CFW_LVGL_SYNC_EXIT_CRITICAL();
}

__attribute__((visibility("default"), used, noinline))
open_cfw_lvgl_thread_sync_result lv_thread_sync_init(
    open_cfw_lvgl_thread_sync * sync
)
{
    if(sync == NULL) return OPEN_CFW_LVGL_THREAD_SYNC_INVALID;
    open_cfw_lvgl_sync_initialize_if_needed(sync);
    return OPEN_CFW_LVGL_THREAD_SYNC_OK;
}

__attribute__((visibility("default"), used, noinline))
open_cfw_lvgl_thread_sync_result lv_thread_sync_wait(
    open_cfw_lvgl_thread_sync * sync
)
{
    void * current_task;
    open_cfw_base_type pending;

    if(sync == NULL) return OPEN_CFW_LVGL_THREAD_SYNC_INVALID;
    open_cfw_lvgl_sync_initialize_if_needed(sync);
    current_task = OPEN_CFW_LVGL_SYNC_CURRENT_TASK();
    if(current_task == NULL) return OPEN_CFW_LVGL_THREAD_SYNC_INVALID;

    OPEN_CFW_LVGL_SYNC_ENTER_CRITICAL();
    pending = sync->signal;
    sync->signal = OPEN_CFW_FALSE;
    if(pending == OPEN_CFW_FALSE) sync->task_to_notify = current_task;
    OPEN_CFW_LVGL_SYNC_EXIT_CRITICAL();

    if(pending == OPEN_CFW_FALSE) {
        (void)open_cfw_lvgl_sync_notify_take(
            current_task, OPEN_CFW_TRUE, UINT32_MAX
        );
    }
    return OPEN_CFW_LVGL_THREAD_SYNC_OK;
}

__attribute__((visibility("default"), used, noinline))
open_cfw_lvgl_thread_sync_result lv_thread_sync_delete(
    open_cfw_lvgl_thread_sync * sync
)
{
    if(sync == NULL) return OPEN_CFW_LVGL_THREAD_SYNC_INVALID;
    OPEN_CFW_LVGL_SYNC_ENTER_CRITICAL();
    sync->task_to_notify = NULL;
    sync->signal = OPEN_CFW_FALSE;
    sync->initialized = OPEN_CFW_FALSE;
    OPEN_CFW_LVGL_SYNC_EXIT_CRITICAL();
    return OPEN_CFW_LVGL_THREAD_SYNC_OK;
}

__attribute__((visibility("default"), used, noinline))
open_cfw_lvgl_thread_sync_result lv_thread_sync_signal(
    open_cfw_lvgl_thread_sync * sync
)
{
    void * task_to_notify;

    if(sync == NULL) return OPEN_CFW_LVGL_THREAD_SYNC_INVALID;
    open_cfw_lvgl_sync_initialize_if_needed(sync);

    OPEN_CFW_LVGL_SYNC_ENTER_CRITICAL();
    task_to_notify = sync->task_to_notify;
    sync->task_to_notify = NULL;
    if(task_to_notify == NULL) sync->signal = OPEN_CFW_TRUE;
    OPEN_CFW_LVGL_SYNC_EXIT_CRITICAL();

    if(task_to_notify != NULL) {
        (void)OPEN_CFW_LVGL_SYNC_TASK_NOTIFY(
            task_to_notify, 0U, 0U, OPEN_CFW_NOTIFY_INCREMENT, NULL
        );
    }
    return OPEN_CFW_LVGL_THREAD_SYNC_OK;
}
