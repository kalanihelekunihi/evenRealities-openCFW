/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_LVGL_AMBIQ_MUTEX_PROVIDER_HOST_CONFIG_H
#define OPENCFW_LVGL_AMBIQ_MUTEX_PROVIDER_HOST_CONFIG_H

#include <stdint.h>

void test_mutex_enter_critical(void);
void test_mutex_exit_critical(void);
void * test_mutex_create_recursive(void);
int32_t test_mutex_take_recursive(void * handle, uint32_t ticks);
int32_t test_mutex_give_recursive(void * handle);
void test_mutex_delete_queue(void * handle);

#define OPEN_CFW_LVGL_MUTEX_ENTER_CRITICAL() test_mutex_enter_critical()
#define OPEN_CFW_LVGL_MUTEX_EXIT_CRITICAL() test_mutex_exit_critical()
#define OPEN_CFW_LVGL_MUTEX_CREATE_RECURSIVE() test_mutex_create_recursive()
#define OPEN_CFW_LVGL_MUTEX_TAKE_RECURSIVE(handle, ticks) \
    test_mutex_take_recursive((handle), (ticks))
#define OPEN_CFW_LVGL_MUTEX_GIVE_RECURSIVE(handle) \
    test_mutex_give_recursive((handle))
#define OPEN_CFW_LVGL_MUTEX_DELETE_QUEUE(handle) test_mutex_delete_queue((handle))

#endif /* OPENCFW_LVGL_AMBIQ_MUTEX_PROVIDER_HOST_CONFIG_H */
