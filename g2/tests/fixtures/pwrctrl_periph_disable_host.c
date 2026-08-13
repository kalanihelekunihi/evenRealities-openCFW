#include <stddef.h>
#include <stdint.h>

#define OPEN_CFW_TEST_DISABLE_TRACE_CAPACITY 96U

enum {
    OPEN_CFW_TEST_DISABLE_EVENT_DESCRIPTOR = 1,
    OPEN_CFW_TEST_DISABLE_EVENT_READ,
    OPEN_CFW_TEST_DISABLE_EVENT_WRITE,
    OPEN_CFW_TEST_DISABLE_EVENT_STATUS_CHECK,
    OPEN_CFW_TEST_DISABLE_EVENT_POSTPONE,
    OPEN_CFW_TEST_DISABLE_EVENT_IRQ_DISABLE,
    OPEN_CFW_TEST_DISABLE_EVENT_IRQ_RESTORE,
    OPEN_CFW_TEST_DISABLE_EVENT_MASK_CHECK,
    OPEN_CFW_TEST_DISABLE_EVENT_MODE_READ,
    OPEN_CFW_TEST_DISABLE_EVENT_MODE_WRITE,
    OPEN_CFW_TEST_DISABLE_EVENT_GPU_SELECT,
    OPEN_CFW_TEST_DISABLE_EVENT_SPOT,
    OPEN_CFW_TEST_DISABLE_EVENT_CLOCK_RELEASE,
    OPEN_CFW_TEST_DISABLE_EVENT_CLOCK_RELEASE_ALL,
    OPEN_CFW_TEST_DISABLE_EVENT_PENDING
};

unsigned int open_cfw_test_disable_trace_count;
unsigned int open_cfw_test_disable_trace_event[
    OPEN_CFW_TEST_DISABLE_TRACE_CAPACITY
];
unsigned int open_cfw_test_disable_trace_a[
    OPEN_CFW_TEST_DISABLE_TRACE_CAPACITY
];
unsigned int open_cfw_test_disable_trace_b[
    OPEN_CFW_TEST_DISABLE_TRACE_CAPACITY
];
unsigned int open_cfw_test_disable_trace_c[
    OPEN_CFW_TEST_DISABLE_TRACE_CAPACITY
];

unsigned int open_cfw_test_disable_descriptor_result;
unsigned int open_cfw_test_disable_enable_address;
unsigned int open_cfw_test_disable_enable_mask;
unsigned int open_cfw_test_disable_status_address;
unsigned int open_cfw_test_disable_status_mask;
unsigned int open_cfw_test_disable_enable_register;
unsigned int open_cfw_test_disable_status_register;
unsigned int open_cfw_test_disable_chip_revision;
unsigned int open_cfw_test_disable_device_status;
unsigned int open_cfw_test_disable_otp_status;
unsigned int open_cfw_test_disable_demcr;
unsigned int open_cfw_test_disable_debug_control;
unsigned int open_cfw_test_disable_current_mode;
unsigned int open_cfw_test_disable_previous_mode;
unsigned int open_cfw_test_disable_primask;
unsigned int open_cfw_test_disable_mask_result;
unsigned int open_cfw_test_disable_status_check_result;
unsigned int open_cfw_test_disable_spot_result;
unsigned int open_cfw_test_disable_gpu_result;
unsigned int open_cfw_test_disable_status_expected;
unsigned int open_cfw_test_disable_status_equal;
unsigned int open_cfw_test_disable_status_call_count;

static void
open_cfw_test_disable_record(
    unsigned int event,
    unsigned int a,
    unsigned int b,
    unsigned int c
)
{
    unsigned int index = open_cfw_test_disable_trace_count++;

    if (index < OPEN_CFW_TEST_DISABLE_TRACE_CAPACITY) {
        open_cfw_test_disable_trace_event[index] = event;
        open_cfw_test_disable_trace_a[index] = a;
        open_cfw_test_disable_trace_b[index] = b;
        open_cfw_test_disable_trace_c[index] = c;
    }
}

static unsigned int
open_cfw_test_disable_read(unsigned int address)
{
    unsigned int value = 0U;

    if (address == open_cfw_test_disable_enable_address) {
        value = open_cfw_test_disable_enable_register;
    }
    else if (address == open_cfw_test_disable_status_address) {
        value = open_cfw_test_disable_status_register;
    }
    else if (address == 0x4002000CU) {
        value = open_cfw_test_disable_chip_revision;
    }
    else if (address == 0x40021008U) {
        value = open_cfw_test_disable_device_status;
    }
    else if (address == 0x40014AC4U) {
        value = open_cfw_test_disable_otp_status;
    }
    else if (address == 0xE000EDFCU) {
        value = open_cfw_test_disable_demcr;
    }
    else if (address == 0x40020250U) {
        value = open_cfw_test_disable_debug_control;
    }
    open_cfw_test_disable_record(
        OPEN_CFW_TEST_DISABLE_EVENT_READ,
        address,
        value,
        0U
    );
    return value;
}

static void
open_cfw_test_disable_write(unsigned int address, unsigned int value)
{
    if (address == open_cfw_test_disable_enable_address) {
        open_cfw_test_disable_enable_register = value;
    }
    else if (address == 0xE000EDFCU) {
        open_cfw_test_disable_demcr = value;
    }
    else if (address == 0x40020250U) {
        open_cfw_test_disable_debug_control = value;
    }
    open_cfw_test_disable_record(
        OPEN_CFW_TEST_DISABLE_EVENT_WRITE,
        address,
        value,
        0U
    );
}

static unsigned int
open_cfw_test_disable_mode_read(unsigned int address)
{
    unsigned int value = address == 0x20074F60U
        ? open_cfw_test_disable_current_mode
        : open_cfw_test_disable_previous_mode;
    open_cfw_test_disable_record(
        OPEN_CFW_TEST_DISABLE_EVENT_MODE_READ,
        address,
        value,
        0U
    );
    return value;
}

static void
open_cfw_test_disable_mode_write(
    unsigned int address,
    unsigned int value
)
{
    if (address == 0x20074F61U) {
        open_cfw_test_disable_previous_mode = value & 0xFFU;
    }
    open_cfw_test_disable_record(
        OPEN_CFW_TEST_DISABLE_EVENT_MODE_WRITE,
        address,
        value & 0xFFU,
        0U
    );
}

static unsigned int open_cfw_test_disable_descriptor_get(
    void *,
    unsigned int
);
static void open_cfw_test_disable_postpone(void);
static void open_cfw_test_disable_pending(void);
static unsigned int open_cfw_test_disable_irq_disable(void);
static void open_cfw_test_disable_irq_restore(unsigned int);
static unsigned int open_cfw_test_disable_mask_check(unsigned int);
static unsigned int open_cfw_test_disable_status_check(
    unsigned int,
    unsigned int,
    unsigned int,
    unsigned int,
    unsigned int
);
static unsigned int open_cfw_test_disable_gpu_select(unsigned int);
static unsigned int open_cfw_test_disable_spot(
    unsigned int,
    unsigned int,
    const void *
);
static unsigned int open_cfw_test_disable_clock_release(
    unsigned int,
    unsigned int
);
static unsigned int open_cfw_test_disable_clock_release_all(
    unsigned int
);

#define OPEN_CFW_PWRCTRL_DISABLE_READ(address) \
    open_cfw_test_disable_read(address)
#define OPEN_CFW_PWRCTRL_DISABLE_WRITE(address, value) \
    open_cfw_test_disable_write((address), (value))
#define OPEN_CFW_PWRCTRL_DISABLE_MODE_READ(address) \
    open_cfw_test_disable_mode_read(address)
#define OPEN_CFW_PWRCTRL_DISABLE_MODE_WRITE(address, value) \
    open_cfw_test_disable_mode_write((address), (value))
#define OPEN_CFW_PWRCTRL_DISABLE_DESCRIPTOR_GET(descriptor, peripheral) \
    open_cfw_test_disable_descriptor_get((descriptor), (peripheral))
#define OPEN_CFW_PWRCTRL_DISABLE_TEMP_CO_POSTPONE() \
    open_cfw_test_disable_postpone()
#define OPEN_CFW_PWRCTRL_DISABLE_TEMP_CO_PENDING() \
    open_cfw_test_disable_pending()
#define OPEN_CFW_PWRCTRL_DISABLE_IRQ_DISABLE() \
    open_cfw_test_disable_irq_disable()
#define OPEN_CFW_PWRCTRL_DISABLE_IRQ_RESTORE(primask) \
    open_cfw_test_disable_irq_restore(primask)
#define OPEN_CFW_PWRCTRL_DISABLE_MASK_CHECK(peripheral) \
    open_cfw_test_disable_mask_check(peripheral)
#define OPEN_CFW_PWRCTRL_DISABLE_STATUS_CHECK( \
    wait, address, mask, expected, equal \
) \
    open_cfw_test_disable_status_check( \
        (wait), (address), (mask), (expected), (equal) \
    )
#define OPEN_CFW_PWRCTRL_DISABLE_GPU_MODE_SELECT(mode) \
    open_cfw_test_disable_gpu_select(mode)
#define OPEN_CFW_PWRCTRL_DISABLE_SPOT_UPDATE(stimulus, enabled, value) \
    open_cfw_test_disable_spot((stimulus), (enabled), (value))
#define OPEN_CFW_PWRCTRL_DISABLE_CLOCK_RELEASE(clock, user) \
    open_cfw_test_disable_clock_release((clock), (user))
#define OPEN_CFW_PWRCTRL_DISABLE_CLOCK_RELEASE_ALL(user) \
    open_cfw_test_disable_clock_release_all(user)

#include "../../components/apollo_main/core_overlay/pwrctrl_periph_disable.c"

static unsigned int
open_cfw_test_disable_descriptor_get(
    void *output,
    unsigned int peripheral
)
{
    open_cfw_pwrctrl_disable_descriptor *descriptor =
        (open_cfw_pwrctrl_disable_descriptor *)output;
    open_cfw_test_disable_record(
        OPEN_CFW_TEST_DISABLE_EVENT_DESCRIPTOR,
        peripheral,
        0U,
        0U
    );
    if (open_cfw_test_disable_descriptor_result != 0U) {
        return open_cfw_test_disable_descriptor_result;
    }
    descriptor->power_enable_register =
        open_cfw_test_disable_enable_address;
    descriptor->peripheral_enable_mask =
        open_cfw_test_disable_enable_mask;
    descriptor->power_status_register =
        open_cfw_test_disable_status_address;
    descriptor->peripheral_status_mask =
        open_cfw_test_disable_status_mask;
    return 0U;
}

static void open_cfw_test_disable_postpone(void)
{
    open_cfw_test_disable_record(
        OPEN_CFW_TEST_DISABLE_EVENT_POSTPONE,
        0U,
        0U,
        0U
    );
}

static void open_cfw_test_disable_pending(void)
{
    open_cfw_test_disable_record(
        OPEN_CFW_TEST_DISABLE_EVENT_PENDING,
        0U,
        0U,
        0U
    );
}

static unsigned int open_cfw_test_disable_irq_disable(void)
{
    open_cfw_test_disable_record(
        OPEN_CFW_TEST_DISABLE_EVENT_IRQ_DISABLE,
        open_cfw_test_disable_primask,
        0U,
        0U
    );
    return open_cfw_test_disable_primask;
}

static void open_cfw_test_disable_irq_restore(unsigned int primask)
{
    open_cfw_test_disable_record(
        OPEN_CFW_TEST_DISABLE_EVENT_IRQ_RESTORE,
        primask,
        0U,
        0U
    );
}

static unsigned int
open_cfw_test_disable_mask_check(unsigned int peripheral)
{
    open_cfw_test_disable_record(
        OPEN_CFW_TEST_DISABLE_EVENT_MASK_CHECK,
        peripheral,
        open_cfw_test_disable_mask_result,
        0U
    );
    return open_cfw_test_disable_mask_result;
}

static unsigned int
open_cfw_test_disable_status_check(
    unsigned int wait,
    unsigned int address,
    unsigned int mask,
    unsigned int expected,
    unsigned int equal
)
{
    ++open_cfw_test_disable_status_call_count;
    open_cfw_test_disable_status_expected = expected;
    open_cfw_test_disable_status_equal = equal;
    open_cfw_test_disable_record(
        OPEN_CFW_TEST_DISABLE_EVENT_STATUS_CHECK,
        wait,
        address,
        mask
    );
    return open_cfw_test_disable_status_check_result;
}

static unsigned int
open_cfw_test_disable_gpu_select(unsigned int mode)
{
    open_cfw_test_disable_record(
        OPEN_CFW_TEST_DISABLE_EVENT_GPU_SELECT,
        mode,
        0U,
        0U
    );
    return open_cfw_test_disable_gpu_result;
}

static unsigned int
open_cfw_test_disable_spot(
    unsigned int stimulus,
    unsigned int enabled,
    const void *value
)
{
    unsigned int observed = stimulus == 1U
        ? *(const unsigned char *)value
        : *(const unsigned int *)value;
    open_cfw_test_disable_record(
        OPEN_CFW_TEST_DISABLE_EVENT_SPOT,
        stimulus,
        enabled,
        observed
    );
    return open_cfw_test_disable_spot_result;
}

static unsigned int
open_cfw_test_disable_clock_release(
    unsigned int clock,
    unsigned int user
)
{
    open_cfw_test_disable_record(
        OPEN_CFW_TEST_DISABLE_EVENT_CLOCK_RELEASE,
        clock,
        user,
        0U
    );
    return 17U;
}

static unsigned int
open_cfw_test_disable_clock_release_all(unsigned int user)
{
    open_cfw_test_disable_record(
        OPEN_CFW_TEST_DISABLE_EVENT_CLOCK_RELEASE_ALL,
        user,
        0U,
        0U
    );
    return 18U;
}

void open_cfw_test_disable_reset(void)
{
    unsigned int index;

    open_cfw_test_disable_trace_count = 0U;
    for (
        index = 0U;
        index < OPEN_CFW_TEST_DISABLE_TRACE_CAPACITY;
        ++index
    ) {
        open_cfw_test_disable_trace_event[index] = 0U;
        open_cfw_test_disable_trace_a[index] = 0U;
        open_cfw_test_disable_trace_b[index] = 0U;
        open_cfw_test_disable_trace_c[index] = 0U;
    }
    open_cfw_test_disable_descriptor_result = 0U;
    open_cfw_test_disable_enable_address = 0x1000U;
    open_cfw_test_disable_enable_mask = 0x20U;
    open_cfw_test_disable_status_address = 0x1004U;
    open_cfw_test_disable_status_mask = 0x200U;
    open_cfw_test_disable_enable_register = 0x20U;
    open_cfw_test_disable_status_register = 0U;
    open_cfw_test_disable_chip_revision = 0x22U;
    open_cfw_test_disable_device_status = 0U;
    open_cfw_test_disable_otp_status = 0U;
    open_cfw_test_disable_demcr = 0xFFFFFFFFU;
    open_cfw_test_disable_debug_control = 0xFFFFFFFFU;
    open_cfw_test_disable_current_mode = 0U;
    open_cfw_test_disable_previous_mode = 0U;
    open_cfw_test_disable_primask = 1U;
    open_cfw_test_disable_mask_result = 1U;
    open_cfw_test_disable_status_check_result = 0U;
    open_cfw_test_disable_spot_result = 0U;
    open_cfw_test_disable_gpu_result = 0U;
    open_cfw_test_disable_status_expected = 0U;
    open_cfw_test_disable_status_equal = 0U;
    open_cfw_test_disable_status_call_count = 0U;
}
