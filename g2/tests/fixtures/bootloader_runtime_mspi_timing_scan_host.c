#include <stddef.h>
#include <stdint.h>

#define OPEN_CFW_MSPI_TIMING_SCAN_HOST 1
#include "../../components/bootloader/core_overlay/runtime_bit_run_helpers_41ff60.c"
#include "../../components/bootloader/core_overlay/runtime_mspi_timing_scan_420002.c"

static uint8_t timing_table[36U * 6U];
static uint32_t requested_masks[36U];
static uint8_t active_configuration[6U];
static size_t control_count;
static size_t read_count;
static size_t log_count;
static uintptr_t logs[3U][12U];

void open_cfw_mspi_timing_scan_fixture_reset(void)
{
    size_t row;
    size_t column;
    for (row = 0U; row < 36U; ++row) {
        timing_table[row * 6U + 0U] = 1U;
        timing_table[row * 6U + 1U] = (uint8_t)(row / 18U);
        timing_table[row * 6U + 2U] = (uint8_t)((row / 9U) & 1U);
        timing_table[row * 6U + 3U] = (uint8_t)((row % 9U) + 1U);
        timing_table[row * 6U + 4U] = 1U;
        timing_table[row * 6U + 5U] = 32U;
        requested_masks[row] = 0U;
    }
    for (column = 0U; column < 6U; ++column) {
        active_configuration[column] = 0U;
    }
    for (row = 0U; row < 3U; ++row) {
        for (column = 0U; column < 12U; ++column) {
            logs[row][column] = 0U;
        }
    }
    control_count = 0U;
    read_count = 0U;
    log_count = 0U;
}

void open_cfw_mspi_timing_scan_fixture_set_mask(uint32_t row, uint32_t mask)
{
    if (row < 36U) {
        requested_masks[row] = mask;
    }
}

const uint8_t *open_cfw_mspi_timing_scan_host_table(void)
{
    return timing_table;
}

void *open_cfw_mspi_timing_scan_host_handle(void)
{
    return (void *)(uintptr_t)0x2468U;
}

uint32_t open_cfw_mspi_timing_scan_host_control(
    void *handle,
    uint32_t request,
    void *configuration)
{
    const uint8_t *bytes = (const uint8_t *)configuration;
    size_t index;
    (void)handle;
    (void)request;
    for (index = 0U; index < 6U; ++index) {
        active_configuration[index] = bytes[index];
    }
    ++control_count;
    return 0xFFFFFFFFU;
}

uint32_t open_cfw_mspi_timing_scan_host_read_id(uint32_t *identifier)
{
    size_t row;
    ++read_count;
    for (row = 0U; row < 36U; ++row) {
        if (active_configuration[0] == timing_table[row * 6U + 0U] &&
            active_configuration[1] == timing_table[row * 6U + 1U] &&
            active_configuration[2] == timing_table[row * 6U + 2U] &&
            active_configuration[3] == timing_table[row * 6U + 3U]) {
            *identifier =
                (requested_masks[row] & (1UL << active_configuration[4])) != 0U
                    ? 0x002539C2U
                    : 0U;
            return 0U;
        }
    }
    *identifier = 0U;
    return 1U;
}

void open_cfw_mspi_timing_scan_host_log(
    uint32_t line,
    uint32_t format,
    uint32_t a0,
    uint32_t a1,
    uint32_t a2,
    uint32_t a3,
    uint32_t a4,
    uint32_t a5,
    uint32_t a6,
    uint32_t a7,
    uint32_t a8,
    uint32_t count)
{
    const uint32_t values[12U] = {
        line, format, a0, a1, a2, a3, a4, a5, a6, a7, a8, count
    };
    size_t index;
    if (log_count < 3U) {
        for (index = 0U; index < 12U; ++index) {
            logs[log_count][index] = values[index];
        }
    }
    ++log_count;
}

uint32_t open_cfw_mspi_timing_scan_fixture_run(uint8_t *result)
{
    return open_cfw_bootloader_mspi_timing_scan_420002(result);
}

size_t open_cfw_mspi_timing_scan_fixture_control_count(void)
{
    return control_count;
}

size_t open_cfw_mspi_timing_scan_fixture_read_count(void)
{
    return read_count;
}

size_t open_cfw_mspi_timing_scan_fixture_log_count(void)
{
    return log_count;
}

uintptr_t open_cfw_mspi_timing_scan_fixture_log(size_t record, size_t field)
{
    return record < 3U && field < 12U ? logs[record][field] : 0U;
}

uint32_t open_cfw_mspi_timing_scan_fixture_table_byte(
    uint32_t row,
    uint32_t column)
{
    return row < 36U && column < 6U
        ? timing_table[row * 6U + column]
        : 0U;
}
