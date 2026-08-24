#include <assert.h>
#include <stdint.h>
#include <string.h>

static uint8_t host_rx[0x1238];
static uint8_t host_tx[0x1238];
static uint8_t host_encoded[0x400];
static uint8_t host_decoded[0x1238];
static uint8_t host_sequence;
static uint32_t host_decode_ok;
static uint32_t host_encode_ok;
static int host_item_result;
static int host_multi_result;
static uint32_t host_item_calls;
static uint32_t host_multi_calls;
static uint32_t host_send_calls;
static uint32_t host_notify_calls;
static uint32_t host_route;
static uint32_t host_service;
static uint32_t host_length;

#define OPEN_CFW_PB_QUICKLIST_MESSAGE_RX host_rx
#define OPEN_CFW_PB_QUICKLIST_MESSAGE_TX host_tx
#define OPEN_CFW_PB_QUICKLIST_ENCODE_BUFFER host_encoded
#define OPEN_CFW_PB_QUICKLIST_DESCRIPTOR ((const void *)(uintptr_t)0x1234U)
#define OPEN_CFW_PB_QUICKLIST_NOTIFY_SEQUENCE (&host_sequence)
#include "../../components/apollo_main/core_overlay/pb_service_quicklist.c"

open_cfw_pb_quicklist_input open_cfw_nanopb_istream_from_buffer(
    const void *data, uint32_t length)
{
    open_cfw_pb_quicklist_input input = {0};
    input.state = (void *)data;
    input.bytes_left = length;
    return input;
}

uint32_t open_cfw_nanopb_decode(
    open_cfw_pb_quicklist_input *input, const void *descriptor, void *message)
{
    assert(input->state != (void *)0);
    assert(descriptor == OPEN_CFW_PB_QUICKLIST_DESCRIPTOR);
    if (host_decode_ok == 0U) {
        return 0U;
    }
    memcpy(message, host_decoded, sizeof(host_decoded));
    return 1U;
}

uint32_t open_cfw_format_message_encode(
    void *raw_output, const void *descriptor, const void *message)
{
    static const uint8_t bytes[] = {0x91U, 0x82U, 0x73U};
    open_cfw_pb_quicklist_output *output = raw_output;
    assert(descriptor == OPEN_CFW_PB_QUICKLIST_DESCRIPTOR);
    assert(message == host_tx);
    if (host_encode_ok == 0U) {
        return 0U;
    }
    return output->write(output, bytes, sizeof(bytes));
}

static int host_transport(
    uint32_t route, uint32_t service, const void *data, uint32_t length)
{
    assert(data == host_encoded);
    host_route = route;
    host_service = service;
    host_length = length;
    return -9;
}

int open_cfw_ble_msgtx_pb_send(
    uint32_t route, uint32_t service, const void *data, uint32_t length)
{
    ++host_send_calls;
    return host_transport(route, service, data, length);
}

int open_cfw_ble_msgtx_pb_notify(
    uint32_t route, uint32_t service, const void *data, uint32_t length)
{
    ++host_notify_calls;
    return host_transport(route, service, data, length);
}

int open_cfw_quicklist_data_manager_load(const void *item)
{
    assert(item == host_rx + 8U);
    ++host_item_calls;
    return host_item_result;
}

int open_cfw_quicklist_data_manager_save(const void *items)
{
    assert(items == host_rx + 8U);
    ++host_multi_calls;
    return host_multi_result;
}

static void reset_host(void)
{
    memset(host_rx, 0xA5, sizeof(host_rx));
    memset(host_tx, 0xA5, sizeof(host_tx));
    memset(host_encoded, 0, sizeof(host_encoded));
    memset(host_decoded, 0, sizeof(host_decoded));
    host_sequence = 0U;
    host_decode_ok = 1U;
    host_encode_ok = 1U;
    host_item_result = host_multi_result = 0;
    host_item_calls = host_multi_calls = 0U;
    host_send_calls = host_notify_calls = 0U;
    host_route = host_service = host_length = 0U;
}

static void assert_transport(uint32_t notify)
{
    assert(host_route == 1U && host_service == 0x0CU && host_length == 3U);
    assert(host_send_calls == (notify == 0U ? 1U : 0U));
    assert(host_notify_calls == (notify != 0U ? 1U : 0U));
}

static void test_decode_callback(void)
{
    reset_host();
    host_rx[0] = 0U;
    assert(APP_DecodePbRxQuicklistData() == 3);
    host_rx[0] = 1U;
    assert(APP_DecodePbRxQuicklistData() == 0 && host_item_calls == 1U);
    host_item_result = -7;
    assert(APP_DecodePbRxQuicklistData() == -7);
    host_rx[0] = 2U;
    assert(APP_DecodePbRxQuicklistData() == 0 && host_multi_calls == 1U);
    host_rx[0] = 3U;
    host_rx[8] = 0xFFU;
    assert(APP_DecodePbRxQuicklistData() == 0);
}

static void test_direct_transmit(void)
{
    uint8_t item[0xE8];
    uint8_t multi[4] = {7U, 8U, 0U, 0U};
    uint8_t event[8] = {2U, 0U, 0U, 0U, 0x78U, 0x56U, 0x34U, 0x12U};
    uint32_t index;
    for (index = 0U; index < sizeof(item); ++index) item[index] = (uint8_t)index;
    reset_host();
    assert(PB_RxQuicklistItem(0U, 0) == 2 && PB_RxQuicklistItem(0U, item) == 0);
    assert(APP_PbTxEncodeQuicklistItem(0x51U, 0) == 2);
    assert(APP_PbTxEncodeQuicklistItem(0x51U, item) == 0);
    assert(host_tx[0] == 1U && host_tx[1] == 0x51U);
    assert(host_tx[2] == 3U && host_tx[3] == 0U);
    assert(memcmp(host_tx + 8U, item, 12U) == 0 && host_tx[0xECU] == 0U);
    assert_transport(0U);
    reset_host(); host_encode_ok = 0U;
    assert(APP_PbTxEncodeQuicklistItem(1U, item) == 0x2B);
    assert(host_send_calls == 0U);

    reset_host();
    assert(PB_RxQuicklistMultItems(0U, 0) == 2);
    assert(APP_PbTxEncodeQuicklistMultItems(0x52U, multi) == 0);
    assert(host_tx[0] == 2U && host_tx[1] == 0x52U);
    assert(host_tx[2] == 4U && host_tx[8] == 7U && host_tx[9] == 8U);
    assert_transport(0U);

    reset_host();
    assert(PB_RxQuicklistEvent(0U, 0) == 2);
    assert(APP_PbTxEncodeQuicklistEvent(0x53U, event) == 0);
    assert(host_tx[0] == 3U && host_tx[1] == 0x53U && host_tx[2] == 5U);
    assert(host_tx[8] == 2U && memcmp(host_tx + 12U, event + 4U, 4U) == 0);
    assert_transport(0U);
}

static void test_notifications(void)
{
    uint8_t multi[8U + 2U * 0xE8U];
    uint8_t event[8] = {1U, 0U, 0U, 0U, 4U, 3U, 2U, 1U};
    uint32_t index;
    memset(multi, 0, sizeof(multi));
    multi[0] = 9U; multi[1] = 10U; multi[2] = 2U;
    for (index = 8U; index < sizeof(multi); ++index) multi[index] = (uint8_t)index;
    reset_host(); host_sequence = 0xFFU;
    assert(APP_PbNotifyEncodeQuicklistMultItems(0U, multi) == 0);
    assert(host_tx[0] == 2U && host_tx[1] == 0xFFU && host_sequence == 0U);
    assert(host_tx[8] == 9U && host_tx[9] == 10U && host_tx[10] == 2U);
    assert(memcmp(host_tx + 0x10U, multi + 8U, 2U * 0xE8U) == 0);
    assert_transport(1U);
    reset_host(); multi[2] = 21U;
    assert(APP_PbNotifyEncodeQuicklistMultItems(0U, multi) == 1);
    assert(host_notify_calls == 0U && host_sequence == 0U);
    assert(APP_PbNotifyEncodeQuicklistMultItems(0U, 0) == 2);

    reset_host(); host_sequence = 6U;
    assert(APP_PbNotifyEncodeQuicklistEvent(0U, event) == 0);
    assert(host_tx[0] == 3U && host_tx[1] == 6U && host_sequence == 7U);
    assert(host_tx[8] == 1U && memcmp(host_tx + 12U, event + 4U, 4U) == 0);
    assert_transport(1U);
    reset_host(); host_encode_ok = 0U;
    assert(APP_PbNotifyEncodeQuicklistEvent(0U, event) == 0x2B);
    assert(host_notify_calls == 0U);
}

static void test_dispatch(void)
{
    static const uint8_t wire[] = {1U, 2U, 3U};
    reset_host();
    assert(APP_PbRxQuicklistFrameDataProcess(0, sizeof(wire)) == 2);
    host_decode_ok = 0U;
    assert(APP_PbRxQuicklistFrameDataProcess(wire, sizeof(wire)) == 0x2B);
    reset_host(); host_decoded[0] = 9U;
    assert(APP_PbRxQuicklistFrameDataProcess(wire, sizeof(wire)) == 1);
    reset_host(); host_decoded[0] = 1U; host_decoded[1] = 0x31U;
    assert(APP_PbRxQuicklistFrameDataProcess(wire, sizeof(wire)) == 0);
    assert(host_tx[0] == 1U && host_tx[1] == 0x31U);
    reset_host(); host_decoded[0] = 2U; host_decoded[1] = 0x32U;
    assert(APP_PbRxQuicklistFrameDataProcess(wire, sizeof(wire)) == 0);
    assert(host_tx[0] == 2U && host_tx[1] == 0x32U);
    reset_host(); host_decoded[0] = 3U; host_decoded[1] = 0x33U;
    assert(APP_PbRxQuicklistFrameDataProcess(wire, sizeof(wire)) == 0);
    assert(host_tx[0] == 3U && host_tx[1] == 0x33U);
}

int main(void)
{
    open_cfw_pb_quicklist_output output;
    uint8_t scratch[4] = {0U};
    static const uint8_t bytes[3] = {1U, 2U, 3U};
    output.write = open_cfw_pb_service_quicklist_buffer_write;
    output.context = scratch;
    output.capacity = sizeof(scratch);
    output.length = 1U;
    output.error = (const char *)0;
    assert(output.write(&output, bytes, 3U) == 1U && output.length == 4U);
    assert(memcmp(scratch + 1U, bytes, 3U) == 0);
    assert(output.write(&output, bytes, 1U) == 0U);
    test_decode_callback();
    test_direct_transmit();
    test_notifications();
    test_dispatch();
    return 0;
}
