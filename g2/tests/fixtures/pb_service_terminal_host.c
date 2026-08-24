#include <assert.h>
#include <stdint.h>
#include <string.h>

static uint8_t host_message[0x850];
static uint8_t host_encode_buffer[0x878];
static uint8_t host_encoded_message[0x850];
static uint8_t host_last_magic;
static uint32_t host_last_tick;
static uint32_t host_now;
static uint32_t host_role;
static uint32_t host_decode_ok;
static uint32_t host_encode_ok;
static uint8_t host_decode_magic;
static uint32_t host_decode_length;
static uint32_t host_transport_calls;
static uint32_t host_transport_kind;
static uint32_t host_transport_route;
static uint32_t host_transport_service;
static uint32_t host_transport_length;

static uint32_t host_decode(void *input, const void *descriptor, void *message);
static uint32_t host_encode(void *output, const void *descriptor,
                            const void *message);
static uint32_t host_tick_get(void);
static uint32_t host_role_get(void);
static int host_send(uint32_t route, uint32_t service,
                     const void *data, uint32_t length);
static int host_notify(uint32_t route, uint32_t service,
                       const void *data, uint32_t length);

#define OPEN_CFW_PB_TERMINAL_MESSAGE host_message
#define OPEN_CFW_PB_TERMINAL_ENCODE_BUFFER host_encode_buffer
#define OPEN_CFW_PB_TERMINAL_DESCRIPTOR ((const void *)(uintptr_t)0x77C634U)
#define OPEN_CFW_PB_TERMINAL_LAST_MAGIC (&host_last_magic)
#define OPEN_CFW_PB_TERMINAL_LAST_TICK (&host_last_tick)
#define OPEN_CFW_PB_TERMINAL_INPUT_FROM_BUFFER(data, length) \
    ((open_cfw_pb_terminal_input){(void *)(data), (void *)0, (length), \
                                  (const char *)0})
#define OPEN_CFW_PB_TERMINAL_DECODE(input, descriptor, message) \
    host_decode((input), (descriptor), (message))
#define OPEN_CFW_PB_TERMINAL_ENCODE(output, descriptor, message) \
    host_encode((output), (descriptor), (message))
#define OPEN_CFW_PB_TERMINAL_TICK_GET() host_tick_get()
#define OPEN_CFW_PB_TERMINAL_ROLE_GET() host_role_get()
#define OPEN_CFW_PB_TERMINAL_SEND(route, service, data, length) \
    host_send((route), (service), (data), (length))
#define OPEN_CFW_PB_TERMINAL_NOTIFY(route, service, data, length) \
    host_notify((route), (service), (data), (length))

#include "../../components/apollo_main/core_overlay/pb_service_terminal.c"

static uint32_t host_decode(void *raw_input, const void *descriptor,
                            void *raw_message)
{
    open_cfw_pb_terminal_input *input =
        (open_cfw_pb_terminal_input *)raw_input;
    uint8_t *message = (uint8_t *)raw_message;
    assert(descriptor == OPEN_CFW_PB_TERMINAL_DESCRIPTOR);
    host_decode_length = input->bytes_left;
    if (host_decode_ok == 0U) {
        input->error = "decode";
        return 0U;
    }
    message[1] = host_decode_magic;
    return 1U;
}

static uint32_t host_encode(void *raw_output, const void *descriptor,
                            const void *raw_message)
{
    open_cfw_pb_terminal_output *output =
        (open_cfw_pb_terminal_output *)raw_output;
    assert(descriptor == OPEN_CFW_PB_TERMINAL_DESCRIPTOR);
    assert(output->write == open_cfw_pb_service_terminal_buffer_write);
    assert(output->context == host_encode_buffer);
    assert(output->capacity == 0x878U);
    memcpy(host_encoded_message, raw_message, sizeof(host_encoded_message));
    if (host_encode_ok == 0U) {
        output->error = "encode";
        return 0U;
    }
    output->length = 0x10003U;
    return 1U;
}

static uint32_t host_tick_get(void) { return host_now; }
static uint32_t host_role_get(void) { return host_role; }

static int host_transport(uint32_t kind, uint32_t route, uint32_t service,
                          const void *data, uint32_t length)
{
    assert(data == host_encode_buffer);
    ++host_transport_calls;
    host_transport_kind = kind;
    host_transport_route = route;
    host_transport_service = service;
    host_transport_length = length;
    return -9;
}

static int host_send(uint32_t route, uint32_t service,
                     const void *data, uint32_t length)
{
    return host_transport(1U, route, service, data, length);
}

static int host_notify(uint32_t route, uint32_t service,
                       const void *data, uint32_t length)
{
    return host_transport(2U, route, service, data, length);
}

static void reset_host(void)
{
    memset(host_message, 0xCC, sizeof(host_message));
    memset(host_encode_buffer, 0, sizeof(host_encode_buffer));
    memset(host_encoded_message, 0, sizeof(host_encoded_message));
    host_last_magic = 0xFEU;
    host_last_tick = 100U;
    host_now = 1000U;
    host_role = 1U;
    host_decode_ok = 1U;
    host_encode_ok = 1U;
    host_decode_magic = 0x42U;
    host_decode_length = 0U;
    host_transport_calls = 0U;
    host_transport_kind = 0U;
    host_transport_route = 0U;
    host_transport_service = 0U;
    host_transport_length = 0U;
}

static uint32_t load_u32(const uint8_t *data)
{
    return (uint32_t)data[0] | ((uint32_t)data[1] << 8) |
        ((uint32_t)data[2] << 16) | ((uint32_t)data[3] << 24);
}

static void assert_envelope(uint8_t command, uint16_t tag, uint32_t kind)
{
    assert(host_encoded_message[0] == command);
    assert(host_encoded_message[1] == 0xFFU);
    assert(host_encoded_message[2] == (uint8_t)tag);
    assert(host_encoded_message[3] == (uint8_t)(tag >> 8));
    assert(host_transport_calls == 1U);
    assert(host_transport_kind == kind);
    assert(host_transport_route == 1U);
    assert(host_transport_service == 0x30U);
    assert(host_transport_length == 3U);
    assert(host_last_magic == 0xFEU);
}

int main(void)
{
    uint8_t input[4] = {1U, 2U, 3U, 4U};
    uint8_t decoded[0x850] = {0};
    uint8_t response = 7U;
    uint8_t status[2] = {0x34U, 0x12U};
    uint8_t voice = 9U;
    uint8_t query[8] = {1U, 2U, 3U, 4U, 5U, 6U, 7U, 8U};
    open_cfw_pb_terminal_output output;

    reset_host();
    output.write = open_cfw_pb_service_terminal_buffer_write;
    output.context = host_encode_buffer;
    output.capacity = sizeof(host_encode_buffer);
    output.length = sizeof(host_encode_buffer) - 2U;
    output.error = (const char *)0;
    assert(output.write(&output, input, 2U) == 1U);
    assert(host_encode_buffer[sizeof(host_encode_buffer) - 2U] == 1U);
    assert(output.write(&output, input, 3U) == 0U);
    output.length = sizeof(host_encode_buffer) + 1U;
    assert(output.write(&output, input, 0U) == 0U);

    assert(APP_PbTerminalRxFrameDataProcess(0, 1U, decoded) == 6U);
    assert(APP_PbTerminalRxFrameDataProcess(input, 1U, 0) == 6U);
    host_decode_ok = 0U;
    assert(APP_PbTerminalRxFrameDataProcess(input, 0x10004U, decoded) == 5U);
    assert(host_decode_length == 4U);
    host_decode_ok = 1U;
    host_last_magic = 0x42U;
    host_now = 3099U;
    assert(APP_PbTerminalRxFrameDataProcess(input, 4U, decoded) == 13U);
    assert(host_last_tick == 100U);
    host_now = 3100U;
    assert(APP_PbTerminalRxFrameDataProcess(input, 4U, decoded) == 0U);
    assert(host_last_tick == 3100U && host_last_magic == 0x42U);
    host_decode_magic = 0x43U;
    host_now = 3101U;
    assert(APP_PbTerminalRxFrameDataProcess(input, 4U, decoded) == 0U);
    assert(host_last_tick == 3101U && host_last_magic == 0x43U);

    reset_host();
    assert(open_cfw_pb_terminal_encode_and_send(
               0x12U, 99U, input, 0x34U, 0U) == 8U);
    assert(host_message[0] == 0x12U && host_message[1] == 0x34U);
    assert(host_message[2] == 99U && host_message[4] == 0U);
    assert(host_transport_calls == 0U);

    reset_host();
    assert(APP_PbTerminalTxEncodeCommResp(0, 3U) == 6U);
    assert(APP_PbTerminalTxEncodeStatusReply(0) == 6U);
    assert(APP_PbTerminalTxEncodeVoiceInput(0) == 6U);
    assert(APP_PbTerminalTxEncodeQueryReply(0) == 6U);

    reset_host();
    assert(APP_PbTerminalTxEncodeCommResp(&response, 0x1A5U) == 0U);
    assert(host_encoded_message[0] == 0xF0U);
    assert(host_encoded_message[1] == 0xA5U);
    assert(host_encoded_message[2] == 13U);
    assert(host_encoded_message[4] == 7U);
    assert(host_transport_kind == 1U && host_transport_service == 0x30U);

    reset_host();
    assert(APP_PbTerminalTxEncodeStatusReply(status) == 0U);
    assert_envelope(0xA1U, 9U, 2U);
    assert(host_encoded_message[4] == 0x34U &&
           host_encoded_message[5] == 0x12U);

    reset_host();
    assert(APP_PbTerminalTxEncodeVoiceInput(&voice) == 0U);
    assert_envelope(0xA2U, 10U, 2U);
    assert(host_encoded_message[4] == 9U);

    reset_host();
    assert(APP_PbTerminalTxEncodeQueryReply(query) == 0U);
    assert_envelope(0xA3U, 11U, 2U);
    assert(memcmp(host_encoded_message + 4U, query, sizeof(query)) == 0);

    reset_host();
    APP_PbTerminalTxEncodeAgentInterrupt();
    assert_envelope(0xA4U, 12U, 2U);
    assert(host_encoded_message[4] == 0U);

    reset_host();
    APP_PbTerminalTxEncodeSessionSwitchRequest(0x11223344U, 0x55667788U);
    assert_envelope(0xA5U, 18U, 2U);
    assert(load_u32(host_encoded_message + 4U) == 0x55667788U);
    assert(load_u32(host_encoded_message + 8U) == 0x11223344U);

    reset_host();
    APP_PbTerminalTxEncodeNewSessionRequest(0x89ABCDEFU);
    assert_envelope(0xA6U, 19U, 2U);
    assert(load_u32(host_encoded_message + 4U) == 0x89ABCDEFU);

    reset_host();
    APP_PbTerminalTxEncodeNewSessionCancel();
    assert_envelope(0xA8U, 22U, 2U);
    assert(host_encoded_message[4] == 0U);

    reset_host();
    APP_PbTerminalTxEncodeDisplayStateNotify(4U, 0x12345678U, 0xABU);
    assert_envelope(0xA7U, 20U, 2U);
    assert(host_encoded_message[4] == 4U);
    assert(load_u32(host_encoded_message + 8U) == 0x12345678U);
    assert(host_encoded_message[12] == 0xABU);

    reset_host();
    APP_PbTerminalTxEncodeDisplayStateNotify(3U, 0x12345678U, 0xABU);
    assert_envelope(0xA7U, 20U, 2U);
    assert(load_u32(host_encoded_message + 8U) == 0U);
    assert(host_encoded_message[12] == 0U);

    reset_host();
    APP_PbTerminalTxEncodeListFocus(0xCAFEBABEU);
    assert_envelope(0xA9U, 24U, 2U);
    assert(load_u32(host_encoded_message + 4U) == 0xCAFEBABEU);

    reset_host();
    APP_PbTerminalTxEncodeOverlayFocus(0x102U, 0x13579BDFU);
    assert_envelope(0xAAU, 25U, 2U);
    assert(host_encoded_message[4] == 2U);
    assert(load_u32(host_encoded_message + 8U) == 0x13579BDFU);

    reset_host();
    host_role = 0U;
    assert(APP_PbTerminalTxEncodeStatusReply(status) == 0U);
    assert(host_transport_calls == 0U);
    reset_host();
    host_encode_ok = 0U;
    assert(APP_PbTerminalTxEncodeStatusReply(status) == 5U);
    assert(host_transport_calls == 0U);
    return 0;
}
