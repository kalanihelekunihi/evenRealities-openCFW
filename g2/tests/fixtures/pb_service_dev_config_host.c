#include <assert.h>
#include <stdint.h>
#include <string.h>

static uint8_t host_message[0xD0];
static uint8_t host_encode_buffer[0x100];
static uint32_t host_timer_token;

#define OPEN_CFW_PB_DEV_CONFIG_MESSAGE host_message
#define OPEN_CFW_PB_DEV_CONFIG_ENCODE_BUFFER host_encode_buffer
#define OPEN_CFW_PB_DEV_CONFIG_HEARTBEAT_TIMER (&host_timer_token)
#include "../../components/apollo_main/core_overlay/pb_service_dev_config.c"

static uint8_t host_decoded[0xD0];
static uint32_t host_decode_ok = 1;
static uint32_t host_encode_ok = 1;
static uint32_t host_input_length;
static int host_rx_id;
static int host_tx_id;
static int host_rx_result;
static uint8_t host_magic;
static const uint8_t *host_payload;
static void *host_tx_buffer;
static uint32_t host_tx_capacity;
static void *host_tx_message;
static uint32_t host_timer_cancel_count;
static uint32_t host_timer_start_count;
static uint32_t host_timer_mode;
static uint32_t host_timer_ms;
static uint32_t host_send_count;
static uint32_t host_send_route;
static uint32_t host_send_service;
static const void *host_send_data;
static uint32_t host_send_length;

open_cfw_pb_dev_config_input open_cfw_nanopb_istream_from_buffer(
    const void *data, uint32_t length)
{
    open_cfw_pb_dev_config_input input;
    input.callback = (void *)data;
    input.state = (void *)0;
    input.bytes_left = length;
    input.error = (const char *)0;
    host_input_length = length;
    return input;
}

uint32_t open_cfw_nanopb_decode(
    open_cfw_pb_dev_config_input *input, const void *descriptor, void *message)
{
    assert(input != (void *)0);
    assert(descriptor == OPEN_CFW_PB_DEV_CONFIG_DESCRIPTOR);
    if (host_decode_ok != 0U) {
        memcpy(message, host_decoded, sizeof(host_decoded));
    }
    return host_decode_ok;
}

uint32_t open_cfw_format_message_encode(
    void *raw_output, const void *descriptor, const void *message)
{
    static const uint8_t encoded[] = {0xDA, 0x80, 0x0A};
    open_cfw_pb_dev_config_output *output = raw_output;
    assert(descriptor == OPEN_CFW_PB_DEV_CONFIG_DESCRIPTOR);
    assert(message == host_message);
    if (host_encode_ok == 0U) {
        return 0U;
    }
    return output->write(output, encoded, sizeof(encoded));
}

int open_cfw_ble_msgtx_pb_send(
    uint32_t route, uint32_t service, const void *data, uint32_t length)
{
    ++host_send_count;
    host_send_route = route;
    host_send_service = service;
    host_send_data = data;
    host_send_length = length;
    return 0;
}

#define HOST_PAIR(name, id) \
    int open_cfw_pb_dev_config_rx_##name( \
        uint8_t magic, const uint8_t *payload) \
    { \
        host_rx_id = (id); \
        host_magic = magic; \
        host_payload = payload; \
        return host_rx_result; \
    } \
    int open_cfw_pb_dev_config_tx_##name( \
        uint8_t magic, void *buffer, uint32_t capacity, void *message, \
        const uint8_t *payload) \
    { \
        host_tx_id = (id); \
        host_magic = magic; \
        host_tx_buffer = buffer; \
        host_tx_capacity = capacity; \
        host_tx_message = message; \
        host_payload = payload; \
        return 0; \
    }

HOST_PAIR(authentication, 4)
HOST_PAIR(pipe_role_change, 5)
HOST_PAIR(ring_connect_info, 6)
HOST_PAIR(ble_connect_param, 7)
HOST_PAIR(disconnect_info, 8)
HOST_PAIR(unpair_info, 9)
HOST_PAIR(restore_factory_settings, 13)
HOST_PAIR(base_connect_heartbeat, 14)
HOST_PAIR(quick_restart, 15)
HOST_PAIR(time_sync, 128)
HOST_PAIR(audio_control, 129)

void open_cfw_pb_dev_config_timer_cancel(void *timer)
{
    assert(timer == &host_timer_token);
    ++host_timer_cancel_count;
}

int open_cfw_pb_dev_config_timer_start(
    void *timer, uint32_t mode, uint32_t milliseconds)
{
    assert(timer == &host_timer_token);
    ++host_timer_start_count;
    host_timer_mode = mode;
    host_timer_ms = milliseconds;
    return 0;
}

static void reset_host(void)
{
    memset(host_message, 0xA5, sizeof(host_message));
    memset(host_encode_buffer, 0, sizeof(host_encode_buffer));
    memset(host_decoded, 0, sizeof(host_decoded));
    host_decode_ok = 1U;
    host_encode_ok = 1U;
    host_input_length = 0U;
    host_rx_id = 0;
    host_tx_id = 0;
    host_rx_result = 0;
    host_magic = 0U;
    host_payload = (void *)0;
    host_tx_buffer = (void *)0;
    host_tx_capacity = 0U;
    host_tx_message = (void *)0;
    host_timer_cancel_count = 0U;
    host_timer_start_count = 0U;
    host_timer_mode = 1U;
    host_timer_ms = 0U;
    host_send_count = 0U;
    host_send_route = 0U;
    host_send_service = 0U;
    host_send_data = (void *)0;
    host_send_length = 0U;
}

static void set_message(uint8_t command, uint8_t magic)
{
    host_decoded[0] = command;
    host_decoded[2] = magic;
    host_decoded[8] = 0x51U;
    host_decoded[9] = 0x52U;
}

static void test_statuses(void)
{
    uint8_t input[4] = {0};
    reset_host();
    assert(APP_PbRxDevCfgFrameDataProcess((void *)0, 4U) == 2);
    reset_host();
    host_decode_ok = 0U;
    assert(APP_PbRxDevCfgFrameDataProcess(input, 0x12345U) == 0x2B);
    assert(host_input_length == 0x2345U);
}

static void test_dispatch(void)
{
    static const uint8_t commands[] = {4, 5, 6, 7, 8, 9, 13, 15, 128, 129};
    uint8_t input[1] = {0};
    uint32_t index;
    for (index = 0U; index < sizeof(commands); ++index) {
        reset_host();
        set_message(commands[index], 0x6AU);
        assert(APP_PbRxDevCfgFrameDataProcess(input, 1U) == 0);
        assert(host_rx_id == commands[index]);
        assert(host_tx_id == commands[index]);
        assert(host_magic == 0x6AU);
        assert(host_payload == &host_message[8]);
        assert(host_tx_buffer == host_encode_buffer);
        assert(host_tx_capacity == 0x100U);
        assert(host_tx_message == host_message);
    }
    reset_host();
    set_message(4U, 3U);
    host_rx_result = 1;
    assert(APP_PbRxDevCfgFrameDataProcess(input, 1U) == 0);
    assert(host_rx_id == 4);
    assert(host_tx_id == 0);
}

static void test_special_commands(void)
{
    uint8_t input[1] = {0};
    reset_host();
    set_message(10U, 7U);
    host_decoded[9] = 9U;
    assert(APP_PbRxDevCfgFrameDataProcess(input, 1U) == 0);
    assert(host_rx_id == 0 && host_tx_id == 0 && host_send_count == 0U);

    reset_host();
    set_message(11U, 7U);
    assert(APP_PbRxDevCfgFrameDataProcess(input, 1U) == 0);
    reset_host();
    set_message(12U, 7U);
    assert(APP_PbRxDevCfgFrameDataProcess(input, 1U) == 0);

    reset_host();
    set_message(14U, 7U);
    assert(APP_PbRxDevCfgFrameDataProcess(input, 1U) == 0);
    assert(host_rx_id == 14 && host_tx_id == 14);
    assert(host_timer_cancel_count == 1U);
    assert(host_timer_start_count == 1U);
    assert(host_timer_mode == 0U && host_timer_ms == 30000U);
}

static void test_error_response(void)
{
    uint8_t input[1] = {0};
    reset_host();
    set_message(0x44U, 0xA7U);
    assert(APP_PbRxDevCfgFrameDataProcess(input, 1U) == 0);
    assert(host_message[0] == 10U);
    assert(host_message[2] == 0xA7U && host_message[3] == 0U);
    assert(host_message[4] == 9U && host_message[5] == 0U);
    assert(host_message[8] == 0x44U && host_message[9] == 8U);
    assert(host_send_count == 1U);
    assert(host_send_route == 1U && host_send_service == 0x80U);
    assert(host_send_data == host_encode_buffer && host_send_length == 3U);
    assert(host_encode_buffer[0] == 0xDAU);

    reset_host();
    host_encode_ok = 0U;
    assert(APP_PbTxEncodeErrorCode(1U, 0x80U, 1U, 2U, 3U) == 0x2B);
    assert(host_send_count == 0U);
}

static void test_buffer_writer(void)
{
    uint8_t output_bytes[4] = {0};
    uint8_t input_bytes[3] = {1, 2, 3};
    open_cfw_pb_dev_config_output output = {
        open_cfw_pb_service_dev_config_buffer_write,
        output_bytes, 4U, 0U, (const char *)0,
    };
    assert(output.write(&output, input_bytes, 3U) == 1U);
    assert(output.length == 3U && output_bytes[2] == 3U);
    assert(output.write(&output, input_bytes, 2U) == 0U);
    assert(output.length == 3U);
}

int main(void)
{
    test_statuses();
    test_dispatch();
    test_special_commands();
    test_error_response();
    test_buffer_writer();
    return 0;
}
