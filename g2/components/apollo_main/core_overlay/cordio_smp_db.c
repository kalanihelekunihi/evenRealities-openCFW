/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * Production adapter for the eleven linked Packetcraft Cordio r20.05c
 * smp_db.c functions retained by G2 2.2.6.10.  The G2 product configuration
 * expands SMP_DB_MAX_DEVICES from three to ten and uses the r20 event ABI.
 */

#include <stddef.h>
#include <stdint.h>

#if !defined(OPEN_CFW_SMP_DB_START_TIMER_ONLY) && \
    !defined(OPEN_CFW_SMP_DB_RECORD_IN_USE_ONLY) && \
    !defined(OPEN_CFW_SMP_DB_ADD_DEVICE_ONLY) && \
    !defined(OPEN_CFW_SMP_DB_GET_RECORD_ONLY) && \
    !defined(OPEN_CFW_SMP_DB_INIT_ONLY) && \
    !defined(OPEN_CFW_SMP_DB_GET_DISABLED_ONLY) && \
    !defined(OPEN_CFW_SMP_DB_SET_FAILURE_ONLY) && \
    !defined(OPEN_CFW_SMP_DB_GET_FAILURE_ONLY) && \
    !defined(OPEN_CFW_SMP_DB_MAX_ATTEMPT_ONLY) && \
    !defined(OPEN_CFW_SMP_DB_PAIRING_FAILED_ONLY) && \
    !defined(OPEN_CFW_SMP_DB_SERVICE_ONLY)
#define OPEN_CFW_SMP_DB_ALL 1
#else
#define OPEN_CFW_SMP_DB_ALL 0
#endif

#define OPEN_CFW_SMP_DB_DEVICE_COUNT 10U
#define OPEN_CFW_SMP_DB_SERVICE_MS 1000U

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
    struct open_cfw_smp_db_device devices[OPEN_CFW_SMP_DB_DEVICE_COUNT];
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

#ifndef OPEN_CFW_SMP_DB_CONTROL_BLOCK
#define OPEN_CFW_SMP_DB_CONTROL_BLOCK \
    (*(struct open_cfw_smp_db_control_block *)(uintptr_t)0x200708ECU)
#endif

#ifndef OPEN_CFW_SMP_DB_CONFIG
#define OPEN_CFW_SMP_DB_CONFIG \
    (**(struct open_cfw_smp_db_config **)(uintptr_t)0x200004B8U)
#endif

#ifndef OPEN_CFW_SMP_DB_HANDLER_ID
#define OPEN_CFW_SMP_DB_HANDLER_ID \
    (*(volatile uint8_t *)(uintptr_t)0x20070BD8U)
#endif

extern void open_cfw_retained_cordio_wsf_timer_start_ms(
    struct open_cfw_smp_db_timer *timer, uint32_t milliseconds);
extern void open_cfw_retained_cordio_wsf_timer_stop(
    struct open_cfw_smp_db_timer *timer);
extern uint8_t open_cfw_retained_cordio_dm_conn_peer_address_type(
    uint8_t connection_id);
extern uint8_t *open_cfw_retained_cordio_dm_conn_peer_address(
    uint8_t connection_id);
extern uint8_t open_cfw_retained_cordio_dm_host_address_type(
    uint8_t address_type);
extern void *open_cfw_runtime_memory_zero(void *destination, uint32_t size);

void open_cfw_cordio_smp_db_start_service_timer(void);
uint8_t open_cfw_cordio_smp_db_record_in_use(
    struct open_cfw_smp_db_device *record);
struct open_cfw_smp_db_device *open_cfw_cordio_smp_db_add_device(
    const uint8_t address[6], uint8_t address_type);
struct open_cfw_smp_db_device *open_cfw_cordio_smp_db_get_record(
    uint8_t connection_id);

static __attribute__((unused)) void open_cfw_smp_db_zero(
    void *destination, uint32_t size)
{
    (void)open_cfw_runtime_memory_zero(destination, size);
}

static __attribute__((unused)) void open_cfw_smp_db_copy_address(
    uint8_t destination[6], const uint8_t source[6])
{
    uint8_t index;
    for (index = 0U; index < 6U; index++) {
        destination[index] = source[index];
    }
}

static __attribute__((unused)) uint8_t open_cfw_smp_db_address_equal(
    const uint8_t left[6], const uint8_t right[6])
{
    uint8_t index;
    for (index = 0U; index < 6U; index++) {
        if (left[index] != right[index]) {
            return 0U;
        }
    }
    return 1U;
}

static __attribute__((unused)) uint16_t open_cfw_smp_db_divide_u16(
    uint16_t numerator, uint16_t denominator)
{
    return (uint16_t)(numerator / denominator);
}

static __attribute__((unused)) uint32_t open_cfw_smp_db_decrement(
    uint32_t value)
{
    return value > OPEN_CFW_SMP_DB_SERVICE_MS
        ? value - OPEN_CFW_SMP_DB_SERVICE_MS : 0U;
}

#if OPEN_CFW_SMP_DB_ALL || defined(OPEN_CFW_SMP_DB_START_TIMER_ONLY)
void open_cfw_cordio_smp_db_start_service_timer(void)
{
    struct open_cfw_smp_db_timer *timer =
        &OPEN_CFW_SMP_DB_CONTROL_BLOCK.service_timer;
    if (timer->is_started == 0U) {
        open_cfw_retained_cordio_wsf_timer_start_ms(
            timer, OPEN_CFW_SMP_DB_SERVICE_MS);
    }
}
#endif

#if OPEN_CFW_SMP_DB_ALL || defined(OPEN_CFW_SMP_DB_RECORD_IN_USE_ONLY)
uint8_t open_cfw_cordio_smp_db_record_in_use(
    struct open_cfw_smp_db_device *record)
{
    return (record->failure_count != 0U || record->lock_ms != 0U ||
        record->attempt_multiplier != 0U) ? 1U : 0U;
}
#endif

#if OPEN_CFW_SMP_DB_ALL || defined(OPEN_CFW_SMP_DB_ADD_DEVICE_ONLY)
struct open_cfw_smp_db_device *open_cfw_cordio_smp_db_add_device(
    const uint8_t address[6], uint8_t address_type)
{
    uint8_t index;
    for (index = 1U; index < OPEN_CFW_SMP_DB_DEVICE_COUNT; index++) {
        struct open_cfw_smp_db_device *record =
            &OPEN_CFW_SMP_DB_CONTROL_BLOCK.devices[index];
        if (open_cfw_cordio_smp_db_record_in_use(record) == 0U) {
            open_cfw_smp_db_zero(record, sizeof(*record));
            record->address_type = address_type;
            open_cfw_smp_db_copy_address(record->peer_address, address);
            return record;
        }
    }
    return NULL;
}
#endif

#if OPEN_CFW_SMP_DB_ALL || defined(OPEN_CFW_SMP_DB_GET_RECORD_ONLY)
struct open_cfw_smp_db_device *open_cfw_cordio_smp_db_get_record(
    uint8_t connection_id)
{
    uint8_t address_type = open_cfw_retained_cordio_dm_host_address_type(
        open_cfw_retained_cordio_dm_conn_peer_address_type(connection_id));
    uint8_t *address =
        open_cfw_retained_cordio_dm_conn_peer_address(connection_id);
    uint8_t index;

    for (index = 1U; index < OPEN_CFW_SMP_DB_DEVICE_COUNT; index++) {
        struct open_cfw_smp_db_device *record =
            &OPEN_CFW_SMP_DB_CONTROL_BLOCK.devices[index];
        if (open_cfw_cordio_smp_db_record_in_use(record) != 0U &&
            record->address_type == address_type &&
            open_cfw_smp_db_address_equal(record->peer_address, address) != 0U) {
            return record;
        }
    }

    {
        struct open_cfw_smp_db_device *record =
            open_cfw_cordio_smp_db_add_device(address, address_type);
        return record != NULL ? record :
            &OPEN_CFW_SMP_DB_CONTROL_BLOCK.devices[0];
    }
}
#endif

#if OPEN_CFW_SMP_DB_ALL || defined(OPEN_CFW_SMP_DB_INIT_ONLY)
void open_cfw_cordio_smp_db_init(void)
{
    struct open_cfw_smp_db_control_block *control =
        &OPEN_CFW_SMP_DB_CONTROL_BLOCK;
    if (control->service_timer.is_started != 0U) {
        open_cfw_retained_cordio_wsf_timer_stop(&control->service_timer);
    }
    open_cfw_smp_db_zero(control, sizeof(*control));
    control->service_timer.handler_id = OPEN_CFW_SMP_DB_HANDLER_ID;
    control->service_timer.message.event = 0x20U;
}
#endif

#if OPEN_CFW_SMP_DB_ALL || defined(OPEN_CFW_SMP_DB_GET_DISABLED_ONLY)
uint32_t open_cfw_cordio_smp_db_get_pairing_disabled_time(
    uint8_t connection_id)
{
    return open_cfw_cordio_smp_db_get_record(connection_id)->lock_ms;
}
#endif

#if OPEN_CFW_SMP_DB_ALL || defined(OPEN_CFW_SMP_DB_SET_FAILURE_ONLY)
void open_cfw_cordio_smp_db_set_failure_count(
    uint8_t connection_id, uint8_t count)
{
    struct open_cfw_smp_db_device *record =
        open_cfw_cordio_smp_db_get_record(connection_id);
    record->failure_count = count;
    if (count != 0U) {
        record->failure_count_timeout_ms =
            OPEN_CFW_SMP_DB_CONFIG.maximum_attempt_timeout_ms;
    }
}
#endif

#if OPEN_CFW_SMP_DB_ALL || defined(OPEN_CFW_SMP_DB_GET_FAILURE_ONLY)
uint8_t open_cfw_cordio_smp_db_get_failure_count(uint8_t connection_id)
{
    return open_cfw_cordio_smp_db_get_record(connection_id)->failure_count;
}
#endif

#if OPEN_CFW_SMP_DB_ALL || defined(OPEN_CFW_SMP_DB_MAX_ATTEMPT_ONLY)
uint32_t open_cfw_cordio_smp_db_max_attempt_reached(uint8_t connection_id)
{
    struct open_cfw_smp_db_device *record =
        open_cfw_cordio_smp_db_get_record(connection_id);
    uint16_t multiplier = record->attempt_multiplier == 0U ? 1U :
        (uint16_t)(record->attempt_multiplier *
            OPEN_CFW_SMP_DB_CONFIG.attempt_exponent);
    uint32_t requested = OPEN_CFW_SMP_DB_CONFIG.attempt_timeout_ms *
        (uint32_t)multiplier;

    if (requested <= OPEN_CFW_SMP_DB_CONFIG.maximum_attempt_timeout_ms) {
        record->lock_ms = requested;
        record->attempt_multiplier = multiplier;
    } else {
        record->lock_ms =
            OPEN_CFW_SMP_DB_CONFIG.maximum_attempt_timeout_ms;
    }
    record->exponent_decrement_ms =
        OPEN_CFW_SMP_DB_CONFIG.attempt_decrement_timeout_ms;
    open_cfw_cordio_smp_db_start_service_timer();
    return record->lock_ms;
}
#endif

#if OPEN_CFW_SMP_DB_ALL || defined(OPEN_CFW_SMP_DB_PAIRING_FAILED_ONLY)
void open_cfw_cordio_smp_db_pairing_failed(uint8_t connection_id)
{
    open_cfw_cordio_smp_db_get_record(connection_id)->exponent_decrement_ms =
        OPEN_CFW_SMP_DB_CONFIG.attempt_decrement_timeout_ms;
}
#endif

#if OPEN_CFW_SMP_DB_ALL || defined(OPEN_CFW_SMP_DB_SERVICE_ONLY)
void open_cfw_cordio_smp_db_service(void)
{
    uint8_t index;
    for (index = 0U; index < OPEN_CFW_SMP_DB_DEVICE_COUNT; index++) {
        struct open_cfw_smp_db_device *record =
            &OPEN_CFW_SMP_DB_CONTROL_BLOCK.devices[index];
        if (open_cfw_cordio_smp_db_record_in_use(record) != 0U) {
            record->exponent_decrement_ms =
                open_cfw_smp_db_decrement(record->exponent_decrement_ms);
            record->lock_ms = open_cfw_smp_db_decrement(record->lock_ms);
            record->failure_count_timeout_ms =
                open_cfw_smp_db_decrement(record->failure_count_timeout_ms);

            if (record->exponent_decrement_ms == 0U) {
                record->attempt_multiplier = open_cfw_smp_db_divide_u16(
                    record->attempt_multiplier,
                    OPEN_CFW_SMP_DB_CONFIG.attempt_exponent);
                if (record->attempt_multiplier != 0U) {
                    record->exponent_decrement_ms =
                        OPEN_CFW_SMP_DB_CONFIG.attempt_decrement_timeout_ms;
                }
            }
            if (record->failure_count_timeout_ms == 0U) {
                record->failure_count = 0U;
            }
            if (open_cfw_cordio_smp_db_record_in_use(record) != 0U) {
                open_cfw_cordio_smp_db_start_service_timer();
            }
        }
    }
}
#endif
