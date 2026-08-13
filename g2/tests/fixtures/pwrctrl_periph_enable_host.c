#include <stddef.h>
#include <stdint.h>

#define OPEN_CFW_TEST_TRACE_CAPACITY 64U

enum {
    OPEN_CFW_TEST_EVENT_DESCRIPTOR = 1,
    OPEN_CFW_TEST_EVENT_READ,
    OPEN_CFW_TEST_EVENT_POSTPONE,
    OPEN_CFW_TEST_EVENT_GPU_SELECT,
    OPEN_CFW_TEST_EVENT_CLOCK,
    OPEN_CFW_TEST_EVENT_SPOT,
    OPEN_CFW_TEST_EVENT_IRQ_DISABLE,
    OPEN_CFW_TEST_EVENT_WRITE,
    OPEN_CFW_TEST_EVENT_IRQ_RESTORE,
    OPEN_CFW_TEST_EVENT_PENDING,
    OPEN_CFW_TEST_EVENT_STATUS_CHECK,
    OPEN_CFW_TEST_EVENT_STATUS_CHANGE,
    OPEN_CFW_TEST_EVENT_DELAY
};

unsigned int open_cfw_test_enable_trace_count;
unsigned int open_cfw_test_enable_trace_event[OPEN_CFW_TEST_TRACE_CAPACITY];
unsigned int open_cfw_test_enable_trace_a[OPEN_CFW_TEST_TRACE_CAPACITY];
unsigned int open_cfw_test_enable_trace_b[OPEN_CFW_TEST_TRACE_CAPACITY];
unsigned int open_cfw_test_enable_trace_c[OPEN_CFW_TEST_TRACE_CAPACITY];

unsigned int open_cfw_test_enable_descriptor_result;
unsigned int open_cfw_test_enable_enable_address;
unsigned int open_cfw_test_enable_enable_mask;
unsigned int open_cfw_test_enable_status_address;
unsigned int open_cfw_test_enable_status_mask;
unsigned int open_cfw_test_enable_enable_register;
unsigned int open_cfw_test_enable_status_register;
unsigned int open_cfw_test_enable_device_status;
unsigned int open_cfw_test_enable_current_mode;
unsigned int open_cfw_test_enable_previous_mode;
unsigned int open_cfw_test_enable_gpu_result;
unsigned int open_cfw_test_enable_spot_result;
unsigned int open_cfw_test_enable_status_check_result;
unsigned int open_cfw_test_enable_status_change_result;
unsigned int open_cfw_test_enable_primask;
unsigned int open_cfw_test_enable_status_equal;

static void
open_cfw_test_enable_record(
    unsigned int event,
    unsigned int a,
    unsigned int b,
    unsigned int c
)
{
    unsigned int index = open_cfw_test_enable_trace_count++;

    if (index < OPEN_CFW_TEST_TRACE_CAPACITY) {
        open_cfw_test_enable_trace_event[index] = event;
        open_cfw_test_enable_trace_a[index] = a;
        open_cfw_test_enable_trace_b[index] = b;
        open_cfw_test_enable_trace_c[index] = c;
    }
}

static unsigned int
open_cfw_test_enable_read(unsigned int address)
{
    unsigned int value = 0U;

    if (address == open_cfw_test_enable_enable_address) {
        value = open_cfw_test_enable_enable_register;
    }
    else if (address == open_cfw_test_enable_status_address) {
        value = open_cfw_test_enable_status_register;
    }
    else if (address == 0x40021008U) {
        value = open_cfw_test_enable_device_status;
    }
    open_cfw_test_enable_record(
        OPEN_CFW_TEST_EVENT_READ,
        address,
        value,
        0U
    );
    return value;
}

static void
open_cfw_test_enable_write(unsigned int address, unsigned int value)
{
    if (address == open_cfw_test_enable_enable_address) {
        open_cfw_test_enable_enable_register = value;
    }
    open_cfw_test_enable_record(
        OPEN_CFW_TEST_EVENT_WRITE,
        address,
        value,
        0U
    );
}

static unsigned int
open_cfw_test_enable_mode_read(unsigned int address)
{
    return address == 0x20074F60U
        ? open_cfw_test_enable_current_mode
        : open_cfw_test_enable_previous_mode;
}

static unsigned int open_cfw_test_enable_descriptor_get(
    void *,
    unsigned int
);
static void open_cfw_test_enable_postpone(void);
static void open_cfw_test_enable_pending(void);
static unsigned int open_cfw_test_enable_gpu_select(unsigned int);
static unsigned int open_cfw_test_enable_clock(unsigned int, unsigned int);
static unsigned int open_cfw_test_enable_spot(
    unsigned int,
    unsigned int,
    const void *
);
static unsigned int open_cfw_test_enable_irq_disable(void);
static void open_cfw_test_enable_irq_restore(unsigned int);
static unsigned int open_cfw_test_enable_status_check(
    unsigned int,
    unsigned int,
    unsigned int,
    unsigned int,
    unsigned int
);
static unsigned int open_cfw_test_enable_status_change(
    unsigned int,
    unsigned int,
    unsigned int,
    unsigned int
);
static void open_cfw_test_enable_delay(unsigned int);

#define OPEN_CFW_PWRCTRL_ENABLE_READ(address) \
    open_cfw_test_enable_read(address)
#define OPEN_CFW_PWRCTRL_ENABLE_WRITE(address, value) \
    open_cfw_test_enable_write((address), (value))
#define OPEN_CFW_PWRCTRL_ENABLE_MODE_READ(address) \
    open_cfw_test_enable_mode_read(address)
#define OPEN_CFW_PWRCTRL_ENABLE_DESCRIPTOR_GET(descriptor, peripheral) \
    open_cfw_test_enable_descriptor_get((descriptor), (peripheral))
#define OPEN_CFW_PWRCTRL_ENABLE_TEMP_CO_POSTPONE() \
    open_cfw_test_enable_postpone()
#define OPEN_CFW_PWRCTRL_ENABLE_TEMP_CO_PENDING() \
    open_cfw_test_enable_pending()
#define OPEN_CFW_PWRCTRL_ENABLE_GPU_MODE_SELECT(mode) \
    open_cfw_test_enable_gpu_select(mode)
#define OPEN_CFW_PWRCTRL_ENABLE_CLOCK_REQUEST(clock, user) \
    open_cfw_test_enable_clock((clock), (user))
#define OPEN_CFW_PWRCTRL_ENABLE_SPOT_UPDATE(stimulus, enabled, value) \
    open_cfw_test_enable_spot((stimulus), (enabled), (value))
#define OPEN_CFW_PWRCTRL_ENABLE_IRQ_DISABLE() \
    open_cfw_test_enable_irq_disable()
#define OPEN_CFW_PWRCTRL_ENABLE_IRQ_RESTORE(primask) \
    open_cfw_test_enable_irq_restore(primask)
#define OPEN_CFW_PWRCTRL_ENABLE_STATUS_CHECK( \
    wait, address, mask, expected, equal \
) \
    open_cfw_test_enable_status_check( \
        (wait), (address), (mask), (expected), (equal) \
    )
#define OPEN_CFW_PWRCTRL_ENABLE_STATUS_CHANGE(wait, address, mask, expected) \
    open_cfw_test_enable_status_change( \
        (wait), (address), (mask), (expected) \
    )
#define OPEN_CFW_PWRCTRL_ENABLE_DELAY_US(microseconds) \
    open_cfw_test_enable_delay(microseconds)

#include "../../components/apollo_main/core_overlay/pwrctrl_periph_enable.c"

static unsigned int
open_cfw_test_enable_descriptor_get(
    void *output,
    unsigned int peripheral
)
{
    open_cfw_pwrctrl_enable_descriptor *descriptor =
        (open_cfw_pwrctrl_enable_descriptor *)output;
    open_cfw_test_enable_record(
        OPEN_CFW_TEST_EVENT_DESCRIPTOR,
        peripheral,
        0U,
        0U
    );
    if (open_cfw_test_enable_descriptor_result != 0U) {
        return open_cfw_test_enable_descriptor_result;
    }
    descriptor->power_enable_register = open_cfw_test_enable_enable_address;
    descriptor->peripheral_enable_mask = open_cfw_test_enable_enable_mask;
    descriptor->power_status_register = open_cfw_test_enable_status_address;
    descriptor->peripheral_status_mask = open_cfw_test_enable_status_mask;
    return 0U;
}

static void open_cfw_test_enable_postpone(void)
{
    open_cfw_test_enable_record(
        OPEN_CFW_TEST_EVENT_POSTPONE, 0U, 0U, 0U
    );
}

static void open_cfw_test_enable_pending(void)
{
    open_cfw_test_enable_record(
        OPEN_CFW_TEST_EVENT_PENDING, 0U, 0U, 0U
    );
}

static unsigned int open_cfw_test_enable_gpu_select(unsigned int mode)
{
    open_cfw_test_enable_record(
        OPEN_CFW_TEST_EVENT_GPU_SELECT, mode, 0U, 0U
    );
    return open_cfw_test_enable_gpu_result;
}

static unsigned int
open_cfw_test_enable_clock(unsigned int clock, unsigned int user)
{
    open_cfw_test_enable_record(
        OPEN_CFW_TEST_EVENT_CLOCK, clock, user, 0U
    );
    return 17U;
}

static unsigned int
open_cfw_test_enable_spot(
    unsigned int stimulus,
    unsigned int enabled,
    const void *value
)
{
    unsigned int observed = stimulus == 1U
        ? *(const unsigned char *)value
        : *(const unsigned int *)value;
    open_cfw_test_enable_record(
        OPEN_CFW_TEST_EVENT_SPOT,
        stimulus,
        enabled,
        observed
    );
    return open_cfw_test_enable_spot_result;
}

static unsigned int open_cfw_test_enable_irq_disable(void)
{
    open_cfw_test_enable_record(
        OPEN_CFW_TEST_EVENT_IRQ_DISABLE,
        open_cfw_test_enable_primask,
        0U,
        0U
    );
    return open_cfw_test_enable_primask;
}

static void open_cfw_test_enable_irq_restore(unsigned int primask)
{
    open_cfw_test_enable_record(
        OPEN_CFW_TEST_EVENT_IRQ_RESTORE, primask, 0U, 0U
    );
}

static unsigned int
open_cfw_test_enable_status_check(
    unsigned int wait,
    unsigned int address,
    unsigned int mask,
    unsigned int expected,
    unsigned int equal
)
{
    open_cfw_test_enable_status_equal = equal;
    open_cfw_test_enable_record(
        OPEN_CFW_TEST_EVENT_STATUS_CHECK,
        wait,
        address,
        mask
    );
    if (expected != mask) {
        return 0xFFFFFFFFU;
    }
    return open_cfw_test_enable_status_check_result;
}

static unsigned int
open_cfw_test_enable_status_change(
    unsigned int wait,
    unsigned int address,
    unsigned int mask,
    unsigned int expected
)
{
    open_cfw_test_enable_record(
        OPEN_CFW_TEST_EVENT_STATUS_CHANGE,
        wait,
        address,
        mask
    );
    if (expected != mask) {
        return 0xFFFFFFFFU;
    }
    return open_cfw_test_enable_status_change_result;
}

static void open_cfw_test_enable_delay(unsigned int microseconds)
{
    open_cfw_test_enable_record(
        OPEN_CFW_TEST_EVENT_DELAY, microseconds, 0U, 0U
    );
}

void open_cfw_test_enable_reset(void)
{
    unsigned int index;

    open_cfw_test_enable_trace_count = 0U;
    for (index = 0U; index < OPEN_CFW_TEST_TRACE_CAPACITY; ++index) {
        open_cfw_test_enable_trace_event[index] = 0U;
        open_cfw_test_enable_trace_a[index] = 0U;
        open_cfw_test_enable_trace_b[index] = 0U;
        open_cfw_test_enable_trace_c[index] = 0U;
    }
    open_cfw_test_enable_descriptor_result = 0U;
    open_cfw_test_enable_enable_address = 0x1000U;
    open_cfw_test_enable_enable_mask = 0x20U;
    open_cfw_test_enable_status_address = 0x1004U;
    open_cfw_test_enable_status_mask = 0x200U;
    open_cfw_test_enable_enable_register = 0U;
    open_cfw_test_enable_status_register = 0x200U;
    open_cfw_test_enable_device_status = 0x08000000U;
    open_cfw_test_enable_current_mode = 0U;
    open_cfw_test_enable_previous_mode = 0U;
    open_cfw_test_enable_gpu_result = 0U;
    open_cfw_test_enable_spot_result = 0U;
    open_cfw_test_enable_status_check_result = 0U;
    open_cfw_test_enable_status_change_result = 0U;
    open_cfw_test_enable_primask = 1U;
    open_cfw_test_enable_status_equal = 0U;
}
