/* SPDX-License-Identifier: MIT */
#include "lvgl_ambiq_lvgl_thread_sync_signal_provider.h"

#include <assert.h>
#include <stdint.h>
#include <string.h>

static unsigned enter_calls;
static unsigned exit_calls;
static unsigned notify_calls;
static unsigned delayed_calls;
static unsigned yield_calls;
static void * observed_task;
static uint32_t observed_index;
static uint32_t observed_value;
static int32_t observed_action;
static uint32_t * observed_previous;
static open_cfw_lvgl_thread_sync * initialize_during_enter;
static void * current_task;
static uint32_t delayed_ticks;
static int32_t delayed_can_block;
static uint32_t notify_value_on_yield;
static unsigned char current_tcb[0x70U];
static unsigned create_calls;
static unsigned delete_calls;
static void (*created_entry)(void *);
static const char * created_name;
static uint16_t created_depth;
static void * created_argument;
static uint32_t created_priority;
static void ** created_handle_slot;
static int32_t create_result;
static void * created_handle;
static void * deleted_task;
static unsigned callback_calls;
static void * callback_argument;

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

void * test_sync_current_task(void) { return current_task; }

void test_sync_add_delayed(uint32_t ticks, int32_t can_block)
{
    delayed_calls++;
    delayed_ticks = ticks;
    delayed_can_block = can_block;
}

void test_sync_yield(void)
{
    yield_calls++;
    memcpy(&current_tcb[0x68U], &notify_value_on_yield, sizeof(notify_value_on_yield));
    if(notify_value_on_yield != 0U) current_tcb[0x6CU] = 2U;
}

int32_t test_thread_task_create(
    void (*callback)(void *), const char * name, uint16_t depth,
    void * argument, uint32_t priority, void ** handle
)
{
    create_calls++;
    created_entry = callback;
    created_name = name;
    created_depth = depth;
    created_argument = argument;
    created_priority = priority;
    created_handle_slot = handle;
    if(create_result == 1 && handle != NULL) *handle = created_handle;
    return create_result;
}

void test_thread_task_delete(void * task)
{
    delete_calls++;
    deleted_task = task;
}

static void test_thread_callback(void * argument)
{
    callback_calls++;
    callback_argument = argument;
}

static void reset(void)
{
    enter_calls = exit_calls = notify_calls = delayed_calls = yield_calls = 0U;
    observed_task = NULL;
    observed_index = observed_value = 0xFFFFFFFFU;
    observed_action = -1;
    observed_previous = (uint32_t *)(uintptr_t)1U;
    initialize_during_enter = NULL;
    memset(current_tcb, 0, sizeof(current_tcb));
    current_task = current_tcb;
    delayed_ticks = 0U;
    delayed_can_block = -1;
    notify_value_on_yield = 1U;
    create_calls = delete_calls = callback_calls = 0U;
    created_entry = NULL;
    created_name = NULL;
    created_depth = 0U;
    created_argument = NULL;
    created_priority = UINT32_MAX;
    created_handle_slot = NULL;
    create_result = 1;
    created_handle = (void *)(uintptr_t)0xC0FFEEU;
    deleted_task = (void *)(uintptr_t)1U;
    callback_argument = NULL;
}

int main(void)
{
    open_cfw_lvgl_thread_sync sync;
    open_cfw_lvgl_thread thread;
    const char name[] = "ambiqdraw";
    void * const user_data = (void *)(uintptr_t)0x3344U;
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

    reset();
    memset(&sync, 0xA5, sizeof(sync));
    sync.initialized = 0;
    assert(lv_thread_sync_init(&sync) == OPEN_CFW_LVGL_THREAD_SYNC_OK);
    assert(sync.initialized == 1 && sync.signal == 0 && sync.task_to_notify == NULL);
    assert(enter_calls == 1U && exit_calls == 1U);
    assert(lv_thread_sync_init(NULL) == OPEN_CFW_LVGL_THREAD_SYNC_INVALID);

    reset();
    sync.initialized = 1;
    sync.signal = 1;
    sync.task_to_notify = (void *)(uintptr_t)0x1111U;
    assert(lv_thread_sync_wait(&sync) == OPEN_CFW_LVGL_THREAD_SYNC_OK);
    assert(sync.signal == 0 && sync.task_to_notify == (void *)(uintptr_t)0x1111U);
    assert(delayed_calls == 0U && yield_calls == 0U);
    assert(enter_calls == 1U && exit_calls == 1U);

    reset();
    sync.initialized = 1;
    sync.signal = 0;
    sync.task_to_notify = NULL;
    assert(lv_thread_sync_wait(&sync) == OPEN_CFW_LVGL_THREAD_SYNC_OK);
    assert(sync.task_to_notify == current_task);
    assert(delayed_calls == 1U && delayed_ticks == UINT32_MAX);
    assert(delayed_can_block == 1 && yield_calls == 1U);
    assert(current_tcb[0x6CU] == 0U);
    {
        uint32_t notification_value = UINT32_MAX;
        memcpy(&notification_value, &current_tcb[0x68U], sizeof(notification_value));
        assert(notification_value == 0U);
    }

    reset();
    current_task = NULL;
    sync.initialized = 1;
    sync.signal = 0;
    assert(lv_thread_sync_wait(&sync) == OPEN_CFW_LVGL_THREAD_SYNC_INVALID);
    assert(enter_calls == 0U && exit_calls == 0U && delayed_calls == 0U);
    assert(lv_thread_sync_wait(NULL) == OPEN_CFW_LVGL_THREAD_SYNC_INVALID);

    reset();
    sync.initialized = 1;
    sync.signal = 1;
    sync.task_to_notify = (void *)(uintptr_t)0x2222U;
    assert(lv_thread_sync_delete(&sync) == OPEN_CFW_LVGL_THREAD_SYNC_OK);
    assert(sync.initialized == 0 && sync.signal == 0 && sync.task_to_notify == NULL);
    assert(enter_calls == 1U && exit_calls == 1U);
    assert(lv_thread_sync_delete(NULL) == OPEN_CFW_LVGL_THREAD_SYNC_INVALID);

    reset();
    memset(&thread, 0xA5, sizeof(thread));
    assert(lv_thread_init(
        &thread, name, OPEN_CFW_LVGL_THREAD_PRIO_HIGH,
        test_thread_callback, 32768U, user_data
    ) == OPEN_CFW_LVGL_THREAD_SYNC_OK);
    assert(create_calls == 1U && delete_calls == 0U);
    assert(created_entry != NULL && created_name == name && created_depth == 8192U);
    assert(created_argument == &thread && created_priority == 3U);
    assert(created_handle_slot == &thread.task_handle);
    assert(thread.start_routine == test_thread_callback);
    assert(thread.task_argument == user_data && thread.task_handle == created_handle);
    created_entry(created_argument);
    assert(callback_calls == 1U && callback_argument == user_data);
    assert(delete_calls == 1U && deleted_task == NULL);

    reset();
    thread.task_handle = created_handle;
    assert(lv_thread_delete(&thread) == OPEN_CFW_LVGL_THREAD_SYNC_OK);
    assert(delete_calls == 1U && deleted_task == created_handle);
    assert(lv_thread_delete(NULL) == OPEN_CFW_LVGL_THREAD_SYNC_INVALID);
    thread.task_handle = NULL;
    assert(lv_thread_delete(&thread) == OPEN_CFW_LVGL_THREAD_SYNC_INVALID);
    assert(delete_calls == 1U);

    reset();
    create_result = 0;
    memset(&thread, 0, sizeof(thread));
    assert(lv_thread_init(
        &thread, name, OPEN_CFW_LVGL_THREAD_PRIO_LOW,
        test_thread_callback, 16U, user_data
    ) == OPEN_CFW_LVGL_THREAD_SYNC_INVALID);
    assert(create_calls == 1U);
    assert(thread.start_routine == test_thread_callback && thread.task_argument == user_data);

    reset();
    assert(lv_thread_init(
        NULL, name, OPEN_CFW_LVGL_THREAD_PRIO_LOW,
        test_thread_callback, 16U, user_data
    ) == OPEN_CFW_LVGL_THREAD_SYNC_INVALID);
    assert(lv_thread_init(
        &thread, NULL, OPEN_CFW_LVGL_THREAD_PRIO_LOW,
        test_thread_callback, 16U, user_data
    ) == OPEN_CFW_LVGL_THREAD_SYNC_INVALID);
    assert(lv_thread_init(
        &thread, name, OPEN_CFW_LVGL_THREAD_PRIO_LOW,
        NULL, 16U, user_data
    ) == OPEN_CFW_LVGL_THREAD_SYNC_INVALID);
    assert(lv_thread_init(
        &thread, name, (open_cfw_lvgl_thread_priority)5,
        test_thread_callback, 16U, user_data
    ) == OPEN_CFW_LVGL_THREAD_SYNC_INVALID);
    assert(lv_thread_init(
        &thread, name, OPEN_CFW_LVGL_THREAD_PRIO_LOW,
        test_thread_callback, 3U, user_data
    ) == OPEN_CFW_LVGL_THREAD_SYNC_INVALID);
    assert(lv_thread_init(
        &thread, name, OPEN_CFW_LVGL_THREAD_PRIO_LOW,
        test_thread_callback, ((size_t)UINT16_MAX + 1U) * 4U, user_data
    ) == OPEN_CFW_LVGL_THREAD_SYNC_INVALID);
    assert(create_calls == 0U);
    return 0;
}
