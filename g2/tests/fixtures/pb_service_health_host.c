#include <assert.h>
#include <stddef.h>
#include <string.h>

static unsigned char message_storage[0x31C];
static unsigned char encode_buffer[0x100];
static unsigned int manager_status[4];
static unsigned int manager_calls[4];
static unsigned int encode_result = 1;
static unsigned int encode_calls;
static unsigned int send_calls;
static unsigned int send_route;
static unsigned int send_service;
static unsigned int send_length;
static const void *send_payload;

struct open_cfw_pb_health_output;
static unsigned int host_encode(void *, const void *, const void *);
static int host_send(unsigned int, unsigned int, const void *, unsigned int);
static int host_save_single(const void *);
static int host_save_multiple(const void *);
static int host_save_single_highlight(const void *);
static int host_save_multiple_highlights(const void *);

#define OPEN_CFW_PB_HEALTH_MESSAGE message_storage
#define OPEN_CFW_PB_HEALTH_BUFFER encode_buffer
#define OPEN_CFW_PB_HEALTH_DESCRIPTOR ((const void *)0x1234)
#define OPEN_CFW_PB_HEALTH_ENCODE(output, descriptor, source) \
    host_encode((output), (descriptor), (source))
#define OPEN_CFW_PB_HEALTH_SEND(route, service, payload, length) \
    host_send((route), (service), (payload), (length))
#define OPEN_CFW_PB_HEALTH_SAVE_SINGLE(input) host_save_single((input))
#define OPEN_CFW_PB_HEALTH_SAVE_MULTIPLE(input) host_save_multiple((input))
#define OPEN_CFW_PB_HEALTH_SAVE_SINGLE_HIGHLIGHT(input) \
    host_save_single_highlight((input))
#define OPEN_CFW_PB_HEALTH_SAVE_MULTIPLE_HIGHLIGHTS(input) \
    host_save_multiple_highlights((input))
#include "../../components/apollo_main/core_overlay/pb_service_health.c"

static unsigned int host_encode(
    void *raw_output, const void *descriptor, const void *source)
{
    struct open_cfw_pb_health_output *output =
        (struct open_cfw_pb_health_output *)raw_output;
    static const unsigned char encoded[] = {0xA1, 0xB2, 0xC3};
    ++encode_calls;
    assert(descriptor == (const void *)0x1234);
    assert(source == message_storage);
    if (encode_result == 0U) {
        output->error = "encode";
        return 0U;
    }
    assert(output->write(output, encoded, sizeof(encoded)) == 1U);
    output->length += sizeof(encoded);
    return 1U;
}

static int host_send(
    unsigned int route, unsigned int service,
    const void *payload, unsigned int length)
{
    ++send_calls; send_route = route; send_service = service;
    send_payload = payload; send_length = length; return -7;
}

static int host_save_single(const void *input)
{ assert(input != NULL); ++manager_calls[0]; return (int)manager_status[0]; }
static int host_save_multiple(const void *input)
{ assert(input != NULL); ++manager_calls[1]; return (int)manager_status[1]; }
static int host_save_single_highlight(const void *input)
{ assert(input != NULL); ++manager_calls[2]; return (int)manager_status[2]; }
static int host_save_multiple_highlights(const void *input)
{ assert(input != NULL); ++manager_calls[3]; return (int)manager_status[3]; }

static void reset_tx(void)
{
    memset(message_storage, 0xA5, sizeof(message_storage));
    memset(encode_buffer, 0, sizeof(encode_buffer));
    encode_result = 1U; encode_calls = 0U; send_calls = 0U;
    send_route = send_service = send_length = 0U; send_payload = NULL;
}

int main(void)
{
    unsigned char input[0x20DU];
    struct open_cfw_pb_health_output output;
    unsigned char scratch[8] = {0};
    static const unsigned char sample[3] = {1, 2, 3};
    unsigned int index;

    output.write = open_cfw_pb_service_health_buffer_write;
    output.context = scratch; output.capacity = sizeof(scratch);
    output.length = 2U; output.error = NULL;
    assert(output.write(&output, sample, 3U) == 1U);
    assert(scratch[2] == 1U && scratch[3] == 2U && scratch[4] == 3U);
    output.length = 7U;
    assert(output.write(&output, sample, 2U) == 0U);

    assert(PB_RxHealthSingleData(9U, NULL) == 2U);
    assert(PB_RxHealthMultData(9U, NULL) == 2U);
    assert(PB_RxHealthSingleHighlight(9U, NULL) == 2U);
    assert(PB_RxHealthMultHighlight(9U, NULL) == 2U);
    for (index = 0U; index < 4U; ++index) manager_status[index] = index;
    assert(PB_RxHealthSingleData(0U, input) == 0U);
    assert(PB_RxHealthMultData(0U, input) == 1U);
    assert(PB_RxHealthSingleHighlight(0U, input) == 1U);
    assert(PB_RxHealthMultHighlight(0U, input) == 1U);

    assert(APP_PbTxEncodeHealthSingleData(1U, NULL) == 2U);
    assert(APP_PbTxEncodeHealthMultData(1U, NULL) == 2U);
    assert(APP_PbTxEncodeHealthSingleHighlight(1U, NULL) == 2U);
    assert(APP_PbTxEncodeHealthMultHighlight(1U, NULL) == 2U);

    memset(input, 0, sizeof(input));
    input[0] = 7U; input[4] = 0x11; input[8] = 0x22;
    input[12] = 0x33; input[16] = 0x44; input[21] = 5U;
    reset_tx();
    assert(APP_PbTxEncodeHealthSingleData(0xA6U, input) == 0U);
    assert(message_storage[0] == 1U && message_storage[1] == 0xA6U);
    assert(message_storage[2] == 3U && message_storage[4] == 7U);
    assert(message_storage[8] == 0x11 && message_storage[12] == 0x22);
    assert(message_storage[16] == 0x33 && message_storage[20] == 0x44);
    assert(message_storage[24] == 0U && message_storage[25] == 5U);
    assert(send_calls == 1U && send_route == 1U && send_service == 0x0EU);
    assert(send_payload == encode_buffer && send_length == 3U);
    assert(encode_buffer[0] == 0xA1 && encode_buffer[2] == 0xC3);

    reset_tx(); input[0] = 8U;
    assert(APP_PbTxEncodeHealthMultData(2U, input) == 0U);
    assert(message_storage[0] == 2U && message_storage[2] == 4U);
    assert(message_storage[4] == 8U && message_storage[0xC8] == 0U);

    reset_tx(); input[0] = 9U;
    assert(APP_PbTxEncodeHealthSingleHighlight(3U, input) == 0U);
    assert(message_storage[0] == 3U && message_storage[2] == 5U);
    assert(message_storage[4] == 9U && message_storage[0x108] == 0U);

    memset(input, 0, sizeof(input)); input[0] = 2U;
    input[2] = 4U; input[0x106] = 1U;
    input[0x108] = 6U; input[0x20C] = 1U;
    reset_tx();
    assert(APP_PbTxEncodeHealthMultHighlight(4U, input) == 0U);
    assert(message_storage[0] == 4U && message_storage[2] == 6U);
    assert(message_storage[4] == 2U && message_storage[6] == 4U);
    assert(message_storage[0x10A] == 1U && message_storage[0x10C] == 6U);
    assert(message_storage[0x210] == 1U && message_storage[0x318] == 0U);

    input[0] = 4U; input[1] = 0U; reset_tx();
    assert(APP_PbTxEncodeHealthMultHighlight(4U, input) == 0x2BU);
    assert(encode_calls == 0U && send_calls == 0U);
    input[0] = 0U; reset_tx(); encode_result = 0U;
    assert(APP_PbTxEncodeHealthMultHighlight(4U, input) == 0x2BU);
    assert(encode_calls == 1U && send_calls == 0U);
    return 0;
}
