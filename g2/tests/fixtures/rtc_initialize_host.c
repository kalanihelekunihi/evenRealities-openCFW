/*
 * SPDX-License-Identifier: MIT
 *
 * Host substitutions for the Apollo510 RTC clock initializer.
 */

#define OPEN_CFW_TEST_RTC_EVENT_READ 1U
#define OPEN_CFW_TEST_RTC_EVENT_WRITE 2U
#define OPEN_CFW_TEST_RTC_CLKGEN_OCTRL_ADDRESS 0x4000400CU
#define OPEN_CFW_TEST_RTC_CONTROL_ADDRESS 0x40004800U

unsigned int open_cfw_test_rtc_clock_control;
unsigned int open_cfw_test_rtc_control;
unsigned int open_cfw_test_rtc_event_count;
unsigned int open_cfw_test_rtc_event_kind[16];
unsigned int open_cfw_test_rtc_event_address[16];
unsigned int open_cfw_test_rtc_event_value[16];

static void open_cfw_test_rtc_record(
    unsigned int kind,
    unsigned int address,
    unsigned int value
)
{
    unsigned int index = open_cfw_test_rtc_event_count++;

    if (index < 16U) {
        open_cfw_test_rtc_event_kind[index] = kind;
        open_cfw_test_rtc_event_address[index] = address;
        open_cfw_test_rtc_event_value[index] = value;
    }
}

void open_cfw_test_rtc_reset(void)
{
    unsigned int index;

    open_cfw_test_rtc_clock_control = 0U;
    open_cfw_test_rtc_control = 0U;
    open_cfw_test_rtc_event_count = 0U;
    for (index = 0U; index < 16U; ++index) {
        open_cfw_test_rtc_event_kind[index] = 0U;
        open_cfw_test_rtc_event_address[index] = 0U;
        open_cfw_test_rtc_event_value[index] = 0U;
    }
}

static unsigned int open_cfw_test_rtc_read(unsigned int address)
{
    unsigned int value;

    if (address == OPEN_CFW_TEST_RTC_CLKGEN_OCTRL_ADDRESS) {
        value = open_cfw_test_rtc_clock_control;
    } else {
        value = open_cfw_test_rtc_control;
    }
    open_cfw_test_rtc_record(
        OPEN_CFW_TEST_RTC_EVENT_READ,
        address,
        value
    );
    return value;
}

static void open_cfw_test_rtc_write(
    unsigned int address,
    unsigned int value
)
{
    if (address == OPEN_CFW_TEST_RTC_CLKGEN_OCTRL_ADDRESS) {
        open_cfw_test_rtc_clock_control = value;
    } else {
        open_cfw_test_rtc_control = value;
    }
    open_cfw_test_rtc_record(
        OPEN_CFW_TEST_RTC_EVENT_WRITE,
        address,
        value
    );
}

#define OPEN_CFW_RTC_READ(address) open_cfw_test_rtc_read(address)
#define OPEN_CFW_RTC_WRITE(address, value) \
    open_cfw_test_rtc_write((address), (value))

#include "../../components/apollo_main/core_overlay/rtc_initialize.c"
