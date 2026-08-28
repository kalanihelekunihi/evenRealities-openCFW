/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded BLE message-transmit thread entry matched to stock
 * 0x00475290...0x00475307.
 */

typedef __UINTPTR_TYPE__ open_cfw_ble_msgtx_uintptr;

#define OPEN_CFW_BLE_MSGTX_THREAD_FLAGS 0x00FFFFFFU
#define OPEN_CFW_BLE_MSGTX_WAIT_ANY 0U
#define OPEN_CFW_BLE_MSGTX_WAIT_FOREVER 0xFFFFFFFFU
#define OPEN_CFW_BLE_MSGTX_FLAG_ERROR 0x80000000U

typedef void (*open_cfw_ble_msgtx_void_function)(void);
typedef unsigned int (*open_cfw_ble_msgtx_wait_function)(
    unsigned int,
    unsigned int,
    unsigned int
);
typedef void (*open_cfw_ble_msgtx_dispatch_function)(unsigned int);
typedef unsigned int (*open_cfw_ble_msgtx_log_level_function)(void);
typedef void (*open_cfw_ble_msgtx_log_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *
);
typedef void (*open_cfw_ble_msgtx_trace_function)(
    unsigned int,
    const void *,
    const void *
);

void open_cfw_ble_msgtx_stage_enter(void);
void open_cfw_ble_msgtx_queue_initialize(void);
void open_cfw_ble_msgtx_application_initialize(void);
void open_cfw_ble_msgtx_thread_initialize(void);
void open_cfw_ble_msgtx_stage_leave(void);
void open_cfw_ble_msgtx_dispatch_flags(unsigned int flags);

#ifndef OPEN_CFW_BLE_MSGTX_STAGE_ENTER
#define OPEN_CFW_BLE_MSGTX_STAGE_ENTER() \
    open_cfw_ble_msgtx_stage_enter()
#endif

#ifndef OPEN_CFW_BLE_MSGTX_QUEUE_INITIALIZE
#define OPEN_CFW_BLE_MSGTX_QUEUE_INITIALIZE() \
    open_cfw_ble_msgtx_queue_initialize()
#endif

#ifndef OPEN_CFW_BLE_MSGTX_APPLICATION_INITIALIZE
#define OPEN_CFW_BLE_MSGTX_APPLICATION_INITIALIZE() \
    open_cfw_ble_msgtx_application_initialize()
#endif

#ifndef OPEN_CFW_BLE_MSGTX_THREAD_INITIALIZE
#define OPEN_CFW_BLE_MSGTX_THREAD_INITIALIZE() \
    open_cfw_ble_msgtx_thread_initialize()
#endif

#ifndef OPEN_CFW_BLE_MSGTX_STAGE_LEAVE
#define OPEN_CFW_BLE_MSGTX_STAGE_LEAVE() \
    open_cfw_ble_msgtx_stage_leave()
#endif

#ifndef OPEN_CFW_BLE_MSGTX_WAIT
#define OPEN_CFW_BLE_MSGTX_WAIT(flags, options, timeout) \
    (((open_cfw_ble_msgtx_wait_function)0x004492C3U)( \
        (flags), \
        (options), \
        (timeout) \
    ))
#endif

#ifndef OPEN_CFW_BLE_MSGTX_DISPATCH
#define OPEN_CFW_BLE_MSGTX_DISPATCH(flags) \
    open_cfw_ble_msgtx_dispatch_flags((flags))
#endif

#ifndef OPEN_CFW_BLE_MSGTX_LOG_LEVEL
#define OPEN_CFW_BLE_MSGTX_LOG_LEVEL() \
    (((open_cfw_ble_msgtx_log_level_function)0x0043D0CFU)())
#endif

#ifndef OPEN_CFW_BLE_MSGTX_LOG
#define OPEN_CFW_BLE_MSGTX_LOG( \
    level, module, file, function, line, message \
) \
    (((open_cfw_ble_msgtx_log_function)0x0043D575U)( \
        (level), \
        (module), \
        (file), \
        (function), \
        (line), \
        (message) \
    ))
#endif

#ifndef OPEN_CFW_BLE_MSGTX_TRACE
#define OPEN_CFW_BLE_MSGTX_TRACE(level, format, argument) \
    (((open_cfw_ble_msgtx_trace_function)0x0043CE9FU)( \
        (level), \
        (format), \
        (argument) \
    ))
#endif

#ifndef OPEN_CFW_BLE_MSGTX_LOOP_CONTINUE
#define OPEN_CFW_BLE_MSGTX_LOOP_CONTINUE() 1
#endif

__attribute__((used, noinline))
void open_cfw_ble_msgtx_thread(void *argument)
{
    unsigned int flags;
    unsigned int level;

    (void)argument;

    OPEN_CFW_BLE_MSGTX_STAGE_ENTER();
    OPEN_CFW_BLE_MSGTX_QUEUE_INITIALIZE();
    OPEN_CFW_BLE_MSGTX_APPLICATION_INITIALIZE();
    OPEN_CFW_BLE_MSGTX_THREAD_INITIALIZE();
    OPEN_CFW_BLE_MSGTX_STAGE_LEAVE();

    for (;;) {
        flags = OPEN_CFW_BLE_MSGTX_WAIT(
            OPEN_CFW_BLE_MSGTX_THREAD_FLAGS,
            OPEN_CFW_BLE_MSGTX_WAIT_ANY,
            OPEN_CFW_BLE_MSGTX_WAIT_FOREVER
        );
        while (
            flags != 0U &&
            flags < OPEN_CFW_BLE_MSGTX_FLAG_ERROR
        ) {
            OPEN_CFW_BLE_MSGTX_DISPATCH(flags);
            flags = OPEN_CFW_BLE_MSGTX_WAIT(
                OPEN_CFW_BLE_MSGTX_THREAD_FLAGS,
                OPEN_CFW_BLE_MSGTX_WAIT_ANY,
                OPEN_CFW_BLE_MSGTX_WAIT_FOREVER
            );
        }

        if ((OPEN_CFW_BLE_MSGTX_LOG_LEVEL() & 2U) != 0U) {
            OPEN_CFW_BLE_MSGTX_LOG(
                1U,
                (const void *)(open_cfw_ble_msgtx_uintptr)0x0078C644U,
                (const void *)(open_cfw_ble_msgtx_uintptr)0x006FE2C4U,
                (const void *)(open_cfw_ble_msgtx_uintptr)0x007841D0U,
                0x67U,
                (const void *)(open_cfw_ble_msgtx_uintptr)0x00789A70U
            );
        }

        level = OPEN_CFW_BLE_MSGTX_LOG_LEVEL();
        if (
            (level & 1U) != 0U ||
            (OPEN_CFW_BLE_MSGTX_LOG_LEVEL() & 4U) != 0U
        ) {
            OPEN_CFW_BLE_MSGTX_TRACE(
                0x04000000U,
                (const void *)(open_cfw_ble_msgtx_uintptr)0x0077354CU,
                (const void *)(open_cfw_ble_msgtx_uintptr)0x0077354CU
            );
        }

        if (!OPEN_CFW_BLE_MSGTX_LOOP_CONTINUE()) {
            return;
        }
    }
}
