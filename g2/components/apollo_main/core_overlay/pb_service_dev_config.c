/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room implementation of the three linked G2
 * pb_service_dev_config.c entries. Diagnostic-only EasyLogger calls are
 * omitted; nanopb decoding/encoding, command dispatch, timer behavior,
 * status values, and BLE transport behavior are preserved.
 */

#include <stdint.h>

typedef struct {
    void *callback;
    void *state;
    uint32_t bytes_left;
    const char *error;
} open_cfw_pb_dev_config_input;

struct open_cfw_pb_dev_config_output;
typedef uint32_t (*open_cfw_pb_dev_config_write_fn)(
    struct open_cfw_pb_dev_config_output *, const void *, uint32_t);
typedef struct open_cfw_pb_dev_config_output {
    open_cfw_pb_dev_config_write_fn write;
    void *context;
    uint32_t capacity;
    uint32_t length;
    const char *error;
} open_cfw_pb_dev_config_output;

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(open_cfw_pb_dev_config_input) == 16U,
    "G2 nanopb input stream ABI changed");
_Static_assert(sizeof(open_cfw_pb_dev_config_output) == 20U,
    "G2 nanopb output stream ABI changed");
#endif

#ifndef OPEN_CFW_PB_DEV_CONFIG_MESSAGE
#define OPEN_CFW_PB_DEV_CONFIG_MESSAGE \
    ((uint8_t *)(uintptr_t)0x200F57B4U)
#endif
#ifndef OPEN_CFW_PB_DEV_CONFIG_ENCODE_BUFFER
#define OPEN_CFW_PB_DEV_CONFIG_ENCODE_BUFFER \
    ((uint8_t *)(uintptr_t)0x2037C3A0U)
#endif
#ifndef OPEN_CFW_PB_DEV_CONFIG_DESCRIPTOR
#define OPEN_CFW_PB_DEV_CONFIG_DESCRIPTOR \
    ((const void *)(uintptr_t)0x007766DCU)
#endif
#ifndef OPEN_CFW_PB_DEV_CONFIG_HEARTBEAT_TIMER
#define OPEN_CFW_PB_DEV_CONFIG_HEARTBEAT_TIMER \
    ((void *)(uintptr_t)0x004B81B9U)
#endif

#ifndef OPEN_CFW_PB_DEV_CONFIG_INPUT_FROM_BUFFER
open_cfw_pb_dev_config_input open_cfw_nanopb_istream_from_buffer(
    const void *data, uint32_t length);
#define OPEN_CFW_PB_DEV_CONFIG_INPUT_FROM_BUFFER(data, length) \
    open_cfw_nanopb_istream_from_buffer((data), (length))
#endif
#ifndef OPEN_CFW_PB_DEV_CONFIG_DECODE
uint32_t open_cfw_nanopb_decode(
    open_cfw_pb_dev_config_input *input, const void *descriptor, void *message);
#define OPEN_CFW_PB_DEV_CONFIG_DECODE(input, descriptor, message) \
    open_cfw_nanopb_decode((input), (descriptor), (message))
#endif
#ifndef OPEN_CFW_PB_DEV_CONFIG_ENCODE
uint32_t open_cfw_format_message_encode(
    void *output, const void *descriptor, const void *message);
#define OPEN_CFW_PB_DEV_CONFIG_ENCODE(output, descriptor, message) \
    open_cfw_format_message_encode((output), (descriptor), (message))
#endif
#ifndef OPEN_CFW_PB_DEV_CONFIG_SEND
int open_cfw_ble_msgtx_pb_send(
    uint32_t route, uint32_t service, const void *data, uint32_t length);
#define OPEN_CFW_PB_DEV_CONFIG_SEND(route, service, data, length) \
    open_cfw_ble_msgtx_pb_send((route), (service), (data), (length))
#endif

typedef int (*open_cfw_pb_dev_config_rx_fn)(
    uint8_t magic, const uint8_t *payload);
typedef int (*open_cfw_pb_dev_config_tx_fn)(
    uint8_t magic, void *buffer, uint32_t capacity, void *message,
    const uint8_t *payload);

#define OPEN_CFW_DECLARE_PAIR(name) \
    int open_cfw_pb_dev_config_rx_##name(uint8_t, const uint8_t *); \
    int open_cfw_pb_dev_config_tx_##name( \
        uint8_t, void *, uint32_t, void *, const uint8_t *)

OPEN_CFW_DECLARE_PAIR(authentication);
OPEN_CFW_DECLARE_PAIR(pipe_role_change);
OPEN_CFW_DECLARE_PAIR(ring_connect_info);
OPEN_CFW_DECLARE_PAIR(ble_connect_param);
OPEN_CFW_DECLARE_PAIR(disconnect_info);
OPEN_CFW_DECLARE_PAIR(unpair_info);
OPEN_CFW_DECLARE_PAIR(restore_factory_settings);
OPEN_CFW_DECLARE_PAIR(base_connect_heartbeat);
OPEN_CFW_DECLARE_PAIR(quick_restart);
OPEN_CFW_DECLARE_PAIR(time_sync);
OPEN_CFW_DECLARE_PAIR(audio_control);

#ifndef OPEN_CFW_PB_DEV_CONFIG_TIMER_CANCEL
void open_cfw_pb_dev_config_timer_cancel(void *timer);
#define OPEN_CFW_PB_DEV_CONFIG_TIMER_CANCEL(timer) \
    open_cfw_pb_dev_config_timer_cancel((timer))
#endif
#ifndef OPEN_CFW_PB_DEV_CONFIG_TIMER_START
int open_cfw_pb_dev_config_timer_start(
    void *timer, uint32_t mode, uint32_t milliseconds);
#define OPEN_CFW_PB_DEV_CONFIG_TIMER_START(timer, mode, milliseconds) \
    open_cfw_pb_dev_config_timer_start((timer), (mode), (milliseconds))
#endif

uint32_t open_cfw_pb_service_dev_config_buffer_write(
    open_cfw_pb_dev_config_output *output, const void *data, uint32_t length);
void open_cfw_pb_service_dev_config_zero(void *data, uint32_t length);
int APP_PbRxErrorCode(uint8_t magic, const uint8_t *payload);
int APP_PbTxEncodeErrorCode(
    uint32_t route, uint32_t service, uint8_t magic,
    uint8_t original_command, uint8_t error_code);

#if defined(OPEN_CFW_PB_DEV_CONFIG_BUFFER_WRITE_ONLY)
#define OPEN_CFW_PB_DEV_CONFIG_INCLUDE_BUFFER_WRITE 1
#elif defined(OPEN_CFW_PB_DEV_CONFIG_ZERO_ONLY)
#define OPEN_CFW_PB_DEV_CONFIG_INCLUDE_ZERO 1
#elif defined(OPEN_CFW_PB_DEV_CONFIG_RX_ONLY)
#define OPEN_CFW_PB_DEV_CONFIG_INCLUDE_RX 1
#elif defined(OPEN_CFW_PB_DEV_CONFIG_ERROR_RX_ONLY)
#define OPEN_CFW_PB_DEV_CONFIG_INCLUDE_ERROR_RX 1
#elif defined(OPEN_CFW_PB_DEV_CONFIG_ERROR_TX_ONLY)
#define OPEN_CFW_PB_DEV_CONFIG_INCLUDE_ERROR_TX 1
#else
#define OPEN_CFW_PB_DEV_CONFIG_INCLUDE_BUFFER_WRITE 1
#define OPEN_CFW_PB_DEV_CONFIG_INCLUDE_ZERO 1
#define OPEN_CFW_PB_DEV_CONFIG_INCLUDE_RX 1
#define OPEN_CFW_PB_DEV_CONFIG_INCLUDE_ERROR_RX 1
#define OPEN_CFW_PB_DEV_CONFIG_INCLUDE_ERROR_TX 1
#endif

#if defined(OPEN_CFW_PB_DEV_CONFIG_INCLUDE_BUFFER_WRITE)
uint32_t open_cfw_pb_service_dev_config_buffer_write(
    open_cfw_pb_dev_config_output *output, const void *data, uint32_t length)
{
    uint8_t *destination = (uint8_t *)output->context;
    const uint8_t *source = (const uint8_t *)data;
    uint32_t index;

    if (length > output->capacity - output->length) {
        return 0U;
    }
    for (index = 0U; index < length; ++index) {
        destination[output->length + index] = source[index];
    }
    output->length += length;
    return 1U;
}
#endif

#if defined(OPEN_CFW_PB_DEV_CONFIG_INCLUDE_ZERO)
void open_cfw_pb_service_dev_config_zero(void *data, uint32_t length)
{
    uint8_t *bytes = (uint8_t *)data;
    uint32_t index;
    for (index = 0U; index < length; ++index) {
        bytes[index] = 0U;
    }
}
#endif

#if defined(OPEN_CFW_PB_DEV_CONFIG_INCLUDE_ERROR_RX)
int APP_PbRxErrorCode(uint8_t magic, const uint8_t *payload)
{
    /* Stock behavior only classifies payload[1] for diagnostics. */
    (void)magic;
    (void)payload;
    return 0;
}
#endif

#if defined(OPEN_CFW_PB_DEV_CONFIG_INCLUDE_ERROR_TX)
int APP_PbTxEncodeErrorCode(
    uint32_t route, uint32_t service, uint8_t magic,
    uint8_t original_command, uint8_t error_code)
{
    uint8_t *message = OPEN_CFW_PB_DEV_CONFIG_MESSAGE;
    open_cfw_pb_dev_config_output output;

    output.write = open_cfw_pb_service_dev_config_buffer_write;
    output.context = OPEN_CFW_PB_DEV_CONFIG_ENCODE_BUFFER;
    output.capacity = 0x100U;
    output.length = 0U;
    output.error = (const char *)0;

    message[0] = 10U;
    message[2] = magic;
    message[3] = 0U;
    message[4] = 9U;
    message[5] = 0U;
    message[8] = original_command;
    message[9] = error_code;
    if (OPEN_CFW_PB_DEV_CONFIG_ENCODE(
            &output, OPEN_CFW_PB_DEV_CONFIG_DESCRIPTOR, message) == 0U) {
        return 0x2B;
    }
    (void)OPEN_CFW_PB_DEV_CONFIG_SEND(
        route, service, OPEN_CFW_PB_DEV_CONFIG_ENCODE_BUFFER,
        output.length & 0xFFFFU);
    return 0;
}
#endif

#if defined(OPEN_CFW_PB_DEV_CONFIG_INCLUDE_RX)
static void open_cfw_pb_dev_config_dispatch_pair(
    open_cfw_pb_dev_config_rx_fn receive,
    open_cfw_pb_dev_config_tx_fn transmit,
    uint8_t magic, uint8_t *message, const uint8_t *payload)
{
    if (receive(magic, payload) == 0) {
        (void)transmit(magic, OPEN_CFW_PB_DEV_CONFIG_ENCODE_BUFFER,
            0x100U, message, payload);
    }
}

int APP_PbRxDevCfgFrameDataProcess(const void *data, uint32_t length)
{
    uint8_t *message = OPEN_CFW_PB_DEV_CONFIG_MESSAGE;
    open_cfw_pb_dev_config_input input;
    uint8_t command;
    uint8_t magic;
    uint8_t *payload;

    if (data == (const void *)0) {
        return 2;
    }
    open_cfw_pb_service_dev_config_zero(message, 0xD0U);
    input = OPEN_CFW_PB_DEV_CONFIG_INPUT_FROM_BUFFER(data, length & 0xFFFFU);
    if (OPEN_CFW_PB_DEV_CONFIG_DECODE(
            &input, OPEN_CFW_PB_DEV_CONFIG_DESCRIPTOR, message) == 0U) {
        return 0x2B;
    }

    command = message[0];
    magic = message[2];
    payload = &message[8];
    switch (command) {
    case 4:
        open_cfw_pb_dev_config_dispatch_pair(
            open_cfw_pb_dev_config_rx_authentication,
            open_cfw_pb_dev_config_tx_authentication,
            magic, message, payload);
        break;
    case 5:
        open_cfw_pb_dev_config_dispatch_pair(
            open_cfw_pb_dev_config_rx_pipe_role_change,
            open_cfw_pb_dev_config_tx_pipe_role_change,
            magic, message, payload);
        break;
    case 6:
        open_cfw_pb_dev_config_dispatch_pair(
            open_cfw_pb_dev_config_rx_ring_connect_info,
            open_cfw_pb_dev_config_tx_ring_connect_info,
            magic, message, payload);
        break;
    case 7:
        open_cfw_pb_dev_config_dispatch_pair(
            open_cfw_pb_dev_config_rx_ble_connect_param,
            open_cfw_pb_dev_config_tx_ble_connect_param,
            magic, message, payload);
        break;
    case 8:
        open_cfw_pb_dev_config_dispatch_pair(
            open_cfw_pb_dev_config_rx_disconnect_info,
            open_cfw_pb_dev_config_tx_disconnect_info,
            magic, message, payload);
        break;
    case 9:
        open_cfw_pb_dev_config_dispatch_pair(
            open_cfw_pb_dev_config_rx_unpair_info,
            open_cfw_pb_dev_config_tx_unpair_info,
            magic, message, payload);
        break;
    case 10:
        (void)APP_PbRxErrorCode(magic, payload);
        break;
    case 11:
    case 12:
        break;
    case 13:
        open_cfw_pb_dev_config_dispatch_pair(
            open_cfw_pb_dev_config_rx_restore_factory_settings,
            open_cfw_pb_dev_config_tx_restore_factory_settings,
            magic, message, payload);
        break;
    case 14:
        if (open_cfw_pb_dev_config_rx_base_connect_heartbeat(
                magic, payload) == 0) {
            OPEN_CFW_PB_DEV_CONFIG_TIMER_CANCEL(
                OPEN_CFW_PB_DEV_CONFIG_HEARTBEAT_TIMER);
            (void)OPEN_CFW_PB_DEV_CONFIG_TIMER_START(
                OPEN_CFW_PB_DEV_CONFIG_HEARTBEAT_TIMER, 0U, 30000U);
            (void)open_cfw_pb_dev_config_tx_base_connect_heartbeat(
                magic, OPEN_CFW_PB_DEV_CONFIG_ENCODE_BUFFER,
                0x100U, message, payload);
        }
        break;
    case 15:
        open_cfw_pb_dev_config_dispatch_pair(
            open_cfw_pb_dev_config_rx_quick_restart,
            open_cfw_pb_dev_config_tx_quick_restart,
            magic, message, payload);
        break;
    case 128:
        open_cfw_pb_dev_config_dispatch_pair(
            open_cfw_pb_dev_config_rx_time_sync,
            open_cfw_pb_dev_config_tx_time_sync,
            magic, message, payload);
        break;
    case 129:
        open_cfw_pb_dev_config_dispatch_pair(
            open_cfw_pb_dev_config_rx_audio_control,
            open_cfw_pb_dev_config_tx_audio_control,
            magic, message, payload);
        break;
    default:
        (void)APP_PbTxEncodeErrorCode(1U, 0x80U, magic, command, 8U);
        break;
    }
    return 0;
}
#endif
