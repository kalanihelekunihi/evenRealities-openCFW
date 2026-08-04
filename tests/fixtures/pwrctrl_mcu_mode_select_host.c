#include <stdint.h>

enum {
    OPEN_CFW_TEST_MCU_SELECT_READ_VR_STATUS = 1,
    OPEN_CFW_TEST_MCU_SELECT_READ_CURRENT_MODE = 2,
    OPEN_CFW_TEST_MCU_SELECT_SWITCH = 3,
    OPEN_CFW_TEST_MCU_SELECT_READ_PERFORMANCE = 4
};

unsigned int open_cfw_test_mcu_select_vr_status;
unsigned int open_cfw_test_mcu_select_performance;
unsigned int open_cfw_test_mcu_select_current_mode;
unsigned int open_cfw_test_mcu_select_switch_status;
unsigned int open_cfw_test_mcu_select_vr_reads;
unsigned int open_cfw_test_mcu_select_current_mode_reads;
unsigned int open_cfw_test_mcu_select_switch_calls;
unsigned int open_cfw_test_mcu_select_performance_reads;
unsigned int open_cfw_test_mcu_select_switch_mode;
unsigned int open_cfw_test_mcu_select_trace_count;
unsigned int open_cfw_test_mcu_select_trace_event[8];
unsigned int open_cfw_test_mcu_select_trace_value[8];

static void
open_cfw_test_mcu_select_trace(unsigned int event, unsigned int value)
{
    unsigned int index = open_cfw_test_mcu_select_trace_count++;

    if (index < 8U) {
        open_cfw_test_mcu_select_trace_event[index] = event;
        open_cfw_test_mcu_select_trace_value[index] = value;
    }
}

void open_cfw_test_mcu_select_reset(void)
{
    unsigned int index;

    open_cfw_test_mcu_select_vr_status = 0x00000030U;
    open_cfw_test_mcu_select_performance = 0x00000010U;
    open_cfw_test_mcu_select_current_mode = 1U;
    open_cfw_test_mcu_select_switch_status = 0U;
    open_cfw_test_mcu_select_vr_reads = 0U;
    open_cfw_test_mcu_select_current_mode_reads = 0U;
    open_cfw_test_mcu_select_switch_calls = 0U;
    open_cfw_test_mcu_select_performance_reads = 0U;
    open_cfw_test_mcu_select_switch_mode = 0U;
    open_cfw_test_mcu_select_trace_count = 0U;
    for (index = 0U; index < 8U; ++index) {
        open_cfw_test_mcu_select_trace_event[index] = 0U;
        open_cfw_test_mcu_select_trace_value[index] = 0U;
    }
}

unsigned int open_cfw_test_mcu_select_read(unsigned int address)
{
    if (address == 0x40021108U) {
        ++open_cfw_test_mcu_select_vr_reads;
        open_cfw_test_mcu_select_trace(
            OPEN_CFW_TEST_MCU_SELECT_READ_VR_STATUS,
            open_cfw_test_mcu_select_vr_status
        );
        return open_cfw_test_mcu_select_vr_status;
    }

    ++open_cfw_test_mcu_select_performance_reads;
    open_cfw_test_mcu_select_trace(
        OPEN_CFW_TEST_MCU_SELECT_READ_PERFORMANCE,
        open_cfw_test_mcu_select_performance
    );
    return open_cfw_test_mcu_select_performance;
}

unsigned int open_cfw_test_mcu_select_current_mode_read(void)
{
    ++open_cfw_test_mcu_select_current_mode_reads;
    open_cfw_test_mcu_select_trace(
        OPEN_CFW_TEST_MCU_SELECT_READ_CURRENT_MODE,
        open_cfw_test_mcu_select_current_mode
    );
    return open_cfw_test_mcu_select_current_mode;
}

unsigned int open_cfw_test_mcu_select_switch(unsigned int requested_mode)
{
    ++open_cfw_test_mcu_select_switch_calls;
    open_cfw_test_mcu_select_switch_mode = requested_mode;
    open_cfw_test_mcu_select_trace(
        OPEN_CFW_TEST_MCU_SELECT_SWITCH,
        requested_mode
    );
    return open_cfw_test_mcu_select_switch_status;
}

#define OPEN_CFW_PWRCTRL_MCU_SELECT_READ(address) \
    open_cfw_test_mcu_select_read((address))
#define OPEN_CFW_PWRCTRL_MCU_SELECT_CURRENT_MODE_READ() \
    open_cfw_test_mcu_select_current_mode_read()
#define OPEN_CFW_PWRCTRL_MCU_SELECT_SWITCH(requested_mode) \
    open_cfw_test_mcu_select_switch((requested_mode))

#include "../../components/apollo_main/core_overlay/pwrctrl_mcu_mode_select.c"
