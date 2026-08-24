/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room implementation of the six linked G2
 * pb_service_conversate.c entries. Diagnostic-only EasyLogger and hexdump
 * calls are omitted; the nanopb, duplicate-filter, envelope, role, and BLE
 * transport contracts are preserved.
 */

#include <stdint.h>

typedef struct {
    void *callback;
    void *state;
    uint32_t bytes_left;
    const char *error;
} open_cfw_pb_conversate_input;

struct open_cfw_pb_conversate_output;
typedef uint32_t (*open_cfw_pb_conversate_write_fn)(
    struct open_cfw_pb_conversate_output *, const void *, uint32_t);
typedef struct open_cfw_pb_conversate_output {
    open_cfw_pb_conversate_write_fn write;
    void *context;
    uint32_t capacity;
    uint32_t length;
    const char *error;
} open_cfw_pb_conversate_output;

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(open_cfw_pb_conversate_input) == 16U,
    "G2 nanopb input stream ABI changed");
_Static_assert(sizeof(open_cfw_pb_conversate_output) == 20U,
    "G2 nanopb output stream ABI changed");
#endif

#ifndef OPEN_CFW_PB_CONVERSATE_MESSAGE
#define OPEN_CFW_PB_CONVERSATE_MESSAGE \
    ((uint8_t *)(uintptr_t)0x200F4808U)
#endif
#ifndef OPEN_CFW_PB_CONVERSATE_ENCODE_BUFFER
#define OPEN_CFW_PB_CONVERSATE_ENCODE_BUFFER \
    ((uint8_t *)(uintptr_t)0x2037C2A0U)
#endif
#ifndef OPEN_CFW_PB_CONVERSATE_DESCRIPTOR
#define OPEN_CFW_PB_CONVERSATE_DESCRIPTOR \
    ((const void *)(uintptr_t)0x00775B24U)
#endif
#ifndef OPEN_CFW_PB_CONVERSATE_LAST_MAGIC
#define OPEN_CFW_PB_CONVERSATE_LAST_MAGIC \
    ((uint8_t *)(uintptr_t)0x20074FF8U)
#endif
#ifndef OPEN_CFW_PB_CONVERSATE_LAST_TICK
#define OPEN_CFW_PB_CONVERSATE_LAST_TICK \
    ((uint32_t *)(uintptr_t)0x2007485CU)
#endif

#ifndef OPEN_CFW_PB_CONVERSATE_INPUT_FROM_BUFFER
open_cfw_pb_conversate_input open_cfw_nanopb_istream_from_buffer(
    const void *data, uint32_t length);
#define OPEN_CFW_PB_CONVERSATE_INPUT_FROM_BUFFER(data, length) \
    open_cfw_nanopb_istream_from_buffer((data), (length))
#endif
#ifndef OPEN_CFW_PB_CONVERSATE_DECODE
uint32_t open_cfw_nanopb_decode(
    open_cfw_pb_conversate_input *input, const void *descriptor, void *message);
#define OPEN_CFW_PB_CONVERSATE_DECODE(input, descriptor, message) \
    open_cfw_nanopb_decode((input), (descriptor), (message))
#endif
#ifndef OPEN_CFW_PB_CONVERSATE_ENCODE
uint32_t open_cfw_format_message_encode(
    void *output, const void *descriptor, const void *message);
#define OPEN_CFW_PB_CONVERSATE_ENCODE(output, descriptor, message) \
    open_cfw_format_message_encode((output), (descriptor), (message))
#endif
#ifndef OPEN_CFW_PB_CONVERSATE_TICK_GET
uint32_t open_cfw_cmsis_kernel_get_tick_count(void);
#define OPEN_CFW_PB_CONVERSATE_TICK_GET() \
    open_cfw_cmsis_kernel_get_tick_count()
#endif
#ifndef OPEN_CFW_PB_CONVERSATE_ROLE_GET
uint32_t open_cfw_lens_side(void);
#define OPEN_CFW_PB_CONVERSATE_ROLE_GET() open_cfw_lens_side()
#endif
#ifndef OPEN_CFW_PB_CONVERSATE_SEND
int open_cfw_ble_msgtx_pb_send(
    uint32_t route, uint32_t service, const void *data, uint32_t length);
#define OPEN_CFW_PB_CONVERSATE_SEND(route, service, data, length) \
    open_cfw_ble_msgtx_pb_send((route), (service), (data), (length))
#endif
#ifndef OPEN_CFW_PB_CONVERSATE_NOTIFY
int open_cfw_ble_msgtx_pb_notify(
    uint32_t route, uint32_t service, const void *data, uint32_t length);
#define OPEN_CFW_PB_CONVERSATE_NOTIFY(route, service, data, length) \
    open_cfw_ble_msgtx_pb_notify((route), (service), (data), (length))
#endif

#if defined(OPEN_CFW_PB_CONVERSATE_RX_ONLY)
#define OPEN_CFW_PB_CONVERSATE_INCLUDE_RX 1
#elif defined(OPEN_CFW_PB_CONVERSATE_NOTIFY_ONLY)
#define OPEN_CFW_PB_CONVERSATE_INCLUDE_NOTIFY 1
#elif defined(OPEN_CFW_PB_CONVERSATE_PREP_LIST_ONLY)
#define OPEN_CFW_PB_CONVERSATE_INCLUDE_PREP_LIST 1
#elif defined(OPEN_CFW_PB_CONVERSATE_PREP_SELECT_ONLY)
#define OPEN_CFW_PB_CONVERSATE_INCLUDE_PREP_SELECT 1
#elif defined(OPEN_CFW_PB_CONVERSATE_COMM_RESP_ONLY)
#define OPEN_CFW_PB_CONVERSATE_INCLUDE_COMM_RESP 1
#elif defined(OPEN_CFW_PB_CONVERSATE_TAG_TRACKING_ONLY)
#define OPEN_CFW_PB_CONVERSATE_INCLUDE_TAG_TRACKING 1
#elif defined(OPEN_CFW_PB_CONVERSATE_BUFFER_WRITE_ONLY)
#define OPEN_CFW_PB_CONVERSATE_INCLUDE_BUFFER_WRITE 1
#elif defined(OPEN_CFW_PB_CONVERSATE_ZERO_ONLY)
#define OPEN_CFW_PB_CONVERSATE_INCLUDE_ZERO 1
#else
#define OPEN_CFW_PB_CONVERSATE_INCLUDE_RX 1
#define OPEN_CFW_PB_CONVERSATE_INCLUDE_NOTIFY 1
#define OPEN_CFW_PB_CONVERSATE_INCLUDE_PREP_LIST 1
#define OPEN_CFW_PB_CONVERSATE_INCLUDE_PREP_SELECT 1
#define OPEN_CFW_PB_CONVERSATE_INCLUDE_COMM_RESP 1
#define OPEN_CFW_PB_CONVERSATE_INCLUDE_TAG_TRACKING 1
#define OPEN_CFW_PB_CONVERSATE_INCLUDE_BUFFER_WRITE 1
#define OPEN_CFW_PB_CONVERSATE_INCLUDE_ZERO 1
#endif

uint32_t open_cfw_pb_service_conversate_buffer_write(
    open_cfw_pb_conversate_output *output, const void *data, uint32_t length);
void open_cfw_pb_service_conversate_zero(void *data, uint32_t length);

static __attribute__((always_inline, unused)) inline void
open_cfw_pb_conversate_output_init(open_cfw_pb_conversate_output *output)
{
    output->write = open_cfw_pb_service_conversate_buffer_write;
    output->context = OPEN_CFW_PB_CONVERSATE_ENCODE_BUFFER;
    output->capacity = 0x100U;
    output->length = 0U;
    output->error = (const char *)0;
}

static __attribute__((always_inline, unused)) inline uint8_t
open_cfw_pb_conversate_next_magic(void)
{
    return (uint8_t)(*OPEN_CFW_PB_CONVERSATE_LAST_MAGIC + 1U);
}

static __attribute__((always_inline, unused)) inline uint32_t
open_cfw_pb_conversate_encode(open_cfw_pb_conversate_output *output)
{
    return OPEN_CFW_PB_CONVERSATE_ENCODE(
        output, OPEN_CFW_PB_CONVERSATE_DESCRIPTOR,
        OPEN_CFW_PB_CONVERSATE_MESSAGE);
}

static __attribute__((always_inline, unused)) inline void
open_cfw_pb_conversate_notify_if_master(
    const open_cfw_pb_conversate_output *output)
{
    if (OPEN_CFW_PB_CONVERSATE_ROLE_GET() == 1U) {
        (void)OPEN_CFW_PB_CONVERSATE_NOTIFY(
            1U, 0x0BU, OPEN_CFW_PB_CONVERSATE_ENCODE_BUFFER,
            (uint16_t)output->length);
    }
}

#if defined(OPEN_CFW_PB_CONVERSATE_INCLUDE_BUFFER_WRITE)
__attribute__((used, noinline))
uint32_t open_cfw_pb_service_conversate_buffer_write(
    open_cfw_pb_conversate_output *output, const void *raw_data, uint32_t length)
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

#if defined(OPEN_CFW_PB_CONVERSATE_INCLUDE_ZERO)
__attribute__((used, noinline))
void open_cfw_pb_service_conversate_zero(void *raw_data, uint32_t length)
{
    uint8_t *data = (uint8_t *)raw_data;
    uint32_t index;
    for (index = 0U; index < length; ++index) {
        data[index] = 0U;
    }
}
#endif

#if defined(OPEN_CFW_PB_CONVERSATE_INCLUDE_RX)
__attribute__((used, noinline))
uint32_t APP_PbConversateRxFrameDataProcess(
    const void *data, uint32_t length, void *message)
{
    open_cfw_pb_conversate_input input;
    uint8_t *bytes = (uint8_t *)message;
    uint32_t now;
    uint32_t elapsed;
    if (data == (const void *)0 || message == (void *)0) {
        return 6U;
    }
    input = OPEN_CFW_PB_CONVERSATE_INPUT_FROM_BUFFER(
        data, (uint16_t)length);
    if (OPEN_CFW_PB_CONVERSATE_DECODE(
            &input, OPEN_CFW_PB_CONVERSATE_DESCRIPTOR, message) == 0U) {
        return 5U;
    }
    now = OPEN_CFW_PB_CONVERSATE_TICK_GET();
    elapsed = now - *OPEN_CFW_PB_CONVERSATE_LAST_TICK;
    if (bytes[1] == *OPEN_CFW_PB_CONVERSATE_LAST_MAGIC && elapsed < 3000U) {
        return 13U;
    }
    *OPEN_CFW_PB_CONVERSATE_LAST_MAGIC = bytes[1];
    *OPEN_CFW_PB_CONVERSATE_LAST_TICK = now;
    return 0U;
}
#endif

#if defined(OPEN_CFW_PB_CONVERSATE_INCLUDE_NOTIFY)
__attribute__((used, noinline))
uint32_t APP_PbConversateTxEncodeNotify(const void *raw_notify)
{
    const uint16_t *notify = (const uint16_t *)raw_notify;
    open_cfw_pb_conversate_output output;
    uint8_t *message = OPEN_CFW_PB_CONVERSATE_MESSAGE;
    if (notify == (const uint16_t *)0) {
        return 6U;
    }
    open_cfw_pb_service_conversate_zero(message, 0xFACU);
    message[0] = 0xA1U;
    message[1] = open_cfw_pb_conversate_next_magic();
    message[2] = 9U;
    message[3] = 0U;
    message[4] = (uint8_t)*notify;
    message[5] = (uint8_t)(*notify >> 8);
    open_cfw_pb_conversate_output_init(&output);
    if (open_cfw_pb_conversate_encode(&output) == 0U) {
        return 5U;
    }
    open_cfw_pb_conversate_notify_if_master(&output);
    return 0U;
}
#endif

#if defined(OPEN_CFW_PB_CONVERSATE_INCLUDE_PREP_LIST)
__attribute__((used, noinline))
uint32_t APP_PbConversateTxEncodePrepNoteListRequest(void)
{
    open_cfw_pb_conversate_output output;
    uint8_t *message = OPEN_CFW_PB_CONVERSATE_MESSAGE;
    open_cfw_pb_service_conversate_zero(message, 0xFACU);
    message[0] = 2U;
    message[1] = open_cfw_pb_conversate_next_magic();
    message[2] = 4U;
    message[3] = 0U;
    message[4] = 0U;
    open_cfw_pb_conversate_output_init(&output);
    if (open_cfw_pb_conversate_encode(&output) == 0U) {
        return 5U;
    }
    open_cfw_pb_conversate_notify_if_master(&output);
    return 0U;
}
#endif

#if defined(OPEN_CFW_PB_CONVERSATE_INCLUDE_PREP_SELECT)
__attribute__((used, noinline))
uint32_t APP_PbConversateTxEncodePrepNoteSelect(
    uint32_t selection, uint32_t note_id)
{
    open_cfw_pb_conversate_output output;
    uint8_t *message = OPEN_CFW_PB_CONVERSATE_MESSAGE;
    open_cfw_pb_service_conversate_zero(message, 0xFACU);
    message[0] = 4U;
    message[1] = open_cfw_pb_conversate_next_magic();
    message[2] = 6U;
    message[3] = 0U;
    message[4] = (uint8_t)selection;
    message[8] = (uint8_t)note_id;
    message[9] = (uint8_t)(note_id >> 8);
    message[10] = (uint8_t)(note_id >> 16);
    message[11] = (uint8_t)(note_id >> 24);
    open_cfw_pb_conversate_output_init(&output);
    if (open_cfw_pb_conversate_encode(&output) == 0U) {
        return 5U;
    }
    open_cfw_pb_conversate_notify_if_master(&output);
    return 0U;
}
#endif

#if defined(OPEN_CFW_PB_CONVERSATE_INCLUDE_COMM_RESP)
__attribute__((used, noinline))
uint32_t APP_PbConversateTxEncodeCommResp(
    const void *raw_response, uint32_t magic)
{
    const uint8_t *response = (const uint8_t *)raw_response;
    open_cfw_pb_conversate_output output;
    uint8_t *message = OPEN_CFW_PB_CONVERSATE_MESSAGE;
    if (response == (const uint8_t *)0) {
        return 6U;
    }
    open_cfw_pb_service_conversate_zero(message, 0xFACU);
    message[0] = 0xA2U;
    message[1] = (uint8_t)magic;
    message[2] = 10U;
    message[3] = 0U;
    message[4] = response[0];
    open_cfw_pb_conversate_output_init(&output);
    if (open_cfw_pb_conversate_encode(&output) == 0U) {
        return 5U;
    }
    if (OPEN_CFW_PB_CONVERSATE_ROLE_GET() == 1U) {
        (void)OPEN_CFW_PB_CONVERSATE_SEND(
            1U, 0x0BU, OPEN_CFW_PB_CONVERSATE_ENCODE_BUFFER,
            (uint16_t)output.length);
    }
    return 0U;
}
#endif

#if defined(OPEN_CFW_PB_CONVERSATE_INCLUDE_TAG_TRACKING)
__attribute__((used, noinline))
uint32_t APP_PbConversateTxEncodeTagTrackingData(const void *raw_tracking)
{
    const uint8_t *tracking = (const uint8_t *)raw_tracking;
    open_cfw_pb_conversate_output output;
    uint8_t *message = OPEN_CFW_PB_CONVERSATE_MESSAGE;
    uint32_t index;
    if (tracking == (const uint8_t *)0) {
        return 6U;
    }
    open_cfw_pb_service_conversate_zero(message, 0xFACU);
    message[0] = 0xA3U;
    message[1] = open_cfw_pb_conversate_next_magic();
    message[2] = 12U;
    message[3] = 0U;
    for (index = 0U; index < 12U; ++index) {
        message[4U + index] = tracking[index];
    }
    open_cfw_pb_conversate_output_init(&output);
    if (open_cfw_pb_conversate_encode(&output) == 0U) {
        return 5U;
    }
    open_cfw_pb_conversate_notify_if_master(&output);
    return 0U;
}
#endif
