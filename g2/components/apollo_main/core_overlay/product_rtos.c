/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room implementation of the G2 product task-vote policy and the
 * application-owned FreeRTOS hooks at 0x0046D67C...0x0046D89F.
 */

#include <stddef.h>
#include <stdint.h>

#define OPEN_CFW_PRODUCT_RTOS_SLOT_COUNT 32U
#define OPEN_CFW_PRODUCT_RTOS_INVALID_SLOT UINT32_MAX

typedef struct open_cfw_product_rtos_vote {
    uint32_t handle;
    uint8_t active;
    uint8_t reserved[3];
} open_cfw_product_rtos_vote;

typedef struct open_cfw_product_rtos_state {
    open_cfw_product_rtos_vote votes[OPEN_CFW_PRODUCT_RTOS_SLOT_COUNT];
    uint32_t active_count;
    uint8_t initialized;
    uint8_t reserved[3];
} open_cfw_product_rtos_state;

_Static_assert(sizeof(open_cfw_product_rtos_vote) == 8U, "G2 vote ABI");
_Static_assert(sizeof(open_cfw_product_rtos_state) == 0x108U, "G2 state ABI");

void *open_cfw_retained_product_rtos_memset(void *, int, size_t);
uint32_t open_cfw_retained_product_rtos_irq_save_disable(void);
void *open_cfw_retained_product_rtos_current_thread(void);
uint32_t open_cfw_retained_product_rtos_sleep(uint32_t mode);
void open_cfw_retained_product_rtos_watchdog_feed(void);
int open_cfw_retained_product_rtos_log(const char *format, ...);

#ifdef OPEN_CFW_PRODUCT_RTOS_TEST_HOST
extern open_cfw_product_rtos_state open_cfw_test_product_rtos_state;
void open_cfw_test_product_rtos_irq_restore(uint32_t primask);
void open_cfw_test_product_rtos_fatal(uint32_t reason);
#define OPEN_CFW_PRODUCT_RTOS_STATE open_cfw_test_product_rtos_state
#define OPEN_CFW_PRODUCT_RTOS_IRQ_RESTORE(value) \
    open_cfw_test_product_rtos_irq_restore((value))
#define OPEN_CFW_PRODUCT_RTOS_HALT(reason) \
    do { open_cfw_test_product_rtos_fatal((reason)); return; } while (0)
#define OPEN_CFW_PRODUCT_RTOS_BREAK_HALT(reason) \
    do { open_cfw_test_product_rtos_fatal((reason)); return; } while (0)
#endif

#ifndef OPEN_CFW_PRODUCT_RTOS_STATE
#define OPEN_CFW_PRODUCT_RTOS_STATE \
    (*(volatile open_cfw_product_rtos_state *)(uintptr_t)0x200700E0U)
#endif
#ifndef OPEN_CFW_PRODUCT_RTOS_MEMSET
#define OPEN_CFW_PRODUCT_RTOS_MEMSET(pointer, value, size) \
    open_cfw_retained_product_rtos_memset((pointer), (value), (size))
#endif
#ifndef OPEN_CFW_PRODUCT_RTOS_IRQ_SAVE_DISABLE
#define OPEN_CFW_PRODUCT_RTOS_IRQ_SAVE_DISABLE() \
    open_cfw_retained_product_rtos_irq_save_disable()
#endif
#ifndef OPEN_CFW_PRODUCT_RTOS_IRQ_RESTORE
#define OPEN_CFW_PRODUCT_RTOS_IRQ_RESTORE(value) \
    __asm volatile("msr primask, %0" : : "r"(value) : "memory")
#endif
#ifndef OPEN_CFW_PRODUCT_RTOS_CURRENT_THREAD
#define OPEN_CFW_PRODUCT_RTOS_CURRENT_THREAD() \
    open_cfw_retained_product_rtos_current_thread()
#endif
#ifndef OPEN_CFW_PRODUCT_RTOS_SLEEP
#define OPEN_CFW_PRODUCT_RTOS_SLEEP(mode) \
    open_cfw_retained_product_rtos_sleep((mode))
#endif
#ifndef OPEN_CFW_PRODUCT_RTOS_WATCHDOG_FEED
#define OPEN_CFW_PRODUCT_RTOS_WATCHDOG_FEED() \
    open_cfw_retained_product_rtos_watchdog_feed()
#endif
#ifndef OPEN_CFW_PRODUCT_RTOS_LOG
#define OPEN_CFW_PRODUCT_RTOS_LOG(...) \
    open_cfw_retained_product_rtos_log(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_PRODUCT_RTOS_HALT
#define OPEN_CFW_PRODUCT_RTOS_HALT(reason) \
    do { \
        (void)(reason); \
        for (;;) { \
            __asm volatile(""); \
        } \
    } while (0)
#endif
#ifndef OPEN_CFW_PRODUCT_RTOS_BREAK_HALT
#define OPEN_CFW_PRODUCT_RTOS_BREAK_HALT(reason) \
    do { \
        (void)(reason); \
        for (;;) { \
            __asm volatile("bkpt #0"); \
        } \
    } while (0)
#endif

#define OPEN_CFW_PRODUCT_RTOS_INIT_MESSAGE \
    ((const char *)(uintptr_t)0x00758F4CU)
#define OPEN_CFW_PRODUCT_RTOS_MALLOC_MESSAGE \
    ((const char *)(uintptr_t)0x00758F70U)
#define OPEN_CFW_PRODUCT_RTOS_STACK_MESSAGE \
    ((const char *)(uintptr_t)0x0077B1C4U)

uint32_t open_cfw_product_rtos_find_slot(void *task_handle);
uint32_t open_cfw_product_rtos_find_free_slot(void);
void open_cfw_product_rtos_init(void);
uint8_t open_cfw_product_rtos_acquire_for_handle(void *task_handle);
uint8_t open_cfw_product_rtos_release_for_handle(void *task_handle);
uint8_t open_cfw_product_rtos_blocks_deep_sleep(void);
void open_cfw_product_rtos_acquire_current(void);
void open_cfw_product_rtos_release_current(void);
uint32_t am_freertos_sleep(uint32_t expected_idle_time);
void am_freertos_wakeup(uint32_t slept_ticks);
void vApplicationMallocFailedHook(void);
void vApplicationStackOverflowHook(void *task, char *task_name);
void vApplicationIdleHook(void);

#if !defined(OPEN_CFW_PRODUCT_RTOS_LEAF_ONLY) || \
    defined(OPEN_CFW_PRODUCT_RTOS_FIND_SLOT_ONLY)
uint32_t open_cfw_product_rtos_find_slot(void *task_handle)
{
    uint32_t handle = (uint32_t)(uintptr_t)task_handle;
    uint32_t index;
#pragma clang loop unroll(disable)
    for (index = 0U; index < OPEN_CFW_PRODUCT_RTOS_SLOT_COUNT; ++index) {
        if (OPEN_CFW_PRODUCT_RTOS_STATE.votes[index].handle == handle) {
            return index;
        }
    }
    return OPEN_CFW_PRODUCT_RTOS_INVALID_SLOT;
}
#endif

#if !defined(OPEN_CFW_PRODUCT_RTOS_LEAF_ONLY) || \
    defined(OPEN_CFW_PRODUCT_RTOS_FIND_FREE_ONLY)
uint32_t open_cfw_product_rtos_find_free_slot(void)
{
    uint32_t index;
#pragma clang loop unroll(disable)
    for (index = 0U; index < OPEN_CFW_PRODUCT_RTOS_SLOT_COUNT; ++index) {
        if (OPEN_CFW_PRODUCT_RTOS_STATE.votes[index].handle == 0U) {
            return index;
        }
    }
    return OPEN_CFW_PRODUCT_RTOS_INVALID_SLOT;
}
#endif

#if !defined(OPEN_CFW_PRODUCT_RTOS_LEAF_ONLY) || \
    defined(OPEN_CFW_PRODUCT_RTOS_INIT_ONLY)
void open_cfw_product_rtos_init(void)
{
    OPEN_CFW_PRODUCT_RTOS_MEMSET(
        (void *)&OPEN_CFW_PRODUCT_RTOS_STATE,
        0,
        sizeof(OPEN_CFW_PRODUCT_RTOS_STATE)
    );
    OPEN_CFW_PRODUCT_RTOS_STATE.initialized = 1U;
    (void)OPEN_CFW_PRODUCT_RTOS_LOG(OPEN_CFW_PRODUCT_RTOS_INIT_MESSAGE);
}
#endif

#if !defined(OPEN_CFW_PRODUCT_RTOS_LEAF_ONLY) || \
    defined(OPEN_CFW_PRODUCT_RTOS_ACQUIRE_HANDLE_ONLY)
uint8_t open_cfw_product_rtos_acquire_for_handle(void *task_handle)
{
    uint32_t index;
    uint32_t primask;
    uint8_t acquired = 0U;

    if (OPEN_CFW_PRODUCT_RTOS_STATE.initialized == 0U || task_handle == NULL) {
        return 0U;
    }
    primask = OPEN_CFW_PRODUCT_RTOS_IRQ_SAVE_DISABLE();
    index = open_cfw_product_rtos_find_slot(task_handle);
    if (index != OPEN_CFW_PRODUCT_RTOS_INVALID_SLOT) {
        if (OPEN_CFW_PRODUCT_RTOS_STATE.votes[index].active == 0U) {
            OPEN_CFW_PRODUCT_RTOS_STATE.votes[index].active = 1U;
            ++OPEN_CFW_PRODUCT_RTOS_STATE.active_count;
            acquired = 1U;
        }
    } else {
        index = open_cfw_product_rtos_find_free_slot();
        if (index != OPEN_CFW_PRODUCT_RTOS_INVALID_SLOT) {
            OPEN_CFW_PRODUCT_RTOS_STATE.votes[index].handle =
                (uint32_t)(uintptr_t)task_handle;
            OPEN_CFW_PRODUCT_RTOS_STATE.votes[index].active = 1U;
            ++OPEN_CFW_PRODUCT_RTOS_STATE.active_count;
            acquired = 1U;
        }
    }
    OPEN_CFW_PRODUCT_RTOS_IRQ_RESTORE(primask);
    return acquired;
}
#endif

#if !defined(OPEN_CFW_PRODUCT_RTOS_LEAF_ONLY) || \
    defined(OPEN_CFW_PRODUCT_RTOS_RELEASE_HANDLE_ONLY)
uint8_t open_cfw_product_rtos_release_for_handle(void *task_handle)
{
    uint32_t index;
    uint32_t primask;
    uint8_t released = 0U;

    if (OPEN_CFW_PRODUCT_RTOS_STATE.initialized == 0U || task_handle == NULL) {
        return 0U;
    }
    primask = OPEN_CFW_PRODUCT_RTOS_IRQ_SAVE_DISABLE();
    index = open_cfw_product_rtos_find_slot(task_handle);
    if (index != OPEN_CFW_PRODUCT_RTOS_INVALID_SLOT &&
        OPEN_CFW_PRODUCT_RTOS_STATE.votes[index].active == 1U) {
        OPEN_CFW_PRODUCT_RTOS_STATE.votes[index].active = 0U;
        --OPEN_CFW_PRODUCT_RTOS_STATE.active_count;
        released = 1U;
    }
    OPEN_CFW_PRODUCT_RTOS_IRQ_RESTORE(primask);
    return released;
}
#endif

#if !defined(OPEN_CFW_PRODUCT_RTOS_LEAF_ONLY) || \
    defined(OPEN_CFW_PRODUCT_RTOS_BLOCKS_SLEEP_ONLY)
uint8_t open_cfw_product_rtos_blocks_deep_sleep(void)
{
    uint32_t primask;
    uint8_t blocked;
    if (OPEN_CFW_PRODUCT_RTOS_STATE.initialized == 0U) {
        return 0U;
    }
    primask = OPEN_CFW_PRODUCT_RTOS_IRQ_SAVE_DISABLE();
    blocked = OPEN_CFW_PRODUCT_RTOS_STATE.active_count != 0U ? 1U : 0U;
    OPEN_CFW_PRODUCT_RTOS_IRQ_RESTORE(primask);
    return blocked;
}
#endif

#if !defined(OPEN_CFW_PRODUCT_RTOS_LEAF_ONLY) || \
    defined(OPEN_CFW_PRODUCT_RTOS_ACQUIRE_CURRENT_ONLY)
void open_cfw_product_rtos_acquire_current(void)
{
    void *task = OPEN_CFW_PRODUCT_RTOS_CURRENT_THREAD();
    if (task != NULL) {
        (void)open_cfw_product_rtos_acquire_for_handle(task);
    }
}
#endif

#if !defined(OPEN_CFW_PRODUCT_RTOS_LEAF_ONLY) || \
    defined(OPEN_CFW_PRODUCT_RTOS_RELEASE_CURRENT_ONLY)
void open_cfw_product_rtos_release_current(void)
{
    void *task = OPEN_CFW_PRODUCT_RTOS_CURRENT_THREAD();
    if (task != NULL) {
        (void)open_cfw_product_rtos_release_for_handle(task);
    }
}
#endif

#if !defined(OPEN_CFW_PRODUCT_RTOS_LEAF_ONLY) || \
    defined(OPEN_CFW_PRODUCT_RTOS_SLEEP_ONLY)
uint32_t am_freertos_sleep(uint32_t expected_idle_time)
{
    (void)expected_idle_time;
    OPEN_CFW_PRODUCT_RTOS_WATCHDOG_FEED();
    (void)OPEN_CFW_PRODUCT_RTOS_SLEEP(
        open_cfw_product_rtos_blocks_deep_sleep() != 0U ? 0U : 1U
    );
    return 0U;
}
#endif

#if !defined(OPEN_CFW_PRODUCT_RTOS_LEAF_ONLY) || \
    defined(OPEN_CFW_PRODUCT_RTOS_WAKEUP_ONLY)
void am_freertos_wakeup(uint32_t slept_ticks)
{
    (void)slept_ticks;
    OPEN_CFW_PRODUCT_RTOS_WATCHDOG_FEED();
}
#endif

#if !defined(OPEN_CFW_PRODUCT_RTOS_LEAF_ONLY) || \
    defined(OPEN_CFW_PRODUCT_RTOS_MALLOC_FAILED_ONLY)
void vApplicationMallocFailedHook(void)
{
    (void)OPEN_CFW_PRODUCT_RTOS_LOG(OPEN_CFW_PRODUCT_RTOS_MALLOC_MESSAGE);
    OPEN_CFW_PRODUCT_RTOS_HALT(1U);
}
#endif

#if !defined(OPEN_CFW_PRODUCT_RTOS_LEAF_ONLY) || \
    defined(OPEN_CFW_PRODUCT_RTOS_STACK_OVERFLOW_ONLY)
void vApplicationStackOverflowHook(void *task, char *task_name)
{
    (void)task;
    (void)OPEN_CFW_PRODUCT_RTOS_LOG(
        OPEN_CFW_PRODUCT_RTOS_STACK_MESSAGE,
        task_name
    );
    OPEN_CFW_PRODUCT_RTOS_BREAK_HALT(2U);
}
#endif

#if !defined(OPEN_CFW_PRODUCT_RTOS_LEAF_ONLY) || \
    defined(OPEN_CFW_PRODUCT_RTOS_IDLE_ONLY)
void vApplicationIdleHook(void)
{
    OPEN_CFW_PRODUCT_RTOS_WATCHDOG_FEED();
}
#endif
