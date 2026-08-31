/* SPDX-License-Identifier: MIT */
#include "../../third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_apollo_hal_provider.h"

#include <stddef.h>
#include <stdint.h>

#define TEST_CLEAN_RESULT       0xA1000001U
#define TEST_INVALIDATE_RESULT  0xA1000002U
#define TEST_ENABLE_RESULT      0xA1000003U
#define TEST_DISABLE_RESULT     0xA1000004U
#define TEST_ENABLED_RESULT     0xA1000005U

static uint32_t clean_calls;
static uint32_t invalidate_calls;
static uint32_t enable_calls;
static uint32_t disable_calls;
static uint32_t enabled_calls;
static const am_hal_cachectrl_range_t *last_cache_range;
static uint32_t last_cache_start;
static uint32_t last_cache_size;
static uint32_t last_clean_selector;
static uint32_t last_enable_peripheral;
static uint32_t last_disable_peripheral;
static uint32_t last_enabled_peripheral;
static uint8_t *last_enabled_pointer;
static uint8_t requested_enabled_value;
static uint8_t enabled_output;
static uint8_t *expected_enabled_pointer;

uint32_t open_cfw_cache_dcache_clean(const am_hal_cachectrl_range_t *range)
{
    ++clean_calls;
    last_cache_range = range;
    if (range != NULL) {
        last_cache_start = range->ui32StartAddr;
        last_cache_size = range->ui32Size;
    }
    return TEST_CLEAN_RESULT;
}

uint32_t open_cfw_cache_dcache_invalidate(
    const am_hal_cachectrl_range_t *range,
    uint32_t clean
)
{
    ++invalidate_calls;
    last_cache_range = range;
    last_clean_selector = clean;
    if (range != NULL) {
        last_cache_start = range->ui32StartAddr;
        last_cache_size = range->ui32Size;
    }
    return TEST_INVALIDATE_RESULT;
}

uint32_t open_cfw_pwrctrl_periph_enable(uint32_t peripheral)
{
    ++enable_calls;
    last_enable_peripheral = peripheral;
    return TEST_ENABLE_RESULT;
}

uint32_t open_cfw_pwrctrl_periph_disable(uint32_t peripheral)
{
    ++disable_calls;
    last_disable_peripheral = peripheral;
    return TEST_DISABLE_RESULT;
}

uint32_t open_cfw_pwrctrl_periph_enabled(uint32_t peripheral, uint8_t *enabled)
{
    ++enabled_calls;
    last_enabled_peripheral = peripheral;
    last_enabled_pointer = enabled;
    if (enabled != NULL) {
        *enabled = requested_enabled_value;
    }
    return TEST_ENABLED_RESULT;
}

void test_apollo_hal_reset(void)
{
    clean_calls = 0U;
    invalidate_calls = 0U;
    enable_calls = 0U;
    disable_calls = 0U;
    enabled_calls = 0U;
    last_cache_range = NULL;
    last_cache_start = 0U;
    last_cache_size = 0U;
    last_clean_selector = 0xFFFFFFFFU;
    last_enable_peripheral = 0U;
    last_disable_peripheral = 0U;
    last_enabled_peripheral = 0U;
    last_enabled_pointer = NULL;
    requested_enabled_value = 0U;
    enabled_output = 0U;
    expected_enabled_pointer = NULL;
}

uint32_t test_apollo_hal_clean(uint32_t start, uint32_t size, uint32_t null_range)
{
    am_hal_cachectrl_range_t range = {start, size};
    return am_hal_cachectrl_dcache_clean(null_range != 0U ? NULL : &range);
}

uint32_t test_apollo_hal_invalidate(
    uint32_t start,
    uint32_t size,
    uint32_t clean,
    uint32_t null_range
)
{
    am_hal_cachectrl_range_t range = {start, size};
    return am_hal_cachectrl_dcache_invalidate(
        null_range != 0U ? NULL : &range,
        clean != 0U
    );
}

uint32_t test_apollo_hal_enable(uint32_t peripheral)
{
    return am_hal_pwrctrl_periph_enable((am_hal_pwrctrl_periph_e)peripheral);
}

uint32_t test_apollo_hal_disable(uint32_t peripheral)
{
    return am_hal_pwrctrl_periph_disable((am_hal_pwrctrl_periph_e)peripheral);
}

uint32_t test_apollo_hal_enabled(
    uint32_t peripheral,
    uint32_t value,
    uint32_t null_output
)
{
    enabled_output = 0x5AU;
    requested_enabled_value = value != 0U ? 1U : 0U;
    expected_enabled_pointer = null_output != 0U ? NULL : &enabled_output;
    return am_hal_pwrctrl_periph_enabled(
        (am_hal_pwrctrl_periph_e)peripheral,
        (bool *)expected_enabled_pointer
    );
}

uint32_t test_apollo_hal_clean_calls(void) { return clean_calls; }
uint32_t test_apollo_hal_invalidate_calls(void) { return invalidate_calls; }
uint32_t test_apollo_hal_enable_calls(void) { return enable_calls; }
uint32_t test_apollo_hal_disable_calls(void) { return disable_calls; }
uint32_t test_apollo_hal_enabled_calls(void) { return enabled_calls; }
uint32_t test_apollo_hal_cache_pointer_is_null(void) { return last_cache_range == NULL; }
uint32_t test_apollo_hal_last_cache_start(void) { return last_cache_start; }
uint32_t test_apollo_hal_last_cache_size(void) { return last_cache_size; }
uint32_t test_apollo_hal_last_clean_selector(void) { return last_clean_selector; }
uint32_t test_apollo_hal_last_enable_peripheral(void) { return last_enable_peripheral; }
uint32_t test_apollo_hal_last_disable_peripheral(void) { return last_disable_peripheral; }
uint32_t test_apollo_hal_last_enabled_peripheral(void) { return last_enabled_peripheral; }
uint32_t test_apollo_hal_enabled_pointer_is_exact(void)
{
    return last_enabled_pointer == expected_enabled_pointer;
}
uint32_t test_apollo_hal_enabled_output(void) { return enabled_output; }

