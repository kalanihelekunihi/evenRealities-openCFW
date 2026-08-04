/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded BLE message-transmit setup and thread lifecycle matched to stock
 * 0x00475334...0x0047538B.
 */

typedef __UINTPTR_TYPE__ open_cfw_ble_msgtx_lifecycle_uintptr;

#define OPEN_CFW_BLE_MSGTX_LIFECYCLE_STATE_ADDRESS 0x20004020U
#define OPEN_CFW_BLE_MSGTX_THREAD_ENTRY 0x00475291U
#define OPEN_CFW_BLE_MSGTX_THREAD_ATTRIBUTES 0x0075B85CU
#define OPEN_CFW_BLE_MSGTX_STAGE_INDEX 8U

typedef struct {
    unsigned int reserved_0;
    unsigned int reserved_4;
    unsigned int thread;
    unsigned int queue;
} open_cfw_ble_msgtx_lifecycle_state;

#ifndef OPEN_CFW_BLE_MSGTX_LIFECYCLE_STATE
#define OPEN_CFW_BLE_MSGTX_LIFECYCLE_STATE \
    ((volatile open_cfw_ble_msgtx_lifecycle_state *) \
        (open_cfw_ble_msgtx_lifecycle_uintptr) \
            OPEN_CFW_BLE_MSGTX_LIFECYCLE_STATE_ADDRESS)
#endif

#ifndef OPEN_CFW_BLE_MSGTX_STAGE_ENTER_BACKEND
typedef void (*open_cfw_ble_msgtx_stage_function)(unsigned int);
#define OPEN_CFW_BLE_MSGTX_STAGE_ENTER_BACKEND(index) \
    (((open_cfw_ble_msgtx_stage_function)0x004C9B87U)((index)))
#endif

#ifndef OPEN_CFW_BLE_MSGTX_STAGE_LEAVE_BACKEND
#define OPEN_CFW_BLE_MSGTX_STAGE_LEAVE_BACKEND(index) \
    (((open_cfw_ble_msgtx_stage_function)0x004C9BE3U)((index)))
#endif

#ifndef OPEN_CFW_BLE_MSGTX_THREAD_NEW
typedef void *(*open_cfw_ble_msgtx_thread_new_function)(
    void *,
    void *,
    const void *
);
#define OPEN_CFW_BLE_MSGTX_THREAD_NEW(entry, argument, attributes) \
    (((open_cfw_ble_msgtx_thread_new_function)0x004490E3U)( \
        (entry), \
        (argument), \
        (attributes) \
    ))
#endif

#ifndef OPEN_CFW_BLE_MSGTX_THREAD_TERMINATE
typedef void (*open_cfw_ble_msgtx_thread_terminate_function)(void *);
#define OPEN_CFW_BLE_MSGTX_THREAD_TERMINATE(thread) \
    (((open_cfw_ble_msgtx_thread_terminate_function)0x004491FFU)( \
        (thread) \
    ))
#endif

#ifndef OPEN_CFW_BLE_MSGTX_THREAD_FAILURE
typedef void (*open_cfw_ble_msgtx_thread_failure_function)(void);
#define OPEN_CFW_BLE_MSGTX_THREAD_FAILURE() \
    do { \
        ((open_cfw_ble_msgtx_thread_failure_function)0x005FA0A5U)(); \
        *(volatile unsigned int *) \
            (open_cfw_ble_msgtx_lifecycle_uintptr)0xFFFFFFFFU = 0U; \
        for (;;) { \
        } \
    } while (0)
#endif

__attribute__((used, noinline))
void open_cfw_ble_msgtx_stage_enter(void)
{
    OPEN_CFW_BLE_MSGTX_STAGE_ENTER_BACKEND(
        OPEN_CFW_BLE_MSGTX_STAGE_INDEX
    );
}

__attribute__((used, noinline))
void open_cfw_ble_msgtx_stage_leave(void)
{
    OPEN_CFW_BLE_MSGTX_STAGE_LEAVE_BACKEND(
        OPEN_CFW_BLE_MSGTX_STAGE_INDEX
    );
}

__attribute__((used, noinline))
void open_cfw_ble_msgtx_thread_create(void)
{
    volatile open_cfw_ble_msgtx_lifecycle_state *state =
        OPEN_CFW_BLE_MSGTX_LIFECYCLE_STATE;

    state->thread = (unsigned int)(open_cfw_ble_msgtx_lifecycle_uintptr)
        OPEN_CFW_BLE_MSGTX_THREAD_NEW(
            (void *)(open_cfw_ble_msgtx_lifecycle_uintptr)
                OPEN_CFW_BLE_MSGTX_THREAD_ENTRY,
            (void *)0,
            (const void *)(open_cfw_ble_msgtx_lifecycle_uintptr)
                OPEN_CFW_BLE_MSGTX_THREAD_ATTRIBUTES
        );
    if (state->thread == 0U) {
        OPEN_CFW_BLE_MSGTX_THREAD_FAILURE();
        return;
    }
}

__attribute__((used, noinline))
void open_cfw_ble_msgtx_thread_destroy(void)
{
    volatile open_cfw_ble_msgtx_lifecycle_state *state =
        OPEN_CFW_BLE_MSGTX_LIFECYCLE_STATE;

    if (state->thread != 0U) {
        OPEN_CFW_BLE_MSGTX_THREAD_TERMINATE(
            (void *)(open_cfw_ble_msgtx_lifecycle_uintptr)state->thread
        );
        state->thread = 0U;
    }
}
