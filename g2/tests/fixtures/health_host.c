#include "health_host.h"

#include <stddef.h>
#include <stdint.h>
#include <string.h>

void *open_cfw_test_health_mutex_cell;
unsigned int open_cfw_test_health_new_calls;
unsigned int open_cfw_test_health_acquire_calls;
unsigned int open_cfw_test_health_release_calls;
uint32_t open_cfw_test_health_acquire_timeout;
unsigned int open_cfw_test_health_provider_calls;
unsigned int open_cfw_test_health_provider_length;
unsigned int open_cfw_test_health_post_calls;
unsigned int open_cfw_test_health_post_service;
unsigned int open_cfw_test_health_post_length;
unsigned int open_cfw_test_health_post_flags;
unsigned char open_cfw_test_health_post_record[6];

static unsigned int open_cfw_test_health_create_success;
static int open_cfw_test_health_acquire_status;
static unsigned int open_cfw_test_health_provider_status;
static unsigned int open_cfw_test_health_lens_value;
static unsigned int open_cfw_test_health_display_value;
static unsigned int open_cfw_test_health_matches_value;

void open_cfw_test_health_reset(
    unsigned int create_success,
    int acquire_status,
    unsigned int provider_status,
    unsigned int lens_side,
    unsigned int display_running,
    unsigned int display_matches
)
{
    open_cfw_test_health_mutex_cell = NULL;
    open_cfw_test_health_new_calls = 0U;
    open_cfw_test_health_acquire_calls = 0U;
    open_cfw_test_health_release_calls = 0U;
    open_cfw_test_health_acquire_timeout = 0U;
    open_cfw_test_health_provider_calls = 0U;
    open_cfw_test_health_provider_length = 0U;
    open_cfw_test_health_post_calls = 0U;
    open_cfw_test_health_post_service = 0U;
    open_cfw_test_health_post_length = 0U;
    open_cfw_test_health_post_flags = 0U;
    memset(open_cfw_test_health_post_record, 0xA5, sizeof(open_cfw_test_health_post_record));
    open_cfw_test_health_create_success = create_success;
    open_cfw_test_health_acquire_status = acquire_status;
    open_cfw_test_health_provider_status = provider_status;
    open_cfw_test_health_lens_value = lens_side;
    open_cfw_test_health_display_value = display_running;
    open_cfw_test_health_matches_value = display_matches;
}

void *open_cfw_test_health_mutex_new(const void *attributes)
{
    (void)attributes;
    ++open_cfw_test_health_new_calls;
    return open_cfw_test_health_create_success != 0U
        ? (void *)(uintptr_t)0x1234U
        : NULL;
}

int open_cfw_test_health_mutex_acquire(void *mutex, uint32_t timeout)
{
    (void)mutex;
    ++open_cfw_test_health_acquire_calls;
    open_cfw_test_health_acquire_timeout = timeout;
    return open_cfw_test_health_acquire_status;
}

int open_cfw_test_health_mutex_release(void *mutex)
{
    (void)mutex;
    ++open_cfw_test_health_release_calls;
    return 0;
}

unsigned int open_cfw_test_health_data_handle(
    unsigned char *data,
    unsigned short length
)
{
    (void)data;
    ++open_cfw_test_health_provider_calls;
    open_cfw_test_health_provider_length = length;
    return open_cfw_test_health_provider_status;
}

unsigned int open_cfw_test_health_lens_side(void)
{
    return open_cfw_test_health_lens_value;
}

unsigned int open_cfw_test_health_display_running(void)
{
    return open_cfw_test_health_display_value;
}

unsigned int open_cfw_test_health_display_matches(unsigned int state)
{
    return state == 1U ? open_cfw_test_health_matches_value : 0U;
}

unsigned int open_cfw_test_health_post_service_record(
    unsigned int service,
    const unsigned char *record,
    unsigned int length,
    unsigned int flags
)
{
    ++open_cfw_test_health_post_calls;
    open_cfw_test_health_post_service = service;
    open_cfw_test_health_post_length = length;
    open_cfw_test_health_post_flags = flags;
    if (length == sizeof(open_cfw_test_health_post_record)) {
        memcpy(open_cfw_test_health_post_record, record, length);
    }
    return 0U;
}
