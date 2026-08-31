/* SPDX-License-Identifier: MIT */
/* Bounded exact-ABI adapter for the notify-mode-independent LVGL mutex API. */

#include "lvgl_ambiq_lvgl_mutex_provider.h"

#include <stddef.h>
#include <stdint.h>

typedef int32_t open_cfw_base_type;
enum {
    OPEN_CFW_FALSE = 0,
    OPEN_CFW_TRUE = 1,
    OPEN_CFW_RECURSIVE_MUTEX_QUEUE_TYPE = 4
};

#if defined(__arm__) || defined(__thumb__)
_Static_assert(sizeof(void *) == 4U, "G2 pointer ABI changed");
_Static_assert(sizeof(open_cfw_base_type) == 4U, "G2 BaseType_t ABI changed");
_Static_assert(sizeof(open_cfw_lvgl_mutex_result) == 1U,
               "G2 short-enum result ABI changed");
_Static_assert(sizeof(open_cfw_lvgl_mutex) == 8U, "G2 lv_mutex_t ABI changed");
_Static_assert(offsetof(open_cfw_lvgl_mutex, initialized) == 0U,
               "G2 lv_mutex_t initialized offset changed");
_Static_assert(offsetof(open_cfw_lvgl_mutex, handle) == 4U,
               "G2 lv_mutex_t handle offset changed");
#endif

#ifndef OPEN_CFW_LVGL_MUTEX_ENTER_CRITICAL
typedef void (*open_cfw_enter_critical_fn)(void);
#define OPEN_CFW_LVGL_MUTEX_ENTER_CRITICAL() \
    (((open_cfw_enter_critical_fn)(uintptr_t)0x004420D1U)())
#endif

#ifndef OPEN_CFW_LVGL_MUTEX_EXIT_CRITICAL
typedef void (*open_cfw_exit_critical_fn)(void);
#define OPEN_CFW_LVGL_MUTEX_EXIT_CRITICAL() \
    (((open_cfw_exit_critical_fn)(uintptr_t)0x004420E9U)())
#endif

#ifndef OPEN_CFW_LVGL_MUTEX_CREATE_RECURSIVE
typedef void *(*open_cfw_create_recursive_mutex_fn)(uint8_t);
#define OPEN_CFW_LVGL_MUTEX_CREATE_RECURSIVE() \
    (((open_cfw_create_recursive_mutex_fn)(uintptr_t)0x004416D7U)( \
        OPEN_CFW_RECURSIVE_MUTEX_QUEUE_TYPE))
#endif

#ifndef OPEN_CFW_LVGL_MUTEX_TAKE_RECURSIVE
typedef open_cfw_base_type (*open_cfw_take_recursive_fn)(void *, uint32_t);
#define OPEN_CFW_LVGL_MUTEX_TAKE_RECURSIVE(handle, ticks) \
    (((open_cfw_take_recursive_fn)(uintptr_t)0x00441751U)((handle), (ticks)))
#endif

#ifndef OPEN_CFW_LVGL_MUTEX_GIVE_RECURSIVE
typedef open_cfw_base_type (*open_cfw_give_recursive_fn)(void *);
#define OPEN_CFW_LVGL_MUTEX_GIVE_RECURSIVE(handle) \
    (((open_cfw_give_recursive_fn)(uintptr_t)0x00441711U)((handle)))
#endif

#ifndef OPEN_CFW_LVGL_MUTEX_DELETE_QUEUE
typedef void (*open_cfw_delete_queue_fn)(void *);
#define OPEN_CFW_LVGL_MUTEX_DELETE_QUEUE(handle) \
    (((open_cfw_delete_queue_fn)(uintptr_t)0x00441EA3U)((handle)))
#endif

static void open_cfw_lvgl_mutex_initialize_if_needed(open_cfw_lvgl_mutex * mutex)
{
    if(mutex->initialized != OPEN_CFW_FALSE) return;

    OPEN_CFW_LVGL_MUTEX_ENTER_CRITICAL();
    if(mutex->initialized == OPEN_CFW_FALSE) {
        void * handle = OPEN_CFW_LVGL_MUTEX_CREATE_RECURSIVE();
        mutex->handle = handle;
        if(handle != NULL) mutex->initialized = OPEN_CFW_TRUE;
    }
    OPEN_CFW_LVGL_MUTEX_EXIT_CRITICAL();
}

__attribute__((visibility("default"), used, noinline))
open_cfw_lvgl_mutex_result lv_mutex_init(open_cfw_lvgl_mutex * mutex)
{
    if(mutex == NULL) return OPEN_CFW_LVGL_MUTEX_INVALID;
    open_cfw_lvgl_mutex_initialize_if_needed(mutex);
    return OPEN_CFW_LVGL_MUTEX_OK;
}

__attribute__((visibility("default"), used, noinline))
open_cfw_lvgl_mutex_result lv_mutex_lock(open_cfw_lvgl_mutex * mutex)
{
    if(mutex == NULL) return OPEN_CFW_LVGL_MUTEX_INVALID;
    open_cfw_lvgl_mutex_initialize_if_needed(mutex);
    if(mutex->initialized == OPEN_CFW_FALSE || mutex->handle == NULL) {
        return OPEN_CFW_LVGL_MUTEX_INVALID;
    }
    return OPEN_CFW_LVGL_MUTEX_TAKE_RECURSIVE(mutex->handle, UINT32_MAX) == OPEN_CFW_TRUE
               ? OPEN_CFW_LVGL_MUTEX_OK
               : OPEN_CFW_LVGL_MUTEX_INVALID;
}

__attribute__((visibility("default"), used, noinline))
open_cfw_lvgl_mutex_result lv_mutex_unlock(open_cfw_lvgl_mutex * mutex)
{
    if(mutex == NULL || mutex->initialized == OPEN_CFW_FALSE || mutex->handle == NULL) {
        return OPEN_CFW_LVGL_MUTEX_INVALID;
    }
    return OPEN_CFW_LVGL_MUTEX_GIVE_RECURSIVE(mutex->handle) == OPEN_CFW_TRUE
               ? OPEN_CFW_LVGL_MUTEX_OK
               : OPEN_CFW_LVGL_MUTEX_INVALID;
}

__attribute__((visibility("default"), used, noinline))
open_cfw_lvgl_mutex_result lv_mutex_delete(open_cfw_lvgl_mutex * mutex)
{
    if(mutex == NULL || mutex->initialized == OPEN_CFW_FALSE || mutex->handle == NULL) {
        return OPEN_CFW_LVGL_MUTEX_INVALID;
    }
    OPEN_CFW_LVGL_MUTEX_DELETE_QUEUE(mutex->handle);
    mutex->handle = NULL;
    mutex->initialized = OPEN_CFW_FALSE;
    return OPEN_CFW_LVGL_MUTEX_OK;
}
