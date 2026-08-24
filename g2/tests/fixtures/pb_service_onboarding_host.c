#include <assert.h>
#include <stdint.h>
#include <string.h>

static uint8_t host_decoded_message[0x10];
static uint8_t host_message[0x10];
static uint8_t host_encode_buffer[0x100];
static uint8_t host_encoded_message[0x10];
static uint8_t host_sequence;
static uint8_t host_display_ready;
static uint32_t host_primary_mode;
static uint32_t host_secondary_mode;
static uint32_t host_wear_state;
static uint32_t host_decode_ok;
static uint32_t host_encode_ok;
static uint32_t host_decode_length;
static uint8_t host_decode_command;
static uint8_t host_decode_magic;
static uint8_t host_decode_payload[12];
static uint32_t host_control_calls;
static uint32_t host_control_command;
static uint8_t host_control_payload[12];
static uint32_t host_transport_calls;
static uint32_t host_transport_kind;
static uint32_t host_transport_route;
static uint32_t host_transport_service;
static uint32_t host_transport_length;

static uint32_t host_decode(void *input, const void *descriptor, void *message);
static uint32_t host_encode(void *output, const void *descriptor,
                            const void *message);
static int host_control(uint32_t command, const uint8_t *payload);
static int host_send(uint32_t route, uint32_t service,
                     const void *data, uint32_t length);
static int host_notify(uint32_t route, uint32_t service,
                       const void *data, uint32_t length);

#define OPEN_CFW_PB_ONBOARDING_DECODED_MESSAGE host_decoded_message
#define OPEN_CFW_PB_ONBOARDING_MESSAGE host_message
#define OPEN_CFW_PB_ONBOARDING_ENCODE_BUFFER host_encode_buffer
#define OPEN_CFW_PB_ONBOARDING_DESCRIPTOR ((const void *)(uintptr_t)0x779C94U)
#define OPEN_CFW_PB_ONBOARDING_NOTIFICATION_SEQUENCE (&host_sequence)
#define OPEN_CFW_PB_ONBOARDING_DISPLAY_READY (&host_display_ready)
#define OPEN_CFW_PB_ONBOARDING_PRIMARY_MODE (&host_primary_mode)
#define OPEN_CFW_PB_ONBOARDING_SECONDARY_MODE (&host_secondary_mode)
#define OPEN_CFW_PB_ONBOARDING_WEAR_STATE (&host_wear_state)
#define OPEN_CFW_PB_ONBOARDING_INPUT_FROM_BUFFER(data, length) \
    ((open_cfw_pb_onboarding_input){(void *)(data), (void *)0, (length), \
                                    (const char *)0})
#define OPEN_CFW_PB_ONBOARDING_DECODE(input, descriptor, message) \
    host_decode((input), (descriptor), (message))
#define OPEN_CFW_PB_ONBOARDING_ENCODE(output, descriptor, message) \
    host_encode((output), (descriptor), (message))
#define OPEN_CFW_PB_ONBOARDING_CONTROL_UPDATE(command, payload) \
    host_control((command), (payload))
#define OPEN_CFW_PB_ONBOARDING_SEND(route, service, data, length) \
    host_send((route), (service), (data), (length))
#define OPEN_CFW_PB_ONBOARDING_NOTIFY(route, service, data, length) \
    host_notify((route), (service), (data), (length))

#include "../../components/apollo_main/core_overlay/pb_service_onboarding.c"

static uint32_t host_decode(void *raw_input, const void *descriptor,
                            void *raw_message)
{
    open_cfw_pb_onboarding_input *input =
        (open_cfw_pb_onboarding_input *)raw_input;
    uint8_t *message = (uint8_t *)raw_message;
    assert(descriptor == OPEN_CFW_PB_ONBOARDING_DESCRIPTOR);
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
    open_cfw_pb_onboarding_output *output =
        (open_cfw_pb_onboarding_output *)raw_output;
    assert(descriptor == OPEN_CFW_PB_ONBOARDING_DESCRIPTOR);
    assert(output->write == open_cfw_pb_service_onboarding_buffer_write);
    assert(output->context == host_encode_buffer);
    assert(output->capacity == sizeof(host_encode_buffer));
    memcpy(host_encoded_message, raw_message, sizeof(host_encoded_message));
    if (host_encode_ok == 0U) {
        output->error = "encode";
        return 0U;
    }
    output->length = 0x10007U;
    return 1U;
}

static int host_control(uint32_t command, const uint8_t *payload)
{
    ++host_control_calls;
    host_control_command = command;
    memcpy(host_control_payload, payload, sizeof(host_control_payload));
    return -7;
}

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

static void store_u32(uint8_t *data, uint32_t value)
{
    data[0] = (uint8_t)value;
    data[1] = (uint8_t)(value >> 8);
    data[2] = (uint8_t)(value >> 16);
    data[3] = (uint8_t)(value >> 24);
}

static uint32_t load_u32(const uint8_t *data)
{
    return (uint32_t)data[0] | ((uint32_t)data[1] << 8) |
        ((uint32_t)data[2] << 16) | ((uint32_t)data[3] << 24);
}

static void reset_host(void)
{
    memset(host_decoded_message, 0xCC, sizeof(host_decoded_message));
    memset(host_message, 0xCC, sizeof(host_message));
    memset(host_encode_buffer, 0, sizeof(host_encode_buffer));
    memset(host_encoded_message, 0, sizeof(host_encoded_message));
    memset(host_decode_payload, 0, sizeof(host_decode_payload));
    memset(host_control_payload, 0, sizeof(host_control_payload));
    host_sequence = 0xFEU;
    host_display_ready = 1U;
    host_primary_mode = 0x10U;
    host_secondary_mode = 0U;
    host_wear_state = 2U;
    host_decode_ok = 1U;
    host_encode_ok = 1U;
    host_decode_length = 0U;
    host_decode_command = 1U;
    host_decode_magic = 0x42U;
    host_control_calls = 0U;
    host_control_command = 0U;
    host_transport_calls = 0U;
    host_transport_kind = 0U;
    host_transport_route = 0U;
    host_transport_service = 0U;
    host_transport_length = 0U;
}

static void assert_transport(uint32_t kind)
{
    assert(host_transport_calls == 1U);
    assert(host_transport_kind == kind);
    assert(host_transport_route == 1U);
    assert(host_transport_service == 0x10U);
    assert(host_transport_length == 7U);
}

int main(void)
{
    uint8_t input[4] = {1U, 2U, 3U, 4U};
    uint8_t config[2] = {7U, 9U};
    uint8_t heartbeat = 0U;
    uint8_t event[12] = {1U};
    open_cfw_pb_onboarding_output output;

    reset_host();
    output.write = open_cfw_pb_service_onboarding_buffer_write;
    output.context = host_encode_buffer;
    output.capacity = sizeof(host_encode_buffer);
    output.length = sizeof(host_encode_buffer) - 2U;
    output.error = (const char *)0;
    assert(output.write(&output, input, 2U) == 1U);
    assert(host_encode_buffer[sizeof(host_encode_buffer) - 2U] == 1U);
    assert(output.write(&output, input, 3U) == 0U);

    assert(APP_PbRxOnboardingFrameDataProcess(0, 1U) == 2U);
    host_decode_ok = 0U;
    assert(APP_PbRxOnboardingFrameDataProcess(input, 0x10004U) == 0x2BU);
    assert(host_decode_length == 4U);
    host_decode_ok = 1U;
    host_decode_command = 0U;
    assert(APP_PbRxOnboardingFrameDataProcess(input, 4U) == 1U);
    assert(host_transport_calls == 0U && host_control_calls == 0U);

    reset_host();
    host_decode_command = 1U;
    host_decode_payload[0] = 7U;
    host_decode_payload[1] = 9U;
    assert(APP_PbRxOnboardingFrameDataProcess(input, 4U) == 0U);
    assert(host_control_calls == 1U && host_control_command == 1U);
    assert(host_control_payload[0] == 7U && host_control_payload[1] == 9U);
    assert(host_encoded_message[0] == 1U);
    assert(host_encoded_message[1] == 0x42U);
    assert(host_encoded_message[2] == 3U);
    assert(host_encoded_message[4] == 7U);
    assert(host_encoded_message[5] == 0U);
    assert_transport(1U);

    reset_host();
    host_decode_command = 2U;
    assert(APP_PbRxOnboardingFrameDataProcess(input, 4U) == 0U);
    assert(host_control_calls == 0U);
    assert(host_encoded_message[0] == 2U && host_encoded_message[2] == 4U);
    assert(host_encoded_message[4] == 0U);
    host_display_ready = 0U;
    assert(APP_PbTxEncodeOnboardingHeartbeat(3U, &heartbeat) == 0U);
    assert(host_encoded_message[4] == 8U);

    reset_host();
    host_decode_command = 3U;
    host_decode_payload[0] = 1U;
    store_u32(host_decode_payload + 4U, 0xAABBCCDDU);
    assert(APP_PbRxOnboardingFrameDataProcess(input, 4U) == 0U);
    assert(host_control_calls == 1U && host_control_command == 3U);
    assert(host_encoded_message[0] == 3U && host_encoded_message[2] == 5U);
    assert(host_encoded_message[4] == 1U);
    assert(load_u32(host_encoded_message + 8U) == 1U);
    host_wear_state = 1U;
    assert(APP_PbTxEncodeOnboardingEvent(5U, host_decode_payload) == 0U);
    assert(load_u32(host_encoded_message + 8U) == 0U);
    host_decode_payload[0] = 2U;
    assert(APP_PbTxEncodeOnboardingEvent(5U, host_decode_payload) == 0U);
    assert(load_u32(host_encoded_message + 8U) == 0xAABBCCDDU);

    assert(PB_RxOnboardingConfig(0U, 0) == 2U);
    assert(PB_RxOnboardingHeartbeat(0U, 0) == 2U);
    assert(PB_RxOnboardingEvent(0U, 0) == 2U);
    assert(APP_PbTxEncodeOnboardingConfig(0U, 0) == 2U);
    assert(APP_PbTxEncodeOnboardingHeartbeat(0U, 0) == 2U);
    assert(APP_PbTxEncodeOnboardingEvent(0U, 0) == 2U);
    assert(APP_PbNotifyEncodeOnboardingConfig(0U, 0) == 2U);
    assert(APP_PbNotifyEncodeOnboardingEvent(0U, 0) == 2U);

    reset_host();
    assert(APP_PbNotifyEncodeOnboardingConfig(99U, config) == 0U);
    assert(host_sequence == 0xFFU);
    assert(host_encoded_message[0] == 1U && host_encoded_message[1] == 0xFEU);
    assert_transport(2U);

    reset_host();
    event[0] = 1U;
    store_u32(event + 4U, 0x12345678U);
    assert(APP_PbNotifyEncodeOnboardingEvent(99U, event) == 0U);
    assert(host_sequence == 0xFFU);
    assert(host_encoded_message[0] == 3U && host_encoded_message[1] == 0xFEU);
    assert(load_u32(host_encoded_message + 8U) == 0x12345678U);
    assert_transport(2U);

    reset_host();
    host_encode_ok = 0U;
    assert(APP_PbNotifyEncodeOnboardingEvent(0U, event) == 0x2BU);
    assert(host_sequence == 0xFFU);
    assert(host_transport_calls == 0U);
    return 0;
}
