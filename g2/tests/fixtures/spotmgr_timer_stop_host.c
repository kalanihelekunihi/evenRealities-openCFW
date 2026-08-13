#include <stdint.h>

#define OPEN_CFW_TEST_SPOTMGR_TIMER_STOP_EVENT_CAPACITY 9U
#define OPEN_CFW_TEST_SPOTMGR_TIMER_STOP_EVENT_CLOCK 1U
#define OPEN_CFW_TEST_SPOTMGR_TIMER_STOP_EVENT_READ 2U
#define OPEN_CFW_TEST_SPOTMGR_TIMER_STOP_EVENT_WRITE 3U

#define OPEN_CFW_TEST_SPOTMGR_TIMER_STOP_CTRL0 0x400083E0U
#define OPEN_CFW_TEST_SPOTMGR_TIMER_STOP_GLOBEN 0x40008010U
#define OPEN_CFW_TEST_SPOTMGR_TIMER_STOP_INTCLR 0x40008068U
#define OPEN_CFW_TEST_SPOTMGR_TIMER_STOP_NVIC_ICER 0xE000E188U
#define OPEN_CFW_TEST_SPOTMGR_TIMER_STOP_NVIC_ICPR 0xE000E288U
#define OPEN_CFW_TEST_SPOTMGR_TIMER_STOP_SYSBUS_FLUSH 0x47FF0000U

uint32_t open_cfw_test_spotmgr_timer_stop_ctrl0;
uint32_t open_cfw_test_spotmgr_timer_stop_globen;
uint32_t open_cfw_test_spotmgr_timer_stop_intclr;
uint32_t open_cfw_test_spotmgr_timer_stop_nvic_icer;
uint32_t open_cfw_test_spotmgr_timer_stop_nvic_icpr;
uint32_t open_cfw_test_spotmgr_timer_stop_sysbus_flush;
uint32_t open_cfw_test_spotmgr_timer_stop_clock_result;
uint32_t open_cfw_test_spotmgr_timer_stop_event_count;
uint32_t open_cfw_test_spotmgr_timer_stop_event_kinds[
    OPEN_CFW_TEST_SPOTMGR_TIMER_STOP_EVENT_CAPACITY
];
uint32_t open_cfw_test_spotmgr_timer_stop_event_a[
    OPEN_CFW_TEST_SPOTMGR_TIMER_STOP_EVENT_CAPACITY
];
uint32_t open_cfw_test_spotmgr_timer_stop_event_b[
    OPEN_CFW_TEST_SPOTMGR_TIMER_STOP_EVENT_CAPACITY
];

static void
open_cfw_test_spotmgr_timer_stop_record(
    uint32_t kind,
    uint32_t a,
    uint32_t b
)
{
    uint32_t index = open_cfw_test_spotmgr_timer_stop_event_count;

    if (index < OPEN_CFW_TEST_SPOTMGR_TIMER_STOP_EVENT_CAPACITY) {
        open_cfw_test_spotmgr_timer_stop_event_kinds[index] = kind;
        open_cfw_test_spotmgr_timer_stop_event_a[index] = a;
        open_cfw_test_spotmgr_timer_stop_event_b[index] = b;
    }
    ++open_cfw_test_spotmgr_timer_stop_event_count;
}

static uint32_t
open_cfw_test_spotmgr_timer_stop_read32(uint32_t address)
{
    uint32_t value = 0U;

    if (address == OPEN_CFW_TEST_SPOTMGR_TIMER_STOP_CTRL0) {
        value = open_cfw_test_spotmgr_timer_stop_ctrl0;
    }
    else if (address == OPEN_CFW_TEST_SPOTMGR_TIMER_STOP_GLOBEN) {
        value = open_cfw_test_spotmgr_timer_stop_globen;
    }
    else if (address == OPEN_CFW_TEST_SPOTMGR_TIMER_STOP_SYSBUS_FLUSH) {
        value = open_cfw_test_spotmgr_timer_stop_sysbus_flush;
    }

    open_cfw_test_spotmgr_timer_stop_record(
        OPEN_CFW_TEST_SPOTMGR_TIMER_STOP_EVENT_READ,
        address,
        value
    );
    return value;
}

static void
open_cfw_test_spotmgr_timer_stop_write32(
    uint32_t address,
    uint32_t value
)
{
    if (address == OPEN_CFW_TEST_SPOTMGR_TIMER_STOP_CTRL0) {
        open_cfw_test_spotmgr_timer_stop_ctrl0 = value;
    }
    else if (address == OPEN_CFW_TEST_SPOTMGR_TIMER_STOP_GLOBEN) {
        open_cfw_test_spotmgr_timer_stop_globen = value;
    }
    else if (address == OPEN_CFW_TEST_SPOTMGR_TIMER_STOP_INTCLR) {
        open_cfw_test_spotmgr_timer_stop_intclr = value;
    }
    else if (address == OPEN_CFW_TEST_SPOTMGR_TIMER_STOP_NVIC_ICER) {
        open_cfw_test_spotmgr_timer_stop_nvic_icer = value;
    }
    else if (address == OPEN_CFW_TEST_SPOTMGR_TIMER_STOP_NVIC_ICPR) {
        open_cfw_test_spotmgr_timer_stop_nvic_icpr = value;
    }

    open_cfw_test_spotmgr_timer_stop_record(
        OPEN_CFW_TEST_SPOTMGR_TIMER_STOP_EVENT_WRITE,
        address,
        value
    );
}

static uint32_t
open_cfw_test_spotmgr_timer_stop_clock_release(
    uint32_t clock,
    uint32_t user
)
{
    open_cfw_test_spotmgr_timer_stop_record(
        OPEN_CFW_TEST_SPOTMGR_TIMER_STOP_EVENT_CLOCK,
        clock,
        user
    );
    return open_cfw_test_spotmgr_timer_stop_clock_result;
}

#define OPEN_CFW_SPOTMGR_TIMER_STOP_READ32(address) \
    open_cfw_test_spotmgr_timer_stop_read32(address)
#define OPEN_CFW_SPOTMGR_TIMER_STOP_WRITE32(address, value) \
    open_cfw_test_spotmgr_timer_stop_write32((address), (value))
#define OPEN_CFW_SPOTMGR_TIMER_STOP_CLOCK_RELEASE(clock, user) \
    open_cfw_test_spotmgr_timer_stop_clock_release((clock), (user))

#include "../../components/apollo_main/core_overlay/spotmgr_timer_stop.c"

void
open_cfw_test_spotmgr_timer_stop_reset(
    uint32_t ctrl0,
    uint32_t globen,
    uint32_t sysbus_flush,
    uint32_t sentinel,
    uint32_t clock_result
)
{
    uint32_t index;

    open_cfw_test_spotmgr_timer_stop_ctrl0 = ctrl0;
    open_cfw_test_spotmgr_timer_stop_globen = globen;
    open_cfw_test_spotmgr_timer_stop_intclr = sentinel;
    open_cfw_test_spotmgr_timer_stop_nvic_icer = sentinel;
    open_cfw_test_spotmgr_timer_stop_nvic_icpr = sentinel;
    open_cfw_test_spotmgr_timer_stop_sysbus_flush = sysbus_flush;
    open_cfw_test_spotmgr_timer_stop_clock_result = clock_result;
    open_cfw_test_spotmgr_timer_stop_event_count = 0U;

    for (
        index = 0U;
        index < OPEN_CFW_TEST_SPOTMGR_TIMER_STOP_EVENT_CAPACITY;
        ++index
    ) {
        open_cfw_test_spotmgr_timer_stop_event_kinds[index] = 0U;
        open_cfw_test_spotmgr_timer_stop_event_a[index] = 0U;
        open_cfw_test_spotmgr_timer_stop_event_b[index] = 0U;
    }
}
