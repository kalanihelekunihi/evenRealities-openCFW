/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room BLE WSF task lifecycle reconstructed from stock
 * 0x004D0AF6...0x004D0B35.
 */

typedef __UINTPTR_TYPE__ open_cfw_ble_wsf_lifecycle_uintptr;

#define OPEN_CFW_BLE_WSF_STATE_ADDRESS 0x20004068U
#define OPEN_CFW_BLE_WSF_TASK_ATTRIBUTES 0x0075B838U

typedef struct {
    unsigned int reserved_0;
    unsigned int reserved_4;
    unsigned int thread;
    unsigned int reserved_c;
    unsigned int reserved_10;
    unsigned int tx_ready;
} open_cfw_ble_wsf_lifecycle_state;

#ifndef OPEN_CFW_BLE_WSF_LIFECYCLE_STATE
#define OPEN_CFW_BLE_WSF_LIFECYCLE_STATE \
    ((volatile open_cfw_ble_wsf_lifecycle_state *) \
        (open_cfw_ble_wsf_lifecycle_uintptr)OPEN_CFW_BLE_WSF_STATE_ADDRESS)
#endif

#ifndef OPEN_CFW_BLE_WSF_THREAD_NEW
typedef void *(*open_cfw_ble_wsf_thread_new_function)(
    void (*)(void *),
    void *,
    const void *
);
#define OPEN_CFW_BLE_WSF_THREAD_NEW(entry, argument, attributes) \
    (((open_cfw_ble_wsf_thread_new_function)0x004490E3U)( \
        (entry), (argument), (attributes)))
#endif

#ifndef OPEN_CFW_BLE_WSF_THREAD_TERMINATE
typedef void (*open_cfw_ble_wsf_thread_terminate_function)(void *);
#define OPEN_CFW_BLE_WSF_THREAD_TERMINATE(thread) \
    (((open_cfw_ble_wsf_thread_terminate_function)0x004491FFU)((thread)))
#endif

#ifndef OPEN_CFW_BLE_WSF_RESOURCE_DEINITIALIZE
typedef void (*open_cfw_ble_wsf_resource_deinitialize_function)(void);
#define OPEN_CFW_BLE_WSF_RESOURCE_DEINITIALIZE() \
    (((open_cfw_ble_wsf_resource_deinitialize_function)0x004ABCBDU)())
#endif

#ifndef OPEN_CFW_BLE_WSF_THREAD_FATAL
typedef void (*open_cfw_ble_wsf_thread_fatal_function)(void);
#define OPEN_CFW_BLE_WSF_THREAD_FATAL() \
    do { \
        ((open_cfw_ble_wsf_thread_fatal_function)0x005FA0A5U)(); \
        *(volatile unsigned int *)(open_cfw_ble_wsf_lifecycle_uintptr) \
            0xFFFFFFFFU = 0U; \
        for (;;) { \
        } \
    } while (0)
#endif

void open_cfw_ble_wsf_task(void *argument);

__attribute__((used, noinline))
void open_cfw_ble_wsf_initialize(void)
{
    volatile open_cfw_ble_wsf_lifecycle_state *state =
        OPEN_CFW_BLE_WSF_LIFECYCLE_STATE;

    state->thread = (unsigned int)(open_cfw_ble_wsf_lifecycle_uintptr)
        OPEN_CFW_BLE_WSF_THREAD_NEW(
            open_cfw_ble_wsf_task,
            (void *)0,
            (const void *)(open_cfw_ble_wsf_lifecycle_uintptr)
                OPEN_CFW_BLE_WSF_TASK_ATTRIBUTES
        );
    if (state->thread == 0U) {
        OPEN_CFW_BLE_WSF_THREAD_FATAL();
    }
}

__attribute__((used, noinline))
void open_cfw_ble_wsf_deinitialize(void)
{
    volatile open_cfw_ble_wsf_lifecycle_state *state =
        OPEN_CFW_BLE_WSF_LIFECYCLE_STATE;

    OPEN_CFW_BLE_WSF_RESOURCE_DEINITIALIZE();
    if (state->thread != 0U) {
        OPEN_CFW_BLE_WSF_THREAD_TERMINATE(
            (void *)(open_cfw_ble_wsf_lifecycle_uintptr)state->thread
        );
        state->thread = 0U;
    }
}
