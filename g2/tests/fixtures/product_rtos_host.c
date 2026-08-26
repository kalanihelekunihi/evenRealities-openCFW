/* Host behavior oracle for the clean-room G2 product RTOS policy/hooks. */
#include <stdarg.h>
#include <stdint.h>
#include <string.h>

#define OPEN_CFW_PRODUCT_RTOS_TEST_HOST 1
#include "../../components/apollo_main/core_overlay/product_rtos.c"

open_cfw_product_rtos_state open_cfw_test_product_rtos_state;

static uint32_t test_irq_save_calls;
static uint32_t test_irq_restore_calls;
static uint32_t test_last_restored_primask;
static uint32_t test_watchdog_calls;
static uint32_t test_sleep_calls;
static uint32_t test_sleep_mode;
static uint32_t test_log_calls;
static uintptr_t test_last_format;
static const char *test_last_task_name;
static uint32_t test_fatal_reason;
static void *test_current_thread;

void *open_cfw_retained_product_rtos_memset(void *p, int value, size_t size)
{
    return memset(p, value, size);
}

uint32_t open_cfw_retained_product_rtos_irq_save_disable(void)
{
    ++test_irq_save_calls;
    return 0xA5000000U | test_irq_save_calls;
}

void open_cfw_test_product_rtos_irq_restore(uint32_t primask)
{
    ++test_irq_restore_calls;
    test_last_restored_primask = primask;
}

void *open_cfw_retained_product_rtos_current_thread(void)
{
    return test_current_thread;
}

uint32_t open_cfw_retained_product_rtos_sleep(uint32_t mode)
{
    ++test_sleep_calls;
    test_sleep_mode = mode;
    return 0U;
}

void open_cfw_retained_product_rtos_watchdog_feed(void)
{
    ++test_watchdog_calls;
}

int open_cfw_retained_product_rtos_log(const char *format, ...)
{
    va_list arguments;
    ++test_log_calls;
    test_last_format = (uintptr_t)format;
    test_last_task_name = NULL;
    va_start(arguments, format);
    if (test_last_format == (uintptr_t)OPEN_CFW_PRODUCT_RTOS_STACK_MESSAGE) {
        test_last_task_name = va_arg(arguments, const char *);
    }
    va_end(arguments);
    return 0;
}

void open_cfw_test_product_rtos_fatal(uint32_t reason)
{
    test_fatal_reason = reason;
}

static void test_reset(void)
{
    memset(&open_cfw_test_product_rtos_state, 0xA5,
           sizeof(open_cfw_test_product_rtos_state));
    test_irq_save_calls = 0U;
    test_irq_restore_calls = 0U;
    test_last_restored_primask = 0U;
    test_watchdog_calls = 0U;
    test_sleep_calls = 0U;
    test_sleep_mode = UINT32_MAX;
    test_log_calls = 0U;
    test_last_format = 0U;
    test_last_task_name = NULL;
    test_fatal_reason = 0U;
    test_current_thread = NULL;
}

uint32_t open_cfw_test_product_rtos_init_scenario(void)
{
    const uint8_t *bytes;
    uint32_t zero_count = 0U;
    uint32_t index;
    uint32_t result = 0U;
    test_reset();
    open_cfw_product_rtos_init();
    bytes = (const uint8_t *)&open_cfw_test_product_rtos_state;
    for (index = 0U; index < sizeof(open_cfw_test_product_rtos_state); ++index) {
        if (index == offsetof(open_cfw_product_rtos_state, initialized)) {
            continue;
        }
        zero_count += bytes[index] == 0U ? 1U : 0U;
    }
    result |= open_cfw_test_product_rtos_state.initialized == 1U ? 1U : 0U;
    result |= zero_count == sizeof(open_cfw_test_product_rtos_state) - 1U
        ? 2U : 0U;
    result |= test_log_calls == 1U ? 4U : 0U;
    result |= test_last_format == (uintptr_t)OPEN_CFW_PRODUCT_RTOS_INIT_MESSAGE
        ? 8U : 0U;
    return result;
}

uint32_t open_cfw_test_product_rtos_vote_scenario(void)
{
    void *first = (void *)(uintptr_t)0x1001U;
    void *second = (void *)(uintptr_t)0x2002U;
    uint32_t result = 0U;
    test_reset();
    result |= open_cfw_product_rtos_acquire_for_handle(first) == 0U ? 1U : 0U;
    open_cfw_product_rtos_init();
    result |= open_cfw_product_rtos_acquire_for_handle(NULL) == 0U ? 2U : 0U;
    result |= open_cfw_product_rtos_acquire_for_handle(first) == 1U ? 4U : 0U;
    result |= open_cfw_product_rtos_acquire_for_handle(first) == 0U ? 8U : 0U;
    result |= open_cfw_product_rtos_acquire_for_handle(second) == 1U ? 16U : 0U;
    result |= open_cfw_test_product_rtos_state.active_count == 2U ? 32U : 0U;
    result |= open_cfw_product_rtos_release_for_handle(first) == 1U ? 64U : 0U;
    result |= open_cfw_product_rtos_release_for_handle(first) == 0U ? 128U : 0U;
    result |= open_cfw_test_product_rtos_state.votes[0].handle == 0x1001U &&
        open_cfw_test_product_rtos_state.votes[0].active == 0U ? 256U : 0U;
    result |= open_cfw_product_rtos_acquire_for_handle(first) == 1U ? 512U : 0U;
    result |= test_irq_save_calls == 7U && test_irq_restore_calls == 7U &&
        test_last_restored_primask == 0xA5000007U ? 1024U : 0U;
    return result;
}

uint32_t open_cfw_test_product_rtos_capacity_scenario(void)
{
    uint32_t index;
    uint32_t result = 0U;
    test_reset();
    open_cfw_product_rtos_init();
    for (index = 0U; index < OPEN_CFW_PRODUCT_RTOS_SLOT_COUNT; ++index) {
        result += open_cfw_product_rtos_acquire_for_handle(
            (void *)(uintptr_t)(index + 1U)
        );
    }
    return
        (result == OPEN_CFW_PRODUCT_RTOS_SLOT_COUNT ? 1U : 0U) |
        (open_cfw_product_rtos_find_free_slot() == UINT32_MAX ? 2U : 0U) |
        (open_cfw_product_rtos_acquire_for_handle(
            (void *)(uintptr_t)0x100U) == 0U ? 4U : 0U) |
        (open_cfw_test_product_rtos_state.active_count == 32U ? 8U : 0U);
}

uint32_t open_cfw_test_product_rtos_current_scenario(void)
{
    uint32_t result = 0U;
    test_reset();
    open_cfw_product_rtos_init();
    open_cfw_product_rtos_acquire_current();
    result |= open_cfw_test_product_rtos_state.active_count == 0U ? 1U : 0U;
    test_current_thread = (void *)(uintptr_t)0x3344U;
    open_cfw_product_rtos_acquire_current();
    result |= open_cfw_test_product_rtos_state.active_count == 1U ? 2U : 0U;
    open_cfw_product_rtos_release_current();
    result |= open_cfw_test_product_rtos_state.active_count == 0U ? 4U : 0U;
    return result;
}

uint32_t open_cfw_test_product_rtos_power_scenario(void)
{
    uint32_t result = 0U;
    test_reset();
    open_cfw_product_rtos_init();
    result |= open_cfw_product_rtos_blocks_deep_sleep() == 0U ? 1U : 0U;
    result |= am_freertos_sleep(1000U) == 0U && test_sleep_mode == 1U
        ? 2U : 0U;
    (void)open_cfw_product_rtos_acquire_for_handle(
        (void *)(uintptr_t)0x55U
    );
    result |= open_cfw_product_rtos_blocks_deep_sleep() == 1U ? 4U : 0U;
    result |= am_freertos_sleep(1000U) == 0U && test_sleep_mode == 0U
        ? 8U : 0U;
    am_freertos_wakeup(1U);
    vApplicationIdleHook();
    result |= test_watchdog_calls == 4U ? 16U : 0U;
    result |= test_sleep_calls == 2U ? 32U : 0U;
    return result;
}

uint32_t open_cfw_test_product_rtos_fatal_scenario(void)
{
    uint32_t result = 0U;
    char name[] = "overflow-task";
    test_reset();
    vApplicationMallocFailedHook();
    result |= test_fatal_reason == 1U ? 1U : 0U;
    result |= test_last_format == (uintptr_t)OPEN_CFW_PRODUCT_RTOS_MALLOC_MESSAGE
        ? 2U : 0U;
    vApplicationStackOverflowHook((void *)(uintptr_t)0x99U, name);
    result |= test_fatal_reason == 2U ? 4U : 0U;
    result |= test_last_format == (uintptr_t)OPEN_CFW_PRODUCT_RTOS_STACK_MESSAGE
        ? 8U : 0U;
    result |= test_last_task_name == name ? 16U : 0U;
    result |= test_log_calls == 2U ? 32U : 0U;
    return result;
}
