/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_LVGL_THREAD_SYNC_SIGNAL_HOST_CONFIG_H
#define OPENCFW_LVGL_THREAD_SYNC_SIGNAL_HOST_CONFIG_H

#include <stdint.h>

void test_sync_enter_critical(void);
void test_sync_exit_critical(void);
int32_t test_sync_task_notify(
    void * task, uint32_t index, uint32_t value,
    int32_t action, uint32_t * previous
);
void * test_sync_current_task(void);
void test_sync_add_delayed(uint32_t ticks, int32_t can_block);
void test_sync_yield(void);
int32_t test_thread_task_create(
    void (*callback)(void *), const char * name, uint16_t depth,
    void * argument, uint32_t priority, void ** handle
);
void test_thread_task_delete(void * task);

#define OPEN_CFW_LVGL_SYNC_ENTER_CRITICAL() test_sync_enter_critical()
#define OPEN_CFW_LVGL_SYNC_EXIT_CRITICAL() test_sync_exit_critical()
#define OPEN_CFW_LVGL_SYNC_TASK_NOTIFY(task, index, value, action, previous) \
    test_sync_task_notify((task), (index), (value), (action), (previous))
#define OPEN_CFW_LVGL_SYNC_CURRENT_TASK() test_sync_current_task()
#define OPEN_CFW_LVGL_SYNC_ADD_DELAYED(ticks, can_block) \
    test_sync_add_delayed((ticks), (can_block))
#define OPEN_CFW_LVGL_SYNC_YIELD() test_sync_yield()
#define OPEN_CFW_LVGL_THREAD_TASK_CREATE(callback, name, depth, argument, priority, handle) \
    test_thread_task_create((callback), (name), (depth), (argument), (priority), (handle))
#define OPEN_CFW_LVGL_THREAD_TASK_DELETE(task) test_thread_task_delete((task))

#endif
