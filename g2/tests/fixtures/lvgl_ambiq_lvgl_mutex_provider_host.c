/* SPDX-License-Identifier: MIT */
#include "lvgl_ambiq_lvgl_mutex_provider.h"

#include <assert.h>
#include <stdint.h>
#include <string.h>

static unsigned enter_calls;
static unsigned exit_calls;
static unsigned create_calls;
static unsigned take_calls;
static unsigned give_calls;
static unsigned delete_calls;
static void * created_handle;
static void * observed_handle;
static uint32_t observed_ticks;
static int32_t take_result;
static int32_t give_result;

void test_mutex_enter_critical(void) { enter_calls++; }
void test_mutex_exit_critical(void) { exit_calls++; }
void * test_mutex_create_recursive(void)
{
    create_calls++;
    return created_handle;
}
int32_t test_mutex_take_recursive(void * handle, uint32_t ticks)
{
    take_calls++;
    observed_handle = handle;
    observed_ticks = ticks;
    return take_result;
}
int32_t test_mutex_give_recursive(void * handle)
{
    give_calls++;
    observed_handle = handle;
    return give_result;
}
void test_mutex_delete_queue(void * handle)
{
    delete_calls++;
    observed_handle = handle;
}

static void reset(void)
{
    enter_calls = exit_calls = create_calls = take_calls = give_calls = delete_calls = 0;
    created_handle = NULL;
    observed_handle = NULL;
    observed_ticks = 0;
    take_result = give_result = 0;
}

int main(void)
{
    open_cfw_lvgl_mutex mutex;
    void * const token = (void *)(uintptr_t)0x1234U;

    reset();
    assert(lv_mutex_init(NULL) == OPEN_CFW_LVGL_MUTEX_INVALID);
    assert(lv_mutex_lock(NULL) == OPEN_CFW_LVGL_MUTEX_INVALID);
    assert(lv_mutex_unlock(NULL) == OPEN_CFW_LVGL_MUTEX_INVALID);
    assert(lv_mutex_delete(NULL) == OPEN_CFW_LVGL_MUTEX_INVALID);
    assert(enter_calls + exit_calls + create_calls + take_calls + give_calls + delete_calls == 0);

    reset();
    memset(&mutex, 0, sizeof(mutex));
    assert(lv_mutex_init(&mutex) == OPEN_CFW_LVGL_MUTEX_OK);
    assert(enter_calls == 1 && exit_calls == 1 && create_calls == 1);
    assert(mutex.initialized == 0 && mutex.handle == NULL);
    assert(lv_mutex_lock(&mutex) == OPEN_CFW_LVGL_MUTEX_INVALID);
    assert(enter_calls == 2 && exit_calls == 2 && create_calls == 2 && take_calls == 0);

    reset();
    memset(&mutex, 0, sizeof(mutex));
    created_handle = token;
    assert(lv_mutex_init(&mutex) == OPEN_CFW_LVGL_MUTEX_OK);
    assert(mutex.initialized == 1 && mutex.handle == token);
    assert(enter_calls == 1 && exit_calls == 1 && create_calls == 1);
    assert(lv_mutex_init(&mutex) == OPEN_CFW_LVGL_MUTEX_OK);
    assert(enter_calls == 1 && exit_calls == 1 && create_calls == 1);

    take_result = 1;
    assert(lv_mutex_lock(&mutex) == OPEN_CFW_LVGL_MUTEX_OK);
    assert(take_calls == 1 && observed_handle == token && observed_ticks == UINT32_MAX);
    take_result = 0;
    assert(lv_mutex_lock(&mutex) == OPEN_CFW_LVGL_MUTEX_INVALID);
    assert(take_calls == 2);

    give_result = 1;
    assert(lv_mutex_unlock(&mutex) == OPEN_CFW_LVGL_MUTEX_OK);
    assert(give_calls == 1 && observed_handle == token);
    give_result = 0;
    assert(lv_mutex_unlock(&mutex) == OPEN_CFW_LVGL_MUTEX_INVALID);
    assert(give_calls == 2);

    assert(lv_mutex_delete(&mutex) == OPEN_CFW_LVGL_MUTEX_OK);
    assert(delete_calls == 1 && observed_handle == token);
    assert(mutex.initialized == 0 && mutex.handle == NULL);
    assert(lv_mutex_delete(&mutex) == OPEN_CFW_LVGL_MUTEX_INVALID);
    assert(delete_calls == 1);

    mutex.initialized = 1;
    mutex.handle = NULL;
    assert(lv_mutex_lock(&mutex) == OPEN_CFW_LVGL_MUTEX_INVALID);
    assert(lv_mutex_unlock(&mutex) == OPEN_CFW_LVGL_MUTEX_INVALID);
    assert(lv_mutex_delete(&mutex) == OPEN_CFW_LVGL_MUTEX_INVALID);
    assert(take_calls == 2 && give_calls == 2 && delete_calls == 1);

    return 0;
}
