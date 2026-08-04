#include <stdint.h>

enum {
    OPEN_CFW_TEST_GPU_SELECT_READ_VR = 1,
    OPEN_CFW_TEST_GPU_SELECT_PERIPH = 2,
    OPEN_CFW_TEST_GPU_SELECT_READ_CURRENT = 3,
    OPEN_CFW_TEST_GPU_SELECT_READ_PREVIOUS = 4,
    OPEN_CFW_TEST_GPU_SELECT_WRITE_PREVIOUS = 5,
    OPEN_CFW_TEST_GPU_SELECT_IRQ_DISABLE = 6,
    OPEN_CFW_TEST_GPU_SELECT_TON = 7,
    OPEN_CFW_TEST_GPU_SELECT_READ_POWER = 8,
    OPEN_CFW_TEST_GPU_SELECT_WRITE_POWER = 9,
    OPEN_CFW_TEST_GPU_SELECT_DELAY = 10,
    OPEN_CFW_TEST_GPU_SELECT_READ_PERFORMANCE = 11,
    OPEN_CFW_TEST_GPU_SELECT_WRITE_PERFORMANCE = 12,
    OPEN_CFW_TEST_GPU_SELECT_WRITE_CURRENT = 13,
    OPEN_CFW_TEST_GPU_SELECT_IRQ_RESTORE = 14
};

unsigned int open_cfw_test_gpu_select_vr_status;
unsigned int open_cfw_test_gpu_select_power_switch;
unsigned int open_cfw_test_gpu_select_performance;
unsigned int open_cfw_test_gpu_select_current_mode;
unsigned int open_cfw_test_gpu_select_previous_mode;
unsigned int open_cfw_test_gpu_select_periph_status;
unsigned int open_cfw_test_gpu_select_graphics_enabled;
unsigned int open_cfw_test_gpu_select_primask;
unsigned int open_cfw_test_gpu_select_restored_primask;
unsigned int open_cfw_test_gpu_select_periph_calls;
unsigned int open_cfw_test_gpu_select_periph_id;
unsigned int open_cfw_test_gpu_select_ton_calls;
unsigned int open_cfw_test_gpu_select_delay_calls;
unsigned int open_cfw_test_gpu_select_delay_total;
unsigned int open_cfw_test_gpu_select_current_writes;
unsigned int open_cfw_test_gpu_select_previous_writes;
unsigned int open_cfw_test_gpu_select_trace_count;
unsigned int open_cfw_test_gpu_select_trace_event[32];
unsigned int open_cfw_test_gpu_select_trace_value[32];

static void
open_cfw_test_gpu_select_trace(unsigned int event, unsigned int value)
{
    unsigned int index = open_cfw_test_gpu_select_trace_count++;

    if (index < 32U) {
        open_cfw_test_gpu_select_trace_event[index] = event;
        open_cfw_test_gpu_select_trace_value[index] = value;
    }
}

void open_cfw_test_gpu_select_reset(void)
{
    unsigned int index;

    open_cfw_test_gpu_select_vr_status = 0x30U;
    open_cfw_test_gpu_select_power_switch = 0xA5A50000U;
    open_cfw_test_gpu_select_performance = 0x5A5A0000U;
    open_cfw_test_gpu_select_current_mode = 0U;
    open_cfw_test_gpu_select_previous_mode = 0U;
    open_cfw_test_gpu_select_periph_status = 0U;
    open_cfw_test_gpu_select_graphics_enabled = 0U;
    open_cfw_test_gpu_select_primask = 0U;
    open_cfw_test_gpu_select_restored_primask = 0xFFFFFFFFU;
    open_cfw_test_gpu_select_periph_calls = 0U;
    open_cfw_test_gpu_select_periph_id = 0U;
    open_cfw_test_gpu_select_ton_calls = 0U;
    open_cfw_test_gpu_select_delay_calls = 0U;
    open_cfw_test_gpu_select_delay_total = 0U;
    open_cfw_test_gpu_select_current_writes = 0U;
    open_cfw_test_gpu_select_previous_writes = 0U;
    open_cfw_test_gpu_select_trace_count = 0U;
    for (index = 0U; index < 32U; ++index) {
        open_cfw_test_gpu_select_trace_event[index] = 0U;
        open_cfw_test_gpu_select_trace_value[index] = 0U;
    }
}

unsigned int open_cfw_test_gpu_select_read(unsigned int address)
{
    if (address == 0x40021108U) {
        open_cfw_test_gpu_select_trace(
            OPEN_CFW_TEST_GPU_SELECT_READ_VR,
            open_cfw_test_gpu_select_vr_status
        );
        return open_cfw_test_gpu_select_vr_status;
    }
    if (address == 0x40021090U) {
        open_cfw_test_gpu_select_trace(
            OPEN_CFW_TEST_GPU_SELECT_READ_POWER,
            open_cfw_test_gpu_select_power_switch
        );
        return open_cfw_test_gpu_select_power_switch;
    }
    open_cfw_test_gpu_select_trace(
        OPEN_CFW_TEST_GPU_SELECT_READ_PERFORMANCE,
        open_cfw_test_gpu_select_performance
    );
    return open_cfw_test_gpu_select_performance;
}

void open_cfw_test_gpu_select_write(
    unsigned int address,
    unsigned int value
)
{
    if (address == 0x40021090U) {
        open_cfw_test_gpu_select_power_switch = value;
        open_cfw_test_gpu_select_trace(
            OPEN_CFW_TEST_GPU_SELECT_WRITE_POWER,
            value
        );
        return;
    }
    open_cfw_test_gpu_select_performance = value;
    open_cfw_test_gpu_select_trace(
        OPEN_CFW_TEST_GPU_SELECT_WRITE_PERFORMANCE,
        value
    );
}

unsigned int open_cfw_test_gpu_select_current_read(void)
{
    open_cfw_test_gpu_select_trace(
        OPEN_CFW_TEST_GPU_SELECT_READ_CURRENT,
        open_cfw_test_gpu_select_current_mode
    );
    return open_cfw_test_gpu_select_current_mode;
}

unsigned int open_cfw_test_gpu_select_previous_read(void)
{
    open_cfw_test_gpu_select_trace(
        OPEN_CFW_TEST_GPU_SELECT_READ_PREVIOUS,
        open_cfw_test_gpu_select_previous_mode
    );
    return open_cfw_test_gpu_select_previous_mode;
}

void open_cfw_test_gpu_select_current_write(unsigned int value)
{
    open_cfw_test_gpu_select_current_mode = value & 0xFFU;
    ++open_cfw_test_gpu_select_current_writes;
    open_cfw_test_gpu_select_trace(
        OPEN_CFW_TEST_GPU_SELECT_WRITE_CURRENT,
        value & 0xFFU
    );
}

void open_cfw_test_gpu_select_previous_write(unsigned int value)
{
    open_cfw_test_gpu_select_previous_mode = value & 0xFFU;
    ++open_cfw_test_gpu_select_previous_writes;
    open_cfw_test_gpu_select_trace(
        OPEN_CFW_TEST_GPU_SELECT_WRITE_PREVIOUS,
        value & 0xFFU
    );
}

unsigned int open_cfw_test_gpu_select_periph_enabled(
    unsigned int id,
    unsigned char *enabled
)
{
    ++open_cfw_test_gpu_select_periph_calls;
    open_cfw_test_gpu_select_periph_id = id;
    *enabled = (unsigned char)open_cfw_test_gpu_select_graphics_enabled;
    open_cfw_test_gpu_select_trace(OPEN_CFW_TEST_GPU_SELECT_PERIPH, id);
    return open_cfw_test_gpu_select_periph_status;
}

unsigned int open_cfw_test_gpu_select_irq_disable(void)
{
    open_cfw_test_gpu_select_trace(
        OPEN_CFW_TEST_GPU_SELECT_IRQ_DISABLE,
        open_cfw_test_gpu_select_primask
    );
    return open_cfw_test_gpu_select_primask;
}

void open_cfw_test_gpu_select_irq_restore(unsigned int primask)
{
    open_cfw_test_gpu_select_restored_primask = primask;
    open_cfw_test_gpu_select_trace(
        OPEN_CFW_TEST_GPU_SELECT_IRQ_RESTORE,
        primask
    );
}

void open_cfw_test_gpu_select_delay(unsigned int microseconds)
{
    ++open_cfw_test_gpu_select_delay_calls;
    open_cfw_test_gpu_select_delay_total += microseconds;
    open_cfw_test_gpu_select_trace(
        OPEN_CFW_TEST_GPU_SELECT_DELAY,
        microseconds
    );
}

void open_cfw_test_gpu_select_ton_update(
    unsigned int enabled,
    unsigned int mode
)
{
    ++open_cfw_test_gpu_select_ton_calls;
    open_cfw_test_gpu_select_trace(
        OPEN_CFW_TEST_GPU_SELECT_TON,
        (enabled << 8U) | mode
    );
}

#define OPEN_CFW_PWRCTRL_GPU_SELECT_READ(address) \
    open_cfw_test_gpu_select_read((address))
#define OPEN_CFW_PWRCTRL_GPU_SELECT_WRITE(address, value) \
    open_cfw_test_gpu_select_write((address), (value))
#define OPEN_CFW_PWRCTRL_GPU_SELECT_CURRENT_MODE_READ() \
    open_cfw_test_gpu_select_current_read()
#define OPEN_CFW_PWRCTRL_GPU_SELECT_PREVIOUS_MODE_READ() \
    open_cfw_test_gpu_select_previous_read()
#define OPEN_CFW_PWRCTRL_GPU_SELECT_CURRENT_MODE_WRITE(value) \
    open_cfw_test_gpu_select_current_write((value))
#define OPEN_CFW_PWRCTRL_GPU_SELECT_PREVIOUS_MODE_WRITE(value) \
    open_cfw_test_gpu_select_previous_write((value))
#define OPEN_CFW_PWRCTRL_GPU_SELECT_PERIPH_ENABLED(id, enabled) \
    open_cfw_test_gpu_select_periph_enabled((id), (enabled))
#define OPEN_CFW_PWRCTRL_GPU_SELECT_IRQ_DISABLE() \
    open_cfw_test_gpu_select_irq_disable()
#define OPEN_CFW_PWRCTRL_GPU_SELECT_IRQ_RESTORE(primask) \
    open_cfw_test_gpu_select_irq_restore((primask))
#define OPEN_CFW_PWRCTRL_GPU_SELECT_DELAY_US(microseconds) \
    open_cfw_test_gpu_select_delay((microseconds))
#define OPEN_CFW_PWRCTRL_GPU_SELECT_TON_UPDATE(enabled, mode) \
    open_cfw_test_gpu_select_ton_update((enabled), (mode))

#include "../../components/apollo_main/core_overlay/pwrctrl_gpu_mode_select.c"
