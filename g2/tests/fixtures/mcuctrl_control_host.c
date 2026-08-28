/* SPDX-License-Identifier: MIT */

unsigned int open_cfw_test_mcuctrl_control_registers[5];
unsigned int open_cfw_test_mcuctrl_control_argument8_sequence[8];
unsigned int open_cfw_test_mcuctrl_control_argument32_sequence[8];
unsigned int open_cfw_test_mcuctrl_control_argument8_count;
unsigned int open_cfw_test_mcuctrl_control_argument32_count;
unsigned int open_cfw_test_mcuctrl_control_argument8_index;
unsigned int open_cfw_test_mcuctrl_control_argument32_index;
unsigned int open_cfw_test_mcuctrl_control_clock_request_result;
unsigned int open_cfw_test_mcuctrl_control_clock_release_result;
unsigned int open_cfw_test_mcuctrl_control_event_count;
unsigned int open_cfw_test_mcuctrl_control_event_kind[128];
unsigned int open_cfw_test_mcuctrl_control_event_address[128];
unsigned int open_cfw_test_mcuctrl_control_event_value[128];
unsigned int open_cfw_test_mcuctrl_control_event_result[128];

static const unsigned int open_cfw_test_mcuctrl_control_addresses[5] = {
    0x40020120U,
    0x40020128U,
    0x4002012CU,
    0x200001E0U,
    0x200001E4U,
};

static void open_cfw_test_mcuctrl_control_event(
    unsigned int kind,
    unsigned int address,
    unsigned int value,
    unsigned int result
)
{
    unsigned int index = open_cfw_test_mcuctrl_control_event_count;

    open_cfw_test_mcuctrl_control_event_kind[index] = kind;
    open_cfw_test_mcuctrl_control_event_address[index] = address;
    open_cfw_test_mcuctrl_control_event_value[index] = value;
    open_cfw_test_mcuctrl_control_event_result[index] = result;
    ++open_cfw_test_mcuctrl_control_event_count;
}

static unsigned int
open_cfw_test_mcuctrl_control_read32(unsigned int address)
{
    unsigned int index;
    unsigned int value = 0U;

    for (index = 0U; index < 5U; ++index) {
        if (open_cfw_test_mcuctrl_control_addresses[index] == address) {
            value = open_cfw_test_mcuctrl_control_registers[index];
            break;
        }
    }
    open_cfw_test_mcuctrl_control_event(1U, address, value, 0U);
    return value;
}

static void open_cfw_test_mcuctrl_control_write32(
    unsigned int address,
    unsigned int value
)
{
    unsigned int index;

    for (index = 0U; index < 5U; ++index) {
        if (open_cfw_test_mcuctrl_control_addresses[index] == address) {
            open_cfw_test_mcuctrl_control_registers[index] = value;
            break;
        }
    }
    open_cfw_test_mcuctrl_control_event(2U, address, value, 0U);
}

static unsigned int
open_cfw_test_mcuctrl_control_argument8(const void *arguments)
{
    unsigned int index = open_cfw_test_mcuctrl_control_argument8_index;
    unsigned int value;

    if (index < open_cfw_test_mcuctrl_control_argument8_count) {
        value = open_cfw_test_mcuctrl_control_argument8_sequence[index];
    }
    else {
        value = *(const unsigned char *)arguments;
    }
    ++open_cfw_test_mcuctrl_control_argument8_index;
    open_cfw_test_mcuctrl_control_event(3U, 0U, value, 0U);
    return value;
}

static unsigned int
open_cfw_test_mcuctrl_control_argument32(const void *arguments)
{
    unsigned int index = open_cfw_test_mcuctrl_control_argument32_index;
    unsigned int value;

    if (index < open_cfw_test_mcuctrl_control_argument32_count) {
        value = open_cfw_test_mcuctrl_control_argument32_sequence[index];
    }
    else {
        value = *(const unsigned int *)arguments;
    }
    ++open_cfw_test_mcuctrl_control_argument32_index;
    open_cfw_test_mcuctrl_control_event(4U, 0U, value, 0U);
    return value;
}

static void
open_cfw_test_mcuctrl_control_delay_us(unsigned int microseconds)
{
    open_cfw_test_mcuctrl_control_event(
        5U,
        0U,
        microseconds,
        0U
    );
}

static unsigned int open_cfw_test_mcuctrl_control_clock_request(
    unsigned int clock,
    unsigned int user
)
{
    unsigned int result =
        open_cfw_test_mcuctrl_control_clock_request_result;
    open_cfw_test_mcuctrl_control_event(6U, clock, user, result);
    return result;
}

static unsigned int open_cfw_test_mcuctrl_control_clock_release(
    unsigned int clock,
    unsigned int user
)
{
    unsigned int result =
        open_cfw_test_mcuctrl_control_clock_release_result;
    open_cfw_test_mcuctrl_control_event(7U, clock, user, result);
    return result;
}

#define OPEN_CFW_MCUCTRL_CONTROL_READ32(address) \
    open_cfw_test_mcuctrl_control_read32(address)
#define OPEN_CFW_MCUCTRL_CONTROL_WRITE32(address, value) \
    open_cfw_test_mcuctrl_control_write32((address), (value))
#define OPEN_CFW_MCUCTRL_CONTROL_ARGUMENT8(arguments) \
    open_cfw_test_mcuctrl_control_argument8(arguments)
#define OPEN_CFW_MCUCTRL_CONTROL_ARGUMENT32(arguments) \
    open_cfw_test_mcuctrl_control_argument32(arguments)
#define OPEN_CFW_MCUCTRL_CONTROL_DELAY_US(microseconds) \
    open_cfw_test_mcuctrl_control_delay_us(microseconds)
#define OPEN_CFW_MCUCTRL_CONTROL_CLOCK_REQUEST(clock, user) \
    open_cfw_test_mcuctrl_control_clock_request((clock), (user))
#define OPEN_CFW_MCUCTRL_CONTROL_CLOCK_RELEASE(clock, user) \
    open_cfw_test_mcuctrl_control_clock_release((clock), (user))

#include "../../components/apollo_main/core_overlay/mcuctrl_control.c"

void open_cfw_test_mcuctrl_control_reset(void)
{
    unsigned int index;

    for (index = 0U; index < 5U; ++index) {
        open_cfw_test_mcuctrl_control_registers[index] = 0U;
    }
    for (index = 0U; index < 8U; ++index) {
        open_cfw_test_mcuctrl_control_argument8_sequence[index] = 0U;
        open_cfw_test_mcuctrl_control_argument32_sequence[index] = 0U;
    }
    for (index = 0U; index < 128U; ++index) {
        open_cfw_test_mcuctrl_control_event_kind[index] = 0U;
        open_cfw_test_mcuctrl_control_event_address[index] = 0U;
        open_cfw_test_mcuctrl_control_event_value[index] = 0U;
        open_cfw_test_mcuctrl_control_event_result[index] = 0U;
    }
    open_cfw_test_mcuctrl_control_argument8_count = 0U;
    open_cfw_test_mcuctrl_control_argument32_count = 0U;
    open_cfw_test_mcuctrl_control_argument8_index = 0U;
    open_cfw_test_mcuctrl_control_argument32_index = 0U;
    open_cfw_test_mcuctrl_control_clock_request_result = 0U;
    open_cfw_test_mcuctrl_control_clock_release_result = 0U;
    open_cfw_test_mcuctrl_control_event_count = 0U;
}
