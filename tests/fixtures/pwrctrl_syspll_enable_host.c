#include <stddef.h>
#include <stdint.h>

#define OPEN_CFW_TEST_SYSPLL_TRACE_CAPACITY 32U

enum {
    OPEN_CFW_TEST_SYSPLL_IRQ_DISABLE = 1U,
    OPEN_CFW_TEST_SYSPLL_READ = 2U,
    OPEN_CFW_TEST_SYSPLL_WRITE = 3U,
    OPEN_CFW_TEST_SYSPLL_DELAY = 4U,
    OPEN_CFW_TEST_SYSPLL_IRQ_RESTORE = 5U,
};

uint32_t open_cfw_test_syspll_chip_revision;
uint32_t open_cfw_test_syspll_d2aspare;
uint32_t open_cfw_test_syspll_pllctl0;
uint32_t open_cfw_test_syspll_primask;
uint32_t open_cfw_test_syspll_restored_primask;
uint32_t open_cfw_test_syspll_pll_inject_after_first_write;
uint32_t open_cfw_test_syspll_pll_write_count;
uint32_t open_cfw_test_syspll_trace_count;
uint32_t open_cfw_test_syspll_trace_event[
    OPEN_CFW_TEST_SYSPLL_TRACE_CAPACITY
];
uint32_t open_cfw_test_syspll_trace_address[
    OPEN_CFW_TEST_SYSPLL_TRACE_CAPACITY
];
uint32_t open_cfw_test_syspll_trace_value[
    OPEN_CFW_TEST_SYSPLL_TRACE_CAPACITY
];

static void
open_cfw_test_syspll_trace(
    uint32_t event,
    uint32_t address,
    uint32_t value
)
{
    uint32_t index = open_cfw_test_syspll_trace_count++;

    if (index < OPEN_CFW_TEST_SYSPLL_TRACE_CAPACITY) {
        open_cfw_test_syspll_trace_event[index] = event;
        open_cfw_test_syspll_trace_address[index] = address;
        open_cfw_test_syspll_trace_value[index] = value;
    }
}

static uint32_t
open_cfw_test_syspll_read32(uint32_t address)
{
    uint32_t value;

    if (address == 0x4002000CU) {
        value = open_cfw_test_syspll_chip_revision;
    }
    else if (address == 0x400201B0U) {
        value = open_cfw_test_syspll_d2aspare;
    }
    else if (address == 0x400204D8U) {
        value = open_cfw_test_syspll_pllctl0;
    }
    else {
        value = 0U;
    }

    open_cfw_test_syspll_trace(
        OPEN_CFW_TEST_SYSPLL_READ,
        address,
        value
    );
    return value;
}

static void
open_cfw_test_syspll_write32(uint32_t address, uint32_t value)
{
    open_cfw_test_syspll_trace(
        OPEN_CFW_TEST_SYSPLL_WRITE,
        address,
        value
    );
    if (address == 0x400201B0U) {
        open_cfw_test_syspll_d2aspare = value;
    }
    else if (address == 0x400204D8U) {
        ++open_cfw_test_syspll_pll_write_count;
        open_cfw_test_syspll_pllctl0 = value;
        if (open_cfw_test_syspll_pll_write_count == 1U) {
            open_cfw_test_syspll_pllctl0 |=
                open_cfw_test_syspll_pll_inject_after_first_write;
        }
    }
}

static uint32_t
open_cfw_test_syspll_irq_disable(void)
{
    open_cfw_test_syspll_trace(
        OPEN_CFW_TEST_SYSPLL_IRQ_DISABLE,
        0U,
        open_cfw_test_syspll_primask
    );
    return open_cfw_test_syspll_primask;
}

static void
open_cfw_test_syspll_irq_restore(uint32_t primask)
{
    open_cfw_test_syspll_restored_primask = primask;
    open_cfw_test_syspll_trace(
        OPEN_CFW_TEST_SYSPLL_IRQ_RESTORE,
        0U,
        primask
    );
}

static void
open_cfw_test_syspll_delay_us(uint32_t microseconds)
{
    open_cfw_test_syspll_trace(
        OPEN_CFW_TEST_SYSPLL_DELAY,
        0U,
        microseconds
    );
}

#define OPEN_CFW_PWRCTRL_SYSPLL_READ32(address) \
    open_cfw_test_syspll_read32(address)
#define OPEN_CFW_PWRCTRL_SYSPLL_WRITE32(address, value) \
    open_cfw_test_syspll_write32((address), (value))
#define OPEN_CFW_PWRCTRL_SYSPLL_IRQ_DISABLE() \
    open_cfw_test_syspll_irq_disable()
#define OPEN_CFW_PWRCTRL_SYSPLL_IRQ_RESTORE(primask) \
    open_cfw_test_syspll_irq_restore(primask)
#define OPEN_CFW_PWRCTRL_SYSPLL_DELAY_US(microseconds) \
    open_cfw_test_syspll_delay_us(microseconds)

#include "../../components/apollo_main/core_overlay/pwrctrl_syspll_enable.c"

void
open_cfw_test_syspll_reset(
    uint32_t revision,
    uint32_t d2aspare,
    uint32_t pllctl0,
    uint32_t primask,
    uint32_t injected_pll_bits
)
{
    uint32_t index;

    open_cfw_test_syspll_chip_revision = revision;
    open_cfw_test_syspll_d2aspare = d2aspare;
    open_cfw_test_syspll_pllctl0 = pllctl0;
    open_cfw_test_syspll_primask = primask;
    open_cfw_test_syspll_restored_primask = 0xFFFFFFFFU;
    open_cfw_test_syspll_pll_inject_after_first_write =
        injected_pll_bits;
    open_cfw_test_syspll_pll_write_count = 0U;
    open_cfw_test_syspll_trace_count = 0U;

    for (index = 0U; index < OPEN_CFW_TEST_SYSPLL_TRACE_CAPACITY; ++index) {
        open_cfw_test_syspll_trace_event[index] = 0U;
        open_cfw_test_syspll_trace_address[index] = 0U;
        open_cfw_test_syspll_trace_value[index] = 0U;
    }
}
