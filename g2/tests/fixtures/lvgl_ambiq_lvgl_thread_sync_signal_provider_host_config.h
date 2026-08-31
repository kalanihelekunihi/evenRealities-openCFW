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

#define OPEN_CFW_LVGL_SYNC_ENTER_CRITICAL() test_sync_enter_critical()
#define OPEN_CFW_LVGL_SYNC_EXIT_CRITICAL() test_sync_exit_critical()
#define OPEN_CFW_LVGL_SYNC_TASK_NOTIFY(task, index, value, action, previous) \
    test_sync_task_notify((task), (index), (value), (action), (previous))

#endif
