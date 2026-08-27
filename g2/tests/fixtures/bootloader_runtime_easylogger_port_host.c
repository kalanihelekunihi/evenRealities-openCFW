#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define OPEN_CFW_BOOTLOADER_EASYLOGGER_PORT_HOST 1
#include "../../components/bootloader/core_overlay/runtime_easylogger_port_41a648.c"

static void *mutex_cell;
static uintptr_t created_handle;
static uint32_t create_calls;
static uint32_t acquire_calls;
static uint32_t release_calls;
static uint32_t acquired_timeout;
static uintptr_t acquired_handle;
static uintptr_t released_handle;
static uint32_t sink_calls;
static const char *sink_log;
static uint32_t sink_size;
static uint32_t sink_level;
static uint32_t tick_value;
static uint32_t kernel_state;
static uintptr_t current_thread;
static const char *thread_name;
static char time_buffer[28];

open_cfw_bootloader_elog_port_handle *
open_cfw_bootloader_easylogger_port_host_mutex_cell(void)
{
    return &mutex_cell;
}

open_cfw_bootloader_elog_port_handle
open_cfw_bootloader_easylogger_port_host_mutex_new(const void *attributes)
{
    ++create_calls;
    if ((uintptr_t)attributes != 0x00433D28U) {
        return (void *)0;
    }
    return (void *)created_handle;
}

open_cfw_bootloader_elog_port_u32
open_cfw_bootloader_easylogger_port_host_mutex_acquire(
    open_cfw_bootloader_elog_port_handle handle,
    open_cfw_bootloader_elog_port_u32 timeout)
{
    ++acquire_calls;
    acquired_handle = (uintptr_t)handle;
    acquired_timeout = timeout;
    return 37U;
}

open_cfw_bootloader_elog_port_u32
open_cfw_bootloader_easylogger_port_host_mutex_release(
    open_cfw_bootloader_elog_port_handle handle)
{
    ++release_calls;
    released_handle = (uintptr_t)handle;
    return 41U;
}

void open_cfw_bootloader_easylogger_port_host_driver_output(
    const char *log,
    open_cfw_bootloader_elog_port_u32 size,
    open_cfw_bootloader_elog_port_u32 level)
{
    ++sink_calls;
    sink_log = log;
    sink_size = size;
    sink_level = level;
}

open_cfw_bootloader_elog_port_u32
open_cfw_bootloader_easylogger_port_host_tick_count(void)
{
    return tick_value;
}

int open_cfw_bootloader_easylogger_port_host_snprintf(
    char *buffer,
    open_cfw_bootloader_elog_port_u32 size,
    const char *format,
    open_cfw_bootloader_elog_port_u32 value)
{
    return snprintf(buffer, size, format, value);
}

open_cfw_bootloader_elog_port_u32
open_cfw_bootloader_easylogger_port_host_kernel_state(void)
{
    return kernel_state;
}

open_cfw_bootloader_elog_port_handle
open_cfw_bootloader_easylogger_port_host_thread_current(void)
{
    return (void *)current_thread;
}

const char *open_cfw_bootloader_easylogger_port_host_thread_name(
    open_cfw_bootloader_elog_port_handle thread)
{
    return (uintptr_t)thread == current_thread ? thread_name : (const char *)0;
}

char *open_cfw_bootloader_easylogger_port_host_time_buffer(void)
{
    return time_buffer;
}

static void reset_state(void)
{
    mutex_cell = (void *)0;
    created_handle = 0x12345678U;
    create_calls = acquire_calls = release_calls = 0U;
    acquired_timeout = 0U;
    acquired_handle = released_handle = 0U;
    sink_calls = sink_size = sink_level = 0U;
    sink_log = (const char *)0;
    tick_value = 0U;
    kernel_state = 0U;
    current_thread = 0x87654321U;
    thread_name = "worker";
    memset(time_buffer, 0xA5, sizeof(time_buffer));
}

uint32_t open_cfw_test_easylogger_port_mutex_lifecycle(void)
{
    reset_state();
    if (open_cfw_bootloader_easylogger_port_init_41a684() != 0U ||
            create_calls != 1U || (uintptr_t)mutex_cell != created_handle) {
        return 0U;
    }
    open_cfw_bootloader_easylogger_port_init_41a684();
    open_cfw_bootloader_easylogger_port_output_lock_41a69a();
    open_cfw_bootloader_easylogger_port_output_unlock_41a6a2();
    return create_calls == 1U && acquire_calls == 1U && release_calls == 1U &&
        acquired_handle == created_handle && released_handle == created_handle &&
        acquired_timeout == 1000U;
}

uint32_t open_cfw_test_easylogger_port_null_mutex_is_noop(void)
{
    reset_state();
    created_handle = 0U;
    open_cfw_bootloader_easylogger_port_init_41a684();
    open_cfw_bootloader_easylogger_port_output_lock_41a69a();
    open_cfw_bootloader_easylogger_port_output_unlock_41a6a2();
    return create_calls == 1U && mutex_cell == (void *)0 &&
        acquire_calls == 0U && release_calls == 0U;
}

uint32_t open_cfw_test_easylogger_port_output_forwards_all_arguments(void)
{
    static const char message[] = "log";
    reset_state();
    open_cfw_bootloader_easylogger_port_output_41a692(message, 3U, 5U);
    return sink_calls == 1U && sink_log == message &&
        sink_size == 3U && sink_level == 5U;
}

uint32_t open_cfw_test_easylogger_port_formats_tick(void)
{
    reset_state();
    tick_value = 4294967295U;
    return open_cfw_bootloader_easylogger_port_get_time_41a6aa() == time_buffer &&
        strcmp(time_buffer, "-1") == 0;
}

uint32_t open_cfw_test_easylogger_port_task_name_policy(void)
{
    const char *process;
    const char *thread;
    reset_state();
    process = open_cfw_bootloader_easylogger_port_get_p_info_41a6f0();
    thread = open_cfw_bootloader_easylogger_port_get_t_info_41a6f8();
    if (strcmp(process, "worker") != 0 || strcmp(thread, "worker") != 0) {
        return 0U;
    }
    kernel_state = 1U;
    return strcmp(open_cfw_bootloader_easylogger_port_get_p_info_41a6f0(),
        "unknown") == 0;
}
