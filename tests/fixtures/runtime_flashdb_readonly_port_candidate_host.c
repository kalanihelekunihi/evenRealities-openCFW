/* Host seam for the production-excluded FlashDB read-only port candidate. */

static signed int open_cfw_test_flashdb_mx25_status;
static signed int open_cfw_test_flashdb_acquire_status;
static signed int open_cfw_test_flashdb_release_status;
static unsigned int open_cfw_test_flashdb_mx25_calls;
static unsigned int open_cfw_test_flashdb_acquire_calls;
static unsigned int open_cfw_test_flashdb_release_calls;
static unsigned int open_cfw_test_flashdb_last_offset;
static unsigned int open_cfw_test_flashdb_last_size;
static unsigned int open_cfw_test_flashdb_last_timeout;
static void *open_cfw_test_flashdb_last_mutex;
static void *open_cfw_test_flashdb_mutex = (void *)0x12345678U;

static signed int open_cfw_test_flashdb_mx25_read(
    unsigned int offset,
    unsigned char *buffer,
    unsigned int size
)
{
    unsigned int index;

    open_cfw_test_flashdb_mx25_calls += 1U;
    open_cfw_test_flashdb_last_offset = offset;
    open_cfw_test_flashdb_last_size = size;
    if (open_cfw_test_flashdb_mx25_status != 0) {
        return open_cfw_test_flashdb_mx25_status;
    }
    for (index = 0U; index < size; index++) {
        buffer[index] = (unsigned char)((offset + index) ^ 0xA5U);
    }
    return 0;
}

static signed int open_cfw_test_flashdb_mutex_acquire(
    void *mutex,
    unsigned int timeout
)
{
    open_cfw_test_flashdb_acquire_calls += 1U;
    open_cfw_test_flashdb_last_mutex = mutex;
    open_cfw_test_flashdb_last_timeout = timeout;
    return open_cfw_test_flashdb_acquire_status;
}

static signed int open_cfw_test_flashdb_mutex_release(void *mutex)
{
    open_cfw_test_flashdb_release_calls += 1U;
    open_cfw_test_flashdb_last_mutex = mutex;
    return open_cfw_test_flashdb_release_status;
}

#define OPEN_CFW_FLASHDB_READONLY_MX25_READ(offset, buffer, size) \
    open_cfw_test_flashdb_mx25_read((offset), (buffer), (size))
#define OPEN_CFW_FLASHDB_READONLY_MUTEX_ID() open_cfw_test_flashdb_mutex
#define OPEN_CFW_FLASHDB_READONLY_MUTEX_ACQUIRE(mutex, timeout) \
    open_cfw_test_flashdb_mutex_acquire((mutex), (timeout))
#define OPEN_CFW_FLASHDB_READONLY_MUTEX_RELEASE(mutex) \
    open_cfw_test_flashdb_mutex_release((mutex))

#include "../../components/shared/flashdb/runtime_flashdb_readonly_port_candidate.c"

void open_cfw_test_flashdb_reset(
    signed int mx25_status,
    signed int acquire_status,
    signed int release_status,
    unsigned int mutex_present
)
{
    open_cfw_test_flashdb_mx25_status = mx25_status;
    open_cfw_test_flashdb_acquire_status = acquire_status;
    open_cfw_test_flashdb_release_status = release_status;
    open_cfw_test_flashdb_mx25_calls = 0U;
    open_cfw_test_flashdb_acquire_calls = 0U;
    open_cfw_test_flashdb_release_calls = 0U;
    open_cfw_test_flashdb_last_offset = 0U;
    open_cfw_test_flashdb_last_size = 0U;
    open_cfw_test_flashdb_last_timeout = 0U;
    open_cfw_test_flashdb_last_mutex = (void *)0;
    open_cfw_test_flashdb_mutex = mutex_present != 0U
        ? (void *)0x12345678U
        : (void *)0;
}

signed int open_cfw_test_flashdb_read(
    unsigned int partition,
    unsigned int address,
    unsigned char *buffer,
    unsigned int size
)
{
    return open_cfw_flashdb_readonly_partition_read(
        open_cfw_flashdb_readonly_partition(partition),
        address,
        buffer,
        size
    );
}

signed int open_cfw_test_flashdb_write(
    unsigned int offset,
    const unsigned char *buffer,
    unsigned int size
)
{
    return open_cfw_flashdb_readonly_norflash_write_denied(
        offset,
        buffer,
        size
    );
}

signed int open_cfw_test_flashdb_erase(
    unsigned int offset,
    unsigned int size
)
{
    return open_cfw_flashdb_readonly_norflash_erase_denied(offset, size);
}

unsigned int open_cfw_test_flashdb_counter(unsigned int index)
{
    switch (index) {
    case 0U:
        return open_cfw_test_flashdb_mx25_calls;
    case 1U:
        return open_cfw_test_flashdb_acquire_calls;
    case 2U:
        return open_cfw_test_flashdb_release_calls;
    case 3U:
        return open_cfw_test_flashdb_last_offset;
    case 4U:
        return open_cfw_test_flashdb_last_size;
    case 5U:
        return open_cfw_test_flashdb_last_timeout;
    default:
        return 0U;
    }
}

unsigned int open_cfw_test_flashdb_mutex_matches(void)
{
    return open_cfw_test_flashdb_last_mutex == (void *)0x12345678U;
}
