#include <assert.h>
#include <stdint.h>
#include <string.h>

static uint8_t host_message[0x20C];
static uint8_t host_encode_buffer[0x100];
static uint8_t host_duplicate_state[2];
static uint8_t host_notify_magic;
static uint32_t host_decode_ok;
static uint32_t host_encode_ok;
static uint8_t host_decode_command;
static uint8_t host_decode_magic;
static uint8_t host_decode_payload[0x208];
static uint32_t host_decode_length;
static int host_dispatch_status;
static uint32_t host_dispatch_calls;
static uint32_t host_dispatch_command;
static uint32_t host_dispatch_length;
static uint8_t host_dispatched_payload[0x208];
static uint32_t host_role;
static uint32_t host_display_ready;
static uint32_t host_role_calls;
static uint32_t host_display_calls;
static uint32_t host_display_selector;
static uint32_t host_transport_calls;
static uint32_t host_transport_kind;
static uint32_t host_transport_route;
static uint32_t host_transport_service;
static uint32_t host_transport_length;
static uint8_t host_encoded_message[0x20C];

static uint32_t host_decode(void *input, const void *descriptor, void *message);
static uint32_t host_encode(void *output, const void *descriptor,
                            const void *message);
static int host_dispatch(uint32_t command, const void *payload, uint32_t length);
static uint32_t host_role_get(void);
static uint32_t host_display_get(uint32_t selector);
static int host_send(uint32_t route, uint32_t service,
                     const void *data, uint32_t length);
static int host_notify(uint32_t route, uint32_t service,
                       const void *data, uint32_t length);

#define OPEN_CFW_PB_EVEN_AI_MESSAGE host_message
#define OPEN_CFW_PB_EVEN_AI_ENCODE_BUFFER host_encode_buffer
#define OPEN_CFW_PB_EVEN_AI_DESCRIPTOR ((const void *)(uintptr_t)0x777144U)
#define OPEN_CFW_PB_EVEN_AI_DUPLICATE_STATE host_duplicate_state
#define OPEN_CFW_PB_EVEN_AI_NOTIFY_MAGIC (&host_notify_magic)
#define OPEN_CFW_PB_EVEN_AI_INPUT_FROM_BUFFER(data, length) \
    ((open_cfw_pb_even_ai_input){(void *)(data), (void *)0, (length), \
                                 (const char *)0})
#define OPEN_CFW_PB_EVEN_AI_DECODE(input, descriptor, message) \
    host_decode((input), (descriptor), (message))
#define OPEN_CFW_PB_EVEN_AI_ENCODE(output, descriptor, message) \
    host_encode((output), (descriptor), (message))
#define OPEN_CFW_PB_EVEN_AI_RX_DISPATCH(command, payload, length) \
    host_dispatch((command), (payload), (length))
#define OPEN_CFW_PB_EVEN_AI_ROLE_GET() host_role_get()
#define OPEN_CFW_PB_EVEN_AI_DISPLAY_READY(selector) host_display_get((selector))
#define OPEN_CFW_PB_EVEN_AI_SEND(route, service, data, length) \
    host_send((route), (service), (data), (length))
#define OPEN_CFW_PB_EVEN_AI_NOTIFY(route, service, data, length) \
    host_notify((route), (service), (data), (length))

#include "../../components/apollo_main/core_overlay/pb_service_even_ai.c"

static uint32_t host_decode(void *raw_input, const void *descriptor,
                            void *raw_message)
{
    open_cfw_pb_even_ai_input *input = (open_cfw_pb_even_ai_input *)raw_input;
    uint8_t *message = (uint8_t *)raw_message;
    assert(descriptor == OPEN_CFW_PB_EVEN_AI_DESCRIPTOR);
    host_decode_length = input->bytes_left;
    if (host_decode_ok == 0U) {
        input->error = "decode";
        return 0U;
    }
    message[0] = host_decode_command;
    message[1] = host_decode_magic;
    memcpy(message + 4U, host_decode_payload, sizeof(host_decode_payload));
    return 1U;
}

static uint32_t host_encode(void *raw_output, const void *descriptor,
                            const void *raw_message)
{
    open_cfw_pb_even_ai_output *output =
        (open_cfw_pb_even_ai_output *)raw_output;
    assert(descriptor == OPEN_CFW_PB_EVEN_AI_DESCRIPTOR);
    memcpy(host_encoded_message, raw_message, sizeof(host_encoded_message));
    if (host_encode_ok == 0U) {
        output->error = "encode";
        return 0U;
    }
    output->length = 3U;
    host_encode_buffer[0] = 0xA5U;
    host_encode_buffer[1] = 0x5AU;
    host_encode_buffer[2] = 0x17U;
    return 1U;
}

static int host_dispatch(uint32_t command, const void *payload, uint32_t length)
{
    ++host_dispatch_calls;
    host_dispatch_command = command;
    host_dispatch_length = length;
    assert(length <= sizeof(host_dispatched_payload));
    memcpy(host_dispatched_payload, payload, length);
    return host_dispatch_status;
}

static uint32_t host_role_get(void)
{
    ++host_role_calls;
    return host_role;
}

static uint32_t host_display_get(uint32_t selector)
{
    ++host_display_calls;
    host_display_selector = selector;
    return host_display_ready;
}

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
    uint32_t index;
    memset(host_message, 0xCC, sizeof(host_message));
    memset(host_encode_buffer, 0, sizeof(host_encode_buffer));
    memset(host_duplicate_state, 0, sizeof(host_duplicate_state));
    memset(host_encoded_message, 0, sizeof(host_encoded_message));
    memset(host_dispatched_payload, 0, sizeof(host_dispatched_payload));
    for (index = 0U; index < sizeof(host_decode_payload); ++index) {
        host_decode_payload[index] = (uint8_t)(0x30U + index);
    }
    host_notify_magic = 0x40U;
    host_decode_ok = 1U;
    host_encode_ok = 1U;
    host_decode_command = 1U;
    host_decode_magic = 0x21U;
    host_decode_length = 0U;
    host_dispatch_status = 0;
    host_dispatch_calls = 0U;
    host_dispatch_command = 0U;
    host_dispatch_length = 0U;
    host_role = 1U;
    host_display_ready = 1U;
    host_role_calls = 0U;
    host_display_calls = 0U;
    host_display_selector = 0U;
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
    assert(host_transport_service == 7U);
    assert(host_transport_length == 3U);
}

static void test_helpers(void)
{
    uint8_t input[4] = {1U, 2U, 3U, 4U};
    open_cfw_pb_even_ai_output output;
    reset_host();
    output.write = open_cfw_pb_service_even_ai_buffer_write;
    output.context = host_encode_buffer;
    output.capacity = sizeof(host_encode_buffer);
    output.length = 254U;
    output.error = (const char *)0;
    assert(output.write(&output, input, 2U) == 1U);
    assert(host_encode_buffer[254] == 1U && host_encode_buffer[255] == 2U);
    assert(output.write(&output, input, 3U) == 0U);
    output.length = 257U;
    assert(output.write(&output, input, 0U) == 0U);
    memset(host_message, 0xA5, sizeof(host_message));
    open_cfw_pb_service_even_ai_zero(host_message, sizeof(host_message));
    assert(host_message[0] == 0U && host_message[sizeof(host_message) - 1U] == 0U);
}

static void test_receive_handlers(void)
{
    typedef uint32_t (*handler_fn)(uint32_t, const void *);
    static const handler_fn handlers[10] = {
        PB_RxEvenAICtrl, PB_RxEvenAIVADInfo, PB_RxEvenAIAskInfo,
        PB_RxEvenAIAnalyseInfo, PB_RxEvenAIReplyInfo, PB_RxEvenAISkillInfo,
        PB_RxEvenAIPromptInfo, PB_RxEvenAIEvent, PB_RxEvenAIHeartbeat,
        PB_RxEvenAIConfig,
    };
    static const uint32_t lengths[10] = {
        2U, 2U, 0x208U, 1U, 0x208U, 0x10CU, 2U, 2U, 2U, 4U,
    };
    uint32_t index;
    reset_host();
    for (index = 0U; index < 10U; ++index) {
        host_dispatch_calls = 0U;
        assert(handlers[index](0x99U, host_decode_payload) == 0U);
        assert(host_dispatch_calls == 1U);
        assert(host_dispatch_command == index + 1U);
        assert(host_dispatch_length == lengths[index]);
        assert(memcmp(host_dispatched_payload, host_decode_payload,
                      lengths[index]) == 0);
        assert(handlers[index](0x99U, (const void *)0) == 2U);
        host_dispatch_status = -1;
        assert(handlers[index](0x99U, host_decode_payload) == 1U);
        host_dispatch_status = 0;
    }
}

static void test_encoders(void)
{
    uint8_t payload[4] = {0x11U, 0x22U, 0x33U, 0x44U};
    uint8_t response = 0x55U;
    reset_host();
    assert(APP_PbTxEncodeEvenAICtrl(0x31U, payload) == 0U);
    assert_envelope(1U, 0x31U, 3U, 1U);
    assert(host_encoded_message[4] == 0x11U && host_encoded_message[5] == 0U);
    reset_host();
    assert(APP_PbTxEncodeEvenAIVADInfo(0x32U, payload) == 0U);
    assert_envelope(2U, 0x32U, 4U, 1U);
    reset_host();
    assert(APP_PbTxEncodeEvenAIAskInfo(0x33U, payload) == 0U);
    assert_envelope(3U, 0x33U, 5U, 1U);
    assert(host_encoded_message[4] == 0x11U && host_encoded_message[0x20B] == 0U);
    reset_host();
    assert(APP_PbTxEncodeEvenAIAnalyseInfo(0x34U, payload) == 0U);
    assert_envelope(4U, 0x34U, 6U, 1U);
    assert(host_encoded_message[4] == 0U);
    reset_host();
    assert(APP_PbTxEncodeEvenAIReplyInfo(0x35U, payload) == 0U);
    assert_envelope(5U, 0x35U, 7U, 1U);
    reset_host();
    assert(APP_PbTxEncodeEvenAISkillInfo(0x36U, payload) == 0U);
    assert_envelope(6U, 0x36U, 8U, 1U);
    assert(host_encoded_message[4] == 0U && host_encoded_message[5] == 0x22U);
    reset_host();
    assert(APP_PbTxEncodeEvenAIPromptInfo(0x37U, payload) == 0U);
    assert_envelope(7U, 0x37U, 9U, 1U);
    reset_host();
    assert(APP_PbTxEncodeEvenAIEvent(0x38U, payload) == 0U);
    assert_envelope(8U, 0x38U, 10U, 1U);
    reset_host();
    assert(APP_PbTxEncodeEvenAIHeartbeat(0x39U, payload) == 0U);
    assert_envelope(9U, 0x39U, 11U, 1U);
    assert(host_encoded_message[4] == 0x11U && host_encoded_message[5] == 0U);
    assert(host_role_calls == 1U && host_display_calls == 1U);
    assert(host_display_selector == 7U);
    reset_host();
    host_role = 0U;
    assert(APP_PbTxEncodeEvenAIHeartbeat(0x39U, payload) == 0U);
    assert(host_encoded_message[5] == 8U);
    assert(host_role_calls == 1U && host_display_calls == 0U);
    reset_host();
    host_display_ready = 0U;
    assert(APP_PbTxEncodeEvenAIHeartbeat(0x39U, payload) == 0U);
    assert(host_encoded_message[5] == 8U);
    reset_host();
    assert(APP_PbTxEncodeEvenAIConfig(0x3AU, payload) == 0U);
    assert_envelope(10U, 0x3AU, 13U, 1U);
    assert(host_encoded_message[4] == 0x11U);
    assert(host_encoded_message[5] == 0x22U);
    assert(host_encoded_message[6] == 0U);
    assert(host_encoded_message[7] == 0x44U);
    reset_host();
    assert(APP_PbTxEncodeEvenAICommResp(0x3BU, &response) == 0U);
    assert_envelope(0xA1U, 0x3BU, 12U, 1U);
    assert(host_encoded_message[4] == 0x55U);
    reset_host();
    assert(APP_PbTxEncodeEvenAICtrl(1U, (const void *)0) == 2U);
    assert(host_transport_calls == 0U);
    reset_host();
    host_encode_ok = 0U;
    assert(APP_PbTxEncodeEvenAICtrl(1U, payload) == 0x2BU);
    assert(host_transport_calls == 0U);
}

static void test_notifications(void)
{
    uint8_t payload[2] = {0x64U, 0x75U};
    reset_host();
    assert(APP_PbNotifyEncodeEvenAICtrl(0xFFFFU, payload) == 0U);
    assert_envelope(1U, 0x40U, 3U, 2U);
    assert(host_notify_magic == 0x41U);
    reset_host();
    assert(APP_PbNotifyEncodeEvenAIVADInfo(0U, payload) == 0U);
    assert_envelope(2U, 0x40U, 4U, 2U);
    assert(host_notify_magic == 0x41U);
    reset_host();
    assert(APP_PbNotifyEncodeEvenAIEvent(0U, payload) == 0U);
    assert_envelope(8U, 0x40U, 10U, 2U);
    assert(host_notify_magic == 0x41U);
    reset_host();
    host_encode_ok = 0U;
    assert(APP_PbNotifyEncodeEvenAIEvent(0U, payload) == 0x2BU);
    assert(host_notify_magic == 0x41U);
    assert(host_transport_calls == 0U);
    reset_host();
    assert(APP_PbNotifyEncodeEvenAIEvent(0U, (const void *)0) == 2U);
    assert(host_notify_magic == 0x40U);
}

static void test_root_dispatch(void)
{
    static const uint32_t lengths[10] = {
        2U, 2U, 0x208U, 1U, 0x208U, 0x10CU, 2U, 2U, 2U, 4U,
    };
    uint8_t input[4] = {1U, 2U, 3U, 4U};
    uint32_t command;
    reset_host();
    assert(APP_PbRxEvenAIFrameDataProcess((const void *)0, 4U) == 2U);
    host_decode_ok = 0U;
    assert(APP_PbRxEvenAIFrameDataProcess(input, 0x10004U) == 0x2BU);
    assert(host_decode_length == 4U);
    for (command = 1U; command <= 10U; ++command) {
        reset_host();
        host_decode_command = (uint8_t)command;
        host_decode_magic = (uint8_t)(0x20U + command);
        assert(APP_PbRxEvenAIFrameDataProcess(input, 4U) == 0U);
        assert(host_dispatch_calls == 1U);
        assert(host_dispatch_command == command);
        assert(host_dispatch_length == lengths[command - 1U]);
        assert(host_transport_calls == 1U);
    }
    reset_host();
    host_dispatch_status = -1;
    assert(APP_PbRxEvenAIFrameDataProcess(input, 4U) == 1U);
    assert(host_transport_calls == 0U);
    reset_host();
    host_encode_ok = 0U;
    assert(APP_PbRxEvenAIFrameDataProcess(input, 4U) == 0x2BU);
    reset_host();
    host_decode_command = 0x44U;
    assert(APP_PbRxEvenAIFrameDataProcess(input, 4U) == 0U);
    assert_envelope(0xA1U, 0x21U, 12U, 1U);
    assert(host_encoded_message[4] == 8U);
    reset_host();
    host_duplicate_state[0] = 1U;
    host_duplicate_state[1] = 0x21U;
    assert(APP_PbRxEvenAIFrameDataProcess(input, 4U) == 1U);
    assert_envelope(0xA1U, 0x21U, 12U, 1U);
    assert(host_encoded_message[4] == 7U);
    assert(host_dispatch_calls == 0U);
}

int main(void)
{
    test_helpers();
    test_receive_handlers();
    test_encoders();
    test_notifications();
    test_root_dispatch();
    return 0;
}
