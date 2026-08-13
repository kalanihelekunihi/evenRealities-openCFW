#include <stdint.h>

#define OPEN_CFW_TEST_SPOTMGR_TIMER_EVENT_CAPACITY 9U
#define OPEN_CFW_TEST_SPOTMGR_TIMER_EVENT_READ 1U
#define OPEN_CFW_TEST_SPOTMGR_TIMER_EVENT_WRITE 2U

#define OPEN_CFW_TEST_SPOTMGR_TIMER_CTRL0 0x400083E0U
#define OPEN_CFW_TEST_SPOTMGR_TIMER_COMPARE0 0x400083E8U
#define OPEN_CFW_TEST_SPOTMGR_TIMER_COMPARE1 0x400083ECU
#define OPEN_CFW_TEST_SPOTMGR_TIMER_MODE0 0x400083F0U
#define OPEN_CFW_TEST_SPOTMGR_TIMER_INTEN 0x40008060U
#define OPEN_CFW_TEST_SPOTMGR_TIMER_INTCLR 0x40008068U

uint32_t open_cfw_test_spotmgr_timer_ctrl0;
uint32_t open_cfw_test_spotmgr_timer_compare0;
uint32_t open_cfw_test_spotmgr_timer_compare1;
uint32_t open_cfw_test_spotmgr_timer_mode0;
uint32_t open_cfw_test_spotmgr_timer_inten;
uint32_t open_cfw_test_spotmgr_timer_intclr;
uint32_t open_cfw_test_spotmgr_timer_event_count;
uint32_t open_cfw_test_spotmgr_timer_event_kinds[
    OPEN_CFW_TEST_SPOTMGR_TIMER_EVENT_CAPACITY
];
uint32_t open_cfw_test_spotmgr_timer_event_addresses[
    OPEN_CFW_TEST_SPOTMGR_TIMER_EVENT_CAPACITY
];
uint32_t open_cfw_test_spotmgr_timer_event_values[
    OPEN_CFW_TEST_SPOTMGR_TIMER_EVENT_CAPACITY
];

static void
open_cfw_test_spotmgr_timer_record(
    uint32_t kind,
    uint32_t address,
    uint32_t value
)
{
    uint32_t index = open_cfw_test_spotmgr_timer_event_count;

    if (index < OPEN_CFW_TEST_SPOTMGR_TIMER_EVENT_CAPACITY) {
        open_cfw_test_spotmgr_timer_event_kinds[index] = kind;
        open_cfw_test_spotmgr_timer_event_addresses[index] = address;
        open_cfw_test_spotmgr_timer_event_values[index] = value;
    }
    ++open_cfw_test_spotmgr_timer_event_count;
}

static uint32_t
open_cfw_test_spotmgr_timer_read32(uint32_t address)
{
    uint32_t value = 0U;

    if (address == OPEN_CFW_TEST_SPOTMGR_TIMER_CTRL0) {
        value = open_cfw_test_spotmgr_timer_ctrl0;
    }
    else if (address == OPEN_CFW_TEST_SPOTMGR_TIMER_INTEN) {
        value = open_cfw_test_spotmgr_timer_inten;
    }

    open_cfw_test_spotmgr_timer_record(
        OPEN_CFW_TEST_SPOTMGR_TIMER_EVENT_READ,
        address,
        value
    );
    return value;
}

static void
open_cfw_test_spotmgr_timer_write32(uint32_t address, uint32_t value)
{
    if (address == OPEN_CFW_TEST_SPOTMGR_TIMER_CTRL0) {
        open_cfw_test_spotmgr_timer_ctrl0 = value;
    }
    else if (address == OPEN_CFW_TEST_SPOTMGR_TIMER_COMPARE0) {
        open_cfw_test_spotmgr_timer_compare0 = value;
    }
    else if (address == OPEN_CFW_TEST_SPOTMGR_TIMER_COMPARE1) {
        open_cfw_test_spotmgr_timer_compare1 = value;
    }
    else if (address == OPEN_CFW_TEST_SPOTMGR_TIMER_MODE0) {
        open_cfw_test_spotmgr_timer_mode0 = value;
    }
    else if (address == OPEN_CFW_TEST_SPOTMGR_TIMER_INTEN) {
        open_cfw_test_spotmgr_timer_inten = value;
    }
    else if (address == OPEN_CFW_TEST_SPOTMGR_TIMER_INTCLR) {
        open_cfw_test_spotmgr_timer_intclr = value;
    }

    open_cfw_test_spotmgr_timer_record(
        OPEN_CFW_TEST_SPOTMGR_TIMER_EVENT_WRITE,
        address,
        value
    );
}

#define OPEN_CFW_SPOTMGR_TIMER_INIT_READ32(address) \
    open_cfw_test_spotmgr_timer_read32(address)
#define OPEN_CFW_SPOTMGR_TIMER_INIT_WRITE32(address, value) \
    open_cfw_test_spotmgr_timer_write32((address), (value))

#include "../../components/apollo_main/core_overlay/spotmgr_timer_init.c"

void
open_cfw_test_spotmgr_timer_reset(
    uint32_t ctrl0,
    uint32_t inten,
    uint32_t sentinel
)
{
    uint32_t index;

    open_cfw_test_spotmgr_timer_ctrl0 = ctrl0;
    open_cfw_test_spotmgr_timer_compare0 = sentinel;
    open_cfw_test_spotmgr_timer_compare1 = sentinel;
    open_cfw_test_spotmgr_timer_mode0 = sentinel;
    open_cfw_test_spotmgr_timer_inten = inten;
    open_cfw_test_spotmgr_timer_intclr = sentinel;
    open_cfw_test_spotmgr_timer_event_count = 0U;

    for (
        index = 0U;
        index < OPEN_CFW_TEST_SPOTMGR_TIMER_EVENT_CAPACITY;
        ++index
    ) {
        open_cfw_test_spotmgr_timer_event_kinds[index] = 0U;
        open_cfw_test_spotmgr_timer_event_addresses[index] = 0U;
        open_cfw_test_spotmgr_timer_event_values[index] = 0U;
    }
}
