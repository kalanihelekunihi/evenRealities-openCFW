/* SPDX-License-Identifier: MIT */
#include "lvgl_ambiq_lvgl_thread_sync_signal_provider.h"

#include <assert.h>
#include <stdint.h>
#include <string.h>

static unsigned enter_calls;
static unsigned exit_calls;
static unsigned notify_calls;
static void * observed_task;
static uint32_t observed_index;
static uint32_t observed_value;
static int32_t observed_action;
static uint32_t * observed_previous;
static open_cfw_lvgl_thread_sync * initialize_during_enter;

void test_sync_enter_critical(void)
{
    enter_calls++;
    if(initialize_during_enter != NULL) {
        initialize_during_enter->initialized = 1;
        initialize_during_enter->signal = 0;
        initialize_during_enter->task_to_notify = (void *)(uintptr_t)0xABCDU;
        initialize_during_enter = NULL;
    }
}

void test_sync_exit_critical(void) { exit_calls++; }

int32_t test_sync_task_notify(
    void * task, uint32_t index, uint32_t value,
    int32_t action, uint32_t * previous
)
{
    notify_calls++;
    observed_task = task;
    observed_index = index;
    observed_value = value;
    observed_action = action;
    observed_previous = previous;
    return 0;
}

static void reset(void)
{
    enter_calls = exit_calls = notify_calls = 0U;
    observed_task = NULL;
    observed_index = observed_value = 0xFFFFFFFFU;
    observed_action = -1;
    observed_previous = (uint32_t *)(uintptr_t)1U;
    initialize_during_enter = NULL;
}

int main(void)
{
    open_cfw_lvgl_thread_sync sync;
    void * const task = (void *)(uintptr_t)0x1234U;

    reset();
    assert(lv_thread_sync_signal(NULL) == OPEN_CFW_LVGL_THREAD_SYNC_INVALID);
    assert(enter_calls == 0U && exit_calls == 0U && notify_calls == 0U);

    reset();
    memset(&sync, 0xA5, sizeof(sync));
    sync.initialized = 0;
    assert(lv_thread_sync_signal(&sync) == OPEN_CFW_LVGL_THREAD_SYNC_OK);
    assert(sync.initialized == 1 && sync.signal == 1 && sync.task_to_notify == NULL);
    assert(enter_calls == 2U && exit_calls == 2U && notify_calls == 0U);

    reset();
    sync.initialized = 1;
    sync.signal = 0;
    sync.task_to_notify = task;
    assert(lv_thread_sync_signal(&sync) == OPEN_CFW_LVGL_THREAD_SYNC_OK);
    assert(sync.initialized == 1 && sync.signal == 0 && sync.task_to_notify == NULL);
    assert(enter_calls == 1U && exit_calls == 1U && notify_calls == 1U);
    assert(observed_task == task && observed_index == 0U && observed_value == 0U);
    assert(observed_action == 2 && observed_previous == NULL);

    reset();
    memset(&sync, 0, sizeof(sync));
    initialize_during_enter = &sync;
    assert(lv_thread_sync_signal(&sync) == OPEN_CFW_LVGL_THREAD_SYNC_OK);
    assert(sync.initialized == 1 && sync.signal == 0 && sync.task_to_notify == NULL);
    assert(enter_calls == 2U && exit_calls == 2U && notify_calls == 1U);
    assert(observed_task == (void *)(uintptr_t)0xABCDU);

    reset();
    sync.initialized = -7;
    sync.signal = -9;
    sync.task_to_notify = NULL;
    assert(lv_thread_sync_signal(&sync) == OPEN_CFW_LVGL_THREAD_SYNC_OK);
    assert(sync.initialized == -7 && sync.signal == 1 && sync.task_to_notify == NULL);
    assert(enter_calls == 1U && exit_calls == 1U && notify_calls == 0U);
    return 0;
}
