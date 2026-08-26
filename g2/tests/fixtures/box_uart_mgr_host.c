#include <string.h>

static unsigned char test_slot;
static unsigned char test_buffers[5][1024];

#define OPEN_CFW_BOX_UART_RX_SLOT test_slot
#define OPEN_CFW_BOX_UART_RX_BUFFER(slot) test_buffers[(slot)]

#include "../../components/apollo_main/core_overlay/box_uart_mgr.c"

static unsigned int calls;
static unsigned int queue_count;
static unsigned int registered_channel;
static void (*registered_callback)(const unsigned char *, unsigned int);
static open_cfw_box_uart_record queued_record;
static unsigned char queued_data[1024];
static int stop_result;
static int clear_result;
static int product_result;
static int send_result;
static int flush_result;
static int start_result;
static int execute_result;
static unsigned int sent_channel;
static unsigned int sent_length;
static unsigned char sent_data[256];
static unsigned int execute_request_length;
static unsigned int execute_response_length;

enum {
    CALL_REGISTER = 1U << 0,
    CALL_RESUME = 1U << 1,
    CALL_START = 1U << 2,
    CALL_STOP = 1U << 3,
    CALL_CLEAR = 1U << 4,
    CALL_PRODUCT = 1U << 5,
    CALL_DELAY = 1U << 6,
    CALL_SEND = 1U << 7,
    CALL_FLUSH = 1U << 8,
    CALL_EXECUTE = 1U << 9
};

void *open_cfw_retained_box_uart_memcpy(
    void *destination,
    const void *source,
    unsigned int length
)
{
    return memcpy(destination, source, length);
}

void *open_cfw_retained_box_uart_memset(
    void *destination,
    int value,
    unsigned int length
)
{
    return memset(destination, value, length);
}

int open_cfw_retained_box_uart_queue(const open_cfw_box_uart_record *record)
{
    ++queue_count;
    queued_record = *record;
    memcpy(queued_data, record->data, record->length);
    queued_record.data = queued_data;
    return 0;
}

int open_cfw_retained_box_uart_register_receive(
    unsigned int channel,
    void (*callback)(const unsigned char *, unsigned int)
)
{
    calls |= CALL_REGISTER;
    registered_channel = channel;
    registered_callback = callback;
    return 0;
}

int open_cfw_retained_box_uart_resume(unsigned int channel)
{
    calls |= CALL_RESUME;
    return channel == 2U ? 0 : -1;
}

int open_cfw_retained_box_uart_start(unsigned int channel)
{
    calls |= CALL_START;
    return channel == 2U ? start_result : -1;
}

int open_cfw_retained_box_uart_stop(unsigned int channel)
{
    calls |= CALL_STOP;
    return channel == 2U ? stop_result : -1;
}

int open_cfw_retained_box_uart_clear(unsigned int channel)
{
    calls |= CALL_CLEAR;
    return channel == 2U ? clear_result : -1;
}

int open_cfw_retained_box_uart_flush(unsigned int channel)
{
    calls |= CALL_FLUSH;
    return channel == 2U ? flush_result : -1;
}

int open_cfw_retained_box_uart_product_test(
    const unsigned char *request,
    unsigned int request_length,
    unsigned char *response,
    unsigned char *response_length
)
{
    calls |= CALL_PRODUCT;
    if (product_result == 0) {
        response[0] = request_length == 0U ? 0U : request[0];
        response[1] = 0xA5U;
        *response_length = 2U;
    }
    return product_result;
}

int open_cfw_retained_box_uart_execute(
    const unsigned char *request,
    unsigned int request_length,
    const unsigned char *response,
    unsigned int response_length
)
{
    (void)request;
    (void)response;
    calls |= CALL_EXECUTE;
    execute_request_length = request_length;
    execute_response_length = response_length;
    return execute_result;
}

int open_cfw_retained_box_uart_delay(unsigned int ticks)
{
    calls |= CALL_DELAY;
    return ticks == 2U ? 0 : -1;
}

unsigned int open_cfw_ui_display_sink(
    unsigned int selector,
    const void *buffer,
    unsigned int length
)
{
    calls |= CALL_SEND;
    sent_channel = selector;
    sent_length = length;
    memcpy(sent_data, buffer, length);
    return (unsigned int)send_result;
}

static void reset_fixture(void)
{
    memset(test_buffers, 0xA5, sizeof(test_buffers));
    memset(queued_data, 0, sizeof(queued_data));
    memset(sent_data, 0, sizeof(sent_data));
    test_slot = 0U;
    calls = 0U;
    queue_count = 0U;
    registered_channel = 0U;
    registered_callback = 0;
    stop_result = 0;
    clear_result = 0;
    product_result = 0;
    send_result = 0;
    flush_result = 0;
    start_result = 0;
    execute_result = 0;
    sent_channel = 0U;
    sent_length = 0U;
    execute_request_length = 0U;
    execute_response_length = 0U;
}

unsigned int open_cfw_test_box_unpack(void)
{
    unsigned char output[16];
    unsigned char length;
    unsigned char zeros[4] = {0U, 0U, 0U, 0U};
    unsigned char text[5] = {0U, 0U, 0x54U, 0x31U, 0x32U};
    unsigned char valid[5] = {0U, 1U, 2U, 3U, 0x87U};
    open_cfw_box_uart_record record;
    unsigned int mask = 0U;

    memset(output, 0xCC, sizeof(output));
    length = 0xAAU;
    if (open_cfw_box_uart_unpack(0, output, &length) == -1) mask |= 1U;
    record.type = 1U;
    record.length = 0U;
    record.data = zeros;
    if (open_cfw_box_uart_unpack(&record, output, &length) == -1) mask |= 2U;
    record.length = 4U;
    if (open_cfw_box_uart_unpack(&record, output, &length) == 0 && length == 0xAAU) mask |= 4U;
    record.length = 5U;
    record.data = text;
    if (open_cfw_box_uart_unpack(&record, output, &length) == 0 && length == 3U && output[0] == 0x54U && output[2] == 0x32U) mask |= 8U;
    record.data = valid;
    if (open_cfw_box_uart_unpack(&record, output, &length) == 0 && length == 4U && output[0] == 1U && output[3] == 0x87U) mask |= 16U;
    valid[4] ^= 1U;
    if (open_cfw_box_uart_unpack(&record, output, &length) == -3) mask |= 32U;
    return mask;
}

unsigned int open_cfw_test_box_receive(void)
{
    unsigned char data[4] = {9U, 8U, 7U, 6U};
    unsigned int index;
    unsigned int mask = 0U;

    reset_fixture();
    open_cfw_box_uart_receive(data, 2U);
    if (queue_count == 0U) mask |= 1U;
    open_cfw_box_uart_receive(data, 4U);
    if (queue_count == 1U && queued_record.type == 1U && queued_record.length == 4U && queued_data[3] == 6U && test_buffers[0][4] == 0U && test_slot == 1U) mask |= 2U;
    for (index = 0U; index < 5U; ++index) {
        open_cfw_box_uart_receive(data, 4U);
    }
    if (test_slot == 1U && queue_count == 6U) mask |= 4U;
    test_slot = 9U;
    open_cfw_box_uart_receive(data, 4U);
    if (test_slot == 1U && queue_count == 7U) mask |= 8U;
    open_cfw_box_uart_receive(data, 1025U);
    if (queue_count == 7U) mask |= 16U;
    return mask;
}

unsigned int open_cfw_test_box_init(void)
{
    reset_fixture();
    open_cfw_box_uart_init();
    return calls == (CALL_REGISTER | CALL_RESUME | CALL_START) &&
        registered_channel == 2U &&
        registered_callback == open_cfw_box_uart_receive;
}

unsigned int open_cfw_test_box_handle(unsigned int scenario)
{
    unsigned char payload[4] = {0x54U, 0x10U, 0x20U, 0x30U};
    open_cfw_box_uart_record record = {1U, 4U, payload};

    reset_fixture();
    if (scenario == 1U) stop_result = -1;
    if (scenario == 2U) product_result = -1;
    if (scenario == 3U) send_result = 1;
    if (scenario == 4U) start_result = -1;
    open_cfw_box_uart_handle(scenario == 5U ? 0 : &record);
    if (scenario == 5U) return calls == 0U;
    if (scenario == 1U) {
        return calls == (CALL_STOP | CALL_START | CALL_EXECUTE) &&
            execute_request_length == 0U && execute_response_length == 0U;
    }
    if (scenario == 2U) {
        return calls == (CALL_STOP | CALL_CLEAR | CALL_PRODUCT | CALL_START | CALL_EXECUTE) &&
            execute_request_length == 4U && execute_response_length == 0U;
    }
    if (scenario == 3U) {
        return calls == (CALL_STOP | CALL_CLEAR | CALL_PRODUCT | CALL_DELAY | CALL_SEND | CALL_START | CALL_EXECUTE) &&
            sent_channel == 2U && sent_length == 2U;
    }
    if (scenario == 4U) {
        return calls == (CALL_STOP | CALL_CLEAR | CALL_PRODUCT | CALL_DELAY | CALL_SEND | CALL_FLUSH | CALL_START);
    }
    return calls == (CALL_STOP | CALL_CLEAR | CALL_PRODUCT | CALL_DELAY | CALL_SEND | CALL_FLUSH | CALL_START | CALL_EXECUTE) &&
        sent_channel == 2U && sent_length == 2U && sent_data[0] == 0x54U &&
        execute_request_length == 4U && execute_response_length == 2U;
}
