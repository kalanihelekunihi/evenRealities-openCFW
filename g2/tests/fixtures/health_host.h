#ifndef OPEN_CFW_TEST_HEALTH_HOST_H
#define OPEN_CFW_TEST_HEALTH_HOST_H

#include <stdint.h>

extern void *open_cfw_test_health_mutex_cell;

void *open_cfw_test_health_mutex_new(const void *attributes);
int open_cfw_test_health_mutex_acquire(void *mutex, uint32_t timeout);
int open_cfw_test_health_mutex_release(void *mutex);
unsigned int open_cfw_test_health_data_handle(
    unsigned char *data,
    unsigned short length
);
unsigned int open_cfw_test_health_lens_side(void);
unsigned int open_cfw_test_health_display_running(void);
unsigned int open_cfw_test_health_display_matches(unsigned int state);
unsigned int open_cfw_test_health_post_service_record(
    unsigned int service,
    const unsigned char *record,
    unsigned int length,
    unsigned int flags
);

#define OPEN_CFW_HEALTH_MUTEX_CELL open_cfw_test_health_mutex_cell
#define OPEN_CFW_HEALTH_MUTEX_NEW(attributes) \
    open_cfw_test_health_mutex_new((attributes))
#define OPEN_CFW_HEALTH_MUTEX_ACQUIRE(mutex, timeout) \
    open_cfw_test_health_mutex_acquire((mutex), (timeout))
#define OPEN_CFW_HEALTH_MUTEX_RELEASE(mutex) \
    open_cfw_test_health_mutex_release((mutex))
#define OPEN_CFW_HEALTH_DATA_HANDLE(data, length) \
    open_cfw_test_health_data_handle((data), (length))
#define OPEN_CFW_HEALTH_LENS_SIDE() open_cfw_test_health_lens_side()
#define OPEN_CFW_HEALTH_DISPLAY_RUNNING() \
    open_cfw_test_health_display_running()
#define OPEN_CFW_HEALTH_DISPLAY_MATCHES(state) \
    open_cfw_test_health_display_matches((state))
#define OPEN_CFW_HEALTH_POST_SERVICE_RECORD(service, record, length, flags) \
    open_cfw_test_health_post_service_record( \
        (service), (record), (length), (flags))

void open_cfw_test_health_reset(
    unsigned int create_success,
    int acquire_status,
    unsigned int provider_status,
    unsigned int lens_side,
    unsigned int display_running,
    unsigned int display_matches
);

extern unsigned int open_cfw_test_health_new_calls;
extern unsigned int open_cfw_test_health_acquire_calls;
extern unsigned int open_cfw_test_health_release_calls;
extern uint32_t open_cfw_test_health_acquire_timeout;
extern unsigned int open_cfw_test_health_provider_calls;
extern unsigned int open_cfw_test_health_provider_length;
extern unsigned int open_cfw_test_health_post_calls;
extern unsigned int open_cfw_test_health_post_service;
extern unsigned int open_cfw_test_health_post_length;
extern unsigned int open_cfw_test_health_post_flags;
extern unsigned char open_cfw_test_health_post_record[6];

#endif
