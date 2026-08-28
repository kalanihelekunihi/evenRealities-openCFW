/* SPDX-License-Identifier: MIT */
#include "runtime_bootloader_mspi_cq_pause_candidate.h"

enum {
    MODE_DISABLED = 0,
    MODE_PAUSED = 1,
    MODE_DELAY_THEN_DISABLED = 2,
    MODE_TIMEOUT = 3,
};

static uint32_t fixture_mode;
static uint32_t fixture_status;
static uint32_t fixture_delay_limit;
static uint32_t fixture_reads;
static uint32_t fixture_writes;
static uint32_t fixture_delays;
static uint32_t fixture_status_calls;
static uint32_t fixture_write_address;
static uint32_t fixture_write_value;
static uint32_t fixture_status_timeout;
static uint32_t fixture_status_address;
static uint32_t fixture_status_mask;
static uint32_t fixture_status_value;
static uint32_t fixture_status_not_equal;

static uint32_t fixture_read(void *context, uint32_t address)
{
    uint32_t offset = address & 0xFFFU;
    (void)context;
    fixture_reads++;
    if (offset == 0x2A0U) {
        if (fixture_mode == MODE_DISABLED) return 0U;
        if (fixture_mode == MODE_DELAY_THEN_DISABLED &&
            fixture_delays >= fixture_delay_limit) return 0U;
        return 1U;
    }
    if (offset == 0x2ACU) return fixture_mode == MODE_PAUSED ? 8U : 0U;
    if (offset == 0x2B8U) return fixture_mode == MODE_PAUSED ? 0x80U : 0U;
    return 0U;
}

static void fixture_write(void *context, uint32_t address, uint32_t value)
{
    (void)context;
    fixture_writes++;
    fixture_write_address = address;
    fixture_write_value = value;
}

static void fixture_delay(void *context, uint32_t microseconds)
{
    (void)context;
    if (microseconds == 1U) fixture_delays++;
}

static uint32_t fixture_status_check(
    void *context, uint32_t timeout, uint32_t address, uint32_t mask,
    uint32_t value, uint32_t not_equal)
{
    (void)context;
    fixture_status_calls++;
    fixture_status_timeout = timeout;
    fixture_status_address = address;
    fixture_status_mask = mask;
    fixture_status_value = value;
    fixture_status_not_equal = not_equal;
    return fixture_status;
}

void open_cfw_test_mspi_cq_pause_reset(uint32_t mode, uint32_t status,
                                       uint32_t delay_limit)
{
    fixture_mode = mode;
    fixture_status = status;
    fixture_delay_limit = delay_limit;
    fixture_reads = fixture_writes = fixture_delays = fixture_status_calls = 0U;
    fixture_write_address = fixture_write_value = 0U;
    fixture_status_timeout = fixture_status_address = 0U;
    fixture_status_mask = fixture_status_value = fixture_status_not_equal = 0U;
}

uint32_t open_cfw_test_mspi_cq_pause_run(uint32_t module)
{
    open_cfw_mspi_cq_pause_context instance = {0U, module};
    const open_cfw_mspi_cq_pause_ports ports = {
        0, fixture_read, fixture_write, fixture_delay, fixture_status_check,
    };
    return open_cfw_bootloader_mspi_cq_pause_423fb8(&instance, &ports);
}

uint32_t open_cfw_test_mspi_cq_pause_value(uint32_t index)
{
    const uint32_t values[] = {
        fixture_reads, fixture_writes, fixture_delays, fixture_status_calls,
        fixture_write_address, fixture_write_value, fixture_status_timeout,
        fixture_status_address, fixture_status_mask, fixture_status_value,
        fixture_status_not_equal,
    };
    return index < sizeof(values) / sizeof(values[0]) ? values[index] : 0U;
}
