/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded BLE connection-mode control helpers matched to stock entries
 * 0x004780F8, 0x00478110, 0x00478160, 0x004781F4, and 0x00478252.
 */

typedef __UINTPTR_TYPE__ open_cfw_ble_control_uintptr;
typedef void (*open_cfw_ble_control_callback)(void *);

typedef unsigned int (*open_cfw_ble_control_tick_function)(void);
typedef unsigned int (*open_cfw_ble_control_log_level_function)(void);
typedef void (*open_cfw_ble_control_log_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
typedef void (*open_cfw_ble_control_trace_function)(
    unsigned int,
    const void *,
    const void *,
    ...
);

#ifndef OPEN_CFW_BLE_CONTROL_CURRENT_MODE
#define OPEN_CFW_BLE_CONTROL_CURRENT_MODE \
    (*(volatile unsigned char *)0x20004542U)
#endif
#ifndef OPEN_CFW_BLE_CONTROL_REMOTE_ACTIVE
#define OPEN_CFW_BLE_CONTROL_REMOTE_ACTIVE \
    (*(volatile unsigned char *)0x20074F8FU)
#endif
#ifndef OPEN_CFW_BLE_CONTROL_RETRY_ACTIVE
#define OPEN_CFW_BLE_CONTROL_RETRY_ACTIVE \
    (*(volatile unsigned char *)0x20074F90U)
#endif
#ifndef OPEN_CFW_BLE_CONTROL_TIMESTAMP
#define OPEN_CFW_BLE_CONTROL_TIMESTAMP \
    (*(volatile unsigned int *)0x20074340U)
#endif
#ifndef OPEN_CFW_BLE_CONTROL_TICK
#define OPEN_CFW_BLE_CONTROL_TICK() \
    (((open_cfw_ble_control_tick_function)0x004490CDU)())
#endif
#ifndef OPEN_CFW_BLE_CONTROL_LOG_LEVEL
#define OPEN_CFW_BLE_CONTROL_LOG_LEVEL() \
    (((open_cfw_ble_control_log_level_function)0x0043D0CFU)())
#endif
#ifndef OPEN_CFW_BLE_CONTROL_LOG
#define OPEN_CFW_BLE_CONTROL_LOG(...) \
    (((open_cfw_ble_control_log_function)0x0043D575U)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_BLE_CONTROL_TRACE
#define OPEN_CFW_BLE_CONTROL_TRACE(...) \
    (((open_cfw_ble_control_trace_function)0x0043CE9FU)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_BLE_CONTROL_CALLBACK
#define OPEN_CFW_BLE_CONTROL_CALLBACK \
    ((open_cfw_ble_control_callback) \
        (open_cfw_ble_control_uintptr)0x0047761DU)
#endif

unsigned char open_cfw_event_loop_remove_delayed(
    open_cfw_ble_control_callback callback
);
void open_cfw_event_loop_push_delayed(
    open_cfw_ble_control_callback callback,
    void *argument,
    unsigned int delay
);

static __attribute__((always_inline)) inline const void *
open_cfw_ble_control_pointer(unsigned int address)
{
    return (const void *)(open_cfw_ble_control_uintptr)address;
}

static __attribute__((always_inline)) inline int
open_cfw_ble_control_trace_enabled(void)
{
    unsigned int level = OPEN_CFW_BLE_CONTROL_LOG_LEVEL();

    if ((level & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_BLE_CONTROL_LOG_LEVEL() & 4U) != 0U;
}

static __attribute__((always_inline)) inline void
open_cfw_ble_control_schedule(
    unsigned int mode,
    unsigned int delay
)
{
    open_cfw_event_loop_push_delayed(
        OPEN_CFW_BLE_CONTROL_CALLBACK,
        (void *)(open_cfw_ble_control_uintptr)mode,
        delay
    );
}

unsigned int open_cfw_ble_connection_stream_ready(void)
{
    return OPEN_CFW_BLE_CONTROL_CURRENT_MODE == 0xA3U ? 1U : 0U;
}

void open_cfw_ble_connection_schedule_short(unsigned int resume_long)
{
    if (OPEN_CFW_BLE_CONTROL_REMOTE_ACTIVE != 0U) {
        OPEN_CFW_BLE_CONTROL_CURRENT_MODE = 0xA4U;
    }

    (void)open_cfw_event_loop_remove_delayed(
        OPEN_CFW_BLE_CONTROL_CALLBACK
    );
    if ((unsigned char)resume_long != 0U) {
        open_cfw_ble_control_schedule(0xA4U, 60000U);
    }
    open_cfw_ble_control_schedule(0xA3U, 0U);
}

void open_cfw_ble_connection_stream_reset(void)
{
    if (
        OPEN_CFW_BLE_CONTROL_RETRY_ACTIVE != 0U
        && OPEN_CFW_BLE_CONTROL_TIMESTAMP != 0U
    ) {
        unsigned int elapsed =
            OPEN_CFW_BLE_CONTROL_TICK() - OPEN_CFW_BLE_CONTROL_TIMESTAMP;

        if (elapsed < 30000U) {
            unsigned int remaining = 30000U - elapsed;

            if ((OPEN_CFW_BLE_CONTROL_LOG_LEVEL() & 2U) != 0U) {
                OPEN_CFW_BLE_CONTROL_LOG(
                    4U,
                    open_cfw_ble_control_pointer(0x0078A0B8U),
                    open_cfw_ble_control_pointer(0x006F81BCU),
                    open_cfw_ble_control_pointer(0x0075DCF0U),
                    0x1E8U,
                    open_cfw_ble_control_pointer(0x006D8454U),
                    elapsed,
                    remaining
                );
            }
            if (open_cfw_ble_control_trace_enabled()) {
                const void *identity =
                    open_cfw_ble_control_pointer(0x0069E20CU);

                OPEN_CFW_BLE_CONTROL_TRACE(
                    0x10800000U,
                    identity,
                    identity,
                    elapsed,
                    remaining
                );
            }
            return;
        }
    }

    (void)open_cfw_event_loop_remove_delayed(
        OPEN_CFW_BLE_CONTROL_CALLBACK
    );
    open_cfw_ble_control_schedule(0xA3U, 0U);
}

void open_cfw_ble_connection_remote_reset(void)
{
    if ((OPEN_CFW_BLE_CONTROL_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_BLE_CONTROL_LOG(
            4U,
            open_cfw_ble_control_pointer(0x0078A0B8U),
            open_cfw_ble_control_pointer(0x006F81BCU),
            open_cfw_ble_control_pointer(0x0075DD10U),
            0x1F3U,
            open_cfw_ble_control_pointer(0x0075DD30U)
        );
    }
    if (open_cfw_ble_control_trace_enabled()) {
        const void *identity =
            open_cfw_ble_control_pointer(0x0073BFE0U);

        OPEN_CFW_BLE_CONTROL_TRACE(
            0x10000000U,
            identity,
            identity
        );
    }

    OPEN_CFW_BLE_CONTROL_REMOTE_ACTIVE = 0U;
    (void)open_cfw_event_loop_remove_delayed(
        OPEN_CFW_BLE_CONTROL_CALLBACK
    );
    open_cfw_ble_control_schedule(0xA3U, 0U);
}

void open_cfw_ble_connection_schedule_long(unsigned int delay)
{
    (void)open_cfw_event_loop_remove_delayed(
        OPEN_CFW_BLE_CONTROL_CALLBACK
    );
    open_cfw_ble_control_schedule(0xA4U, delay);
}
