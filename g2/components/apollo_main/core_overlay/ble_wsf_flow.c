/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room BLE WSF transmit-ready flow control reconstructed from stock
 * 0x004D0B36...0x004D0CDB.
 */

typedef __UINTPTR_TYPE__ open_cfw_ble_wsf_flow_uintptr;

#define OPEN_CFW_BLE_WSF_STATE_ADDRESS 0x20004068U
#define OPEN_CFW_BLE_WSF_RETRY_TIMEOUT 10U
#define OPEN_CFW_BLE_WSF_RETRY_DELAY 10U
#define OPEN_CFW_BLE_WSF_RETRY_LIMIT 20U

typedef struct {
    unsigned int reserved_0;
    unsigned int reserved_4;
    unsigned int thread;
    unsigned int reserved_c;
    unsigned int reserved_10;
    unsigned int tx_ready;
} open_cfw_ble_wsf_flow_state;

#ifndef OPEN_CFW_BLE_WSF_FLOW_STATE
#define OPEN_CFW_BLE_WSF_FLOW_STATE \
    ((volatile open_cfw_ble_wsf_flow_state *) \
        (open_cfw_ble_wsf_flow_uintptr)OPEN_CFW_BLE_WSF_STATE_ADDRESS)
#endif

#ifndef OPEN_CFW_BLE_WSF_SEMAPHORE_ACQUIRE
typedef int (*open_cfw_ble_wsf_semaphore_acquire_function)(void *, unsigned int);
#define OPEN_CFW_BLE_WSF_SEMAPHORE_ACQUIRE(semaphore, timeout) \
    (((open_cfw_ble_wsf_semaphore_acquire_function)0x0044994FU)( \
        (semaphore), (timeout)))
#endif

#ifndef OPEN_CFW_BLE_WSF_KERNEL_TICK
typedef unsigned int (*open_cfw_ble_wsf_kernel_tick_function)(void);
#define OPEN_CFW_BLE_WSF_KERNEL_TICK() \
    (((open_cfw_ble_wsf_kernel_tick_function)0x004490CDU)())
#endif

#ifndef OPEN_CFW_BLE_WSF_DELAY
typedef unsigned int (*open_cfw_ble_wsf_delay_function)(unsigned int);
#define OPEN_CFW_BLE_WSF_DELAY(ticks) \
    (((open_cfw_ble_wsf_delay_function)0x00449377U)((ticks)))
#endif

#ifndef OPEN_CFW_BLE_WSF_SEMAPHORE_COUNT
typedef unsigned int (*open_cfw_ble_wsf_semaphore_count_function)(void *);
#define OPEN_CFW_BLE_WSF_SEMAPHORE_COUNT(semaphore) \
    (((open_cfw_ble_wsf_semaphore_count_function)0x00449A0FU)((semaphore)))
#endif

#ifndef OPEN_CFW_BLE_WSF_SEMAPHORE_RELEASE
typedef int (*open_cfw_ble_wsf_semaphore_release_function)(void *);
#define OPEN_CFW_BLE_WSF_SEMAPHORE_RELEASE(semaphore) \
    (((open_cfw_ble_wsf_semaphore_release_function)0x004499B9U)((semaphore)))
#endif

#ifndef OPEN_CFW_BLE_WSF_WAIT_BOUND_DIAGNOSTIC
#define OPEN_CFW_BLE_WSF_WAIT_BOUND_DIAGNOSTIC() ((void)0)
#endif

#ifndef OPEN_CFW_BLE_WSF_WAIT_RESULT_DIAGNOSTIC
#define OPEN_CFW_BLE_WSF_WAIT_RESULT_DIAGNOSTIC(elapsed, retries) \
    do { \
        (void)(elapsed); \
        (void)(retries); \
    } while (0)
#endif

#ifndef OPEN_CFW_BLE_WSF_RELEASE_FAILURE_DIAGNOSTIC
#define OPEN_CFW_BLE_WSF_RELEASE_FAILURE_DIAGNOSTIC(status, count) \
    do { \
        (void)(status); \
        (void)(count); \
    } while (0)
#endif

#ifndef OPEN_CFW_BLE_WSF_ALREADY_FULL_DIAGNOSTIC
#define OPEN_CFW_BLE_WSF_ALREADY_FULL_DIAGNOSTIC(count) ((void)(count))
#endif

__attribute__((used, noinline))
unsigned int open_cfw_ble_wsf_take_tx_ready(unsigned short timeout)
{
    volatile open_cfw_ble_wsf_flow_state *state = OPEN_CFW_BLE_WSF_FLOW_STATE;

    if (state->tx_ready == 0U) {
        return 0U;
    }
    return OPEN_CFW_BLE_WSF_SEMAPHORE_ACQUIRE(
        (void *)(open_cfw_ble_wsf_flow_uintptr)state->tx_ready,
        (unsigned int)timeout
    ) == 0 ? 1U : 0U;
}

__attribute__((used, noinline))
void open_cfw_ble_wsf_wait_tx_ready(void)
{
    unsigned int start = OPEN_CFW_BLE_WSF_KERNEL_TICK();
    unsigned char retries = 0U;
    unsigned char acquired = (unsigned char)open_cfw_ble_wsf_take_tx_ready(0U);

    if (acquired == 0U) {
        do {
            acquired = (unsigned char)open_cfw_ble_wsf_take_tx_ready(
                OPEN_CFW_BLE_WSF_RETRY_TIMEOUT
            );
            if (acquired == 0U) {
                (void)OPEN_CFW_BLE_WSF_DELAY(OPEN_CFW_BLE_WSF_RETRY_DELAY);
            }
            ++retries;
        } while (retries < OPEN_CFW_BLE_WSF_RETRY_LIMIT && acquired == 0U);

        if (retries >= OPEN_CFW_BLE_WSF_RETRY_LIMIT) {
            OPEN_CFW_BLE_WSF_WAIT_BOUND_DIAGNOSTIC();
        }
    }

    OPEN_CFW_BLE_WSF_WAIT_RESULT_DIAGNOSTIC(
        OPEN_CFW_BLE_WSF_KERNEL_TICK() - start,
        retries
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_ble_wsf_wait_once(unsigned short timeout)
{
    return open_cfw_ble_wsf_take_tx_ready(timeout);
}

__attribute__((used, noinline))
void open_cfw_ble_wsf_tx_complete_notify(void)
{
    volatile open_cfw_ble_wsf_flow_state *state = OPEN_CFW_BLE_WSF_FLOW_STATE;
    unsigned int count;
    int status;

    if (state->tx_ready == 0U) {
        return;
    }
    count = OPEN_CFW_BLE_WSF_SEMAPHORE_COUNT(
        (void *)(open_cfw_ble_wsf_flow_uintptr)state->tx_ready
    );
    if (count != 0U) {
        OPEN_CFW_BLE_WSF_ALREADY_FULL_DIAGNOSTIC(count);
        return;
    }
    status = OPEN_CFW_BLE_WSF_SEMAPHORE_RELEASE(
        (void *)(open_cfw_ble_wsf_flow_uintptr)state->tx_ready
    );
    if (status != 0) {
        OPEN_CFW_BLE_WSF_RELEASE_FAILURE_DIAGNOSTIC(status, count);
    }
}
