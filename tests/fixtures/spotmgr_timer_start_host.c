#include <stdint.h>

#define OPEN_CFW_TEST_SPOTMGR_TIMER_START_EVENT_CAPACITY 11U
#define OPEN_CFW_TEST_SPOTMGR_TIMER_START_EVENT_CLOCK 1U
#define OPEN_CFW_TEST_SPOTMGR_TIMER_START_EVENT_READ 2U
#define OPEN_CFW_TEST_SPOTMGR_TIMER_START_EVENT_WRITE 3U

#define OPEN_CFW_TEST_SPOTMGR_TIMER_START_CTRL0 0x400083E0U
#define OPEN_CFW_TEST_SPOTMGR_TIMER_START_COMPARE0 0x400083E8U
#define OPEN_CFW_TEST_SPOTMGR_TIMER_START_GLOBEN 0x40008010U
#define OPEN_CFW_TEST_SPOTMGR_TIMER_START_NVIC_ISER 0xE000E108U

uint32_t open_cfw_test_spotmgr_timer_start_ctrl0;
uint32_t open_cfw_test_spotmgr_timer_start_compare0;
uint32_t open_cfw_test_spotmgr_timer_start_globen;
uint32_t open_cfw_test_spotmgr_timer_start_nvic_iser;
uint32_t open_cfw_test_spotmgr_timer_start_clock_result;
uint32_t open_cfw_test_spotmgr_timer_start_event_count;
uint32_t open_cfw_test_spotmgr_timer_start_event_kinds[
    OPEN_CFW_TEST_SPOTMGR_TIMER_START_EVENT_CAPACITY
];
uint32_t open_cfw_test_spotmgr_timer_start_event_a[
    OPEN_CFW_TEST_SPOTMGR_TIMER_START_EVENT_CAPACITY
];
uint32_t open_cfw_test_spotmgr_timer_start_event_b[
    OPEN_CFW_TEST_SPOTMGR_TIMER_START_EVENT_CAPACITY
];

static void
open_cfw_test_spotmgr_timer_start_record(
    uint32_t kind,
    uint32_t a,
    uint32_t b
)
{
    uint32_t index = open_cfw_test_spotmgr_timer_start_event_count;

    if (index < OPEN_CFW_TEST_SPOTMGR_TIMER_START_EVENT_CAPACITY) {
        open_cfw_test_spotmgr_timer_start_event_kinds[index] = kind;
        open_cfw_test_spotmgr_timer_start_event_a[index] = a;
        open_cfw_test_spotmgr_timer_start_event_b[index] = b;
    }
    ++open_cfw_test_spotmgr_timer_start_event_count;
}

static uint32_t
open_cfw_test_spotmgr_timer_start_read32(uint32_t address)
{
    uint32_t value = 0U;

    if (address == OPEN_CFW_TEST_SPOTMGR_TIMER_START_CTRL0) {
        value = open_cfw_test_spotmgr_timer_start_ctrl0;
    }
    else if (address == OPEN_CFW_TEST_SPOTMGR_TIMER_START_GLOBEN) {
        value = open_cfw_test_spotmgr_timer_start_globen;
    }

    open_cfw_test_spotmgr_timer_start_record(
        OPEN_CFW_TEST_SPOTMGR_TIMER_START_EVENT_READ,
        address,
        value
    );
    return value;
}

static void
open_cfw_test_spotmgr_timer_start_write32(
    uint32_t address,
    uint32_t value
)
{
    if (address == OPEN_CFW_TEST_SPOTMGR_TIMER_START_CTRL0) {
        open_cfw_test_spotmgr_timer_start_ctrl0 = value;
    }
    else if (address == OPEN_CFW_TEST_SPOTMGR_TIMER_START_COMPARE0) {
        open_cfw_test_spotmgr_timer_start_compare0 = value;
    }
    else if (address == OPEN_CFW_TEST_SPOTMGR_TIMER_START_GLOBEN) {
        open_cfw_test_spotmgr_timer_start_globen = value;
    }
    else if (address == OPEN_CFW_TEST_SPOTMGR_TIMER_START_NVIC_ISER) {
        open_cfw_test_spotmgr_timer_start_nvic_iser = value;
    }

    open_cfw_test_spotmgr_timer_start_record(
        OPEN_CFW_TEST_SPOTMGR_TIMER_START_EVENT_WRITE,
        address,
        value
    );
}

static uint32_t
open_cfw_test_spotmgr_timer_start_clock_request(
    uint32_t clock,
    uint32_t user
)
{
    open_cfw_test_spotmgr_timer_start_record(
        OPEN_CFW_TEST_SPOTMGR_TIMER_START_EVENT_CLOCK,
        clock,
        user
    );
    return open_cfw_test_spotmgr_timer_start_clock_result;
}

#define OPEN_CFW_SPOTMGR_TIMER_START_READ32(address) \
    open_cfw_test_spotmgr_timer_start_read32(address)
#define OPEN_CFW_SPOTMGR_TIMER_START_WRITE32(address, value) \
    open_cfw_test_spotmgr_timer_start_write32((address), (value))
#define OPEN_CFW_SPOTMGR_TIMER_START_CLOCK_REQUEST(clock, user) \
    open_cfw_test_spotmgr_timer_start_clock_request((clock), (user))

#include "../../components/apollo_main/core_overlay/spotmgr_timer_start.c"

void
open_cfw_test_spotmgr_timer_start_reset(
    uint32_t ctrl0,
    uint32_t globen,
    uint32_t sentinel,
    uint32_t clock_result
)
{
    uint32_t index;

    open_cfw_test_spotmgr_timer_start_ctrl0 = ctrl0;
    open_cfw_test_spotmgr_timer_start_compare0 = sentinel;
    open_cfw_test_spotmgr_timer_start_globen = globen;
    open_cfw_test_spotmgr_timer_start_nvic_iser = sentinel;
    open_cfw_test_spotmgr_timer_start_clock_result = clock_result;
    open_cfw_test_spotmgr_timer_start_event_count = 0U;

    for (
        index = 0U;
        index < OPEN_CFW_TEST_SPOTMGR_TIMER_START_EVENT_CAPACITY;
        ++index
    ) {
        open_cfw_test_spotmgr_timer_start_event_kinds[index] = 0U;
        open_cfw_test_spotmgr_timer_start_event_a[index] = 0U;
        open_cfw_test_spotmgr_timer_start_event_b[index] = 0U;
    }
}
