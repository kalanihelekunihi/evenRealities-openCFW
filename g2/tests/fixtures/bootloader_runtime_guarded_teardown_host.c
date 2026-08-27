#include <stdint.h>

#define OPEN_CFW_GUARDED_TEARDOWN_HOST 1

static uint8_t fixture_guard;
static uint32_t fixture_pin_config;
static uint32_t fixture_stage_one_result;
static uint32_t fixture_stage_two_result;
static uint32_t fixture_stage_one_calls;
static uint32_t fixture_stage_two_calls;
static uint32_t fixture_store_calls;
static uint32_t fixture_store_value;
static uint32_t fixture_pin_calls;
static uint32_t fixture_pin;
static uint32_t fixture_pin_value;
static uint32_t fixture_fail_stage;

uint8_t *open_cfw_guarded_teardown_host_guard(void)
{
    return &fixture_guard;
}

const uint32_t *open_cfw_guarded_teardown_host_pin_config(void)
{
    return &fixture_pin_config;
}

uint32_t open_cfw_guarded_teardown_host_stage_one(void)
{
    ++fixture_stage_one_calls;
    return fixture_stage_one_result;
}

uint32_t open_cfw_guarded_teardown_host_stage_two(void)
{
    ++fixture_stage_two_calls;
    return fixture_stage_two_result;
}

void open_cfw_guarded_teardown_host_store_state(uint32_t value)
{
    ++fixture_store_calls;
    fixture_store_value = value;
}

uint32_t open_cfw_guarded_teardown_host_configure_pin(
    uint32_t pin,
    uint32_t configuration)
{
    ++fixture_pin_calls;
    fixture_pin = pin;
    fixture_pin_value = configuration;
    return 0U;
}

void open_cfw_guarded_teardown_host_fail_stop(uint32_t stage)
{
    fixture_fail_stage = stage;
}

#include "../../components/bootloader/core_overlay/runtime_guarded_teardown_41fa98.c"

static void reset(uint8_t guard, uint32_t first, uint32_t second)
{
    fixture_guard = guard;
    fixture_pin_config = 0xA5C33C5AU;
    fixture_stage_one_result = first;
    fixture_stage_two_result = second;
    fixture_stage_one_calls = 0U;
    fixture_stage_two_calls = 0U;
    fixture_store_calls = 0U;
    fixture_store_value = 0xFFFFFFFFU;
    fixture_pin_calls = 0U;
    fixture_pin = 0U;
    fixture_pin_value = 0U;
    fixture_fail_stage = 0U;
}

uint32_t open_cfw_test_guarded_teardown_inactive(void)
{
    reset(0U, 0U, 0U);
    open_cfw_bootloader_guarded_teardown_41fa98();
    if (fixture_stage_one_calls != 0U || fixture_stage_two_calls != 0U ||
        fixture_store_calls != 0U || fixture_pin_calls != 0U ||
        fixture_guard != 0U) {
        return 0U;
    }
    reset(2U, 0U, 0U);
    open_cfw_bootloader_guarded_teardown_41fa98();
    return fixture_stage_one_calls == 0U && fixture_guard == 2U;
}

uint32_t open_cfw_test_guarded_teardown_stage_one_failure(void)
{
    reset(1U, 7U, 0U);
    open_cfw_bootloader_guarded_teardown_41fa98();
    return fixture_stage_one_calls == 1U && fixture_stage_two_calls == 0U &&
        fixture_store_calls == 0U && fixture_pin_calls == 0U &&
        fixture_fail_stage == 1U && fixture_guard == 1U;
}

uint32_t open_cfw_test_guarded_teardown_stage_two_failure(void)
{
    reset(1U, 0U, 9U);
    open_cfw_bootloader_guarded_teardown_41fa98();
    return fixture_stage_one_calls == 1U && fixture_stage_two_calls == 1U &&
        fixture_store_calls == 0U && fixture_pin_calls == 0U &&
        fixture_fail_stage == 2U && fixture_guard == 1U;
}

uint32_t open_cfw_test_guarded_teardown_success(void)
{
    reset(1U, 0U, 0U);
    open_cfw_bootloader_guarded_teardown_41fa98();
    return fixture_stage_one_calls == 1U && fixture_stage_two_calls == 1U &&
        fixture_store_calls == 1U && fixture_store_value == 0U &&
        fixture_pin_calls == 1U && fixture_pin == 0x1CU &&
        fixture_pin_value == 0xA5C33C5AU && fixture_fail_stage == 0U &&
        fixture_guard == 0U;
}
