#include <stddef.h>

unsigned int open_cfw_test_sram_power_enable;
unsigned int open_cfw_test_sram_power_status;
unsigned int open_cfw_test_sram_retention;
unsigned int open_cfw_test_sram_override;
unsigned int open_cfw_test_sram_status_check_result;
unsigned int open_cfw_test_sram_status_check_applies_expected;
unsigned int open_cfw_test_sram_spot_result;
unsigned int open_cfw_test_sram_spot_calls;
unsigned int open_cfw_test_sram_spot_stimulus[4];
unsigned int open_cfw_test_sram_spot_enabled[4];
unsigned int open_cfw_test_sram_spot_is_null[4];
unsigned int open_cfw_test_sram_spot_value[4];
unsigned int open_cfw_test_sram_status_check_calls;
unsigned int open_cfw_test_sram_status_check_wait;
unsigned int open_cfw_test_sram_status_check_address;
unsigned int open_cfw_test_sram_status_check_mask;
unsigned int open_cfw_test_sram_status_check_expected;
unsigned int open_cfw_test_sram_status_check_equal;
unsigned int open_cfw_test_sram_trace_count;
unsigned int open_cfw_test_sram_trace_event[128];
unsigned int open_cfw_test_sram_trace_address[128];
unsigned int open_cfw_test_sram_trace_value[128];

enum {
    OPEN_CFW_TEST_SRAM_READ = 1,
    OPEN_CFW_TEST_SRAM_WRITE = 2,
    OPEN_CFW_TEST_SRAM_SPOT = 3,
    OPEN_CFW_TEST_SRAM_STATUS_CHECK = 4,
};

static void
open_cfw_test_sram_trace(
    unsigned int event,
    unsigned int address,
    unsigned int value
)
{
    unsigned int index = open_cfw_test_sram_trace_count++;

    if (index < 128U) {
        open_cfw_test_sram_trace_event[index] = event;
        open_cfw_test_sram_trace_address[index] = address;
        open_cfw_test_sram_trace_value[index] = value;
    }
}

static unsigned int
open_cfw_test_sram_read(unsigned int address)
{
    unsigned int value = 0U;

    if (address == 0x40021024U) {
        value = open_cfw_test_sram_power_enable;
    } else if (address == 0x40021028U) {
        value = open_cfw_test_sram_power_status;
    } else if (address == 0x4002102CU) {
        value = open_cfw_test_sram_retention;
    } else if (address == 0x40021040U) {
        value = open_cfw_test_sram_override;
    }
    open_cfw_test_sram_trace(
        OPEN_CFW_TEST_SRAM_READ,
        address,
        value
    );
    return value;
}

static void
open_cfw_test_sram_write(
    unsigned int address,
    unsigned int value
)
{
    if (address == 0x40021024U) {
        open_cfw_test_sram_power_enable = value;
    } else if (address == 0x40021028U) {
        open_cfw_test_sram_power_status = value;
    } else if (address == 0x4002102CU) {
        open_cfw_test_sram_retention = value;
    } else if (address == 0x40021040U) {
        open_cfw_test_sram_override = value;
    }
    open_cfw_test_sram_trace(
        OPEN_CFW_TEST_SRAM_WRITE,
        address,
        value
    );
}

static unsigned int
open_cfw_test_sram_spot_update(
    unsigned int stimulus,
    unsigned int enabled,
    const void *value
)
{
    unsigned int index = open_cfw_test_sram_spot_calls++;

    if (index < 4U) {
        open_cfw_test_sram_spot_stimulus[index] = stimulus;
        open_cfw_test_sram_spot_enabled[index] = enabled;
        open_cfw_test_sram_spot_is_null[index] = value == NULL;
        open_cfw_test_sram_spot_value[index] =
            value == NULL ? 0U : *(const unsigned char *)value;
    }
    open_cfw_test_sram_trace(
        OPEN_CFW_TEST_SRAM_SPOT,
        stimulus,
        enabled
    );
    return open_cfw_test_sram_spot_result;
}

static unsigned int
open_cfw_test_sram_status_check(
    unsigned int maximum_wait_us,
    unsigned int address,
    unsigned int mask,
    unsigned int expected,
    unsigned int equal
)
{
    ++open_cfw_test_sram_status_check_calls;
    open_cfw_test_sram_status_check_wait = maximum_wait_us;
    open_cfw_test_sram_status_check_address = address;
    open_cfw_test_sram_status_check_mask = mask;
    open_cfw_test_sram_status_check_expected = expected;
    open_cfw_test_sram_status_check_equal = equal;
    open_cfw_test_sram_trace(
        OPEN_CFW_TEST_SRAM_STATUS_CHECK,
        address,
        expected
    );
    if (
        open_cfw_test_sram_status_check_result == 0U
        && open_cfw_test_sram_status_check_applies_expected != 0U
    ) {
        open_cfw_test_sram_power_status =
            (
                open_cfw_test_sram_power_status
                & ~mask
            ) | (expected & mask);
    }
    return open_cfw_test_sram_status_check_result;
}

#define OPEN_CFW_PWRCTRL_SRAM_CONFIG_READ(address) \
    open_cfw_test_sram_read(address)
#define OPEN_CFW_PWRCTRL_SRAM_CONFIG_WRITE(address, value) \
    open_cfw_test_sram_write((address), (value))
#define OPEN_CFW_PWRCTRL_SRAM_CONFIG_SPOT_UPDATE( \
    stimulus, enabled, value \
) \
    open_cfw_test_sram_spot_update((stimulus), (enabled), (value))
#define OPEN_CFW_PWRCTRL_SRAM_CONFIG_STATUS_CHECK( \
    maximum_wait_us, address, mask, expected, equal \
) \
    open_cfw_test_sram_status_check( \
        (maximum_wait_us), \
        (address), \
        (mask), \
        (expected), \
        (equal) \
    )

#include "../../components/apollo_main/core_overlay/pwrctrl_sram_config.c"

void
open_cfw_test_sram_reset(void)
{
    unsigned int index;

    open_cfw_test_sram_power_enable = 0U;
    open_cfw_test_sram_power_status = 0U;
    open_cfw_test_sram_retention = 0U;
    open_cfw_test_sram_override = 0U;
    open_cfw_test_sram_status_check_result = 0U;
    open_cfw_test_sram_status_check_applies_expected = 1U;
    open_cfw_test_sram_spot_result = 0U;
    open_cfw_test_sram_spot_calls = 0U;
    open_cfw_test_sram_status_check_calls = 0U;
    open_cfw_test_sram_status_check_wait = 0U;
    open_cfw_test_sram_status_check_address = 0U;
    open_cfw_test_sram_status_check_mask = 0U;
    open_cfw_test_sram_status_check_expected = 0U;
    open_cfw_test_sram_status_check_equal = 0U;
    open_cfw_test_sram_trace_count = 0U;
    for (index = 0U; index < 4U; ++index) {
        open_cfw_test_sram_spot_stimulus[index] = 0U;
        open_cfw_test_sram_spot_enabled[index] = 0U;
        open_cfw_test_sram_spot_is_null[index] = 0U;
        open_cfw_test_sram_spot_value[index] = 0U;
    }
    for (index = 0U; index < 128U; ++index) {
        open_cfw_test_sram_trace_event[index] = 0U;
        open_cfw_test_sram_trace_address[index] = 0U;
        open_cfw_test_sram_trace_value[index] = 0U;
    }
}
