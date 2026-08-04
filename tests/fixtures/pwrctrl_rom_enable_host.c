#include <stddef.h>

unsigned int open_cfw_test_rom_enable_mode;
unsigned int open_cfw_test_rom_enable_memory_enable;
unsigned int open_cfw_test_rom_enable_memory_status;
unsigned int open_cfw_test_rom_enable_spot_result;
unsigned int open_cfw_test_rom_enable_ready_after_polls;
unsigned int open_cfw_test_rom_enable_poll_reads;
unsigned int open_cfw_test_rom_enable_spot_calls;
unsigned int open_cfw_test_rom_enable_spot_stimulus;
unsigned int open_cfw_test_rom_enable_spot_enabled;
unsigned int open_cfw_test_rom_enable_spot_value;
unsigned int open_cfw_test_rom_enable_trace_count;
unsigned int open_cfw_test_rom_enable_trace_event[64];
unsigned int open_cfw_test_rom_enable_trace_value[64];
unsigned int open_cfw_test_rom_enable_polling;

enum {
    OPEN_CFW_TEST_ROM_ENABLE_MODE_READ = 1,
    OPEN_CFW_TEST_ROM_ENABLE_STATUS_READ = 2,
    OPEN_CFW_TEST_ROM_ENABLE_SPOT_UPDATE = 3,
    OPEN_CFW_TEST_ROM_ENABLE_ENABLE_READ = 4,
    OPEN_CFW_TEST_ROM_ENABLE_ENABLE_WRITE = 5,
};

static void
open_cfw_test_rom_enable_trace(
    unsigned int event,
    unsigned int value
)
{
    unsigned int index = open_cfw_test_rom_enable_trace_count++;

    if (index < 64U) {
        open_cfw_test_rom_enable_trace_event[index] = event;
        open_cfw_test_rom_enable_trace_value[index] = value;
    }
}

static unsigned int
open_cfw_test_rom_enable_mode_read(void)
{
    unsigned int mode =
        (unsigned int)(unsigned char)open_cfw_test_rom_enable_mode;

    open_cfw_test_rom_enable_trace(
        OPEN_CFW_TEST_ROM_ENABLE_MODE_READ,
        mode
    );
    return mode;
}

static unsigned int
open_cfw_test_rom_enable_read(unsigned int address)
{
    if (address == 0x40021018U) {
        if (open_cfw_test_rom_enable_polling != 0U) {
            ++open_cfw_test_rom_enable_poll_reads;
            if (
                open_cfw_test_rom_enable_ready_after_polls
                    < open_cfw_test_rom_enable_poll_reads
            ) {
                open_cfw_test_rom_enable_memory_status |= 0x80U;
            }
        }
        open_cfw_test_rom_enable_trace(
            OPEN_CFW_TEST_ROM_ENABLE_STATUS_READ,
            open_cfw_test_rom_enable_memory_status
        );
        return open_cfw_test_rom_enable_memory_status;
    }

    if (address == 0x40021014U) {
        open_cfw_test_rom_enable_trace(
            OPEN_CFW_TEST_ROM_ENABLE_ENABLE_READ,
            open_cfw_test_rom_enable_memory_enable
        );
        return open_cfw_test_rom_enable_memory_enable;
    }

    return 0U;
}

static void
open_cfw_test_rom_enable_write(
    unsigned int address,
    unsigned int value
)
{
    if (address == 0x40021014U) {
        open_cfw_test_rom_enable_memory_enable = value;
        open_cfw_test_rom_enable_polling = 1U;
        open_cfw_test_rom_enable_trace(
            OPEN_CFW_TEST_ROM_ENABLE_ENABLE_WRITE,
            value
        );
    }
}

static unsigned int
open_cfw_test_rom_enable_spot_update(
    unsigned int stimulus,
    unsigned int enabled,
    const void *value
)
{
    ++open_cfw_test_rom_enable_spot_calls;
    open_cfw_test_rom_enable_spot_stimulus = stimulus;
    open_cfw_test_rom_enable_spot_enabled = enabled;
    open_cfw_test_rom_enable_spot_value =
        *(const unsigned int *)value;
    open_cfw_test_rom_enable_trace(
        OPEN_CFW_TEST_ROM_ENABLE_SPOT_UPDATE,
        open_cfw_test_rom_enable_spot_value
    );
    return open_cfw_test_rom_enable_spot_result;
}

#define OPEN_CFW_PWRCTRL_ROM_ENABLE_MODE_READ() \
    open_cfw_test_rom_enable_mode_read()
#define OPEN_CFW_PWRCTRL_ROM_ENABLE_READ(address) \
    open_cfw_test_rom_enable_read(address)
#define OPEN_CFW_PWRCTRL_ROM_ENABLE_WRITE(address, value) \
    open_cfw_test_rom_enable_write((address), (value))
#define OPEN_CFW_PWRCTRL_ROM_ENABLE_SPOT_UPDATE( \
    stimulus, enabled, value \
) \
    open_cfw_test_rom_enable_spot_update( \
        (stimulus), \
        (enabled), \
        (value) \
    )

#include "../../components/apollo_main/core_overlay/pwrctrl_rom_enable.c"

void
open_cfw_test_rom_enable_reset(void)
{
    unsigned int index;

    open_cfw_test_rom_enable_mode = 0U;
    open_cfw_test_rom_enable_memory_enable = 0U;
    open_cfw_test_rom_enable_memory_status = 0U;
    open_cfw_test_rom_enable_spot_result = 0U;
    open_cfw_test_rom_enable_ready_after_polls = 10000U;
    open_cfw_test_rom_enable_poll_reads = 0U;
    open_cfw_test_rom_enable_spot_calls = 0U;
    open_cfw_test_rom_enable_spot_stimulus = 0U;
    open_cfw_test_rom_enable_spot_enabled = 0U;
    open_cfw_test_rom_enable_spot_value = 0U;
    open_cfw_test_rom_enable_trace_count = 0U;
    open_cfw_test_rom_enable_polling = 0U;
    for (index = 0U; index < 64U; ++index) {
        open_cfw_test_rom_enable_trace_event[index] = 0U;
        open_cfw_test_rom_enable_trace_value[index] = 0U;
    }
}
