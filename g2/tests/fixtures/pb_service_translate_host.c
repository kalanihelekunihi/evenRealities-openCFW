#include <assert.h>
#include <stdint.h>
#include <string.h>

static uint8_t host_message[0x854];
static uint8_t host_encode_buffer[0x100];
static uint8_t host_encoded_message[0x854];
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

#define OPEN_CFW_PB_TRANSLATE_MESSAGE host_message
#define OPEN_CFW_PB_TRANSLATE_ENCODE_BUFFER host_encode_buffer
#define OPEN_CFW_PB_TRANSLATE_DESCRIPTOR ((const void *)(uintptr_t)0x77CE5CU)
#define OPEN_CFW_PB_TRANSLATE_LAST_MAGIC (&host_last_magic)
#define OPEN_CFW_PB_TRANSLATE_LAST_TICK (&host_last_tick)
#define OPEN_CFW_PB_TRANSLATE_INPUT_FROM_BUFFER(data, length) \
    ((open_cfw_pb_translate_input){(void *)(data), (void *)0, (length), \
                                   (const char *)0})
#define OPEN_CFW_PB_TRANSLATE_DECODE(input, descriptor, message) \
    host_decode((input), (descriptor), (message))
#define OPEN_CFW_PB_TRANSLATE_ENCODE(output, descriptor, message) \
    host_encode((output), (descriptor), (message))
#define OPEN_CFW_PB_TRANSLATE_TICK_GET() host_tick_get()
#define OPEN_CFW_PB_TRANSLATE_ROLE_GET() host_role_get()
#define OPEN_CFW_PB_TRANSLATE_SEND(route, service, data, length) \
    host_send((route), (service), (data), (length))
#define OPEN_CFW_PB_TRANSLATE_NOTIFY(route, service, data, length) \
    host_notify((route), (service), (data), (length))

#include "../../components/apollo_main/core_overlay/pb_service_translate.c"

static uint32_t host_decode(void *raw_input, const void *descriptor,
                            void *raw_message)
{
    open_cfw_pb_translate_input *input =
        (open_cfw_pb_translate_input *)raw_input;
    uint8_t *message = (uint8_t *)raw_message;
    assert(descriptor == OPEN_CFW_PB_TRANSLATE_DESCRIPTOR);
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
    open_cfw_pb_translate_output *output =
        (open_cfw_pb_translate_output *)raw_output;
    assert(descriptor == OPEN_CFW_PB_TRANSLATE_DESCRIPTOR);
    assert(output->write == open_cfw_pb_service_translate_buffer_write);
    assert(output->context == host_encode_buffer);
    assert(output->capacity == 0x100U);
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

int main(void)
{
    uint8_t input[4] = {1U, 2U, 3U, 4U};
    uint8_t decoded[0x854] = {0};
    uint8_t response = 7U;
    uint16_t notification = 0x1234U;
    uint32_t mode = 0x89ABCDEFU;
    open_cfw_pb_translate_output output;

    reset_host();
    output.write = open_cfw_pb_service_translate_buffer_write;
    output.context = host_encode_buffer;
    output.capacity = sizeof(host_encode_buffer);
    output.length = sizeof(host_encode_buffer) - 2U;
    output.error = (const char *)0;
    assert(output.write(&output, input, 2U) == 1U);
    assert(host_encode_buffer[sizeof(host_encode_buffer) - 2U] == 1U);
    assert(output.write(&output, input, 3U) == 0U);

    assert(APP_PbTranslateRxFrameDataProcess(0, 1U, decoded) == 6U);
    assert(APP_PbTranslateRxFrameDataProcess(input, 1U, 0) == 6U);
    host_decode_ok = 0U;
    assert(APP_PbTranslateRxFrameDataProcess(input, 0x10004U, decoded) == 5U);
    assert(host_decode_length == 4U);
    host_decode_ok = 1U;
    host_last_magic = 0x42U;
    host_now = 3099U;
    assert(APP_PbTranslateRxFrameDataProcess(input, 4U, decoded) == 13U);
    assert(host_last_tick == 100U);
    host_now = 3100U;
    assert(APP_PbTranslateRxFrameDataProcess(input, 4U, decoded) == 0U);
    assert(host_last_tick == 3100U && host_last_magic == 0x42U);
    host_decode_magic = 0x43U;
    host_now = 3101U;
    assert(APP_PbTranslateRxFrameDataProcess(input, 4U, decoded) == 0U);

    reset_host();
    assert(APP_PbTranslateTxEncodeNotify(0) == 6U);
    assert(APP_PbTranslateTxEncodeCommResp(0, 1U) == 6U);
    assert(APP_PbTranslateTxEncodeModeSwitch(0) == 6U);

    reset_host();
    assert(APP_PbTranslateTxEncodeNotify(&notification) == 0U);
    assert(host_encoded_message[0] == 0xA1U);
    assert(host_encoded_message[1] == 0xFFU);
    assert(host_encoded_message[2] == 5U);
    assert(host_encoded_message[4] == 0x34U);
    assert(host_encoded_message[5] == 0x12U);
    assert(host_transport_kind == 2U);

    reset_host();
    assert(APP_PbTranslateTxEncodeCommResp(&response, 0x1A5U) == 0U);
    assert(host_encoded_message[0] == 0xA2U);
    assert(host_encoded_message[1] == 0xA5U);
    assert(host_encoded_message[2] == 7U);
    assert(host_encoded_message[4] == 7U);
    assert(host_transport_kind == 1U);

    reset_host();
    assert(APP_PbTranslateTxEncodeModeSwitch(&mode) == 0U);
    assert(host_encoded_message[0] == 0xA3U);
    assert(host_encoded_message[1] == 0xFFU);
    assert(host_encoded_message[2] == 6U);
    assert(load_u32(host_encoded_message + 4U) == mode);
    assert(host_transport_kind == 2U);

    assert(host_transport_calls == 1U);
    assert(host_transport_route == 1U);
    assert(host_transport_service == 5U);
    assert(host_transport_length == 3U);

    reset_host();
    host_encode_ok = 0U;
    assert(APP_PbTranslateTxEncodeCommResp(&response, 1U) == 5U);
    assert(host_transport_calls == 0U);

    reset_host();
    host_role = 0U;
    assert(APP_PbTranslateTxEncodeModeSwitch(&mode) == 0U);
    assert(host_transport_calls == 0U);
    return 0;
}
