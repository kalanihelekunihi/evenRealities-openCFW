#include <assert.h>
#include <stddef.h>
#include <string.h>

static unsigned char message_storage[0x68];
static unsigned char encode_buffer[0x100];
static unsigned char decoded_storage[0x68];
static unsigned char config_storage[0x44];
static unsigned char runtime_storage[0x44];
static unsigned int last_command;
static unsigned int last_magic;
static unsigned int duplicate_magic;
static unsigned int notification_magic;
static unsigned int role = 1U;
static unsigned int unread_count = 7U;
static unsigned int decode_result = 1U;
static unsigned int encode_result = 1U;
static unsigned int encode_calls;
static unsigned int send_calls;
static unsigned int notify_calls;
static unsigned int sent_route;
static unsigned int sent_service;
static unsigned int sent_length;
static unsigned int request_left_version_calls;

struct open_cfw_pb_setting_output;
static void *host_input_from_buffer(const void *, unsigned int);
static unsigned int host_decode(void *, const void *, void *);
static unsigned int host_encode(void *, const void *, const void *);
static int host_send(unsigned int, unsigned int, const void *, unsigned int);
static int host_notify(unsigned int, unsigned int, const void *, unsigned int);
static void *host_config(void);
static void *host_runtime(void);
static void host_request_left_version(void);
static unsigned int host_unread_count(void);

#define OPEN_CFW_PB_SETTING_HOST_ALL 1
#define OPEN_CFW_PB_SETTING_INPUT_FROM_BUFFER(data, length) \
    (*(open_cfw_pb_setting_input *)host_input_from_buffer((data), (length)))
#define OPEN_CFW_PB_SETTING_DECODE(input, descriptor, message) \
    host_decode((input), (descriptor), (message))
#define OPEN_CFW_PB_SETTING_ENCODE(output, descriptor, message) \
    host_encode((output), (descriptor), (message))
#define OPEN_CFW_PB_SETTING_SEND(route_value, service_value, data, length) \
    host_send((route_value), (service_value), (data), (length))
#define OPEN_CFW_PB_SETTING_NOTIFY(route_value, service_value, data, length) \
    host_notify((route_value), (service_value), (data), (length))
#define OPEN_CFW_PB_SETTING_ROLE() role
#define OPEN_CFW_PB_SETTING_CONFIG() host_config()
#define OPEN_CFW_PB_SETTING_RUNTIME() host_runtime()
#define OPEN_CFW_PB_SETTING_REQUEST_LEFT_VERSION() host_request_left_version()
#define OPEN_CFW_PB_SETTING_UNREAD_COUNT() host_unread_count()
#define OPEN_CFW_PB_SETTING_MESSAGE message_storage
#define OPEN_CFW_PB_SETTING_BUFFER encode_buffer
#define OPEN_CFW_PB_SETTING_DESCRIPTOR ((const void *)0x1234U)
#define OPEN_CFW_PB_SETTING_LAST_COMMAND last_command
#define OPEN_CFW_PB_SETTING_LAST_MAGIC last_magic
#define OPEN_CFW_PB_SETTING_DUPLICATE_MAGIC duplicate_magic
#define OPEN_CFW_PB_SETTING_NOTIFICATION_MAGIC notification_magic
#include "../../components/apollo_main/core_overlay/pb_service_setting.c"

static open_cfw_pb_setting_input host_input;

static void *host_input_from_buffer(const void *data, unsigned int length)
{
    assert(data != NULL);
    memset(&host_input, 0, sizeof(host_input));
    host_input.bytes_left = length;
    return &host_input;
}

static unsigned int host_decode(
    void *input, const void *descriptor, void *message)
{
    assert(input != NULL);
    assert(descriptor == (const void *)0x1234U);
    if (decode_result == 0U) {
        return 0U;
    }
    memcpy(message, decoded_storage, sizeof(decoded_storage));
    return 1U;
}

static unsigned int host_encode(
    void *raw_output, const void *descriptor, const void *message)
{
    struct open_cfw_pb_setting_output *output = raw_output;
    static const unsigned char encoded[] = {0x91, 0x92, 0x93};
    ++encode_calls;
    assert(descriptor == (const void *)0x1234U);
    assert(message == message_storage);
    if (encode_result == 0U) {
        return 0U;
    }
    assert(output->write(output, encoded, sizeof(encoded)) == 1U);
    output->length += sizeof(encoded);
    return 1U;
}

static int host_send(
    unsigned int route_value, unsigned int service_value,
    const void *data, unsigned int length)
{
    ++send_calls;
    sent_route = route_value;
    sent_service = service_value;
    sent_length = length;
    assert(data == encode_buffer);
    return -1;
}

static int host_notify(
    unsigned int route_value, unsigned int service_value,
    const void *data, unsigned int length)
{
    ++notify_calls;
    sent_route = route_value;
    sent_service = service_value;
    sent_length = length;
    assert(data == encode_buffer);
    return -1;
}

static void *host_config(void) { return config_storage; }
static void *host_runtime(void) { return runtime_storage; }
static void host_request_left_version(void) { ++request_left_version_calls; }
static unsigned int host_unread_count(void) { return unread_count; }

static void store32(unsigned char *data, unsigned int value)
{
    data[0] = (unsigned char)value;
    data[1] = (unsigned char)(value >> 8);
    data[2] = (unsigned char)(value >> 16);
    data[3] = (unsigned char)(value >> 24);
}

static void reset_transport(void)
{
    memset(message_storage, 0xA5, sizeof(message_storage));
    memset(encode_buffer, 0, sizeof(encode_buffer));
    encode_result = 1U;
    encode_calls = send_calls = notify_calls = 0U;
    sent_route = sent_service = sent_length = 0U;
}

int main(void)
{
    unsigned char raw[4] = {1, 2, 3, 4};
    unsigned char output_buffer[16] = {0};
    unsigned char status[0x68];
    unsigned int length;

    duplicate_magic = 0x11223344U;
    assert(setting_is_duplicate_message(0x11223344U) == 1U);
    assert(setting_is_duplicate_message(0x55667788U) == 0U);
    assert(duplicate_magic == 0x55667788U);

    assert(setting_parse_data_package(NULL, 4U, decoded_storage) == 0U);
    assert(setting_parse_data_package(raw, 4U, NULL) == 0U);
    memset(decoded_storage, 0, sizeof(decoded_storage));
    decoded_storage[0] = 9U;
    store32(decoded_storage + 4U, 0xA1B2C3D4U);
    decode_result = 0U;
    assert(setting_parse_data_package(raw, 4U, status) == 0U);
    decode_result = 1U;
    assert(setting_parse_data_package(raw, 4U, status) == 1U);
    assert(last_command == 9U && last_magic == 0xA1B2C3D4U);
    assert(setting_parse_data_package(raw, 4U, status) == 0U);

    memset(config_storage, 0, sizeof(config_storage));
    memset(runtime_storage, 0, sizeof(runtime_storage));
    config_storage[1] = 33U;
    config_storage[2] = 44U;
    config_storage[8] = 1U;
    config_storage[9] = 55U;
    config_storage[10] = 1U;
    config_storage[0x0CU] = 0x78U;
    config_storage[0x14U] = 66U;
    memcpy(runtime_storage, "2.2.5.9", 8U);
    runtime_storage[0x15U] = 77U;
    runtime_storage[0x16U] = 1U;
    runtime_storage[0x17U] = 2U;
    store32(runtime_storage + 0x34U, 0x01020304U);
    store32(runtime_storage + 0x38U, 0x11121314U);
    store32(runtime_storage + 0x3CU, 0x21222324U);
    store32(runtime_storage + 0x40U, 0x31323334U);
    assert(setting_build_full_status_package(NULL) == 0U);
    assert(setting_build_full_status_package(status) == 1U);
    assert(status[0] == 2U && status[8] == 4U);
    assert(status[0x10U] == 33U && status[0x60U] == 44U);
    assert(status[0x14U] == 1U && status[0x18U] == 55U);
    assert(memcmp(status + 0x1CU, "2.2.5.9", 8U) == 0);
    assert(memcmp(status + 0x28U, "2.2.6.10", 8U) == 0);
    assert(status[0x34U] == 1U && status[0x38U] == 0x78U);
    assert(status[0x40U] == 66U && status[0x44U] == 0x04U);
    assert(status[0x50U] == 77U && status[0x54U] == 1U);
    assert(status[0x58U] == 2U && status[0x5CU] == 0x34U);
    assert(status[0x64U] == 7U);
    runtime_storage[0] = 0U;
    request_left_version_calls = 0U;
    assert(setting_build_full_status_package(status) == 1U);
    assert(request_left_version_calls == 1U);

    last_magic = 0xCAFEBABEU;
    length = sizeof(output_buffer);
    reset_transport();
    assert(setting_respond_to_app(output_buffer, &length) == 1U);
    assert(length == 3U && message_storage[0] == 1U);
    assert(message_storage[4] == 0xBEU && message_storage[7] == 0xCAU);
    assert(setting_respond_to_app(NULL, &length) == 0U);
    encode_result = 0U;
    length = sizeof(output_buffer);
    assert(setting_respond_to_app(output_buffer, &length) == 0U);

    role = 0U;
    assert(setting_respond_to_app_serialize() == 0U);
    role = 1U;
    last_command = 0U;
    assert(setting_respond_to_app_serialize() == 1U);
    last_command = 1U;
    reset_transport();
    assert(setting_respond_to_app_serialize() == 0U);
    assert(send_calls == 1U && sent_route == 1U && sent_service == 9U);
    assert(sent_length == 3U);
    reset_transport();
    encode_result = 0U;
    assert(setting_respond_to_app_serialize() == 0x2BU);
    assert(send_calls == 0U);

    role = 1U;
    notification_magic = 10U;
    memset(status, 0, sizeof(status));
    status[0] = 3U;
    reset_transport();
    assert(setting_notify_common(status) == 0U);
    assert(notification_magic == 11U);
    assert(message_storage[0] == 3U && message_storage[4] == 11U);
    assert(notify_calls == 1U && sent_service == 9U);
    assert(setting_notify_common(NULL) == 1U);
    reset_transport();
    setting_notify_recalibration_status_to_app(0x12345678U);
    assert(message_storage[0] == 3U && message_storage[8] == 5U);
    assert(message_storage[12] == 1U && message_storage[16] == 0x78U);
    reset_transport();
    notify_silent_mode_to_app(1U);
    assert(message_storage[12] == 2U && message_storage[16] == 1U);
    return 0;
}
