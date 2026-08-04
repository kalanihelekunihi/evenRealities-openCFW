#include <stdint.h>

enum {
    OPEN_CFW_TEST_MCU_SWITCH_IRQ_DISABLE = 1,
    OPEN_CFW_TEST_MCU_SWITCH_SPOT_UPDATE = 2,
    OPEN_CFW_TEST_MCU_SWITCH_READ_MISC = 3,
    OPEN_CFW_TEST_MCU_SWITCH_WRITE_MISC = 4,
    OPEN_CFW_TEST_MCU_SWITCH_DELAY = 5,
    OPEN_CFW_TEST_MCU_SWITCH_DELAY_STATUS = 6,
    OPEN_CFW_TEST_MCU_SWITCH_READ_CLOCK = 7,
    OPEN_CFW_TEST_MCU_SWITCH_READ_PERFORMANCE = 8,
    OPEN_CFW_TEST_MCU_SWITCH_WRITE_PERFORMANCE = 9,
    OPEN_CFW_TEST_MCU_SWITCH_SPOT_POST = 10,
    OPEN_CFW_TEST_MCU_SWITCH_CURRENT_MODE_WRITE = 11,
    OPEN_CFW_TEST_MCU_SWITCH_IRQ_RESTORE = 12
};

unsigned int open_cfw_test_mcu_switch_misc;
unsigned int open_cfw_test_mcu_switch_clock_status;
unsigned int open_cfw_test_mcu_switch_performance;
unsigned int open_cfw_test_mcu_switch_current_mode;
unsigned int open_cfw_test_mcu_switch_initial_current_mode;
unsigned int open_cfw_test_mcu_switch_primask;
unsigned int open_cfw_test_mcu_switch_restored_primask;
unsigned int open_cfw_test_mcu_switch_hp_spot_status;
unsigned int open_cfw_test_mcu_switch_lp_spot_status;
unsigned int open_cfw_test_mcu_switch_delay_status_result;
int open_cfw_test_mcu_switch_ack_after_reads;

unsigned int open_cfw_test_mcu_switch_spot_calls;
unsigned int open_cfw_test_mcu_switch_hp_spot_calls;
unsigned int open_cfw_test_mcu_switch_lp_spot_calls;
unsigned int open_cfw_test_mcu_switch_post_calls;
unsigned int open_cfw_test_mcu_switch_delay_calls;
unsigned int open_cfw_test_mcu_switch_delay_total;
unsigned int open_cfw_test_mcu_switch_delay_status_calls;
unsigned int open_cfw_test_mcu_switch_ack_reads;
unsigned int open_cfw_test_mcu_switch_performance_writes;
unsigned int open_cfw_test_mcu_switch_current_mode_writes;

unsigned int open_cfw_test_mcu_switch_delay_status_maximum;
unsigned int open_cfw_test_mcu_switch_delay_status_address;
unsigned int open_cfw_test_mcu_switch_delay_status_mask;
unsigned int open_cfw_test_mcu_switch_delay_status_expected;

unsigned int open_cfw_test_mcu_switch_trace_count;
unsigned int open_cfw_test_mcu_switch_trace_event[256];
unsigned int open_cfw_test_mcu_switch_trace_value[256];

static unsigned int open_cfw_test_mcu_switch_request_written;

static void
open_cfw_test_mcu_switch_trace(unsigned int event, unsigned int value)
{
    unsigned int index = open_cfw_test_mcu_switch_trace_count++;

    if (index < 256U) {
        open_cfw_test_mcu_switch_trace_event[index] = event;
        open_cfw_test_mcu_switch_trace_value[index] = value;
    }
}

void open_cfw_test_mcu_switch_reset(void)
{
    unsigned int index;

    open_cfw_test_mcu_switch_misc = 0U;
    open_cfw_test_mcu_switch_clock_status = 0x01000000U;
    open_cfw_test_mcu_switch_performance = 0xA5A50000U;
    open_cfw_test_mcu_switch_current_mode = 0xFFU;
    open_cfw_test_mcu_switch_initial_current_mode = 0xFFU;
    open_cfw_test_mcu_switch_primask = 0U;
    open_cfw_test_mcu_switch_restored_primask = 0xFFFFFFFFU;
    open_cfw_test_mcu_switch_hp_spot_status = 0U;
    open_cfw_test_mcu_switch_lp_spot_status = 0U;
    open_cfw_test_mcu_switch_delay_status_result = 0U;
    open_cfw_test_mcu_switch_ack_after_reads = 0;
    open_cfw_test_mcu_switch_spot_calls = 0U;
    open_cfw_test_mcu_switch_hp_spot_calls = 0U;
    open_cfw_test_mcu_switch_lp_spot_calls = 0U;
    open_cfw_test_mcu_switch_post_calls = 0U;
    open_cfw_test_mcu_switch_delay_calls = 0U;
    open_cfw_test_mcu_switch_delay_total = 0U;
    open_cfw_test_mcu_switch_delay_status_calls = 0U;
    open_cfw_test_mcu_switch_ack_reads = 0U;
    open_cfw_test_mcu_switch_performance_writes = 0U;
    open_cfw_test_mcu_switch_current_mode_writes = 0U;
    open_cfw_test_mcu_switch_delay_status_maximum = 0U;
    open_cfw_test_mcu_switch_delay_status_address = 0U;
    open_cfw_test_mcu_switch_delay_status_mask = 0U;
    open_cfw_test_mcu_switch_delay_status_expected = 0U;
    open_cfw_test_mcu_switch_trace_count = 0U;
    open_cfw_test_mcu_switch_request_written = 0U;
    for (index = 0U; index < 256U; ++index) {
        open_cfw_test_mcu_switch_trace_event[index] = 0U;
        open_cfw_test_mcu_switch_trace_value[index] = 0U;
    }
}

unsigned int open_cfw_test_mcu_switch_read(unsigned int address)
{
    if (address == 0x40004044U) {
        open_cfw_test_mcu_switch_trace(
            OPEN_CFW_TEST_MCU_SWITCH_READ_MISC,
            open_cfw_test_mcu_switch_misc
        );
        return open_cfw_test_mcu_switch_misc;
    }
    if (address == 0x40004030U) {
        open_cfw_test_mcu_switch_trace(
            OPEN_CFW_TEST_MCU_SWITCH_READ_CLOCK,
            open_cfw_test_mcu_switch_clock_status
        );
        return open_cfw_test_mcu_switch_clock_status;
    }

    open_cfw_test_mcu_switch_trace(
        OPEN_CFW_TEST_MCU_SWITCH_READ_PERFORMANCE,
        open_cfw_test_mcu_switch_performance
    );
    if (open_cfw_test_mcu_switch_request_written != 0U) {
        int read_index = (int)open_cfw_test_mcu_switch_ack_reads++;

        if (
            open_cfw_test_mcu_switch_ack_after_reads >= 0
            && read_index >= open_cfw_test_mcu_switch_ack_after_reads
        ) {
            return open_cfw_test_mcu_switch_performance | 4U;
        }
        return open_cfw_test_mcu_switch_performance & ~4U;
    }
    return open_cfw_test_mcu_switch_performance;
}

void open_cfw_test_mcu_switch_write(
    unsigned int address,
    unsigned int value
)
{
    if (address == 0x40004044U) {
        open_cfw_test_mcu_switch_misc = value;
        open_cfw_test_mcu_switch_trace(
            OPEN_CFW_TEST_MCU_SWITCH_WRITE_MISC,
            value
        );
        return;
    }

    open_cfw_test_mcu_switch_performance = value;
    open_cfw_test_mcu_switch_request_written = 1U;
    ++open_cfw_test_mcu_switch_performance_writes;
    open_cfw_test_mcu_switch_trace(
        OPEN_CFW_TEST_MCU_SWITCH_WRITE_PERFORMANCE,
        value
    );
}

void open_cfw_test_mcu_switch_current_mode_write(unsigned int value)
{
    open_cfw_test_mcu_switch_current_mode = value & 0xFFU;
    ++open_cfw_test_mcu_switch_current_mode_writes;
    open_cfw_test_mcu_switch_trace(
        OPEN_CFW_TEST_MCU_SWITCH_CURRENT_MODE_WRITE,
        value & 0xFFU
    );
}

unsigned int open_cfw_test_mcu_switch_irq_disable(void)
{
    open_cfw_test_mcu_switch_trace(
        OPEN_CFW_TEST_MCU_SWITCH_IRQ_DISABLE,
        open_cfw_test_mcu_switch_primask
    );
    return open_cfw_test_mcu_switch_primask;
}

void open_cfw_test_mcu_switch_irq_restore(unsigned int value)
{
    open_cfw_test_mcu_switch_restored_primask = value;
    open_cfw_test_mcu_switch_trace(
        OPEN_CFW_TEST_MCU_SWITCH_IRQ_RESTORE,
        value
    );
}

void open_cfw_test_mcu_switch_delay(unsigned int microseconds)
{
    ++open_cfw_test_mcu_switch_delay_calls;
    open_cfw_test_mcu_switch_delay_total += microseconds;
    open_cfw_test_mcu_switch_trace(
        OPEN_CFW_TEST_MCU_SWITCH_DELAY,
        microseconds
    );
}

unsigned int open_cfw_test_mcu_switch_delay_status(
    unsigned int maximum_delay,
    unsigned int address,
    unsigned int mask,
    unsigned int expected
)
{
    ++open_cfw_test_mcu_switch_delay_status_calls;
    open_cfw_test_mcu_switch_delay_status_maximum = maximum_delay;
    open_cfw_test_mcu_switch_delay_status_address = address;
    open_cfw_test_mcu_switch_delay_status_mask = mask;
    open_cfw_test_mcu_switch_delay_status_expected = expected;
    open_cfw_test_mcu_switch_trace(
        OPEN_CFW_TEST_MCU_SWITCH_DELAY_STATUS,
        maximum_delay
    );
    return open_cfw_test_mcu_switch_delay_status_result;
}

unsigned int open_cfw_test_mcu_switch_spot_update(
    unsigned int stimulus,
    unsigned int enabled,
    const void *state_pointer
)
{
    unsigned int state = *(const unsigned char *)state_pointer;

    ++open_cfw_test_mcu_switch_spot_calls;
    open_cfw_test_mcu_switch_trace(
        OPEN_CFW_TEST_MCU_SWITCH_SPOT_UPDATE,
        (stimulus << 16U) | (enabled << 8U) | state
    );
    if (state == 1U) {
        ++open_cfw_test_mcu_switch_hp_spot_calls;
        return open_cfw_test_mcu_switch_hp_spot_status;
    }
    ++open_cfw_test_mcu_switch_lp_spot_calls;
    return open_cfw_test_mcu_switch_lp_spot_status;
}

void open_cfw_test_mcu_switch_spot_post(void)
{
    ++open_cfw_test_mcu_switch_post_calls;
    open_cfw_test_mcu_switch_trace(
        OPEN_CFW_TEST_MCU_SWITCH_SPOT_POST,
        0U
    );
}

#define OPEN_CFW_PWRCTRL_MCU_SWITCH_READ(address) \
    open_cfw_test_mcu_switch_read((address))
#define OPEN_CFW_PWRCTRL_MCU_SWITCH_WRITE(address, value) \
    open_cfw_test_mcu_switch_write((address), (value))
#define OPEN_CFW_PWRCTRL_MCU_SWITCH_CURRENT_MODE_WRITE(value) \
    open_cfw_test_mcu_switch_current_mode_write((value))
#define OPEN_CFW_PWRCTRL_MCU_SWITCH_IRQ_DISABLE() \
    open_cfw_test_mcu_switch_irq_disable()
#define OPEN_CFW_PWRCTRL_MCU_SWITCH_IRQ_RESTORE(primask) \
    open_cfw_test_mcu_switch_irq_restore((primask))
#define OPEN_CFW_PWRCTRL_MCU_SWITCH_DELAY_US(microseconds) \
    open_cfw_test_mcu_switch_delay((microseconds))
#define OPEN_CFW_PWRCTRL_MCU_SWITCH_SPOT_UPDATE( \
    stimulus, enabled, state \
) \
    open_cfw_test_mcu_switch_spot_update( \
        (stimulus), \
        (enabled), \
        (state) \
    )
#define OPEN_CFW_PWRCTRL_MCU_SWITCH_SPOT_POST() \
    open_cfw_test_mcu_switch_spot_post()
#define OPEN_CFW_PWRCTRL_MCU_SWITCH_DELAY_STATUS( \
    maximum_delay, address, mask, expected \
) \
    open_cfw_test_mcu_switch_delay_status( \
        (maximum_delay), \
        (address), \
        (mask), \
        (expected) \
    )

#include "../../components/apollo_main/core_overlay/pwrctrl_mcu_switch_sequence.c"
