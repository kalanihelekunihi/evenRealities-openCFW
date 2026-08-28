/* SPDX-License-Identifier: MIT */

#include <stdint.h>

static volatile uint8_t *open_cfw_poll_fixture_active;
static uint32_t open_cfw_poll_fixture_calls;
static uint32_t open_cfw_poll_fixture_last_duration;
static uint32_t open_cfw_poll_fixture_clear_after;

void open_cfw_poll_host_delay(uint32_t duration)
{
    open_cfw_poll_fixture_calls += 1U;
    open_cfw_poll_fixture_last_duration = duration;
    if (open_cfw_poll_fixture_clear_after != 0U &&
        open_cfw_poll_fixture_calls >= open_cfw_poll_fixture_clear_after) {
        *open_cfw_poll_fixture_active = 0U;
    }
}

#include "../../components/bootloader/core_overlay/runtime_poll_delay_4216b2.c"

void open_cfw_poll_fixture_reset(
    volatile uint8_t *active, uint32_t clear_after)
{
    open_cfw_poll_fixture_active = active;
    open_cfw_poll_fixture_calls = 0U;
    open_cfw_poll_fixture_last_duration = 0U;
    open_cfw_poll_fixture_clear_after = clear_after;
}

uint32_t open_cfw_poll_fixture_calls_get(void)
{
    return open_cfw_poll_fixture_calls;
}

uint32_t open_cfw_poll_fixture_last_duration_get(void)
{
    return open_cfw_poll_fixture_last_duration;
}
