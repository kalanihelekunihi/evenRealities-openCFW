#include <stddef.h>
#include <stdint.h>

static uint8_t open_cfw_active[8];
static uint8_t open_cfw_scan_result[6];
static uint32_t open_cfw_scan_status;
static uint32_t open_cfw_scan_count;
static uint32_t open_cfw_log_count;
static uint32_t open_cfw_log[12];

#define OPEN_CFW_MSPI_TIMING_AUTO_HOST 1
#include "../../components/bootloader/core_overlay/runtime_mspi_timing_auto_4201ba.c"

open_cfw_timing_auto_u8 *open_cfw_mspi_timing_auto_host_active(void)
{
    return open_cfw_active;
}

open_cfw_timing_auto_u32 open_cfw_mspi_timing_auto_host_scan(
    open_cfw_timing_auto_u8 *result)
{
    size_t index;
    ++open_cfw_scan_count;
    for (index = 0U; index < 6U; ++index) {
        result[index] = open_cfw_scan_result[index];
    }
    return open_cfw_scan_status;
}

void open_cfw_mspi_timing_auto_host_log(
    open_cfw_timing_auto_u32 level,
    open_cfw_timing_auto_u32 line,
    open_cfw_timing_auto_u32 format,
    open_cfw_timing_auto_u32 value0,
    open_cfw_timing_auto_u32 value1,
    open_cfw_timing_auto_u32 value2,
    open_cfw_timing_auto_u32 value3,
    open_cfw_timing_auto_u32 value4,
    open_cfw_timing_auto_u32 value5,
    open_cfw_timing_auto_u32 unused0,
    open_cfw_timing_auto_u32 unused1,
    open_cfw_timing_auto_u32 argument_count)
{
    open_cfw_log[0] = level;
    open_cfw_log[1] = line;
    open_cfw_log[2] = format;
    open_cfw_log[3] = value0;
    open_cfw_log[4] = value1;
    open_cfw_log[5] = value2;
    open_cfw_log[6] = value3;
    open_cfw_log[7] = value4;
    open_cfw_log[8] = value5;
    open_cfw_log[9] = unused0;
    open_cfw_log[10] = unused1;
    open_cfw_log[11] = argument_count;
    ++open_cfw_log_count;
}

void open_cfw_mspi_timing_auto_fixture_reset(void)
{
    size_t index;
    for (index = 0U; index < 8U; ++index) {
        open_cfw_active[index] = (uint8_t)(0xA0U + index);
    }
    for (index = 0U; index < 6U; ++index) {
        open_cfw_scan_result[index] = (uint8_t)(0x10U + index);
    }
    open_cfw_scan_status = 0U;
    open_cfw_scan_count = 0U;
    open_cfw_log_count = 0U;
    for (index = 0U; index < 12U; ++index) {
        open_cfw_log[index] = 0U;
    }
}

void open_cfw_mspi_timing_auto_fixture_set_status(uint32_t status)
{
    open_cfw_scan_status = status;
}

void open_cfw_mspi_timing_auto_fixture_set_result(size_t index, uint32_t value)
{
    if (index < 6U) {
        open_cfw_scan_result[index] = (uint8_t)value;
    }
}

void open_cfw_mspi_timing_auto_fixture_run(void)
{
    open_cfw_bootloader_mspi_timing_auto_4201ba();
}

uint32_t open_cfw_mspi_timing_auto_fixture_active(size_t index)
{
    return index < 8U ? open_cfw_active[index] : 0U;
}

uint32_t open_cfw_mspi_timing_auto_fixture_scan_count(void)
{
    return open_cfw_scan_count;
}

uint32_t open_cfw_mspi_timing_auto_fixture_log_count(void)
{
    return open_cfw_log_count;
}

uint32_t open_cfw_mspi_timing_auto_fixture_log(size_t index)
{
    return index < 12U ? open_cfw_log[index] : 0U;
}
