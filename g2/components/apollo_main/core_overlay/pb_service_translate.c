/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room implementation of the four linked G2
 * pb_service_translate.c entries. Diagnostic-only EasyLogger/hexdump calls
 * are omitted; nanopb, replay suppression, envelope, role-gating, and BLE
 * transport behavior are preserved.
 */

#include <stdint.h>

typedef struct {
    void *callback;
    void *state;
    uint32_t bytes_left;
    const char *error;
} open_cfw_pb_translate_input;

struct open_cfw_pb_translate_output;
typedef uint32_t (*open_cfw_pb_translate_write_fn)(
    struct open_cfw_pb_translate_output *, const void *, uint32_t);
typedef struct open_cfw_pb_translate_output {
    open_cfw_pb_translate_write_fn write;
    void *context;
    uint32_t capacity;
    uint32_t length;
    const char *error;
} open_cfw_pb_translate_output;

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(open_cfw_pb_translate_input) == 16U,
    "G2 nanopb input stream ABI changed");
_Static_assert(sizeof(open_cfw_pb_translate_output) == 20U,
    "G2 nanopb output stream ABI changed");
#endif

#ifndef OPEN_CFW_PB_TRANSLATE_MESSAGE
#define OPEN_CFW_PB_TRANSLATE_MESSAGE \
    ((uint8_t *)(uintptr_t)0x200F9EE4U)
#endif
#ifndef OPEN_CFW_PB_TRANSLATE_ENCODE_BUFFER
#define OPEN_CFW_PB_TRANSLATE_ENCODE_BUFFER \
    ((uint8_t *)(uintptr_t)0x2037CAA0U)
#endif
#ifndef OPEN_CFW_PB_TRANSLATE_DESCRIPTOR
#define OPEN_CFW_PB_TRANSLATE_DESCRIPTOR \
    ((const void *)(uintptr_t)0x0077CE5CU)
#endif
#ifndef OPEN_CFW_PB_TRANSLATE_LAST_MAGIC
#define OPEN_CFW_PB_TRANSLATE_LAST_MAGIC \
    ((uint8_t *)(uintptr_t)0x20075000U)
#endif
#ifndef OPEN_CFW_PB_TRANSLATE_LAST_TICK
#define OPEN_CFW_PB_TRANSLATE_LAST_TICK \
    ((uint32_t *)(uintptr_t)0x20074878U)
#endif

#ifndef OPEN_CFW_PB_TRANSLATE_INPUT_FROM_BUFFER
open_cfw_pb_translate_input open_cfw_nanopb_istream_from_buffer(
    const void *data, uint32_t length);
#define OPEN_CFW_PB_TRANSLATE_INPUT_FROM_BUFFER(data, length) \
    open_cfw_nanopb_istream_from_buffer((data), (length))
#endif
#ifndef OPEN_CFW_PB_TRANSLATE_DECODE
uint32_t open_cfw_nanopb_decode(
    open_cfw_pb_translate_input *input, const void *descriptor, void *message);
#define OPEN_CFW_PB_TRANSLATE_DECODE(input, descriptor, message) \
    open_cfw_nanopb_decode((input), (descriptor), (message))
#endif
#ifndef OPEN_CFW_PB_TRANSLATE_ENCODE
uint32_t open_cfw_format_message_encode(
    void *output, const void *descriptor, const void *message);
#define OPEN_CFW_PB_TRANSLATE_ENCODE(output, descriptor, message) \
    open_cfw_format_message_encode((output), (descriptor), (message))
#endif
#ifndef OPEN_CFW_PB_TRANSLATE_TICK_GET
uint32_t open_cfw_cmsis_kernel_get_tick_count(void);
#define OPEN_CFW_PB_TRANSLATE_TICK_GET() \
    open_cfw_cmsis_kernel_get_tick_count()
#endif
#ifndef OPEN_CFW_PB_TRANSLATE_ROLE_GET
uint32_t open_cfw_lens_side(void);
#define OPEN_CFW_PB_TRANSLATE_ROLE_GET() open_cfw_lens_side()
#endif
#ifndef OPEN_CFW_PB_TRANSLATE_SEND
int open_cfw_ble_msgtx_pb_send(
    uint32_t route, uint32_t service, const void *data, uint32_t length);
#define OPEN_CFW_PB_TRANSLATE_SEND(route, service, data, length) \
    open_cfw_ble_msgtx_pb_send((route), (service), (data), (length))
#endif
#ifndef OPEN_CFW_PB_TRANSLATE_NOTIFY
int open_cfw_ble_msgtx_pb_notify(
    uint32_t route, uint32_t service, const void *data, uint32_t length);
#define OPEN_CFW_PB_TRANSLATE_NOTIFY(route, service, data, length) \
    open_cfw_ble_msgtx_pb_notify((route), (service), (data), (length))
#endif

#if defined(OPEN_CFW_PB_TRANSLATE_ENCODE_ONLY)
#define OPEN_CFW_PB_TRANSLATE_INCLUDE_ENCODE 1
#elif defined(OPEN_CFW_PB_TRANSLATE_RX_ONLY)
#define OPEN_CFW_PB_TRANSLATE_INCLUDE_RX 1
#elif defined(OPEN_CFW_PB_TRANSLATE_NOTIFY_ONLY)
#define OPEN_CFW_PB_TRANSLATE_INCLUDE_NOTIFY 1
#elif defined(OPEN_CFW_PB_TRANSLATE_COMM_RESP_ONLY)
#define OPEN_CFW_PB_TRANSLATE_INCLUDE_COMM_RESP 1
#elif defined(OPEN_CFW_PB_TRANSLATE_MODE_SWITCH_ONLY)
#define OPEN_CFW_PB_TRANSLATE_INCLUDE_MODE_SWITCH 1
#elif defined(OPEN_CFW_PB_TRANSLATE_BUFFER_WRITE_ONLY)
#define OPEN_CFW_PB_TRANSLATE_INCLUDE_BUFFER_WRITE 1
#elif defined(OPEN_CFW_PB_TRANSLATE_ZERO_ONLY)
#define OPEN_CFW_PB_TRANSLATE_INCLUDE_ZERO 1
#else
#define OPEN_CFW_PB_TRANSLATE_INCLUDE_ENCODE 1
#define OPEN_CFW_PB_TRANSLATE_INCLUDE_RX 1
#define OPEN_CFW_PB_TRANSLATE_INCLUDE_NOTIFY 1
#define OPEN_CFW_PB_TRANSLATE_INCLUDE_COMM_RESP 1
#define OPEN_CFW_PB_TRANSLATE_INCLUDE_MODE_SWITCH 1
#define OPEN_CFW_PB_TRANSLATE_INCLUDE_BUFFER_WRITE 1
#define OPEN_CFW_PB_TRANSLATE_INCLUDE_ZERO 1
#endif

uint32_t open_cfw_pb_service_translate_buffer_write(
    open_cfw_pb_translate_output *output, const void *data, uint32_t length);
void open_cfw_pb_service_translate_zero(void *data, uint32_t length);
uint32_t open_cfw_pb_translate_encode_and_send(
    uint32_t command, uint32_t tag, const void *payload,
    uint32_t payload_bytes, uint32_t magic, uint32_t notify);

#if defined(OPEN_CFW_PB_TRANSLATE_INCLUDE_BUFFER_WRITE)
__attribute__((used, noinline))
uint32_t open_cfw_pb_service_translate_buffer_write(
    open_cfw_pb_translate_output *output, const void *raw_data, uint32_t length)
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

#if defined(OPEN_CFW_PB_TRANSLATE_INCLUDE_ZERO)
__attribute__((used, noinline))
void open_cfw_pb_service_translate_zero(void *raw_data, uint32_t length)
{
    uint8_t *data = (uint8_t *)raw_data;
    uint32_t index;
    for (index = 0U; index < length; ++index) {
        data[index] = 0U;
    }
}
#endif

#if defined(OPEN_CFW_PB_TRANSLATE_INCLUDE_ENCODE)
__attribute__((used, noinline))
uint32_t open_cfw_pb_translate_encode_and_send(
    uint32_t command, uint32_t tag, const void *raw_payload,
    uint32_t payload_bytes, uint32_t magic, uint32_t notify)
{
    const uint8_t *payload = (const uint8_t *)raw_payload;
    uint8_t *message = OPEN_CFW_PB_TRANSLATE_MESSAGE;
    open_cfw_pb_translate_output output;
    uint32_t index;

    open_cfw_pb_service_translate_zero(message, 0x854U);
    message[0] = (uint8_t)command;
    message[1] = (uint8_t)magic;
    message[2] = (uint8_t)tag;
    message[3] = (uint8_t)(tag >> 8);
    for (index = 0U; index < payload_bytes; ++index) {
        message[4U + index] = payload[index];
    }
    output.write = open_cfw_pb_service_translate_buffer_write;
    output.context = OPEN_CFW_PB_TRANSLATE_ENCODE_BUFFER;
    output.capacity = 0x100U;
    output.length = 0U;
    output.error = (const char *)0;
    if (OPEN_CFW_PB_TRANSLATE_ENCODE(
            &output, OPEN_CFW_PB_TRANSLATE_DESCRIPTOR, message) == 0U) {
        return 5U;
    }
    if (OPEN_CFW_PB_TRANSLATE_ROLE_GET() == 1U) {
        if (notify == 0U) {
            (void)OPEN_CFW_PB_TRANSLATE_SEND(
                1U, 5U, OPEN_CFW_PB_TRANSLATE_ENCODE_BUFFER,
                (uint16_t)output.length);
        } else {
            (void)OPEN_CFW_PB_TRANSLATE_NOTIFY(
                1U, 5U, OPEN_CFW_PB_TRANSLATE_ENCODE_BUFFER,
                (uint16_t)output.length);
        }
    }
    return 0U;
}
#endif

#if defined(OPEN_CFW_PB_TRANSLATE_INCLUDE_RX)
__attribute__((used, noinline))
uint32_t APP_PbTranslateRxFrameDataProcess(
    const void *data, uint32_t length, void *message)
{
    open_cfw_pb_translate_input input;
    uint8_t *bytes = (uint8_t *)message;
    uint32_t now;
    uint32_t elapsed;
    if (data == (const void *)0 || message == (void *)0) {
        return 6U;
    }
    input = OPEN_CFW_PB_TRANSLATE_INPUT_FROM_BUFFER(data, (uint16_t)length);
    if (OPEN_CFW_PB_TRANSLATE_DECODE(
            &input, OPEN_CFW_PB_TRANSLATE_DESCRIPTOR, message) == 0U) {
        return 5U;
    }
    now = OPEN_CFW_PB_TRANSLATE_TICK_GET();
    elapsed = now - *OPEN_CFW_PB_TRANSLATE_LAST_TICK;
    if (bytes[1] == *OPEN_CFW_PB_TRANSLATE_LAST_MAGIC && elapsed < 3000U) {
        return 13U;
    }
    *OPEN_CFW_PB_TRANSLATE_LAST_MAGIC = bytes[1];
    *OPEN_CFW_PB_TRANSLATE_LAST_TICK = now;
    return 0U;
}
#endif

#if defined(OPEN_CFW_PB_TRANSLATE_INCLUDE_NOTIFY)
__attribute__((used, noinline))
uint32_t APP_PbTranslateTxEncodeNotify(const void *payload)
{
    if (payload == (const void *)0) {
        return 6U;
    }
    return open_cfw_pb_translate_encode_and_send(
        0xA1U, 5U, payload, 2U,
        (uint8_t)(*OPEN_CFW_PB_TRANSLATE_LAST_MAGIC + 1U), 1U);
}
#endif

#if defined(OPEN_CFW_PB_TRANSLATE_INCLUDE_COMM_RESP)
__attribute__((used, noinline))
uint32_t APP_PbTranslateTxEncodeCommResp(
    const void *payload, uint32_t magic)
{
    if (payload == (const void *)0) {
        return 6U;
    }
    return open_cfw_pb_translate_encode_and_send(
        0xA2U, 7U, payload, 1U, magic, 0U);
}
#endif

#if defined(OPEN_CFW_PB_TRANSLATE_INCLUDE_MODE_SWITCH)
__attribute__((used, noinline))
uint32_t APP_PbTranslateTxEncodeModeSwitch(const void *payload)
{
    if (payload == (const void *)0) {
        return 6U;
    }
    return open_cfw_pb_translate_encode_and_send(
        0xA3U, 6U, payload, 4U,
        (uint8_t)(*OPEN_CFW_PB_TRANSLATE_LAST_MAGIC + 1U), 1U);
}
#endif
