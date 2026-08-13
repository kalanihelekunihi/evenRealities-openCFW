#include <stddef.h>
#include <stdint.h>

#define OPEN_CFW_TEST_RTC_GET_EVENT_READ 1U
#define OPEN_CFW_TEST_RTC_GET_EVENT_WRITE 2U
#define OPEN_CFW_TEST_RTC_GET_EVENT_IRQ_DISABLE 3U
#define OPEN_CFW_TEST_RTC_GET_EVENT_IRQ_RESTORE 4U
#define OPEN_CFW_TEST_RTC_GET_EVENT_DELAY 5U

#define OPEN_CFW_TEST_RTC_GET_CLKGEN_OCTRL_ADDRESS 0x4000400CU
#define OPEN_CFW_TEST_RTC_GET_COUNTER_LOW_ADDRESS 0x40004820U
#define OPEN_CFW_TEST_RTC_GET_COUNTER_UP_ADDRESS 0x40004824U
#define OPEN_CFW_TEST_RTC_GET_TIMER_CONTROL_ADDRESS 0x400083C0U
#define OPEN_CFW_TEST_RTC_GET_TIMER_COUNTER_ADDRESS 0x400083C4U
#define OPEN_CFW_TEST_RTC_GET_TIMER_COMPARE0_ADDRESS 0x400083C8U
#define OPEN_CFW_TEST_RTC_GET_TIMER_COMPARE1_ADDRESS 0x400083CCU
#define OPEN_CFW_TEST_RTC_GET_TIMER_GLOBAL_ENABLE_ADDRESS 0x40008010U

unsigned int open_cfw_test_rtc_get_event_kind[128];
unsigned int open_cfw_test_rtc_get_event_address[128];
unsigned int open_cfw_test_rtc_get_event_value[128];
unsigned int open_cfw_test_rtc_get_event_count;

unsigned int open_cfw_test_rtc_get_clock_control;
unsigned int open_cfw_test_rtc_get_timer_control;
unsigned int open_cfw_test_rtc_get_timer_compare0;
unsigned int open_cfw_test_rtc_get_timer_compare1;
unsigned int open_cfw_test_rtc_get_timer_global_enable;
unsigned int open_cfw_test_rtc_get_counter_low;
unsigned int open_cfw_test_rtc_get_counter_up;
unsigned int open_cfw_test_rtc_get_primask;

unsigned int open_cfw_test_rtc_get_timer_values[32];
unsigned int open_cfw_test_rtc_get_timer_value_count;
unsigned int open_cfw_test_rtc_get_timer_value_index;

static void
open_cfw_test_rtc_get_record(
    unsigned int kind,
    unsigned int address,
    unsigned int value
)
{
    unsigned int index = open_cfw_test_rtc_get_event_count;

    if (index < 128U) {
        open_cfw_test_rtc_get_event_kind[index] = kind;
        open_cfw_test_rtc_get_event_address[index] = address;
        open_cfw_test_rtc_get_event_value[index] = value;
    }
    open_cfw_test_rtc_get_event_count = index + 1U;
}

static unsigned int open_cfw_test_rtc_get_read(unsigned int address)
{
    unsigned int value;

    if (address == OPEN_CFW_TEST_RTC_GET_CLKGEN_OCTRL_ADDRESS) {
        value = open_cfw_test_rtc_get_clock_control;
    } else if (address == OPEN_CFW_TEST_RTC_GET_COUNTER_LOW_ADDRESS) {
        value = open_cfw_test_rtc_get_counter_low;
    } else if (address == OPEN_CFW_TEST_RTC_GET_COUNTER_UP_ADDRESS) {
        value = open_cfw_test_rtc_get_counter_up;
    } else if (address == OPEN_CFW_TEST_RTC_GET_TIMER_CONTROL_ADDRESS) {
        value = open_cfw_test_rtc_get_timer_control;
    } else if (
        address == OPEN_CFW_TEST_RTC_GET_TIMER_GLOBAL_ENABLE_ADDRESS
    ) {
        value = open_cfw_test_rtc_get_timer_global_enable;
    } else if (address == OPEN_CFW_TEST_RTC_GET_TIMER_COUNTER_ADDRESS) {
        unsigned int index = open_cfw_test_rtc_get_timer_value_index;
        unsigned int count = open_cfw_test_rtc_get_timer_value_count;

        if (count == 0U) {
            value = 0U;
        } else {
            if (index >= count) {
                index = count - 1U;
            }
            value = open_cfw_test_rtc_get_timer_values[index];
            if (open_cfw_test_rtc_get_timer_value_index < count) {
                open_cfw_test_rtc_get_timer_value_index++;
            }
        }
    } else {
        value = 0U;
    }

    open_cfw_test_rtc_get_record(
        OPEN_CFW_TEST_RTC_GET_EVENT_READ,
        address,
        value
    );
    return value;
}

static void
open_cfw_test_rtc_get_write(unsigned int address, unsigned int value)
{
    if (address == OPEN_CFW_TEST_RTC_GET_TIMER_CONTROL_ADDRESS) {
        open_cfw_test_rtc_get_timer_control = value;
    } else if (address == OPEN_CFW_TEST_RTC_GET_TIMER_COMPARE0_ADDRESS) {
        open_cfw_test_rtc_get_timer_compare0 = value;
    } else if (address == OPEN_CFW_TEST_RTC_GET_TIMER_COMPARE1_ADDRESS) {
        open_cfw_test_rtc_get_timer_compare1 = value;
    } else if (
        address == OPEN_CFW_TEST_RTC_GET_TIMER_GLOBAL_ENABLE_ADDRESS
    ) {
        open_cfw_test_rtc_get_timer_global_enable = value;
    }
    open_cfw_test_rtc_get_record(
        OPEN_CFW_TEST_RTC_GET_EVENT_WRITE,
        address,
        value
    );
}

static unsigned int open_cfw_test_rtc_get_irq_disable(void)
{
    open_cfw_test_rtc_get_record(
        OPEN_CFW_TEST_RTC_GET_EVENT_IRQ_DISABLE,
        0U,
        open_cfw_test_rtc_get_primask
    );
    return open_cfw_test_rtc_get_primask;
}

static void open_cfw_test_rtc_get_irq_restore(unsigned int primask)
{
    open_cfw_test_rtc_get_record(
        OPEN_CFW_TEST_RTC_GET_EVENT_IRQ_RESTORE,
        0U,
        primask
    );
}

static void open_cfw_test_rtc_get_delay(unsigned int microseconds)
{
    open_cfw_test_rtc_get_record(
        OPEN_CFW_TEST_RTC_GET_EVENT_DELAY,
        0U,
        microseconds
    );
}

#define OPEN_CFW_RTC_GET_READ(address) \
    open_cfw_test_rtc_get_read(address)
#define OPEN_CFW_RTC_GET_WRITE(address, value) \
    open_cfw_test_rtc_get_write((address), (value))
#define OPEN_CFW_RTC_GET_IRQ_DISABLE() \
    open_cfw_test_rtc_get_irq_disable()
#define OPEN_CFW_RTC_GET_IRQ_RESTORE(primask) \
    open_cfw_test_rtc_get_irq_restore(primask)
#define OPEN_CFW_RTC_GET_DELAY_US(microseconds) \
    open_cfw_test_rtc_get_delay(microseconds)

#include "../../components/apollo_main/core_overlay/rtc_time_get.c"

void open_cfw_test_rtc_get_reset(void)
{
    unsigned int index;

    open_cfw_test_rtc_get_event_count = 0U;
    open_cfw_test_rtc_get_clock_control = 0U;
    open_cfw_test_rtc_get_timer_control = 0U;
    open_cfw_test_rtc_get_timer_compare0 = 0U;
    open_cfw_test_rtc_get_timer_compare1 = 0U;
    open_cfw_test_rtc_get_timer_global_enable = 0U;
    open_cfw_test_rtc_get_counter_low = 0U;
    open_cfw_test_rtc_get_counter_up = 0U;
    open_cfw_test_rtc_get_primask = 0U;
    open_cfw_test_rtc_get_timer_value_count = 2U;
    open_cfw_test_rtc_get_timer_value_index = 0U;
    open_cfw_test_rtc_get_timer_values[0] = 100U;
    open_cfw_test_rtc_get_timer_values[1] = 101U;
    for (index = 2U; index < 32U; ++index) {
        open_cfw_test_rtc_get_timer_values[index] = 0U;
    }
}
