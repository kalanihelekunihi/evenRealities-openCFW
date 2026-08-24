#include <assert.h>
#include <stdint.h>
#include <string.h>

static uint8_t host_message[0xFAC];
static uint8_t host_encode_buffer[0x100];
static uint8_t host_last_magic;
static uint32_t host_last_tick;
static uint32_t host_now;
static uint32_t host_role;
static uint32_t host_decode_ok;
static uint32_t host_encode_ok;
static uint8_t host_decode_command;
static uint8_t host_decode_magic;
static uint32_t host_decode_length;
static uint32_t host_transport_calls;
static uint32_t host_transport_kind;
static uint32_t host_transport_route;
static uint32_t host_transport_service;
static uint32_t host_transport_length;
static uint8_t host_encoded_message[0xFAC];

static uint32_t host_decode(void *input, const void *descriptor, void *message);
static uint32_t host_encode(void *output, const void *descriptor, const void *message);
static uint32_t host_tick_get(void);
static uint32_t host_role_get(void);
static int host_send(uint32_t route, uint32_t service, const void *data, uint32_t length);
static int host_notify(uint32_t route, uint32_t service, const void *data, uint32_t length);

#define OPEN_CFW_PB_CONVERSATE_MESSAGE host_message
#define OPEN_CFW_PB_CONVERSATE_ENCODE_BUFFER host_encode_buffer
#define OPEN_CFW_PB_CONVERSATE_DESCRIPTOR ((const void *)(uintptr_t)0x775B24U)
#define OPEN_CFW_PB_CONVERSATE_LAST_MAGIC (&host_last_magic)
#define OPEN_CFW_PB_CONVERSATE_LAST_TICK (&host_last_tick)
#define OPEN_CFW_PB_CONVERSATE_INPUT_FROM_BUFFER(data, length) \
    ((open_cfw_pb_conversate_input){(void *)(data), (void *)0, (length), (const char *)0})
#define OPEN_CFW_PB_CONVERSATE_DECODE(input, descriptor, message) \
    host_decode((input), (descriptor), (message))
#define OPEN_CFW_PB_CONVERSATE_ENCODE(output, descriptor, message) \
    host_encode((output), (descriptor), (message))
#define OPEN_CFW_PB_CONVERSATE_TICK_GET() host_tick_get()
#define OPEN_CFW_PB_CONVERSATE_ROLE_GET() host_role_get()
#define OPEN_CFW_PB_CONVERSATE_SEND(route, service, data, length) \
    host_send((route), (service), (data), (length))
#define OPEN_CFW_PB_CONVERSATE_NOTIFY(route, service, data, length) \
    host_notify((route), (service), (data), (length))

#include "../../components/apollo_main/core_overlay/pb_service_conversate.c"

static uint32_t host_decode(void *raw_input, const void *descriptor, void *raw_message)
{
    open_cfw_pb_conversate_input *input =
        (open_cfw_pb_conversate_input *)raw_input;
    uint8_t *message = (uint8_t *)raw_message;
    assert(descriptor == OPEN_CFW_PB_CONVERSATE_DESCRIPTOR);
    host_decode_length = input->bytes_left;
    if (host_decode_ok == 0U) {
        input->error = "decode";
        return 0U;
    }
    message[0] = host_decode_command;
    message[1] = host_decode_magic;
    return 1U;
}

static uint32_t host_encode(void *raw_output, const void *descriptor,
                            const void *raw_message)
{
    open_cfw_pb_conversate_output *output =
        (open_cfw_pb_conversate_output *)raw_output;
    assert(descriptor == OPEN_CFW_PB_CONVERSATE_DESCRIPTOR);
    memcpy(host_encoded_message, raw_message, sizeof(host_encoded_message));
    if (host_encode_ok == 0U) {
        output->error = "encode";
        return 0U;
    }
    output->length = 3U;
    host_encode_buffer[0] = 0xA5U;
    host_encode_buffer[1] = 0x5AU;
    host_encode_buffer[2] = 0x11U;
    return 1U;
}

static uint32_t host_tick_get(void) { return host_now; }
static uint32_t host_role_get(void) { return host_role; }

static int host_transport(uint32_t kind, uint32_t route, uint32_t service,
                          const void *data, uint32_t length)
{
    assert(data == host_encode_buffer);
    assert(host_encode_buffer[0] == 0xA5U);
    ++host_transport_calls;
    host_transport_kind = kind;
    host_transport_route = route;
    host_transport_service = service;
    host_transport_length = length;
    return -7;
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
    host_last_magic = 0x20U;
    host_last_tick = 100U;
    host_now = 1000U;
    host_role = 1U;
    host_decode_ok = 1U;
    host_encode_ok = 1U;
    host_decode_command = 0x44U;
    host_decode_magic = 0x21U;
    host_decode_length = 0U;
    host_transport_calls = 0U;
    host_transport_kind = 0U;
    host_transport_route = 0U;
    host_transport_service = 0U;
    host_transport_length = 0U;
}

static void assert_envelope(uint8_t command, uint8_t magic, uint16_t tag,
                            uint32_t transport_kind)
{
    assert(host_encoded_message[0] == command);
    assert(host_encoded_message[1] == magic);
    assert(host_encoded_message[2] == (uint8_t)tag);
    assert(host_encoded_message[3] == (uint8_t)(tag >> 8));
    assert(host_transport_calls == 1U);
    assert(host_transport_kind == transport_kind);
    assert(host_transport_route == 1U);
    assert(host_transport_service == 0x0BU);
    assert(host_transport_length == 3U);
    assert(host_last_magic == 0x20U);
}

int main(void)
{
    uint8_t input[4] = {1U, 2U, 3U, 4U};
    uint8_t decoded[0xFAC] = {0};
    uint16_t notify = 0xBEEFU;
    uint8_t response = 0x37U;
    uint8_t tracking[12];
    open_cfw_pb_conversate_output output;
    uint32_t index;

    reset_host();
    output.write = open_cfw_pb_service_conversate_buffer_write;
    output.context = host_encode_buffer;
    output.capacity = sizeof(host_encode_buffer);
    output.length = 254U;
    output.error = (const char *)0;
    assert(output.write(&output, input, 2U) == 1U);
    assert(host_encode_buffer[254] == 1U && host_encode_buffer[255] == 2U);
    assert(output.write(&output, input, 3U) == 0U);
    output.length = 257U;
    assert(output.write(&output, input, 0U) == 0U);

    assert(APP_PbConversateRxFrameDataProcess((const void *)0, 1U, decoded) == 6U);
    assert(APP_PbConversateRxFrameDataProcess(input, 1U, (void *)0) == 6U);
    host_decode_ok = 0U;
    assert(APP_PbConversateRxFrameDataProcess(input, 0x10001U, decoded) == 5U);
    assert(host_decode_length == 1U);
    host_decode_ok = 1U;
    host_last_magic = 0x21U;
    host_last_tick = 100U;
    host_now = 3099U;
    assert(APP_PbConversateRxFrameDataProcess(input, 4U, decoded) == 13U);
    assert(host_last_tick == 100U);
    host_now = 3100U;
    assert(APP_PbConversateRxFrameDataProcess(input, 4U, decoded) == 0U);
    assert(host_last_magic == 0x21U && host_last_tick == 3100U);
    host_decode_magic = 0x22U;
    host_now = 3101U;
    assert(APP_PbConversateRxFrameDataProcess(input, 4U, decoded) == 0U);
    assert(host_last_magic == 0x22U && host_last_tick == 3101U);

    reset_host();
    assert(APP_PbConversateTxEncodeNotify((const void *)0) == 6U);
    assert(APP_PbConversateTxEncodeNotify(&notify) == 0U);
    assert_envelope(0xA1U, 0x21U, 9U, 2U);
    assert(host_encoded_message[4] == 0xEFU && host_encoded_message[5] == 0xBEU);
    assert(host_encoded_message[6] == 0U);

    reset_host();
    assert(APP_PbConversateTxEncodePrepNoteListRequest() == 0U);
    assert_envelope(2U, 0x21U, 4U, 2U);
    assert(host_encoded_message[4] == 0U);

    reset_host();
    assert(APP_PbConversateTxEncodePrepNoteSelect(0x123U, 0x89ABCDEFU) == 0U);
    assert_envelope(4U, 0x21U, 6U, 2U);
    assert(host_encoded_message[4] == 0x23U);
    assert(host_encoded_message[5] == 0U && host_encoded_message[7] == 0U);
    assert(host_encoded_message[8] == 0xEFU && host_encoded_message[11] == 0x89U);

    reset_host();
    assert(APP_PbConversateTxEncodeCommResp((const void *)0, 7U) == 6U);
    assert(APP_PbConversateTxEncodeCommResp(&response, 0x1A5U) == 0U);
    assert_envelope(0xA2U, 0xA5U, 10U, 1U);
    assert(host_encoded_message[4] == 0x37U);

    for (index = 0U; index < 12U; ++index) {
        tracking[index] = (uint8_t)(0x80U + index);
    }
    reset_host();
    assert(APP_PbConversateTxEncodeTagTrackingData((const void *)0) == 6U);
    assert(APP_PbConversateTxEncodeTagTrackingData(tracking) == 0U);
    assert_envelope(0xA3U, 0x21U, 12U, 2U);
    assert(memcmp(host_encoded_message + 4U, tracking, 12U) == 0);

    reset_host();
    host_role = 0U;
    assert(APP_PbConversateTxEncodeNotify(&notify) == 0U);
    assert(host_transport_calls == 0U);
    reset_host();
    host_encode_ok = 0U;
    assert(APP_PbConversateTxEncodeNotify(&notify) == 5U);
    assert(host_transport_calls == 0U);
    return 0;
}
