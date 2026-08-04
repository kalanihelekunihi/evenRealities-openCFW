unsigned int open_cfw_test_crypto_powerdown;
unsigned int open_cfw_test_crypto_results[3];
unsigned int open_cfw_test_crypto_result_count;
unsigned int open_cfw_test_crypto_calls;
unsigned int open_cfw_test_crypto_wait[3];
unsigned int open_cfw_test_crypto_address[3];
unsigned int open_cfw_test_crypto_mask[3];
unsigned int open_cfw_test_crypto_expected[3];
unsigned int open_cfw_test_crypto_reads;
unsigned int open_cfw_test_crypto_writes;
unsigned int open_cfw_test_crypto_trace_count;
unsigned int open_cfw_test_crypto_trace_event[8];
unsigned int open_cfw_test_crypto_trace_value[8];

enum {
    OPEN_CFW_TEST_CRYPTO_STATUS = 1,
    OPEN_CFW_TEST_CRYPTO_READ = 2,
    OPEN_CFW_TEST_CRYPTO_WRITE = 3,
};

static void
open_cfw_test_crypto_trace(unsigned int event, unsigned int value)
{
    unsigned int index = open_cfw_test_crypto_trace_count++;

    if (index < 8U) {
        open_cfw_test_crypto_trace_event[index] = event;
        open_cfw_test_crypto_trace_value[index] = value;
    }
}

static unsigned int
open_cfw_test_crypto_read(unsigned int address)
{
    ++open_cfw_test_crypto_reads;
    open_cfw_test_crypto_trace(OPEN_CFW_TEST_CRYPTO_READ, address);
    return open_cfw_test_crypto_powerdown;
}

static void
open_cfw_test_crypto_write(unsigned int address, unsigned int value)
{
    ++open_cfw_test_crypto_writes;
    open_cfw_test_crypto_powerdown = value;
    open_cfw_test_crypto_trace(OPEN_CFW_TEST_CRYPTO_WRITE, value);
    (void)address;
}

static unsigned int
open_cfw_test_crypto_status_change(
    unsigned int maximum_wait_us,
    unsigned int address,
    unsigned int mask,
    unsigned int expected
)
{
    unsigned int index = open_cfw_test_crypto_calls++;
    unsigned int result = 0U;

    if (index < 3U) {
        open_cfw_test_crypto_wait[index] = maximum_wait_us;
        open_cfw_test_crypto_address[index] = address;
        open_cfw_test_crypto_mask[index] = mask;
        open_cfw_test_crypto_expected[index] = expected;
    }
    if (index < open_cfw_test_crypto_result_count) {
        result = open_cfw_test_crypto_results[index];
    }
    open_cfw_test_crypto_trace(OPEN_CFW_TEST_CRYPTO_STATUS, address);
    return result;
}

#define OPEN_CFW_PWRCTRL_CRYPTO_QUIESCE_READ(address) \
    open_cfw_test_crypto_read(address)
#define OPEN_CFW_PWRCTRL_CRYPTO_QUIESCE_WRITE(address, value) \
    open_cfw_test_crypto_write((address), (value))
#define OPEN_CFW_PWRCTRL_CRYPTO_QUIESCE_STATUS_CHANGE( \
    maximum_wait_us, address, mask, expected \
) \
    open_cfw_test_crypto_status_change( \
        (maximum_wait_us), \
        (address), \
        (mask), \
        (expected) \
    )

#include "../../components/apollo_main/core_overlay/pwrctrl_crypto_quiesce.c"

void
open_cfw_test_crypto_reset(void)
{
    unsigned int index;

    open_cfw_test_crypto_powerdown = 0U;
    open_cfw_test_crypto_result_count = 3U;
    open_cfw_test_crypto_calls = 0U;
    open_cfw_test_crypto_reads = 0U;
    open_cfw_test_crypto_writes = 0U;
    open_cfw_test_crypto_trace_count = 0U;
    for (index = 0U; index < 3U; ++index) {
        open_cfw_test_crypto_results[index] = 0U;
        open_cfw_test_crypto_wait[index] = 0U;
        open_cfw_test_crypto_address[index] = 0U;
        open_cfw_test_crypto_mask[index] = 0U;
        open_cfw_test_crypto_expected[index] = 0U;
    }
    for (index = 0U; index < 8U; ++index) {
        open_cfw_test_crypto_trace_event[index] = 0U;
        open_cfw_test_crypto_trace_value[index] = 0U;
    }
}
