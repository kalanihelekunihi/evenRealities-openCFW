#include <stdint.h>

enum {
    OPEN_CFW_TEST_MEMORY_ROM_WRITE = 1,
    OPEN_CFW_TEST_MEMORY_READ_STATUS = 2,
    OPEN_CFW_TEST_MEMORY_READ_FORCE = 3,
    OPEN_CFW_TEST_MEMORY_WRITE_FORCE = 4,
    OPEN_CFW_TEST_MEMORY_READ_ENABLE = 5,
    OPEN_CFW_TEST_MEMORY_WRITE_ENABLE = 6,
    OPEN_CFW_TEST_MEMORY_DELAY_STATUS = 7,
    OPEN_CFW_TEST_MEMORY_SPOT_UPDATE = 8,
    OPEN_CFW_TEST_MEMORY_READ_DEVICE_STATUS = 9,
    OPEN_CFW_TEST_MEMORY_READ_DEVICE_ENABLE = 10,
    OPEN_CFW_TEST_MEMORY_READ_RETENTION = 11,
    OPEN_CFW_TEST_MEMORY_WRITE_RETENTION = 12
};

unsigned int open_cfw_test_memory_enable;
unsigned int open_cfw_test_memory_status;
unsigned int open_cfw_test_memory_retention;
unsigned int open_cfw_test_memory_device_enable;
unsigned int open_cfw_test_memory_device_status;
unsigned int open_cfw_test_memory_force_axi_clock;
unsigned int open_cfw_test_memory_current_rom_mode;
unsigned int open_cfw_test_memory_delay_result[2];
unsigned int open_cfw_test_memory_delay_updates_status;
unsigned int open_cfw_test_memory_delay_calls;
unsigned int open_cfw_test_memory_delay_maximum[2];
unsigned int open_cfw_test_memory_delay_address[2];
unsigned int open_cfw_test_memory_delay_mask[2];
unsigned int open_cfw_test_memory_delay_expected[2];
unsigned int open_cfw_test_memory_delay_wait[2];
unsigned int open_cfw_test_memory_spot_result;
unsigned int open_cfw_test_memory_spot_calls;
unsigned int open_cfw_test_memory_spot_stimulus;
unsigned int open_cfw_test_memory_spot_enabled;
unsigned int open_cfw_test_memory_spot_value;
unsigned int open_cfw_test_memory_trace_count;
unsigned int open_cfw_test_memory_trace_event[64];
unsigned int open_cfw_test_memory_trace_value[64];

static void
open_cfw_test_memory_trace(unsigned int event, unsigned int value)
{
    unsigned int index = open_cfw_test_memory_trace_count++;

    if (index < 64U) {
        open_cfw_test_memory_trace_event[index] = event;
        open_cfw_test_memory_trace_value[index] = value;
    }
}

void open_cfw_test_memory_reset(void)
{
    unsigned int index;

    open_cfw_test_memory_enable = 0U;
    open_cfw_test_memory_status = 0U;
    open_cfw_test_memory_retention = 0U;
    open_cfw_test_memory_device_enable = 0U;
    open_cfw_test_memory_device_status = 0U;
    open_cfw_test_memory_force_axi_clock = 0U;
    open_cfw_test_memory_current_rom_mode = 0xFFU;
    open_cfw_test_memory_delay_result[0] = 0U;
    open_cfw_test_memory_delay_result[1] = 0U;
    open_cfw_test_memory_delay_updates_status = 1U;
    open_cfw_test_memory_delay_calls = 0U;
    open_cfw_test_memory_spot_result = 0U;
    open_cfw_test_memory_spot_calls = 0U;
    open_cfw_test_memory_spot_stimulus = 0U;
    open_cfw_test_memory_spot_enabled = 0U;
    open_cfw_test_memory_spot_value = 0U;
    open_cfw_test_memory_trace_count = 0U;
    for (index = 0U; index < 2U; ++index) {
        open_cfw_test_memory_delay_maximum[index] = 0U;
        open_cfw_test_memory_delay_address[index] = 0U;
        open_cfw_test_memory_delay_mask[index] = 0U;
        open_cfw_test_memory_delay_expected[index] = 0U;
        open_cfw_test_memory_delay_wait[index] = 0U;
    }
    for (index = 0U; index < 64U; ++index) {
        open_cfw_test_memory_trace_event[index] = 0U;
        open_cfw_test_memory_trace_value[index] = 0U;
    }
}

unsigned int open_cfw_test_memory_read(unsigned int address)
{
    if (address == 0x40021018U) {
        open_cfw_test_memory_trace(
            OPEN_CFW_TEST_MEMORY_READ_STATUS,
            open_cfw_test_memory_status
        );
        return open_cfw_test_memory_status;
    }
    if (address == 0x40020284U) {
        open_cfw_test_memory_trace(
            OPEN_CFW_TEST_MEMORY_READ_FORCE,
            open_cfw_test_memory_force_axi_clock
        );
        return open_cfw_test_memory_force_axi_clock;
    }
    if (address == 0x40021014U) {
        open_cfw_test_memory_trace(
            OPEN_CFW_TEST_MEMORY_READ_ENABLE,
            open_cfw_test_memory_enable
        );
        return open_cfw_test_memory_enable;
    }
    if (address == 0x40021008U) {
        open_cfw_test_memory_trace(
            OPEN_CFW_TEST_MEMORY_READ_DEVICE_STATUS,
            open_cfw_test_memory_device_status
        );
        return open_cfw_test_memory_device_status;
    }
    if (address == 0x40021004U) {
        open_cfw_test_memory_trace(
            OPEN_CFW_TEST_MEMORY_READ_DEVICE_ENABLE,
            open_cfw_test_memory_device_enable
        );
        return open_cfw_test_memory_device_enable;
    }
    open_cfw_test_memory_trace(
        OPEN_CFW_TEST_MEMORY_READ_RETENTION,
        open_cfw_test_memory_retention
    );
    return open_cfw_test_memory_retention;
}

void open_cfw_test_memory_write(
    unsigned int address,
    unsigned int value
)
{
    if (address == 0x40020284U) {
        open_cfw_test_memory_force_axi_clock = value;
        open_cfw_test_memory_trace(
            OPEN_CFW_TEST_MEMORY_WRITE_FORCE,
            value
        );
        return;
    }
    if (address == 0x40021014U) {
        open_cfw_test_memory_enable = value;
        open_cfw_test_memory_trace(
            OPEN_CFW_TEST_MEMORY_WRITE_ENABLE,
            value
        );
        return;
    }
    open_cfw_test_memory_retention = value;
    open_cfw_test_memory_trace(
        OPEN_CFW_TEST_MEMORY_WRITE_RETENTION,
        value
    );
}

void open_cfw_test_memory_rom_write(unsigned int value)
{
    open_cfw_test_memory_current_rom_mode = value & 0xFFU;
    open_cfw_test_memory_trace(
        OPEN_CFW_TEST_MEMORY_ROM_WRITE,
        value & 0xFFU
    );
}

unsigned int open_cfw_test_memory_delay_status(
    unsigned int maximum_wait,
    unsigned int address,
    unsigned int mask,
    unsigned int expected,
    unsigned int wait_for_match
)
{
    unsigned int index = open_cfw_test_memory_delay_calls++;

    if (index < 2U) {
        open_cfw_test_memory_delay_maximum[index] = maximum_wait;
        open_cfw_test_memory_delay_address[index] = address;
        open_cfw_test_memory_delay_mask[index] = mask;
        open_cfw_test_memory_delay_expected[index] = expected;
        open_cfw_test_memory_delay_wait[index] = wait_for_match;
    }
    open_cfw_test_memory_trace(
        OPEN_CFW_TEST_MEMORY_DELAY_STATUS,
        expected
    );
    index = index < 2U ? index : 1U;
    if (
        open_cfw_test_memory_delay_result[index] == 0U
        && open_cfw_test_memory_delay_updates_status != 0U
    ) {
        open_cfw_test_memory_status = expected;
    }
    return open_cfw_test_memory_delay_result[index];
}

unsigned int open_cfw_test_memory_spot_update(
    unsigned int stimulus,
    unsigned int enabled,
    const void *value
)
{
    ++open_cfw_test_memory_spot_calls;
    open_cfw_test_memory_spot_stimulus = stimulus;
    open_cfw_test_memory_spot_enabled = enabled;
    open_cfw_test_memory_spot_value =
        *(const unsigned int *)value;
    open_cfw_test_memory_trace(
        OPEN_CFW_TEST_MEMORY_SPOT_UPDATE,
        open_cfw_test_memory_spot_value
    );
    return open_cfw_test_memory_spot_result;
}

#define OPEN_CFW_PWRCTRL_MEMORY_READ(address) \
    open_cfw_test_memory_read((address))
#define OPEN_CFW_PWRCTRL_MEMORY_WRITE(address, value) \
    open_cfw_test_memory_write((address), (value))
#define OPEN_CFW_PWRCTRL_MEMORY_ROM_MODE_WRITE(value) \
    open_cfw_test_memory_rom_write((value))
#define OPEN_CFW_PWRCTRL_MEMORY_DELAY_STATUS( \
    maximum_wait, address, mask, expected, wait_for_match \
) \
    open_cfw_test_memory_delay_status( \
        (maximum_wait), \
        (address), \
        (mask), \
        (expected), \
        (wait_for_match) \
    )
#define OPEN_CFW_PWRCTRL_MEMORY_SPOT_UPDATE(stimulus, enabled, value) \
    open_cfw_test_memory_spot_update((stimulus), (enabled), (value))

#include "../../components/apollo_main/core_overlay/pwrctrl_mcu_memory_config.c"
