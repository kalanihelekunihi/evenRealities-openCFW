/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room implementation of the ten linked G2
 * pb_service_dev_setting.c entries. Diagnostic-only EasyLogger/assertion
 * construction is omitted; control effects, status values, nanopb layouts,
 * cached time state, and service-0x80 transport are preserved.
 */

#include <stdint.h>

typedef struct {
    uint32_t (*write)(void *, const void *, uint32_t);
    void *context;
    uint32_t capacity;
    uint32_t length;
    const char *error;
} open_cfw_pb_dev_setting_output;

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(open_cfw_pb_dev_setting_output) == 20U,
    "G2 nanopb output stream ABI changed");
#endif

#ifndef OPEN_CFW_PB_DEV_SETTING_DESCRIPTOR
#define OPEN_CFW_PB_DEV_SETTING_DESCRIPTOR \
    ((const void *)(uintptr_t)0x007766DCU)
#endif
#ifndef OPEN_CFW_PB_DEV_SETTING_TIME_CACHE
#define OPEN_CFW_PB_DEV_SETTING_TIME_CACHE \
    ((volatile uint8_t *)(uintptr_t)0x20004394U)
#endif
#ifndef OPEN_CFW_PB_DEV_SETTING_WHITELIST_PATH
#define OPEN_CFW_PB_DEV_SETTING_WHITELIST_PATH \
    ((const char *)(uintptr_t)0x0076F518U)
#endif

#ifndef OPEN_CFW_PB_DEV_SETTING_ENCODE
uint32_t open_cfw_format_message_encode(
    void *output, const void *descriptor, const void *message);
#define OPEN_CFW_PB_DEV_SETTING_ENCODE(output, descriptor, message) \
    open_cfw_format_message_encode((output), (descriptor), (message))
#endif
#ifndef OPEN_CFW_PB_DEV_SETTING_SEND
int open_cfw_ble_msgtx_pb_send(
    uint32_t route, uint32_t service, const void *data, uint32_t length);
#define OPEN_CFW_PB_DEV_SETTING_SEND(route, service, data, length) \
    open_cfw_ble_msgtx_pb_send((route), (service), (data), (length))
#endif
#ifndef OPEN_CFW_PB_DEV_SETTING_DIRECT_SEND
int open_cfw_ble_msgtx_pb_direct_send(
    uint32_t route, uint32_t service, const void *data, uint32_t length);
#define OPEN_CFW_PB_DEV_SETTING_DIRECT_SEND(route, service, data, length) \
    open_cfw_ble_msgtx_pb_direct_send((route), (service), (data), (length))
#endif

#ifndef OPEN_CFW_PB_DEV_SETTING_DISPLAY_ACTIVE
int open_cfw_pb_dev_setting_display_active(void);
#define OPEN_CFW_PB_DEV_SETTING_DISPLAY_ACTIVE() \
    open_cfw_pb_dev_setting_display_active()
#endif
#ifndef OPEN_CFW_PB_DEV_SETTING_DISPLAY_LEFT_ACTIVE
int open_cfw_pb_dev_setting_display_left_active(void);
#define OPEN_CFW_PB_DEV_SETTING_DISPLAY_LEFT_ACTIVE() \
    open_cfw_pb_dev_setting_display_left_active()
#endif
#ifndef OPEN_CFW_PB_DEV_SETTING_DISPLAY_RIGHT_ACTIVE
int open_cfw_pb_dev_setting_display_right_active(void);
#define OPEN_CFW_PB_DEV_SETTING_DISPLAY_RIGHT_ACTIVE() \
    open_cfw_pb_dev_setting_display_right_active()
#endif
#ifndef OPEN_CFW_PB_DEV_SETTING_ROLE
int open_cfw_lens_side(void);
#define OPEN_CFW_PB_DEV_SETTING_ROLE() open_cfw_lens_side()
#endif
#ifndef OPEN_CFW_PB_DEV_SETTING_DISPLAY_STOP
void open_cfw_pb_dev_setting_display_stop(
    uint32_t, uint32_t, uint32_t, uint32_t);
#define OPEN_CFW_PB_DEV_SETTING_DISPLAY_STOP() \
    open_cfw_pb_dev_setting_display_stop(0U, 0U, 0U, 0U)
#endif
#ifndef OPEN_CFW_PB_DEV_SETTING_DELAY
void open_cfw_cmsis_delay(uint32_t milliseconds);
#define OPEN_CFW_PB_DEV_SETTING_DELAY(milliseconds) \
    open_cfw_cmsis_delay((milliseconds))
#endif
#ifndef OPEN_CFW_PB_DEV_SETTING_KVDB_INVALIDATE
void open_cfw_pb_dev_setting_kvdb_invalidate(void);
#define OPEN_CFW_PB_DEV_SETTING_KVDB_INVALIDATE() \
    open_cfw_pb_dev_setting_kvdb_invalidate()
#endif
#ifndef OPEN_CFW_PB_DEV_SETTING_ONBOARDING_RESET
int open_cfw_kvdb_onboarding_config_update_and_persist(
    uint32_t index, const void *value);
#define OPEN_CFW_PB_DEV_SETTING_ONBOARDING_RESET(index, value) \
    open_cfw_kvdb_onboarding_config_update_and_persist((index), (value))
#endif
#ifndef OPEN_CFW_PB_DEV_SETTING_FILE_REMOVE
int open_cfw_file_remove(const char *path);
#define OPEN_CFW_PB_DEV_SETTING_FILE_REMOVE(path) open_cfw_file_remove((path))
#endif
#ifndef OPEN_CFW_PB_DEV_SETTING_CLEAN_BONDS
void open_cfw_pb_dev_setting_clean_bonds(void);
#define OPEN_CFW_PB_DEV_SETTING_CLEAN_BONDS() \
    open_cfw_pb_dev_setting_clean_bonds()
#endif
#ifndef OPEN_CFW_PB_DEV_SETTING_FILESYSTEM_FORMAT
int open_cfw_file_system_format(void);
#define OPEN_CFW_PB_DEV_SETTING_FILESYSTEM_FORMAT() open_cfw_file_system_format()
#endif
#ifndef OPEN_CFW_PB_DEV_SETTING_RESTART
void open_cfw_pb_dev_setting_restart(void);
#define OPEN_CFW_PB_DEV_SETTING_RESTART() open_cfw_pb_dev_setting_restart()
#endif
#ifndef OPEN_CFW_PB_DEV_SETTING_HEARTBEAT_STATE
void open_cfw_pb_dev_setting_heartbeat_state(uint32_t connected);
#define OPEN_CFW_PB_DEV_SETTING_HEARTBEAT_STATE(connected) \
    open_cfw_pb_dev_setting_heartbeat_state((connected))
#endif
#ifndef OPEN_CFW_PB_DEV_SETTING_SYSTEM_TIME_SYNC
void open_cfw_pb_dev_setting_system_time_sync(uint32_t utc, int32_t timezone);
#define OPEN_CFW_PB_DEV_SETTING_SYSTEM_TIME_SYNC(utc, timezone) \
    open_cfw_pb_dev_setting_system_time_sync((utc), (timezone))
#endif
#ifndef OPEN_CFW_PB_DEV_SETTING_PEER_TIME_SYNC
void open_cfw_pb_dev_setting_peer_time_sync(uint32_t mode);
#define OPEN_CFW_PB_DEV_SETTING_PEER_TIME_SYNC(mode) \
    open_cfw_pb_dev_setting_peer_time_sync((mode))
#endif
#ifndef OPEN_CFW_PB_DEV_SETTING_TIME_PERSIST
void open_cfw_kvdb_write_time(uint32_t timestamp, int8_t timezone);
#define OPEN_CFW_PB_DEV_SETTING_TIME_PERSIST(timestamp, timezone) \
    open_cfw_kvdb_write_time((timestamp), (timezone))
#endif

uint32_t open_cfw_pb_service_dev_setting_buffer_write(
    void *raw_output, const void *data, uint32_t length);
int open_cfw_pb_service_dev_setting_transmit(
    uint8_t magic, void *buffer, uint32_t capacity, uint8_t *message,
    const uint8_t *payload, uint8_t command, uint16_t tag,
    uint32_t direct_transport);
int PB_RxRestoreFactory(uint8_t magic, const uint8_t *payload);
int PB_TxEncodeRestoreFactory(
    uint8_t magic, void *buffer, uint16_t capacity, uint8_t *message,
    const uint8_t *payload);
int PB_RxQuickRestart(uint8_t magic, const uint8_t *payload);
int PB_TxEncodeQuickRestart(
    uint8_t magic, void *buffer, uint16_t capacity, uint8_t *message,
    const uint8_t *payload);
int PB_RxBaseConnHeartBeat(uint8_t magic, const uint8_t *payload);
int PB_TxEncodeBaseConnHeartBeat(
    uint8_t magic, void *buffer, uint16_t capacity, uint8_t *message,
    const uint8_t *payload);
int PB_RxTimeSyncInfo(uint8_t magic, const uint8_t *payload);
int PB_TxEncodeTimeSyncInfo(
    uint8_t magic, void *buffer, uint16_t capacity, uint8_t *message,
    const uint8_t *payload);
int PB_RxAudControl(uint8_t magic, const uint8_t *payload);
int PB_TxEncodeAudControl(
    uint8_t magic, void *buffer, uint16_t capacity, uint8_t *message,
    const uint8_t *payload);

#if defined(OPEN_CFW_PB_DEV_SETTING_BUFFER_WRITE_ONLY)
#define OPEN_CFW_PB_DEV_SETTING_INCLUDE_BUFFER_WRITE 1
#elif defined(OPEN_CFW_PB_DEV_SETTING_TRANSMIT_ONLY)
#define OPEN_CFW_PB_DEV_SETTING_INCLUDE_TRANSMIT 1
#elif defined(OPEN_CFW_PB_DEV_SETTING_RX_RESTORE_ONLY)
#define OPEN_CFW_PB_DEV_SETTING_INCLUDE_RX_RESTORE 1
#elif defined(OPEN_CFW_PB_DEV_SETTING_TX_RESTORE_ONLY)
#define OPEN_CFW_PB_DEV_SETTING_INCLUDE_TX_RESTORE 1
#elif defined(OPEN_CFW_PB_DEV_SETTING_RX_RESTART_ONLY)
#define OPEN_CFW_PB_DEV_SETTING_INCLUDE_RX_RESTART 1
#elif defined(OPEN_CFW_PB_DEV_SETTING_TX_RESTART_ONLY)
#define OPEN_CFW_PB_DEV_SETTING_INCLUDE_TX_RESTART 1
#elif defined(OPEN_CFW_PB_DEV_SETTING_RX_HEARTBEAT_ONLY)
#define OPEN_CFW_PB_DEV_SETTING_INCLUDE_RX_HEARTBEAT 1
#elif defined(OPEN_CFW_PB_DEV_SETTING_TX_HEARTBEAT_ONLY)
#define OPEN_CFW_PB_DEV_SETTING_INCLUDE_TX_HEARTBEAT 1
#elif defined(OPEN_CFW_PB_DEV_SETTING_RX_TIME_ONLY)
#define OPEN_CFW_PB_DEV_SETTING_INCLUDE_RX_TIME 1
#elif defined(OPEN_CFW_PB_DEV_SETTING_TX_TIME_ONLY)
#define OPEN_CFW_PB_DEV_SETTING_INCLUDE_TX_TIME 1
#elif defined(OPEN_CFW_PB_DEV_SETTING_RX_AUDIO_ONLY)
#define OPEN_CFW_PB_DEV_SETTING_INCLUDE_RX_AUDIO 1
#elif defined(OPEN_CFW_PB_DEV_SETTING_TX_AUDIO_ONLY)
#define OPEN_CFW_PB_DEV_SETTING_INCLUDE_TX_AUDIO 1
#else
#define OPEN_CFW_PB_DEV_SETTING_INCLUDE_BUFFER_WRITE 1
#define OPEN_CFW_PB_DEV_SETTING_INCLUDE_TRANSMIT 1
#define OPEN_CFW_PB_DEV_SETTING_INCLUDE_RX_RESTORE 1
#define OPEN_CFW_PB_DEV_SETTING_INCLUDE_TX_RESTORE 1
#define OPEN_CFW_PB_DEV_SETTING_INCLUDE_RX_RESTART 1
#define OPEN_CFW_PB_DEV_SETTING_INCLUDE_TX_RESTART 1
#define OPEN_CFW_PB_DEV_SETTING_INCLUDE_RX_HEARTBEAT 1
#define OPEN_CFW_PB_DEV_SETTING_INCLUDE_TX_HEARTBEAT 1
#define OPEN_CFW_PB_DEV_SETTING_INCLUDE_RX_TIME 1
#define OPEN_CFW_PB_DEV_SETTING_INCLUDE_TX_TIME 1
#define OPEN_CFW_PB_DEV_SETTING_INCLUDE_RX_AUDIO 1
#define OPEN_CFW_PB_DEV_SETTING_INCLUDE_TX_AUDIO 1
#endif

#if defined(OPEN_CFW_PB_DEV_SETTING_INCLUDE_BUFFER_WRITE)
uint32_t open_cfw_pb_service_dev_setting_buffer_write(
    void *raw_output, const void *data, uint32_t length)
{
    open_cfw_pb_dev_setting_output *output = raw_output;
    const uint8_t *source = data;
    uint8_t *destination = output->context;
    uint32_t index;

    if (output->length > output->capacity ||
            length > output->capacity - output->length) {
        return 0U;
    }
    for (index = 0U; index < length; ++index) {
        destination[output->length + index] = source[index];
    }
    output->length += length;
    return 1U;
}
#endif

#if defined(OPEN_CFW_PB_DEV_SETTING_INCLUDE_TRANSMIT)
int open_cfw_pb_service_dev_setting_transmit(
    uint8_t magic, void *buffer, uint32_t capacity, uint8_t *message,
    const uint8_t *payload, uint8_t command, uint16_t tag,
    uint32_t direct_transport)
{
    open_cfw_pb_dev_setting_output output;
    uint8_t *bytes = buffer;
    uint32_t index;

    if (buffer == (void *)0 || message == (void *)0 || payload == (void *)0) {
        return 2;
    }
    for (index = 0U; index < capacity; ++index) {
        bytes[index] = 0U;
    }
    output.write = open_cfw_pb_service_dev_setting_buffer_write;
    output.context = buffer;
    output.capacity = capacity;
    output.length = 0U;
    output.error = (const char *)0;
    message[0] = command;
    message[2] = magic;
    message[3] = 0U;
    message[4] = (uint8_t)tag;
    message[5] = (uint8_t)(tag >> 8);
    if (OPEN_CFW_PB_DEV_SETTING_ENCODE(
            &output, OPEN_CFW_PB_DEV_SETTING_DESCRIPTOR, message) == 0U) {
        return 0x2B;
    }
    if (direct_transport != 0U) {
        (void)OPEN_CFW_PB_DEV_SETTING_DIRECT_SEND(
            1U, 0x80U, buffer, output.length & 0xFFFFU);
    } else {
        (void)OPEN_CFW_PB_DEV_SETTING_SEND(
            1U, 0x80U, buffer, output.length & 0xFFFFU);
    }
    return 0;
}
#endif

#if defined(OPEN_CFW_PB_DEV_SETTING_INCLUDE_RX_RESTORE)
int PB_RxRestoreFactory(uint8_t magic, const uint8_t *payload)
{
    uint8_t reset = 1U;
    int role;
    (void)magic;
    if (payload == (const uint8_t *)0) {
        return 2;
    }
    role = OPEN_CFW_PB_DEV_SETTING_ROLE();
    if (OPEN_CFW_PB_DEV_SETTING_DISPLAY_ACTIVE() == 1) {
        if (OPEN_CFW_PB_DEV_SETTING_DISPLAY_LEFT_ACTIVE() == 1) {
            if (role == 1) {
                OPEN_CFW_PB_DEV_SETTING_DISPLAY_STOP();
            }
            OPEN_CFW_PB_DEV_SETTING_DELAY(500U);
        }
        if (OPEN_CFW_PB_DEV_SETTING_DISPLAY_RIGHT_ACTIVE() == 1) {
            if (role == 1) {
                OPEN_CFW_PB_DEV_SETTING_DISPLAY_STOP();
            }
            OPEN_CFW_PB_DEV_SETTING_DELAY(500U);
        }
    }
    OPEN_CFW_PB_DEV_SETTING_KVDB_INVALIDATE();
    (void)OPEN_CFW_PB_DEV_SETTING_ONBOARDING_RESET(0U, &reset);
    (void)OPEN_CFW_PB_DEV_SETTING_FILE_REMOVE(
        OPEN_CFW_PB_DEV_SETTING_WHITELIST_PATH);
    OPEN_CFW_PB_DEV_SETTING_CLEAN_BONDS();
    (void)OPEN_CFW_PB_DEV_SETTING_FILESYSTEM_FORMAT();
    OPEN_CFW_PB_DEV_SETTING_RESTART();
    return 0;
}
#endif

#if defined(OPEN_CFW_PB_DEV_SETTING_INCLUDE_TX_RESTORE)
int PB_TxEncodeRestoreFactory(
    uint8_t magic, void *buffer, uint16_t capacity, uint8_t *message,
    const uint8_t *payload)
{
    if (message != (void *)0) {
        message[8] = 0U;
    }
    return open_cfw_pb_service_dev_setting_transmit(
        magic, buffer, capacity, message, payload, 0x0DU, 0x0CU, 0U);
}
#endif

#if defined(OPEN_CFW_PB_DEV_SETTING_INCLUDE_RX_RESTART)
int PB_RxQuickRestart(uint8_t magic, const uint8_t *payload)
{
    (void)magic;
    if (payload == (const uint8_t *)0) {
        return 2;
    }
    OPEN_CFW_PB_DEV_SETTING_RESTART();
    return 0;
}
#endif

#if defined(OPEN_CFW_PB_DEV_SETTING_INCLUDE_TX_RESTART)
int PB_TxEncodeQuickRestart(
    uint8_t magic, void *buffer, uint16_t capacity, uint8_t *message,
    const uint8_t *payload)
{
    if (message != (void *)0) {
        message[8] = 0U;
    }
    return open_cfw_pb_service_dev_setting_transmit(
        magic, buffer, capacity, message, payload, 0x0FU, 0x0EU, 0U);
}
#endif

#if defined(OPEN_CFW_PB_DEV_SETTING_INCLUDE_RX_HEARTBEAT)
int PB_RxBaseConnHeartBeat(uint8_t magic, const uint8_t *payload)
{
    (void)magic;
    if (payload == (const uint8_t *)0) {
        return 2;
    }
    OPEN_CFW_PB_DEV_SETTING_HEARTBEAT_STATE(1U);
    return 0;
}
#endif

#if defined(OPEN_CFW_PB_DEV_SETTING_INCLUDE_TX_HEARTBEAT)
int PB_TxEncodeBaseConnHeartBeat(
    uint8_t magic, void *buffer, uint16_t capacity, uint8_t *message,
    const uint8_t *payload)
{
    if (message != (void *)0) {
        message[8] = 0U;
    }
    return open_cfw_pb_service_dev_setting_transmit(
        magic, buffer, capacity, message, payload, 0x0EU, 0x0DU, 1U);
}
#endif

#if defined(OPEN_CFW_PB_DEV_SETTING_INCLUDE_RX_TIME)
int PB_RxTimeSyncInfo(uint8_t magic, const uint8_t *payload)
{
    volatile uint8_t *cache = OPEN_CFW_PB_DEV_SETTING_TIME_CACHE;
    uint32_t utc;
    int8_t timezone;
    (void)magic;
    if (payload == (const uint8_t *)0) {
        return 2;
    }
    utc = (uint32_t)payload[0] | ((uint32_t)payload[1] << 8) |
        ((uint32_t)payload[2] << 16) | ((uint32_t)payload[3] << 24);
    timezone = (int8_t)payload[4];
    cache[0] = payload[0];
    cache[1] = payload[1];
    cache[2] = payload[2];
    cache[3] = payload[3];
    cache[4] = payload[4];
    OPEN_CFW_PB_DEV_SETTING_SYSTEM_TIME_SYNC(utc, timezone);
    OPEN_CFW_PB_DEV_SETTING_PEER_TIME_SYNC(0U);
    OPEN_CFW_PB_DEV_SETTING_HEARTBEAT_STATE(1U);
    return 0;
}
#endif

#if defined(OPEN_CFW_PB_DEV_SETTING_INCLUDE_TX_TIME)
int PB_TxEncodeTimeSyncInfo(
    uint8_t magic, void *buffer, uint16_t capacity, uint8_t *message,
    const uint8_t *payload)
{
    volatile uint8_t *cache = OPEN_CFW_PB_DEV_SETTING_TIME_CACHE;
    uint32_t utc;
    int status;
    if (message != (void *)0) {
        message[13] = 0U;
    }
    status = open_cfw_pb_service_dev_setting_transmit(
        magic, buffer, capacity, message, payload, 0x80U, 0x80U, 0U);
    if (status == 0) {
        utc = (uint32_t)cache[0] | ((uint32_t)cache[1] << 8) |
            ((uint32_t)cache[2] << 16) | ((uint32_t)cache[3] << 24);
        OPEN_CFW_PB_DEV_SETTING_TIME_PERSIST(utc, (int8_t)cache[4]);
    }
    return status;
}
#endif

#if defined(OPEN_CFW_PB_DEV_SETTING_INCLUDE_RX_AUDIO)
int PB_RxAudControl(uint8_t magic, const uint8_t *payload)
{
    (void)magic;
    return payload == (const uint8_t *)0 ? 2 : 0;
}
#endif

#if defined(OPEN_CFW_PB_DEV_SETTING_INCLUDE_TX_AUDIO)
int PB_TxEncodeAudControl(
    uint8_t magic, void *buffer, uint16_t capacity, uint8_t *message,
    const uint8_t *payload)
{
    if (message != (void *)0) {
        message[12] = 0U;
        message[13] = 0U;
        message[14] = 0U;
        message[15] = 0U;
        message[16] = 0U;
    }
    return open_cfw_pb_service_dev_setting_transmit(
        magic, buffer, capacity, message, payload, 0x81U, 0x81U, 0U);
}
#endif
