/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Host substitutions for the wrap-extending monotonic-seconds helper.
 */

unsigned int open_cfw_test_monotonic_last_tick;
unsigned int open_cfw_test_monotonic_wrap_count;
unsigned int open_cfw_test_monotonic_tick_result;
unsigned int open_cfw_test_monotonic_prior_primask;
unsigned int open_cfw_test_monotonic_restored_primask;
unsigned int open_cfw_test_monotonic_irq_disable_calls;
unsigned int open_cfw_test_monotonic_irq_restore_calls;
unsigned int open_cfw_test_monotonic_tick_calls;
unsigned int open_cfw_test_monotonic_divmod_calls;
unsigned int open_cfw_test_monotonic_dividend_low;
unsigned int open_cfw_test_monotonic_dividend_high;
unsigned int open_cfw_test_monotonic_divisor_low;
unsigned int open_cfw_test_monotonic_divisor_high;
unsigned int open_cfw_test_monotonic_trace[8];
unsigned int open_cfw_test_monotonic_trace_count;

static void open_cfw_test_monotonic_record(unsigned int event)
{
    open_cfw_test_monotonic_trace[
        open_cfw_test_monotonic_trace_count
    ] = event;
    open_cfw_test_monotonic_trace_count += 1U;
}

static unsigned int open_cfw_test_monotonic_tick_get(void)
{
    open_cfw_test_monotonic_tick_calls += 1U;
    open_cfw_test_monotonic_record(2U);
    return open_cfw_test_monotonic_tick_result;
}

static unsigned int open_cfw_test_monotonic_irq_disable(void)
{
    open_cfw_test_monotonic_irq_disable_calls += 1U;
    open_cfw_test_monotonic_record(1U);
    return open_cfw_test_monotonic_prior_primask;
}

static void open_cfw_test_monotonic_irq_restore(unsigned int primask)
{
    open_cfw_test_monotonic_irq_restore_calls += 1U;
    open_cfw_test_monotonic_restored_primask = primask;
    open_cfw_test_monotonic_record(3U);
}

#define OPEN_CFW_MONOTONIC_TICK_GET() \
    open_cfw_test_monotonic_tick_get()
#define OPEN_CFW_MONOTONIC_LAST_TICK \
    open_cfw_test_monotonic_last_tick
#define OPEN_CFW_MONOTONIC_WRAP_COUNT \
    open_cfw_test_monotonic_wrap_count
#define OPEN_CFW_MONOTONIC_IRQ_DISABLE() \
    open_cfw_test_monotonic_irq_disable()
#define OPEN_CFW_MONOTONIC_IRQ_RESTORE(primask) \
    open_cfw_test_monotonic_irq_restore(primask)

#include "../../components/apollo_main/core_overlay/monotonic_time.c"

void open_cfw_aeabi_uldivmod_core(
    unsigned int dividend_low,
    unsigned int dividend_high,
    unsigned int divisor_low,
    unsigned int divisor_high,
    struct open_cfw_aeabi_divmod_result *result
)
{
    unsigned int *result_words = (unsigned int *)(void *)result;
    unsigned long long dividend =
        ((unsigned long long)dividend_high << 32U) | dividend_low;
    unsigned long long divisor =
        ((unsigned long long)divisor_high << 32U) | divisor_low;
    unsigned long long quotient = dividend / divisor;
    unsigned long long remainder = dividend % divisor;

    open_cfw_test_monotonic_divmod_calls += 1U;
    open_cfw_test_monotonic_dividend_low = dividend_low;
    open_cfw_test_monotonic_dividend_high = dividend_high;
    open_cfw_test_monotonic_divisor_low = divisor_low;
    open_cfw_test_monotonic_divisor_high = divisor_high;
    open_cfw_test_monotonic_record(4U);
    result_words[0] = (unsigned int)quotient;
    result_words[1] = (unsigned int)(quotient >> 32U);
    result_words[2] = (unsigned int)remainder;
    result_words[3] = (unsigned int)(remainder >> 32U);
}
