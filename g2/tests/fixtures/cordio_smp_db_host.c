#include <stdint.h>
#include <string.h>

#include "cordio_smp_db_host.h"

struct open_cfw_smp_db_header {
    uint16_t param;
    uint8_t event;
    uint8_t status;
};

struct open_cfw_smp_db_timer {
    uint32_t next;
    struct open_cfw_smp_db_header message;
    uint32_t ticks;
    uint8_t handler_id;
    uint8_t is_started;
    uint8_t reserved[2];
};

struct open_cfw_smp_db_device {
    uint8_t peer_address[6];
    uint8_t address_type;
    uint8_t failure_count;
    uint16_t attempt_multiplier;
    uint8_t reserved[2];
    uint32_t lock_ms;
    uint32_t exponent_decrement_ms;
    uint32_t failure_count_timeout_ms;
};

struct open_cfw_smp_db_control_block {
    struct open_cfw_smp_db_device devices[10];
    struct open_cfw_smp_db_timer service_timer;
};

struct open_cfw_smp_db_config {
    uint32_t attempt_timeout_ms;
    uint8_t io_capability;
    uint8_t minimum_key_length;
    uint8_t maximum_key_length;
    uint8_t maximum_attempts;
    uint8_t authentication;
    uint8_t reserved[3];
    uint32_t maximum_attempt_timeout_ms;
    uint32_t attempt_decrement_timeout_ms;
    uint16_t attempt_exponent;
    uint8_t tail_reserved[2];
};

struct open_cfw_smp_db_control_block open_cfw_test_smp_db_control;
struct open_cfw_smp_db_config open_cfw_test_smp_db_config;
uint8_t open_cfw_test_smp_db_handler_id;

static uint8_t peer_addresses[16][6];
static uint8_t peer_types[16];
static uint32_t timer_start_calls;
static uint32_t timer_stop_calls;

void open_cfw_retained_cordio_wsf_timer_start_ms(
    struct open_cfw_smp_db_timer *timer, uint32_t milliseconds)
{
    timer_start_calls++;
    timer->ticks = milliseconds;
    timer->is_started = 1U;
}

void open_cfw_retained_cordio_wsf_timer_stop(
    struct open_cfw_smp_db_timer *timer)
{
    timer_stop_calls++;
    timer->is_started = 0U;
}

void *open_cfw_runtime_memory_zero(void *destination, uint32_t size)
{
    return memset(destination, 0, size);
}

uint8_t open_cfw_retained_cordio_dm_conn_peer_address_type(
    uint8_t connection_id)
{
    return peer_types[connection_id];
}

uint8_t *open_cfw_retained_cordio_dm_conn_peer_address(uint8_t connection_id)
{
    return peer_addresses[connection_id];
}

uint8_t open_cfw_retained_cordio_dm_host_address_type(uint8_t address_type)
{
    return (uint8_t)(address_type & 1U);
}

extern void open_cfw_cordio_smp_db_init(void);
extern uint32_t open_cfw_cordio_smp_db_get_pairing_disabled_time(uint8_t);
extern void open_cfw_cordio_smp_db_set_failure_count(uint8_t, uint8_t);
extern uint8_t open_cfw_cordio_smp_db_get_failure_count(uint8_t);
extern uint32_t open_cfw_cordio_smp_db_max_attempt_reached(uint8_t);
extern void open_cfw_cordio_smp_db_pairing_failed(uint8_t);
extern void open_cfw_cordio_smp_db_service(void);

static void reset_fixture(void)
{
    memset(&open_cfw_test_smp_db_control, 0xA5,
        sizeof(open_cfw_test_smp_db_control));
    memset(peer_addresses, 0, sizeof(peer_addresses));
    memset(peer_types, 0, sizeof(peer_types));
    memset(&open_cfw_test_smp_db_config, 0,
        sizeof(open_cfw_test_smp_db_config));
    open_cfw_test_smp_db_config.attempt_timeout_ms = 3000U;
    open_cfw_test_smp_db_config.maximum_attempt_timeout_ms = 64000U;
    open_cfw_test_smp_db_config.attempt_decrement_timeout_ms = 64000U;
    open_cfw_test_smp_db_config.attempt_exponent = 2U;
    open_cfw_test_smp_db_handler_id = 0x5AU;
    timer_start_calls = 0U;
    timer_stop_calls = 0U;
}

int open_cfw_test_smp_db_init_contract(void)
{
    unsigned int index;
    reset_fixture();
    open_cfw_test_smp_db_control.service_timer.is_started = 1U;
    open_cfw_cordio_smp_db_init();
    if (timer_stop_calls != 1U ||
        open_cfw_test_smp_db_control.service_timer.handler_id != 0x5AU ||
        open_cfw_test_smp_db_control.service_timer.message.event != 0x20U) {
        return 1;
    }
    for (index = 0U; index < sizeof(open_cfw_test_smp_db_control.devices);
         index++) {
        if (((uint8_t *)open_cfw_test_smp_db_control.devices)[index] != 0U) {
            return 2;
        }
    }
    return 0;
}

int open_cfw_test_smp_db_record_reuse_and_failure(void)
{
    reset_fixture();
    memset(&open_cfw_test_smp_db_control, 0,
        sizeof(open_cfw_test_smp_db_control));
    peer_types[1] = 3U;
    memcpy(peer_addresses[1], "ABCDEF", 6U);
    open_cfw_cordio_smp_db_set_failure_count(1U, 4U);
    if (open_cfw_test_smp_db_control.devices[1].failure_count != 4U ||
        open_cfw_test_smp_db_control.devices[1].address_type != 1U ||
        memcmp(open_cfw_test_smp_db_control.devices[1].peer_address,
            "ABCDEF", 6U) != 0 ||
        open_cfw_test_smp_db_control.devices[1].failure_count_timeout_ms !=
            64000U || open_cfw_cordio_smp_db_get_failure_count(1U) != 4U) {
        return 1;
    }
    open_cfw_cordio_smp_db_set_failure_count(1U, 0U);
    return open_cfw_cordio_smp_db_get_failure_count(1U) == 0U ? 0 : 2;
}

int open_cfw_test_smp_db_full_falls_back_to_common(void)
{
    uint8_t index;
    reset_fixture();
    memset(&open_cfw_test_smp_db_control, 0,
        sizeof(open_cfw_test_smp_db_control));
    for (index = 1U; index < 10U; index++) {
        open_cfw_test_smp_db_control.devices[index].failure_count = 1U;
    }
    peer_addresses[2][0] = 0x99U;
    open_cfw_cordio_smp_db_set_failure_count(2U, 7U);
    return open_cfw_test_smp_db_control.devices[0].failure_count == 7U ? 0 : 1;
}

int open_cfw_test_smp_db_backoff_and_clamp(void)
{
    struct open_cfw_smp_db_device *record;
    reset_fixture();
    memset(&open_cfw_test_smp_db_control, 0,
        sizeof(open_cfw_test_smp_db_control));
    peer_addresses[3][0] = 3U;
    if (open_cfw_cordio_smp_db_max_attempt_reached(3U) != 3000U) {
        return 1;
    }
    record = &open_cfw_test_smp_db_control.devices[1];
    if (record->attempt_multiplier != 1U || record->lock_ms != 3000U ||
        record->exponent_decrement_ms != 64000U || timer_start_calls != 1U) {
        return 2;
    }
    record->attempt_multiplier = 32U;
    open_cfw_test_smp_db_control.service_timer.is_started = 0U;
    if (open_cfw_cordio_smp_db_max_attempt_reached(3U) != 64000U ||
        record->attempt_multiplier != 32U || timer_start_calls != 2U) {
        return 3;
    }
    return 0;
}

int open_cfw_test_smp_db_service_and_pairing_failed(void)
{
    struct open_cfw_smp_db_device *record;
    reset_fixture();
    memset(&open_cfw_test_smp_db_control, 0,
        sizeof(open_cfw_test_smp_db_control));
    peer_addresses[4][0] = 4U;
    open_cfw_cordio_smp_db_set_failure_count(4U, 2U);
    record = &open_cfw_test_smp_db_control.devices[1];
    record->attempt_multiplier = 4U;
    record->lock_ms = 500U;
    record->exponent_decrement_ms = 500U;
    record->failure_count_timeout_ms = 500U;
    open_cfw_cordio_smp_db_service();
    if (record->attempt_multiplier != 2U || record->lock_ms != 0U ||
        record->failure_count != 0U ||
        record->exponent_decrement_ms != 64000U || timer_start_calls != 1U) {
        return 1;
    }
    record->exponent_decrement_ms = 1U;
    open_cfw_cordio_smp_db_pairing_failed(4U);
    if (record->exponent_decrement_ms != 64000U ||
        open_cfw_cordio_smp_db_get_pairing_disabled_time(4U) != 0U) {
        return 2;
    }
    return 0;
}
