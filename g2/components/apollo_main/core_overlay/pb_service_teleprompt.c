/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room implementation of the seven linked G2
 * pb_service_teleprompt.c entries. Diagnostic-only EasyLogger and hexdump
 * calls are omitted; the nanopb, duplicate-filter, envelope, role, and BLE
 * transport contracts are preserved.
 */

#include <stdint.h>

typedef struct {
    void *callback;
    void *state;
    uint32_t bytes_left;
    const char *error;
} open_cfw_pb_teleprompt_input;

struct open_cfw_pb_teleprompt_output;
typedef uint32_t (*open_cfw_pb_teleprompt_write_fn)(
    struct open_cfw_pb_teleprompt_output *, const void *, uint32_t);
typedef struct open_cfw_pb_teleprompt_output {
    open_cfw_pb_teleprompt_write_fn write;
    void *context;
    uint32_t capacity;
    uint32_t length;
    const char *error;
} open_cfw_pb_teleprompt_output;

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(open_cfw_pb_teleprompt_input) == 16U,
    "G2 nanopb input stream ABI changed");
_Static_assert(sizeof(open_cfw_pb_teleprompt_output) == 20U,
    "G2 nanopb output stream ABI changed");
#endif

#ifndef OPEN_CFW_PB_TELEPROMPT_MESSAGE
#define OPEN_CFW_PB_TELEPROMPT_MESSAGE \
    ((uint8_t *)(uintptr_t)0x200F873CU)
#endif
#ifndef OPEN_CFW_PB_TELEPROMPT_ENCODE_BUFFER
#define OPEN_CFW_PB_TELEPROMPT_ENCODE_BUFFER \
    ((uint8_t *)(uintptr_t)0x2037C9A0U)
#endif
#ifndef OPEN_CFW_PB_TELEPROMPT_DESCRIPTOR
#define OPEN_CFW_PB_TELEPROMPT_DESCRIPTOR \
    ((const void *)(uintptr_t)0x0077C304U)
#endif
#ifndef OPEN_CFW_PB_TELEPROMPT_LAST_MAGIC
#define OPEN_CFW_PB_TELEPROMPT_LAST_MAGIC \
    ((uint8_t *)(uintptr_t)0x20074FFEU)
#endif
#ifndef OPEN_CFW_PB_TELEPROMPT_LAST_TICK
#define OPEN_CFW_PB_TELEPROMPT_LAST_TICK \
    ((uint32_t *)(uintptr_t)0x20074870U)
#endif

#ifndef OPEN_CFW_PB_TELEPROMPT_INPUT_FROM_BUFFER
open_cfw_pb_teleprompt_input open_cfw_nanopb_istream_from_buffer(
    const void *data, uint32_t length);
#define OPEN_CFW_PB_TELEPROMPT_INPUT_FROM_BUFFER(data, length) \
    open_cfw_nanopb_istream_from_buffer((data), (length))
#endif
#ifndef OPEN_CFW_PB_TELEPROMPT_DECODE
uint32_t open_cfw_nanopb_decode(
    open_cfw_pb_teleprompt_input *input, const void *descriptor, void *message);
#define OPEN_CFW_PB_TELEPROMPT_DECODE(input, descriptor, message) \
    open_cfw_nanopb_decode((input), (descriptor), (message))
#endif
#ifndef OPEN_CFW_PB_TELEPROMPT_ENCODE
uint32_t open_cfw_format_message_encode(
    void *output, const void *descriptor, const void *message);
#define OPEN_CFW_PB_TELEPROMPT_ENCODE(output, descriptor, message) \
    open_cfw_format_message_encode((output), (descriptor), (message))
#endif
#ifndef OPEN_CFW_PB_TELEPROMPT_TICK_GET
uint32_t open_cfw_cmsis_kernel_get_tick_count(void);
#define OPEN_CFW_PB_TELEPROMPT_TICK_GET() \
    open_cfw_cmsis_kernel_get_tick_count()
#endif
#ifndef OPEN_CFW_PB_TELEPROMPT_ROLE_GET
uint32_t open_cfw_lens_side(void);
#define OPEN_CFW_PB_TELEPROMPT_ROLE_GET() open_cfw_lens_side()
#endif
#ifndef OPEN_CFW_PB_TELEPROMPT_SEND
int open_cfw_ble_msgtx_pb_send(
    uint32_t route, uint32_t service, const void *data, uint32_t length);
#define OPEN_CFW_PB_TELEPROMPT_SEND(route, service, data, length) \
    open_cfw_ble_msgtx_pb_send((route), (service), (data), (length))
#endif
#ifndef OPEN_CFW_PB_TELEPROMPT_NOTIFY
int open_cfw_ble_msgtx_pb_notify(
    uint32_t route, uint32_t service, const void *data, uint32_t length);
#define OPEN_CFW_PB_TELEPROMPT_NOTIFY(route, service, data, length) \
    open_cfw_ble_msgtx_pb_notify((route), (service), (data), (length))
#endif

#if defined(OPEN_CFW_PB_TELEPROMPT_RX_ONLY)
#define OPEN_CFW_PB_TELEPROMPT_INCLUDE_RX 1
#elif defined(OPEN_CFW_PB_TELEPROMPT_COMM_RESP_ONLY)
#define OPEN_CFW_PB_TELEPROMPT_INCLUDE_COMM_RESP 1
#elif defined(OPEN_CFW_PB_TELEPROMPT_STATUS_ONLY)
#define OPEN_CFW_PB_TELEPROMPT_INCLUDE_STATUS 1
#elif defined(OPEN_CFW_PB_TELEPROMPT_FILE_LIST_ONLY)
#define OPEN_CFW_PB_TELEPROMPT_INCLUDE_FILE_LIST 1
#elif defined(OPEN_CFW_PB_TELEPROMPT_FILE_SELECT_ONLY)
#define OPEN_CFW_PB_TELEPROMPT_INCLUDE_FILE_SELECT 1
#elif defined(OPEN_CFW_PB_TELEPROMPT_PAGE_DATA_ONLY)
#define OPEN_CFW_PB_TELEPROMPT_INCLUDE_PAGE_DATA 1
#elif defined(OPEN_CFW_PB_TELEPROMPT_SCROLL_SYNC_ONLY)
#define OPEN_CFW_PB_TELEPROMPT_INCLUDE_SCROLL_SYNC 1
#elif defined(OPEN_CFW_PB_TELEPROMPT_BUFFER_WRITE_ONLY)
#define OPEN_CFW_PB_TELEPROMPT_INCLUDE_BUFFER_WRITE 1
#elif defined(OPEN_CFW_PB_TELEPROMPT_ZERO_ONLY)
#define OPEN_CFW_PB_TELEPROMPT_INCLUDE_ZERO 1
#else
#define OPEN_CFW_PB_TELEPROMPT_INCLUDE_RX 1
#define OPEN_CFW_PB_TELEPROMPT_INCLUDE_COMM_RESP 1
#define OPEN_CFW_PB_TELEPROMPT_INCLUDE_STATUS 1
#define OPEN_CFW_PB_TELEPROMPT_INCLUDE_FILE_LIST 1
#define OPEN_CFW_PB_TELEPROMPT_INCLUDE_FILE_SELECT 1
#define OPEN_CFW_PB_TELEPROMPT_INCLUDE_PAGE_DATA 1
#define OPEN_CFW_PB_TELEPROMPT_INCLUDE_SCROLL_SYNC 1
#define OPEN_CFW_PB_TELEPROMPT_INCLUDE_BUFFER_WRITE 1
#define OPEN_CFW_PB_TELEPROMPT_INCLUDE_ZERO 1
#endif

uint32_t open_cfw_pb_service_teleprompt_buffer_write(
    open_cfw_pb_teleprompt_output *output, const void *data, uint32_t length);
void open_cfw_pb_service_teleprompt_zero(void *data, uint32_t length);

static __attribute__((always_inline, unused)) inline void
open_cfw_pb_teleprompt_output_init(open_cfw_pb_teleprompt_output *output)
{
    output->write = open_cfw_pb_service_teleprompt_buffer_write;
    output->context = OPEN_CFW_PB_TELEPROMPT_ENCODE_BUFFER;
    output->capacity = 0x100U;
    output->length = 0U;
    output->error = (const char *)0;
}

static __attribute__((always_inline, unused)) inline uint8_t
open_cfw_pb_teleprompt_next_magic(void)
{
    return (uint8_t)(*OPEN_CFW_PB_TELEPROMPT_LAST_MAGIC + 1U);
}

static __attribute__((always_inline, unused)) inline uint32_t
open_cfw_pb_teleprompt_encode(open_cfw_pb_teleprompt_output *output)
{
    return OPEN_CFW_PB_TELEPROMPT_ENCODE(
        output, OPEN_CFW_PB_TELEPROMPT_DESCRIPTOR,
        OPEN_CFW_PB_TELEPROMPT_MESSAGE);
}

static __attribute__((always_inline, unused)) inline void
open_cfw_pb_teleprompt_notify_if_master(
    const open_cfw_pb_teleprompt_output *output)
{
    if (OPEN_CFW_PB_TELEPROMPT_ROLE_GET() == 1U) {
        (void)OPEN_CFW_PB_TELEPROMPT_NOTIFY(
            1U, 6U, OPEN_CFW_PB_TELEPROMPT_ENCODE_BUFFER,
            (uint16_t)output->length);
    }
}

static __attribute__((always_inline, unused)) inline void
open_cfw_pb_teleprompt_store_u16(uint8_t *destination, uint16_t value)
{
    destination[0] = (uint8_t)value;
    destination[1] = (uint8_t)(value >> 8);
}

static __attribute__((always_inline, unused)) inline void
open_cfw_pb_teleprompt_store_u32(uint8_t *destination, uint32_t value)
{
    destination[0] = (uint8_t)value;
    destination[1] = (uint8_t)(value >> 8);
    destination[2] = (uint8_t)(value >> 16);
    destination[3] = (uint8_t)(value >> 24);
}

#if defined(OPEN_CFW_PB_TELEPROMPT_INCLUDE_BUFFER_WRITE)
__attribute__((used, noinline))
uint32_t open_cfw_pb_service_teleprompt_buffer_write(
    open_cfw_pb_teleprompt_output *output, const void *raw_data, uint32_t length)
{
    const uint8_t *data = (const uint8_t *)raw_data;
    uint8_t *destination = (uint8_t *)output->context;
    uint32_t index;
    if (output->length > output->capacity ||
        length > output->capacity - output->length) {
        return 0U;
    }
    for (index = 0U; index < length; ++index) {
        destination[output->length + index] = data[index];
    }
    return 1U;
}
#endif

#if defined(OPEN_CFW_PB_TELEPROMPT_INCLUDE_ZERO)
__attribute__((used, noinline))
void open_cfw_pb_service_teleprompt_zero(void *raw_data, uint32_t length)
{
    uint8_t *data = (uint8_t *)raw_data;
    uint32_t index;
    for (index = 0U; index < length; ++index) {
        data[index] = 0U;
    }
}
#endif

#if defined(OPEN_CFW_PB_TELEPROMPT_INCLUDE_RX)
__attribute__((used, noinline))
uint32_t APP_PbRxTelepromptFrameDataProcess(
    const void *data, uint32_t length, void *message)
{
    open_cfw_pb_teleprompt_input input;
    uint8_t *bytes = (uint8_t *)message;
    uint32_t now;
    uint32_t elapsed;
    if (data == (const void *)0 || message == (void *)0) {
        return 6U;
    }
    input = OPEN_CFW_PB_TELEPROMPT_INPUT_FROM_BUFFER(
        data, (uint16_t)length);
    if (OPEN_CFW_PB_TELEPROMPT_DECODE(
            &input, OPEN_CFW_PB_TELEPROMPT_DESCRIPTOR, message) == 0U) {
        return 5U;
    }
    now = OPEN_CFW_PB_TELEPROMPT_TICK_GET();
    elapsed = now - *OPEN_CFW_PB_TELEPROMPT_LAST_TICK;
    if (bytes[1] == *OPEN_CFW_PB_TELEPROMPT_LAST_MAGIC && elapsed < 3000U) {
        return 13U;
    }
    *OPEN_CFW_PB_TELEPROMPT_LAST_MAGIC = bytes[1];
    *OPEN_CFW_PB_TELEPROMPT_LAST_TICK = now;
    return 0U;
}
#endif

#if defined(OPEN_CFW_PB_TELEPROMPT_INCLUDE_COMM_RESP)
__attribute__((used, noinline))
uint32_t APP_PbTelepromptTxEncodeCommResp(
    uint32_t magic, const void *raw_response)
{
    const uint8_t *response = (const uint8_t *)raw_response;
    open_cfw_pb_teleprompt_output output;
    uint8_t *message = OPEN_CFW_PB_TELEPROMPT_MESSAGE;
    open_cfw_pb_service_teleprompt_zero(message, 0xF58U);
    message[0] = 0xA6U;
    message[1] = (uint8_t)magic;
    open_cfw_pb_teleprompt_store_u16(message + 2U, 12U);
    message[4] = response[0];
    open_cfw_pb_teleprompt_output_init(&output);
    if (open_cfw_pb_teleprompt_encode(&output) == 0U) {
        return 0x2BU;
    }
    if (OPEN_CFW_PB_TELEPROMPT_ROLE_GET() == 1U) {
        (void)OPEN_CFW_PB_TELEPROMPT_SEND(
            1U, 6U, OPEN_CFW_PB_TELEPROMPT_ENCODE_BUFFER,
            (uint16_t)output.length);
    }
    return 0U;
}
#endif

#if defined(OPEN_CFW_PB_TELEPROMPT_INCLUDE_STATUS)
__attribute__((used, noinline))
uint32_t APP_PbTxEncodeStatusNotify(const void *raw_status)
{
    const uint16_t *status = (const uint16_t *)raw_status;
    open_cfw_pb_teleprompt_output output;
    uint8_t *message = OPEN_CFW_PB_TELEPROMPT_MESSAGE;
    open_cfw_pb_service_teleprompt_zero(message, 0xF58U);
    message[0] = 0xA1U;
    message[1] = open_cfw_pb_teleprompt_next_magic();
    open_cfw_pb_teleprompt_store_u16(message + 2U, 7U);
    open_cfw_pb_teleprompt_store_u16(message + 4U, *status);
    open_cfw_pb_teleprompt_output_init(&output);
    if (open_cfw_pb_teleprompt_encode(&output) == 0U) {
        return 0x2BU;
    }
    open_cfw_pb_teleprompt_notify_if_master(&output);
    return 0U;
}
#endif

#if defined(OPEN_CFW_PB_TELEPROMPT_INCLUDE_FILE_LIST)
__attribute__((used, noinline))
uint32_t APP_PbTxEncodeFileListRequest(const void *raw_request)
{
    const uint8_t *request = (const uint8_t *)raw_request;
    open_cfw_pb_teleprompt_output output;
    uint8_t *message = OPEN_CFW_PB_TELEPROMPT_MESSAGE;
    open_cfw_pb_service_teleprompt_zero(message, 0xF58U);
    message[0] = 0xA2U;
    message[1] = open_cfw_pb_teleprompt_next_magic();
    open_cfw_pb_teleprompt_store_u16(message + 2U, 8U);
    message[4] = request[0];
    open_cfw_pb_teleprompt_output_init(&output);
    if (open_cfw_pb_teleprompt_encode(&output) == 0U) {
        return 0x2BU;
    }
    open_cfw_pb_teleprompt_notify_if_master(&output);
    return 0U;
}
#endif

#if defined(OPEN_CFW_PB_TELEPROMPT_INCLUDE_FILE_SELECT)
__attribute__((used, noinline))
uint32_t APP_PbTxEncodeFileSelect(const void *raw_selection)
{
    const uint8_t *selection = (const uint8_t *)raw_selection;
    open_cfw_pb_teleprompt_output output;
    uint8_t *message = OPEN_CFW_PB_TELEPROMPT_MESSAGE;
    uint32_t index;
    open_cfw_pb_service_teleprompt_zero(message, 0xF58U);
    message[0] = 0xA3U;
    message[1] = open_cfw_pb_teleprompt_next_magic();
    open_cfw_pb_teleprompt_store_u16(message + 2U, 9U);
    for (index = 0U; index < 0x42U; ++index) {
        message[4U + index] = selection[index];
    }
    open_cfw_pb_teleprompt_output_init(&output);
    if (open_cfw_pb_teleprompt_encode(&output) == 0U) {
        return 0x2BU;
    }
    open_cfw_pb_teleprompt_notify_if_master(&output);
    return 0U;
}
#endif

#if defined(OPEN_CFW_PB_TELEPROMPT_INCLUDE_PAGE_DATA)
__attribute__((used, noinline))
uint32_t APP_PbTxEncodePageDataRequest(const void *raw_page)
{
    const uint32_t *page = (const uint32_t *)raw_page;
    open_cfw_pb_teleprompt_output output;
    uint8_t *message = OPEN_CFW_PB_TELEPROMPT_MESSAGE;
    open_cfw_pb_service_teleprompt_zero(message, 0xF58U);
    message[0] = 0xA4U;
    message[1] = open_cfw_pb_teleprompt_next_magic();
    open_cfw_pb_teleprompt_store_u16(message + 2U, 10U);
    open_cfw_pb_teleprompt_store_u32(message + 4U, *page);
    open_cfw_pb_teleprompt_output_init(&output);
    if (open_cfw_pb_teleprompt_encode(&output) == 0U) {
        return 0x2BU;
    }
    open_cfw_pb_teleprompt_notify_if_master(&output);
    return 0U;
}
#endif

#if defined(OPEN_CFW_PB_TELEPROMPT_INCLUDE_SCROLL_SYNC)
__attribute__((used, noinline))
uint32_t APP_PbTxEncodeScrollSync(const void *raw_scroll)
{
    const uint8_t *scroll = (const uint8_t *)raw_scroll;
    open_cfw_pb_teleprompt_output output;
    uint8_t *message = OPEN_CFW_PB_TELEPROMPT_MESSAGE;
    uint32_t index;
    open_cfw_pb_service_teleprompt_zero(message, 0xF58U);
    message[0] = 0xA5U;
    message[1] = open_cfw_pb_teleprompt_next_magic();
    open_cfw_pb_teleprompt_store_u16(message + 2U, 11U);
    for (index = 0U; index < 12U; ++index) {
        message[4U + index] = scroll[index];
    }
    open_cfw_pb_teleprompt_output_init(&output);
    if (open_cfw_pb_teleprompt_encode(&output) == 0U) {
        return 0x2BU;
    }
    open_cfw_pb_teleprompt_notify_if_master(&output);
    return 0U;
}
#endif
