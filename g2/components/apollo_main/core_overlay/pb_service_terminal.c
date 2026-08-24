/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room implementation of the thirteen linked G2
 * pb_service_terminal.c entries. Diagnostic-only EasyLogger calls are
 * omitted; nanopb, replay suppression, envelope, role-gating, and BLE
 * transport behavior are preserved.
 */

#include <stdint.h>

typedef struct {
    void *callback;
    void *state;
    uint32_t bytes_left;
    const char *error;
} open_cfw_pb_terminal_input;

struct open_cfw_pb_terminal_output;
typedef uint32_t (*open_cfw_pb_terminal_write_fn)(
    struct open_cfw_pb_terminal_output *, const void *, uint32_t);
typedef struct open_cfw_pb_terminal_output {
    open_cfw_pb_terminal_write_fn write;
    void *context;
    uint32_t capacity;
    uint32_t length;
    const char *error;
} open_cfw_pb_terminal_output;

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(open_cfw_pb_terminal_input) == 16U,
    "G2 nanopb input stream ABI changed");
_Static_assert(sizeof(open_cfw_pb_terminal_output) == 20U,
    "G2 nanopb output stream ABI changed");
#endif

#ifndef OPEN_CFW_PB_TERMINAL_MESSAGE
#define OPEN_CFW_PB_TERMINAL_MESSAGE \
    ((uint8_t *)(uintptr_t)0x200F9694U)
#endif
#ifndef OPEN_CFW_PB_TERMINAL_ENCODE_BUFFER
#define OPEN_CFW_PB_TERMINAL_ENCODE_BUFFER \
    ((uint8_t *)(uintptr_t)0x20374378U)
#endif
#ifndef OPEN_CFW_PB_TERMINAL_DESCRIPTOR
#define OPEN_CFW_PB_TERMINAL_DESCRIPTOR \
    ((const void *)(uintptr_t)0x0077C634U)
#endif
#ifndef OPEN_CFW_PB_TERMINAL_LAST_MAGIC
#define OPEN_CFW_PB_TERMINAL_LAST_MAGIC \
    ((uint8_t *)(uintptr_t)0x20074FFFU)
#endif
#ifndef OPEN_CFW_PB_TERMINAL_LAST_TICK
#define OPEN_CFW_PB_TERMINAL_LAST_TICK \
    ((uint32_t *)(uintptr_t)0x20074874U)
#endif

#ifndef OPEN_CFW_PB_TERMINAL_INPUT_FROM_BUFFER
open_cfw_pb_terminal_input open_cfw_nanopb_istream_from_buffer(
    const void *data, uint32_t length);
#define OPEN_CFW_PB_TERMINAL_INPUT_FROM_BUFFER(data, length) \
    open_cfw_nanopb_istream_from_buffer((data), (length))
#endif
#ifndef OPEN_CFW_PB_TERMINAL_DECODE
uint32_t open_cfw_nanopb_decode(
    open_cfw_pb_terminal_input *input, const void *descriptor, void *message);
#define OPEN_CFW_PB_TERMINAL_DECODE(input, descriptor, message) \
    open_cfw_nanopb_decode((input), (descriptor), (message))
#endif
#ifndef OPEN_CFW_PB_TERMINAL_ENCODE
uint32_t open_cfw_format_message_encode(
    void *output, const void *descriptor, const void *message);
#define OPEN_CFW_PB_TERMINAL_ENCODE(output, descriptor, message) \
    open_cfw_format_message_encode((output), (descriptor), (message))
#endif
#ifndef OPEN_CFW_PB_TERMINAL_TICK_GET
uint32_t open_cfw_cmsis_kernel_get_tick_count(void);
#define OPEN_CFW_PB_TERMINAL_TICK_GET() \
    open_cfw_cmsis_kernel_get_tick_count()
#endif
#ifndef OPEN_CFW_PB_TERMINAL_ROLE_GET
uint32_t open_cfw_lens_side(void);
#define OPEN_CFW_PB_TERMINAL_ROLE_GET() open_cfw_lens_side()
#endif
#ifndef OPEN_CFW_PB_TERMINAL_SEND
int open_cfw_ble_msgtx_pb_send(
    uint32_t route, uint32_t service, const void *data, uint32_t length);
#define OPEN_CFW_PB_TERMINAL_SEND(route, service, data, length) \
    open_cfw_ble_msgtx_pb_send((route), (service), (data), (length))
#endif
#ifndef OPEN_CFW_PB_TERMINAL_NOTIFY
int open_cfw_ble_msgtx_pb_notify(
    uint32_t route, uint32_t service, const void *data, uint32_t length);
#define OPEN_CFW_PB_TERMINAL_NOTIFY(route, service, data, length) \
    open_cfw_ble_msgtx_pb_notify((route), (service), (data), (length))
#endif

#if defined(OPEN_CFW_PB_TERMINAL_ENCODE_ONLY)
#define OPEN_CFW_PB_TERMINAL_INCLUDE_ENCODE 1
#elif defined(OPEN_CFW_PB_TERMINAL_RX_ONLY)
#define OPEN_CFW_PB_TERMINAL_INCLUDE_RX 1
#elif defined(OPEN_CFW_PB_TERMINAL_COMM_RESP_ONLY)
#define OPEN_CFW_PB_TERMINAL_INCLUDE_COMM_RESP 1
#elif defined(OPEN_CFW_PB_TERMINAL_STATUS_REPLY_ONLY)
#define OPEN_CFW_PB_TERMINAL_INCLUDE_STATUS_REPLY 1
#elif defined(OPEN_CFW_PB_TERMINAL_VOICE_INPUT_ONLY)
#define OPEN_CFW_PB_TERMINAL_INCLUDE_VOICE_INPUT 1
#elif defined(OPEN_CFW_PB_TERMINAL_QUERY_REPLY_ONLY)
#define OPEN_CFW_PB_TERMINAL_INCLUDE_QUERY_REPLY 1
#elif defined(OPEN_CFW_PB_TERMINAL_AGENT_INTERRUPT_ONLY)
#define OPEN_CFW_PB_TERMINAL_INCLUDE_AGENT_INTERRUPT 1
#elif defined(OPEN_CFW_PB_TERMINAL_SESSION_SWITCH_ONLY)
#define OPEN_CFW_PB_TERMINAL_INCLUDE_SESSION_SWITCH 1
#elif defined(OPEN_CFW_PB_TERMINAL_NEW_SESSION_ONLY)
#define OPEN_CFW_PB_TERMINAL_INCLUDE_NEW_SESSION 1
#elif defined(OPEN_CFW_PB_TERMINAL_NEW_SESSION_CANCEL_ONLY)
#define OPEN_CFW_PB_TERMINAL_INCLUDE_NEW_SESSION_CANCEL 1
#elif defined(OPEN_CFW_PB_TERMINAL_DISPLAY_STATE_ONLY)
#define OPEN_CFW_PB_TERMINAL_INCLUDE_DISPLAY_STATE 1
#elif defined(OPEN_CFW_PB_TERMINAL_LIST_FOCUS_ONLY)
#define OPEN_CFW_PB_TERMINAL_INCLUDE_LIST_FOCUS 1
#elif defined(OPEN_CFW_PB_TERMINAL_OVERLAY_FOCUS_ONLY)
#define OPEN_CFW_PB_TERMINAL_INCLUDE_OVERLAY_FOCUS 1
#elif defined(OPEN_CFW_PB_TERMINAL_BUFFER_WRITE_ONLY)
#define OPEN_CFW_PB_TERMINAL_INCLUDE_BUFFER_WRITE 1
#elif defined(OPEN_CFW_PB_TERMINAL_ZERO_ONLY)
#define OPEN_CFW_PB_TERMINAL_INCLUDE_ZERO 1
#else
#define OPEN_CFW_PB_TERMINAL_INCLUDE_ENCODE 1
#define OPEN_CFW_PB_TERMINAL_INCLUDE_RX 1
#define OPEN_CFW_PB_TERMINAL_INCLUDE_COMM_RESP 1
#define OPEN_CFW_PB_TERMINAL_INCLUDE_STATUS_REPLY 1
#define OPEN_CFW_PB_TERMINAL_INCLUDE_VOICE_INPUT 1
#define OPEN_CFW_PB_TERMINAL_INCLUDE_QUERY_REPLY 1
#define OPEN_CFW_PB_TERMINAL_INCLUDE_AGENT_INTERRUPT 1
#define OPEN_CFW_PB_TERMINAL_INCLUDE_SESSION_SWITCH 1
#define OPEN_CFW_PB_TERMINAL_INCLUDE_NEW_SESSION 1
#define OPEN_CFW_PB_TERMINAL_INCLUDE_NEW_SESSION_CANCEL 1
#define OPEN_CFW_PB_TERMINAL_INCLUDE_DISPLAY_STATE 1
#define OPEN_CFW_PB_TERMINAL_INCLUDE_LIST_FOCUS 1
#define OPEN_CFW_PB_TERMINAL_INCLUDE_OVERLAY_FOCUS 1
#define OPEN_CFW_PB_TERMINAL_INCLUDE_BUFFER_WRITE 1
#define OPEN_CFW_PB_TERMINAL_INCLUDE_ZERO 1
#endif

uint32_t open_cfw_pb_service_terminal_buffer_write(
    open_cfw_pb_terminal_output *output, const void *data, uint32_t length);
void open_cfw_pb_service_terminal_zero(void *data, uint32_t length);
uint32_t open_cfw_pb_terminal_encode_and_send(
    uint32_t command, uint32_t tag, const void *payload,
    uint32_t magic, uint32_t notify);

static __attribute__((always_inline, unused)) inline void
open_cfw_pb_terminal_store_u32(uint8_t *destination, uint32_t value)
{
    destination[0] = (uint8_t)value;
    destination[1] = (uint8_t)(value >> 8);
    destination[2] = (uint8_t)(value >> 16);
    destination[3] = (uint8_t)(value >> 24);
}

static __attribute__((always_inline, unused)) inline uint32_t
open_cfw_pb_terminal_load_u32(const uint8_t *source)
{
    return (uint32_t)source[0] |
        ((uint32_t)source[1] << 8) |
        ((uint32_t)source[2] << 16) |
        ((uint32_t)source[3] << 24);
}

static __attribute__((always_inline, unused)) inline uint32_t
open_cfw_pb_terminal_next_magic(void)
{
    return (uint8_t)(*OPEN_CFW_PB_TERMINAL_LAST_MAGIC + 1U);
}

#if defined(OPEN_CFW_PB_TERMINAL_INCLUDE_BUFFER_WRITE)
__attribute__((used, noinline))
uint32_t open_cfw_pb_service_terminal_buffer_write(
    open_cfw_pb_terminal_output *output, const void *raw_data, uint32_t length)
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

#if defined(OPEN_CFW_PB_TERMINAL_INCLUDE_ZERO)
__attribute__((used, noinline))
void open_cfw_pb_service_terminal_zero(void *raw_data, uint32_t length)
{
    uint8_t *data = (uint8_t *)raw_data;
    uint32_t index;
    for (index = 0U; index < length; ++index) {
        data[index] = 0U;
    }
}
#endif

#if defined(OPEN_CFW_PB_TERMINAL_INCLUDE_ENCODE)
__attribute__((used, noinline))
uint32_t open_cfw_pb_terminal_encode_and_send(
    uint32_t command, uint32_t tag, const void *raw_payload,
    uint32_t magic, uint32_t notify)
{
    const uint8_t *payload = (const uint8_t *)raw_payload;
    uint8_t *message = OPEN_CFW_PB_TERMINAL_MESSAGE;
    open_cfw_pb_terminal_output output;
    uint32_t payload_bytes;
    uint32_t index;

    open_cfw_pb_service_terminal_zero(message, 0x850U);
    message[0] = (uint8_t)command;
    message[1] = (uint8_t)magic;
    message[2] = (uint8_t)tag;
    message[3] = (uint8_t)(tag >> 8);
    switch (tag) {
    case 9U: payload_bytes = 2U; break;
    case 10U: payload_bytes = 1U; break;
    case 11U: payload_bytes = 8U; break;
    case 12U: payload_bytes = 1U; break;
    case 13U: payload_bytes = 1U; break;
    case 18U: payload_bytes = 8U; break;
    case 19U: payload_bytes = 4U; break;
    case 20U: payload_bytes = 12U; break;
    case 22U: payload_bytes = 1U; break;
    case 24U: payload_bytes = 4U; break;
    case 25U: payload_bytes = 8U; break;
    default: return 8U;
    }

    for (index = 0U; index < payload_bytes; ++index) {
        message[4U + index] = payload[index];
    }

    output.write = open_cfw_pb_service_terminal_buffer_write;
    output.context = OPEN_CFW_PB_TERMINAL_ENCODE_BUFFER;
    output.capacity = 0x878U;
    output.length = 0U;
    output.error = (const char *)0;
    if (OPEN_CFW_PB_TERMINAL_ENCODE(
            &output, OPEN_CFW_PB_TERMINAL_DESCRIPTOR, message) == 0U) {
        return 5U;
    }
    if (OPEN_CFW_PB_TERMINAL_ROLE_GET() == 1U) {
        if (notify == 0U) {
            (void)OPEN_CFW_PB_TERMINAL_SEND(
                1U, 0x30U, OPEN_CFW_PB_TERMINAL_ENCODE_BUFFER,
                (uint16_t)output.length);
        } else {
            (void)OPEN_CFW_PB_TERMINAL_NOTIFY(
                1U, 0x30U, OPEN_CFW_PB_TERMINAL_ENCODE_BUFFER,
                (uint16_t)output.length);
        }
    }
    return 0U;
}
#endif

#if defined(OPEN_CFW_PB_TERMINAL_INCLUDE_RX)
__attribute__((used, noinline))
uint32_t APP_PbTerminalRxFrameDataProcess(
    const void *data, uint32_t length, void *message)
{
    open_cfw_pb_terminal_input input;
    uint8_t *bytes = (uint8_t *)message;
    uint32_t now;
    uint32_t elapsed;
    if (data == (const void *)0 || message == (void *)0) {
        return 6U;
    }
    input = OPEN_CFW_PB_TERMINAL_INPUT_FROM_BUFFER(data, (uint16_t)length);
    if (OPEN_CFW_PB_TERMINAL_DECODE(
            &input, OPEN_CFW_PB_TERMINAL_DESCRIPTOR, message) == 0U) {
        return 5U;
    }
    now = OPEN_CFW_PB_TERMINAL_TICK_GET();
    elapsed = now - *OPEN_CFW_PB_TERMINAL_LAST_TICK;
    if (bytes[1] == *OPEN_CFW_PB_TERMINAL_LAST_MAGIC && elapsed < 3000U) {
        return 13U;
    }
    *OPEN_CFW_PB_TERMINAL_LAST_MAGIC = bytes[1];
    *OPEN_CFW_PB_TERMINAL_LAST_TICK = now;
    return 0U;
}
#endif

#if defined(OPEN_CFW_PB_TERMINAL_INCLUDE_COMM_RESP)
__attribute__((used, noinline))
uint32_t APP_PbTerminalTxEncodeCommResp(
    const void *response, uint32_t magic)
{
    if (response == (const void *)0) {
        return 6U;
    }
    return open_cfw_pb_terminal_encode_and_send(
        0xF0U, 13U, response, magic, 0U);
}
#endif

#if defined(OPEN_CFW_PB_TERMINAL_INCLUDE_STATUS_REPLY)
__attribute__((used, noinline))
uint32_t APP_PbTerminalTxEncodeStatusReply(const void *status)
{
    if (status == (const void *)0) {
        return 6U;
    }
    return open_cfw_pb_terminal_encode_and_send(
        0xA1U, 9U, status, open_cfw_pb_terminal_next_magic(), 1U);
}
#endif

#if defined(OPEN_CFW_PB_TERMINAL_INCLUDE_VOICE_INPUT)
__attribute__((used, noinline))
uint32_t APP_PbTerminalTxEncodeVoiceInput(const void *voice_input)
{
    if (voice_input == (const void *)0) {
        return 6U;
    }
    return open_cfw_pb_terminal_encode_and_send(
        0xA2U, 10U, voice_input, open_cfw_pb_terminal_next_magic(), 1U);
}
#endif

#if defined(OPEN_CFW_PB_TERMINAL_INCLUDE_QUERY_REPLY)
__attribute__((used, noinline))
uint32_t APP_PbTerminalTxEncodeQueryReply(const void *query_reply)
{
    if (query_reply == (const void *)0) {
        return 6U;
    }
    return open_cfw_pb_terminal_encode_and_send(
        0xA3U, 11U, query_reply, open_cfw_pb_terminal_next_magic(), 1U);
}
#endif

#if defined(OPEN_CFW_PB_TERMINAL_INCLUDE_AGENT_INTERRUPT)
__attribute__((used, noinline))
void APP_PbTerminalTxEncodeAgentInterrupt(void)
{
    uint8_t payload = 0U;
    (void)open_cfw_pb_terminal_encode_and_send(
        0xA4U, 12U, &payload, open_cfw_pb_terminal_next_magic(), 1U);
}
#endif

#if defined(OPEN_CFW_PB_TERMINAL_INCLUDE_SESSION_SWITCH)
__attribute__((used, noinline))
void APP_PbTerminalTxEncodeSessionSwitchRequest(
    uint32_t first, uint32_t second)
{
    uint8_t payload[8];
    open_cfw_pb_terminal_store_u32(payload, second);
    open_cfw_pb_terminal_store_u32(payload + 4U, first);
    (void)open_cfw_pb_terminal_encode_and_send(
        0xA5U, 18U, payload, open_cfw_pb_terminal_next_magic(), 1U);
}
#endif

#if defined(OPEN_CFW_PB_TERMINAL_INCLUDE_NEW_SESSION)
__attribute__((used, noinline))
void APP_PbTerminalTxEncodeNewSessionRequest(uint32_t session)
{
    uint8_t payload[4];
    open_cfw_pb_terminal_store_u32(payload, session);
    (void)open_cfw_pb_terminal_encode_and_send(
        0xA6U, 19U, payload, open_cfw_pb_terminal_next_magic(), 1U);
}
#endif

#if defined(OPEN_CFW_PB_TERMINAL_INCLUDE_NEW_SESSION_CANCEL)
__attribute__((used, noinline))
void APP_PbTerminalTxEncodeNewSessionCancel(void)
{
    uint8_t payload = 0U;
    (void)open_cfw_pb_terminal_encode_and_send(
        0xA8U, 22U, &payload, open_cfw_pb_terminal_next_magic(), 1U);
}
#endif

#if defined(OPEN_CFW_PB_TERMINAL_INCLUDE_DISPLAY_STATE)
__attribute__((used, noinline))
void APP_PbTerminalTxEncodeDisplayStateNotify(
    uint32_t state, uint32_t session, uint32_t overlay)
{
    uint8_t payload[12];
    open_cfw_pb_service_terminal_zero(payload, sizeof(payload));
    if ((uint8_t)state != 4U) {
        session = 0U;
        overlay = 0U;
    }
    payload[0] = (uint8_t)state;
    open_cfw_pb_terminal_store_u32(payload + 4U, session);
    payload[8] = (uint8_t)overlay;
    (void)open_cfw_pb_terminal_encode_and_send(
        0xA7U, 20U, payload, open_cfw_pb_terminal_next_magic(), 1U);
}
#endif

#if defined(OPEN_CFW_PB_TERMINAL_INCLUDE_LIST_FOCUS)
__attribute__((used, noinline))
void APP_PbTerminalTxEncodeListFocus(uint32_t focus)
{
    uint8_t payload[4];
    open_cfw_pb_terminal_store_u32(payload, focus);
    (void)open_cfw_pb_terminal_encode_and_send(
        0xA9U, 24U, payload, open_cfw_pb_terminal_next_magic(), 1U);
}
#endif

#if defined(OPEN_CFW_PB_TERMINAL_INCLUDE_OVERLAY_FOCUS)
__attribute__((used, noinline))
void APP_PbTerminalTxEncodeOverlayFocus(uint32_t focus, uint32_t session)
{
    uint8_t payload[8];
    open_cfw_pb_service_terminal_zero(payload, sizeof(payload));
    payload[0] = (uint8_t)focus;
    open_cfw_pb_terminal_store_u32(payload + 4U, session);
    (void)open_cfw_pb_terminal_encode_and_send(
        0xAAU, 25U, payload, open_cfw_pb_terminal_next_magic(), 1U);
}
#endif
