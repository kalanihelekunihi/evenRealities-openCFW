/*
 * Copyright (c) 2015-2018, Armink, <armink.ztl@gmail.com>
 * SPDX-License-Identifier: MIT
 *
 * Freestanding EasyLogger boot-port adaptation for the authenticated Even
 * Realities G2 S200 bootloader ABI.  The RTOS and transport calls remain
 * explicit, pinned Thumb seams so every source-owned leaf is independently
 * placeable by the overlay builder.
 */

typedef __UINT8_TYPE__ open_cfw_bootloader_elog_port_u8;
typedef __UINT32_TYPE__ open_cfw_bootloader_elog_port_u32;
typedef __UINTPTR_TYPE__ open_cfw_bootloader_elog_port_uintptr;
typedef void *open_cfw_bootloader_elog_port_handle;

enum {
    OPEN_CFW_BOOTLOADER_ELOG_MUTEX_HANDLE_ADDRESS = 0x200270E8U,
    OPEN_CFW_BOOTLOADER_ELOG_MUTEX_ATTRIBUTES_ADDRESS = 0x00433D28U,
    OPEN_CFW_BOOTLOADER_ELOG_TIME_BUFFER_ADDRESS = 0x20026F18U,
    OPEN_CFW_BOOTLOADER_ELOG_TIME_BUFFER_SIZE = 28U,
    OPEN_CFW_BOOTLOADER_ELOG_TIME_FORMAT_ADDRESS = 0x0041A6DCU,
    OPEN_CFW_BOOTLOADER_ELOG_UNKNOWN_ADDRESS = 0x00434084U,
    OPEN_CFW_BOOTLOADER_ELOG_MUTEX_NEW_THUMB = 0x00416611U,
    OPEN_CFW_BOOTLOADER_ELOG_MUTEX_ACQUIRE_THUMB = 0x004166ABU,
    OPEN_CFW_BOOTLOADER_ELOG_MUTEX_RELEASE_THUMB = 0x00416711U,
    OPEN_CFW_BOOTLOADER_ELOG_DRIVER_OUTPUT_THUMB = 0x0041B855U,
    OPEN_CFW_BOOTLOADER_ELOG_TICK_COUNT_THUMB = 0x004160E9U,
    OPEN_CFW_BOOTLOADER_ELOG_SNPRINTF_THUMB = 0x0041B219U,
    OPEN_CFW_BOOTLOADER_ELOG_KERNEL_STATE_THUMB = 0x00418B57U,
    OPEN_CFW_BOOTLOADER_ELOG_THREAD_CURRENT_THUMB = 0x00418B4FU,
    OPEN_CFW_BOOTLOADER_ELOG_THREAD_NAME_THUMB = 0x00418373U,
    OPEN_CFW_BOOTLOADER_ELOG_MUTEX_CREATE_THUMB = 0x0041A649U,
    OPEN_CFW_BOOTLOADER_ELOG_MUTEX_ACQUIRE_HELPER_THUMB = 0x0041A65DU,
    OPEN_CFW_BOOTLOADER_ELOG_MUTEX_RELEASE_HELPER_THUMB = 0x0041A673U,
    OPEN_CFW_BOOTLOADER_ELOG_TASK_NAME_HELPER_THUMB = 0x0041A6C3U,
    OPEN_CFW_BOOTLOADER_ELOG_MUTEX_TIMEOUT = 1000U
};

typedef open_cfw_bootloader_elog_port_handle
(*open_cfw_bootloader_elog_mutex_new_fn)(const void *attributes);
typedef open_cfw_bootloader_elog_port_u32
(*open_cfw_bootloader_elog_mutex_acquire_fn)(
    open_cfw_bootloader_elog_port_handle handle,
    open_cfw_bootloader_elog_port_u32 timeout);
typedef open_cfw_bootloader_elog_port_u32
(*open_cfw_bootloader_elog_mutex_release_fn)(
    open_cfw_bootloader_elog_port_handle handle);
typedef void (*open_cfw_bootloader_elog_driver_output_fn)(
    const char *log,
    open_cfw_bootloader_elog_port_u32 size,
    open_cfw_bootloader_elog_port_u32 level);
typedef open_cfw_bootloader_elog_port_u32
(*open_cfw_bootloader_elog_tick_count_fn)(void);
typedef int (*open_cfw_bootloader_elog_snprintf_fn)(
    char *buffer,
    open_cfw_bootloader_elog_port_u32 size,
    const char *format,
    ...);
typedef open_cfw_bootloader_elog_port_u32
(*open_cfw_bootloader_elog_kernel_state_fn)(void);
typedef open_cfw_bootloader_elog_port_handle
(*open_cfw_bootloader_elog_thread_current_fn)(void);
typedef const char *(*open_cfw_bootloader_elog_thread_name_fn)(
    open_cfw_bootloader_elog_port_handle thread);
typedef void (*open_cfw_bootloader_elog_void_fn)(void);
typedef const char *(*open_cfw_bootloader_elog_string_fn)(void);

#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_PORT_HOST)
open_cfw_bootloader_elog_port_handle *
open_cfw_bootloader_easylogger_port_host_mutex_cell(void);
open_cfw_bootloader_elog_port_handle
open_cfw_bootloader_easylogger_port_host_mutex_new(const void *attributes);
open_cfw_bootloader_elog_port_u32
open_cfw_bootloader_easylogger_port_host_mutex_acquire(
    open_cfw_bootloader_elog_port_handle handle,
    open_cfw_bootloader_elog_port_u32 timeout);
open_cfw_bootloader_elog_port_u32
open_cfw_bootloader_easylogger_port_host_mutex_release(
    open_cfw_bootloader_elog_port_handle handle);
void open_cfw_bootloader_easylogger_port_host_driver_output(
    const char *log,
    open_cfw_bootloader_elog_port_u32 size,
    open_cfw_bootloader_elog_port_u32 level);
open_cfw_bootloader_elog_port_u32
open_cfw_bootloader_easylogger_port_host_tick_count(void);
int open_cfw_bootloader_easylogger_port_host_snprintf(
    char *buffer,
    open_cfw_bootloader_elog_port_u32 size,
    const char *format,
    open_cfw_bootloader_elog_port_u32 value);
open_cfw_bootloader_elog_port_u32
open_cfw_bootloader_easylogger_port_host_kernel_state(void);
open_cfw_bootloader_elog_port_handle
open_cfw_bootloader_easylogger_port_host_thread_current(void);
const char *open_cfw_bootloader_easylogger_port_host_thread_name(
    open_cfw_bootloader_elog_port_handle thread);
char *open_cfw_bootloader_easylogger_port_host_time_buffer(void);
#endif

static __attribute__((always_inline)) inline
open_cfw_bootloader_elog_port_handle *
open_cfw_bootloader_easylogger_port_mutex_cell(void)
{
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_PORT_HOST)
    return open_cfw_bootloader_easylogger_port_host_mutex_cell();
#else
    return (open_cfw_bootloader_elog_port_handle *)
        (open_cfw_bootloader_elog_port_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_MUTEX_HANDLE_ADDRESS;
#endif
}

static __attribute__((always_inline)) inline
open_cfw_bootloader_elog_port_handle
open_cfw_bootloader_easylogger_port_mutex_new(void)
{
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_PORT_HOST)
    return open_cfw_bootloader_easylogger_port_host_mutex_new(
        (const void *)(open_cfw_bootloader_elog_port_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_MUTEX_ATTRIBUTES_ADDRESS);
#else
    return ((open_cfw_bootloader_elog_mutex_new_fn)
        (open_cfw_bootloader_elog_port_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_MUTEX_NEW_THUMB)(
                (const void *)(open_cfw_bootloader_elog_port_uintptr)
                    OPEN_CFW_BOOTLOADER_ELOG_MUTEX_ATTRIBUTES_ADDRESS);
#endif
}

static __attribute__((always_inline)) inline void
open_cfw_bootloader_easylogger_port_mutex_acquire(
    open_cfw_bootloader_elog_port_handle handle)
{
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_PORT_HOST)
    (void)open_cfw_bootloader_easylogger_port_host_mutex_acquire(
        handle, OPEN_CFW_BOOTLOADER_ELOG_MUTEX_TIMEOUT);
#else
    (void)((open_cfw_bootloader_elog_mutex_acquire_fn)
        (open_cfw_bootloader_elog_port_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_MUTEX_ACQUIRE_THUMB)(
                handle, OPEN_CFW_BOOTLOADER_ELOG_MUTEX_TIMEOUT);
#endif
}

static __attribute__((always_inline)) inline void
open_cfw_bootloader_easylogger_port_mutex_release(
    open_cfw_bootloader_elog_port_handle handle)
{
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_PORT_HOST)
    (void)open_cfw_bootloader_easylogger_port_host_mutex_release(handle);
#else
    (void)((open_cfw_bootloader_elog_mutex_release_fn)
        (open_cfw_bootloader_elog_port_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_MUTEX_RELEASE_THUMB)(handle);
#endif
}

__attribute__((used, noinline))
void open_cfw_bootloader_easylogger_mutex_create_41a648(void)
{
    open_cfw_bootloader_elog_port_handle *const cell =
        open_cfw_bootloader_easylogger_port_mutex_cell();

    if (*cell == (open_cfw_bootloader_elog_port_handle)0) {
        *cell = open_cfw_bootloader_easylogger_port_mutex_new();
    }
}

__attribute__((used, noinline))
void open_cfw_bootloader_easylogger_mutex_acquire_41a65c(void)
{
    open_cfw_bootloader_elog_port_handle const handle =
        *open_cfw_bootloader_easylogger_port_mutex_cell();

    if (handle != (open_cfw_bootloader_elog_port_handle)0) {
        open_cfw_bootloader_easylogger_port_mutex_acquire(handle);
    }
}

__attribute__((used, noinline))
void open_cfw_bootloader_easylogger_mutex_release_41a672(void)
{
    open_cfw_bootloader_elog_port_handle const handle =
        *open_cfw_bootloader_easylogger_port_mutex_cell();

    if (handle != (open_cfw_bootloader_elog_port_handle)0) {
        open_cfw_bootloader_easylogger_port_mutex_release(handle);
    }
}

__attribute__((used, noinline))
open_cfw_bootloader_elog_port_u8
open_cfw_bootloader_easylogger_port_init_41a684(void)
{
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_PORT_HOST)
    open_cfw_bootloader_easylogger_mutex_create_41a648();
#else
    ((open_cfw_bootloader_elog_void_fn)
        (open_cfw_bootloader_elog_port_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_MUTEX_CREATE_THUMB)();
#endif
    return 0U;
}

__attribute__((used, noinline))
void open_cfw_bootloader_easylogger_port_output_41a692(
    const char *log,
    open_cfw_bootloader_elog_port_u32 size,
    open_cfw_bootloader_elog_port_u32 level)
{
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_PORT_HOST)
    open_cfw_bootloader_easylogger_port_host_driver_output(log, size, level);
#else
    ((open_cfw_bootloader_elog_driver_output_fn)
        (open_cfw_bootloader_elog_port_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_DRIVER_OUTPUT_THUMB)(log, size, level);
#endif
}

__attribute__((used, noinline))
void open_cfw_bootloader_easylogger_port_output_lock_41a69a(void)
{
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_PORT_HOST)
    open_cfw_bootloader_easylogger_mutex_acquire_41a65c();
#else
    ((open_cfw_bootloader_elog_void_fn)
        (open_cfw_bootloader_elog_port_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_MUTEX_ACQUIRE_HELPER_THUMB)();
#endif
}

__attribute__((used, noinline))
void open_cfw_bootloader_easylogger_port_output_unlock_41a6a2(void)
{
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_PORT_HOST)
    open_cfw_bootloader_easylogger_mutex_release_41a672();
#else
    ((open_cfw_bootloader_elog_void_fn)
        (open_cfw_bootloader_elog_port_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_MUTEX_RELEASE_HELPER_THUMB)();
#endif
}

__attribute__((used, noinline))
const char *open_cfw_bootloader_easylogger_port_get_time_41a6aa(void)
{
    open_cfw_bootloader_elog_port_u32 tick;
    char *buffer;

#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_PORT_HOST)
    tick = open_cfw_bootloader_easylogger_port_host_tick_count();
    buffer = open_cfw_bootloader_easylogger_port_host_time_buffer();
    (void)open_cfw_bootloader_easylogger_port_host_snprintf(
        buffer, OPEN_CFW_BOOTLOADER_ELOG_TIME_BUFFER_SIZE, "%d", tick);
#else
    tick = ((open_cfw_bootloader_elog_tick_count_fn)
        (open_cfw_bootloader_elog_port_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_TICK_COUNT_THUMB)();
    buffer = (char *)(open_cfw_bootloader_elog_port_uintptr)
        OPEN_CFW_BOOTLOADER_ELOG_TIME_BUFFER_ADDRESS;
    (void)((open_cfw_bootloader_elog_snprintf_fn)
        (open_cfw_bootloader_elog_port_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_SNPRINTF_THUMB)(
                buffer,
                OPEN_CFW_BOOTLOADER_ELOG_TIME_BUFFER_SIZE,
                (const char *)(open_cfw_bootloader_elog_port_uintptr)
                    OPEN_CFW_BOOTLOADER_ELOG_TIME_FORMAT_ADDRESS,
                tick);
#endif
    return buffer;
}

__attribute__((used, noinline))
const char *open_cfw_bootloader_easylogger_task_name_41a6c2(void)
{
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_PORT_HOST)
    if (open_cfw_bootloader_easylogger_port_host_kernel_state() == 1U) {
        return "unknown";
    }
    return open_cfw_bootloader_easylogger_port_host_thread_name(
        open_cfw_bootloader_easylogger_port_host_thread_current());
#else
    if (((open_cfw_bootloader_elog_kernel_state_fn)
            (open_cfw_bootloader_elog_port_uintptr)
                OPEN_CFW_BOOTLOADER_ELOG_KERNEL_STATE_THUMB)() == 1U) {
        return (const char *)(open_cfw_bootloader_elog_port_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_UNKNOWN_ADDRESS;
    }
    return ((open_cfw_bootloader_elog_thread_name_fn)
        (open_cfw_bootloader_elog_port_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_THREAD_NAME_THUMB)(
                ((open_cfw_bootloader_elog_thread_current_fn)
                    (open_cfw_bootloader_elog_port_uintptr)
                        OPEN_CFW_BOOTLOADER_ELOG_THREAD_CURRENT_THUMB)());
#endif
}

__attribute__((used, noinline))
const char *open_cfw_bootloader_easylogger_port_get_p_info_41a6f0(void)
{
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_PORT_HOST)
    return open_cfw_bootloader_easylogger_task_name_41a6c2();
#else
    return ((open_cfw_bootloader_elog_string_fn)
        (open_cfw_bootloader_elog_port_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_TASK_NAME_HELPER_THUMB)();
#endif
}

__attribute__((used, noinline))
const char *open_cfw_bootloader_easylogger_port_get_t_info_41a6f8(void)
{
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_PORT_HOST)
    return open_cfw_bootloader_easylogger_task_name_41a6c2();
#else
    return ((open_cfw_bootloader_elog_string_fn)
        (open_cfw_bootloader_elog_port_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_TASK_NAME_HELPER_THUMB)();
#endif
}
