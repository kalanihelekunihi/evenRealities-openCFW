#include <stdint.h>

#define OPEN_CFW_TEST_SPOTMGR_TIMER_RESTART_EVENT_CAPACITY 11U
#define OPEN_CFW_TEST_SPOTMGR_TIMER_RESTART_EVENT_READ 1U
#define OPEN_CFW_TEST_SPOTMGR_TIMER_RESTART_EVENT_WRITE 2U

#define OPEN_CFW_TEST_SPOTMGR_TIMER_RESTART_CTRL0 0x400083E0U
#define OPEN_CFW_TEST_SPOTMGR_TIMER_RESTART_COMPARE0 0x400083E8U
#define OPEN_CFW_TEST_SPOTMGR_TIMER_RESTART_INTCLR 0x40008068U
#define OPEN_CFW_TEST_SPOTMGR_TIMER_RESTART_NVIC_ICPR 0xE000E288U

uint32_t open_cfw_test_spotmgr_timer_restart_ctrl0;
uint32_t open_cfw_test_spotmgr_timer_restart_compare0;
uint32_t open_cfw_test_spotmgr_timer_restart_intclr;
uint32_t open_cfw_test_spotmgr_timer_restart_nvic_icpr;
uint32_t open_cfw_test_spotmgr_timer_restart_event_count;
uint32_t open_cfw_test_spotmgr_timer_restart_event_kinds[
    OPEN_CFW_TEST_SPOTMGR_TIMER_RESTART_EVENT_CAPACITY
];
uint32_t open_cfw_test_spotmgr_timer_restart_event_addresses[
    OPEN_CFW_TEST_SPOTMGR_TIMER_RESTART_EVENT_CAPACITY
];
uint32_t open_cfw_test_spotmgr_timer_restart_event_values[
    OPEN_CFW_TEST_SPOTMGR_TIMER_RESTART_EVENT_CAPACITY
];

static void
open_cfw_test_spotmgr_timer_restart_record(
    uint32_t kind,
    uint32_t address,
    uint32_t value
)
{
    uint32_t index = open_cfw_test_spotmgr_timer_restart_event_count;

    if (index < OPEN_CFW_TEST_SPOTMGR_TIMER_RESTART_EVENT_CAPACITY) {
        open_cfw_test_spotmgr_timer_restart_event_kinds[index] = kind;
        open_cfw_test_spotmgr_timer_restart_event_addresses[index] = address;
        open_cfw_test_spotmgr_timer_restart_event_values[index] = value;
    }
    ++open_cfw_test_spotmgr_timer_restart_event_count;
}

static uint32_t
open_cfw_test_spotmgr_timer_restart_read32(uint32_t address)
{
    uint32_t value = 0U;

    if (address == OPEN_CFW_TEST_SPOTMGR_TIMER_RESTART_CTRL0) {
        value = open_cfw_test_spotmgr_timer_restart_ctrl0;
    }

    open_cfw_test_spotmgr_timer_restart_record(
        OPEN_CFW_TEST_SPOTMGR_TIMER_RESTART_EVENT_READ,
        address,
        value
    );
    return value;
}

static void
open_cfw_test_spotmgr_timer_restart_write32(
    uint32_t address,
    uint32_t value
)
{
    if (address == OPEN_CFW_TEST_SPOTMGR_TIMER_RESTART_CTRL0) {
        open_cfw_test_spotmgr_timer_restart_ctrl0 = value;
    }
    else if (address == OPEN_CFW_TEST_SPOTMGR_TIMER_RESTART_COMPARE0) {
        open_cfw_test_spotmgr_timer_restart_compare0 = value;
    }
    else if (address == OPEN_CFW_TEST_SPOTMGR_TIMER_RESTART_INTCLR) {
        open_cfw_test_spotmgr_timer_restart_intclr = value;
    }
    else if (address == OPEN_CFW_TEST_SPOTMGR_TIMER_RESTART_NVIC_ICPR) {
        open_cfw_test_spotmgr_timer_restart_nvic_icpr = value;
    }

    open_cfw_test_spotmgr_timer_restart_record(
        OPEN_CFW_TEST_SPOTMGR_TIMER_RESTART_EVENT_WRITE,
        address,
        value
    );
}

#define OPEN_CFW_SPOTMGR_TIMER_RESTART_READ32(address) \
    open_cfw_test_spotmgr_timer_restart_read32(address)
#define OPEN_CFW_SPOTMGR_TIMER_RESTART_WRITE32(address, value) \
    open_cfw_test_spotmgr_timer_restart_write32((address), (value))

#include "../../components/apollo_main/core_overlay/spotmgr_timer_restart.c"

void
open_cfw_test_spotmgr_timer_restart_reset(
    uint32_t ctrl0,
    uint32_t sentinel
)
{
    uint32_t index;

    open_cfw_test_spotmgr_timer_restart_ctrl0 = ctrl0;
    open_cfw_test_spotmgr_timer_restart_compare0 = sentinel;
    open_cfw_test_spotmgr_timer_restart_intclr = sentinel;
    open_cfw_test_spotmgr_timer_restart_nvic_icpr = sentinel;
    open_cfw_test_spotmgr_timer_restart_event_count = 0U;

    for (
        index = 0U;
        index < OPEN_CFW_TEST_SPOTMGR_TIMER_RESTART_EVENT_CAPACITY;
        ++index
    ) {
        open_cfw_test_spotmgr_timer_restart_event_kinds[index] = 0U;
        open_cfw_test_spotmgr_timer_restart_event_addresses[index] = 0U;
        open_cfw_test_spotmgr_timer_restart_event_values[index] = 0U;
    }
}
