/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room implementation of the 25 linked G2 pb_service_even_ai.c
 * entries. Diagnostic-only EasyLogger, assertion, and hexdump calls are
 * omitted; nanopb, duplicate filtering, dispatch, envelope, heartbeat, and
 * BLE transport behavior is preserved.
 */

#include <stdint.h>

typedef struct {
    void *callback;
    void *state;
    uint32_t bytes_left;
    const char *error;
} open_cfw_pb_even_ai_input;

struct open_cfw_pb_even_ai_output;
typedef uint32_t (*open_cfw_pb_even_ai_write_fn)(
    struct open_cfw_pb_even_ai_output *, const void *, uint32_t);
typedef struct open_cfw_pb_even_ai_output {
    open_cfw_pb_even_ai_write_fn write;
    void *context;
    uint32_t capacity;
    uint32_t length;
    const char *error;
} open_cfw_pb_even_ai_output;

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(open_cfw_pb_even_ai_input) == 16U,
    "G2 nanopb input stream ABI changed");
_Static_assert(sizeof(open_cfw_pb_even_ai_output) == 20U,
    "G2 nanopb output stream ABI changed");
#endif

#ifndef OPEN_CFW_PB_EVEN_AI_MESSAGE
#define OPEN_CFW_PB_EVEN_AI_MESSAGE \
    ((uint8_t *)(uintptr_t)0x200F5884U)
#endif
#ifndef OPEN_CFW_PB_EVEN_AI_ENCODE_BUFFER
#define OPEN_CFW_PB_EVEN_AI_ENCODE_BUFFER \
    ((uint8_t *)(uintptr_t)0x2037C4A0U)
#endif
#ifndef OPEN_CFW_PB_EVEN_AI_DESCRIPTOR
#define OPEN_CFW_PB_EVEN_AI_DESCRIPTOR \
    ((const void *)(uintptr_t)0x00777144U)
#endif
#ifndef OPEN_CFW_PB_EVEN_AI_DUPLICATE_STATE
#define OPEN_CFW_PB_EVEN_AI_DUPLICATE_STATE \
    ((uint8_t *)(uintptr_t)0x20074F36U)
#endif
#ifndef OPEN_CFW_PB_EVEN_AI_NOTIFY_MAGIC
#define OPEN_CFW_PB_EVEN_AI_NOTIFY_MAGIC \
    ((uint8_t *)(uintptr_t)0x20074FF9U)
#endif
#ifndef OPEN_CFW_PB_EVEN_AI_DUPLICATE_RESPONSE
#define OPEN_CFW_PB_EVEN_AI_DUPLICATE_RESPONSE 7U
#endif
#ifndef OPEN_CFW_PB_EVEN_AI_UNKNOWN_RESPONSE
#define OPEN_CFW_PB_EVEN_AI_UNKNOWN_RESPONSE 8U
#endif

#ifndef OPEN_CFW_PB_EVEN_AI_INPUT_FROM_BUFFER
open_cfw_pb_even_ai_input open_cfw_nanopb_istream_from_buffer(
    const void *data, uint32_t length);
#define OPEN_CFW_PB_EVEN_AI_INPUT_FROM_BUFFER(data, length) \
    open_cfw_nanopb_istream_from_buffer((data), (length))
#endif
#ifndef OPEN_CFW_PB_EVEN_AI_DECODE
uint32_t open_cfw_nanopb_decode(
    open_cfw_pb_even_ai_input *input, const void *descriptor, void *message);
#define OPEN_CFW_PB_EVEN_AI_DECODE(input, descriptor, message) \
    open_cfw_nanopb_decode((input), (descriptor), (message))
#endif
#ifndef OPEN_CFW_PB_EVEN_AI_ENCODE
uint32_t open_cfw_format_message_encode(
    void *output, const void *descriptor, const void *message);
#define OPEN_CFW_PB_EVEN_AI_ENCODE(output, descriptor, message) \
    open_cfw_format_message_encode((output), (descriptor), (message))
#endif
#ifndef OPEN_CFW_PB_EVEN_AI_RX_DISPATCH
int open_cfw_even_ai_rx_dispatch(
    uint32_t command, const void *payload, uint32_t length);
#define OPEN_CFW_PB_EVEN_AI_RX_DISPATCH(command, payload, length) \
    open_cfw_even_ai_rx_dispatch((command), (payload), (length))
#endif
#ifndef OPEN_CFW_PB_EVEN_AI_ROLE_GET
uint32_t open_cfw_lens_side(void);
#define OPEN_CFW_PB_EVEN_AI_ROLE_GET() open_cfw_lens_side()
#endif
#ifndef OPEN_CFW_PB_EVEN_AI_DISPLAY_READY
uint32_t open_cfw_display_ready(uint32_t selector);
#define OPEN_CFW_PB_EVEN_AI_DISPLAY_READY(selector) \
    open_cfw_display_ready((selector))
#endif
#ifndef OPEN_CFW_PB_EVEN_AI_SEND
int open_cfw_ble_msgtx_pb_send(
    uint32_t route, uint32_t service, const void *data, uint32_t length);
#define OPEN_CFW_PB_EVEN_AI_SEND(route, service, data, length) \
    open_cfw_ble_msgtx_pb_send((route), (service), (data), (length))
#endif
#ifndef OPEN_CFW_PB_EVEN_AI_NOTIFY
int open_cfw_ble_msgtx_pb_notify(
    uint32_t route, uint32_t service, const void *data, uint32_t length);
#define OPEN_CFW_PB_EVEN_AI_NOTIFY(route, service, data, length) \
    open_cfw_ble_msgtx_pb_notify((route), (service), (data), (length))
#endif

uint32_t open_cfw_pb_service_even_ai_buffer_write(
    open_cfw_pb_even_ai_output *output, const void *data, uint32_t length);
void open_cfw_pb_service_even_ai_zero(void *data, uint32_t length);

uint32_t PB_RxEvenAICtrl(uint32_t magic, const void *payload);
uint32_t APP_PbTxEncodeEvenAICtrl(uint32_t magic, const void *payload);
uint32_t PB_RxEvenAIVADInfo(uint32_t magic, const void *payload);
uint32_t APP_PbTxEncodeEvenAIVADInfo(uint32_t magic, const void *payload);
uint32_t PB_RxEvenAIAskInfo(uint32_t magic, const void *payload);
uint32_t APP_PbTxEncodeEvenAIAskInfo(uint32_t magic, const void *payload);
uint32_t PB_RxEvenAIAnalyseInfo(uint32_t magic, const void *payload);
uint32_t APP_PbTxEncodeEvenAIAnalyseInfo(uint32_t magic, const void *payload);
uint32_t PB_RxEvenAIReplyInfo(uint32_t magic, const void *payload);
uint32_t APP_PbTxEncodeEvenAIReplyInfo(uint32_t magic, const void *payload);
uint32_t PB_RxEvenAISkillInfo(uint32_t magic, const void *payload);
uint32_t APP_PbTxEncodeEvenAISkillInfo(uint32_t magic, const void *payload);
uint32_t PB_RxEvenAIPromptInfo(uint32_t magic, const void *payload);
uint32_t APP_PbTxEncodeEvenAIPromptInfo(uint32_t magic, const void *payload);
uint32_t PB_RxEvenAIEvent(uint32_t magic, const void *payload);
uint32_t APP_PbTxEncodeEvenAIEvent(uint32_t magic, const void *payload);
uint32_t PB_RxEvenAIHeartbeat(uint32_t magic, const void *payload);
uint32_t APP_PbTxEncodeEvenAIHeartbeat(uint32_t magic, const void *payload);
uint32_t PB_RxEvenAIConfig(uint32_t magic, const void *payload);
uint32_t APP_PbTxEncodeEvenAIConfig(uint32_t magic, const void *payload);
uint32_t APP_PbTxEncodeEvenAICommResp(uint32_t magic, const void *payload);

#if defined(OPEN_CFW_PB_EVEN_AI_RX_FRAME_ONLY)
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_RX_FRAME 1
#elif defined(OPEN_CFW_PB_EVEN_AI_RX_CTRL_ONLY)
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_RX_CTRL 1
#elif defined(OPEN_CFW_PB_EVEN_AI_TX_CTRL_ONLY)
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_TX_CTRL 1
#elif defined(OPEN_CFW_PB_EVEN_AI_NOTIFY_CTRL_ONLY)
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_NOTIFY_CTRL 1
#elif defined(OPEN_CFW_PB_EVEN_AI_RX_VAD_ONLY)
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_RX_VAD 1
#elif defined(OPEN_CFW_PB_EVEN_AI_TX_VAD_ONLY)
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_TX_VAD 1
#elif defined(OPEN_CFW_PB_EVEN_AI_NOTIFY_VAD_ONLY)
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_NOTIFY_VAD 1
#elif defined(OPEN_CFW_PB_EVEN_AI_RX_ASK_ONLY)
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_RX_ASK 1
#elif defined(OPEN_CFW_PB_EVEN_AI_TX_ASK_ONLY)
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_TX_ASK 1
#elif defined(OPEN_CFW_PB_EVEN_AI_RX_ANALYSE_ONLY)
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_RX_ANALYSE 1
#elif defined(OPEN_CFW_PB_EVEN_AI_TX_ANALYSE_ONLY)
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_TX_ANALYSE 1
#elif defined(OPEN_CFW_PB_EVEN_AI_RX_REPLY_ONLY)
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_RX_REPLY 1
#elif defined(OPEN_CFW_PB_EVEN_AI_TX_REPLY_ONLY)
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_TX_REPLY 1
#elif defined(OPEN_CFW_PB_EVEN_AI_RX_SKILL_ONLY)
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_RX_SKILL 1
#elif defined(OPEN_CFW_PB_EVEN_AI_TX_SKILL_ONLY)
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_TX_SKILL 1
#elif defined(OPEN_CFW_PB_EVEN_AI_RX_PROMPT_ONLY)
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_RX_PROMPT 1
#elif defined(OPEN_CFW_PB_EVEN_AI_TX_PROMPT_ONLY)
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_TX_PROMPT 1
#elif defined(OPEN_CFW_PB_EVEN_AI_RX_EVENT_ONLY)
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_RX_EVENT 1
#elif defined(OPEN_CFW_PB_EVEN_AI_TX_EVENT_ONLY)
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_TX_EVENT 1
#elif defined(OPEN_CFW_PB_EVEN_AI_NOTIFY_EVENT_ONLY)
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_NOTIFY_EVENT 1
#elif defined(OPEN_CFW_PB_EVEN_AI_RX_HEARTBEAT_ONLY)
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_RX_HEARTBEAT 1
#elif defined(OPEN_CFW_PB_EVEN_AI_TX_HEARTBEAT_ONLY)
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_TX_HEARTBEAT 1
#elif defined(OPEN_CFW_PB_EVEN_AI_RX_CONFIG_ONLY)
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_RX_CONFIG 1
#elif defined(OPEN_CFW_PB_EVEN_AI_TX_CONFIG_ONLY)
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_TX_CONFIG 1
#elif defined(OPEN_CFW_PB_EVEN_AI_COMM_RESP_ONLY)
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_COMM_RESP 1
#elif defined(OPEN_CFW_PB_EVEN_AI_BUFFER_WRITE_ONLY)
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_BUFFER_WRITE 1
#elif defined(OPEN_CFW_PB_EVEN_AI_ZERO_ONLY)
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_ZERO 1
#else
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_RX_FRAME 1
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_RX_CTRL 1
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_TX_CTRL 1
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_NOTIFY_CTRL 1
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_RX_VAD 1
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_TX_VAD 1
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_NOTIFY_VAD 1
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_RX_ASK 1
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_TX_ASK 1
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_RX_ANALYSE 1
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_TX_ANALYSE 1
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_RX_REPLY 1
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_TX_REPLY 1
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_RX_SKILL 1
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_TX_SKILL 1
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_RX_PROMPT 1
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_TX_PROMPT 1
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_RX_EVENT 1
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_TX_EVENT 1
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_NOTIFY_EVENT 1
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_RX_HEARTBEAT 1
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_TX_HEARTBEAT 1
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_RX_CONFIG 1
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_TX_CONFIG 1
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_COMM_RESP 1
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_BUFFER_WRITE 1
#define OPEN_CFW_PB_EVEN_AI_INCLUDE_ZERO 1
#endif

static __attribute__((always_inline, unused)) inline void
open_cfw_pb_even_ai_output_init(open_cfw_pb_even_ai_output *output)
{
    output->write = open_cfw_pb_service_even_ai_buffer_write;
    output->context = OPEN_CFW_PB_EVEN_AI_ENCODE_BUFFER;
    output->capacity = 0x100U;
    output->length = 0U;
    output->error = (const char *)0;
}

static __attribute__((always_inline, unused)) inline void
open_cfw_pb_even_ai_store_tag(uint8_t *message, uint16_t tag)
{
    message[2] = (uint8_t)tag;
    message[3] = (uint8_t)(tag >> 8);
}

static __attribute__((always_inline, unused)) inline uint32_t
open_cfw_pb_even_ai_finish(uint32_t notify)
{
    open_cfw_pb_even_ai_output output;
    open_cfw_pb_even_ai_output_init(&output);
    if (OPEN_CFW_PB_EVEN_AI_ENCODE(
            &output, OPEN_CFW_PB_EVEN_AI_DESCRIPTOR,
            OPEN_CFW_PB_EVEN_AI_MESSAGE) == 0U) {
        return 0x2BU;
    }
    if (notify != 0U) {
        (void)OPEN_CFW_PB_EVEN_AI_NOTIFY(
            1U, 7U, OPEN_CFW_PB_EVEN_AI_ENCODE_BUFFER,
            (uint16_t)output.length);
    } else {
        (void)OPEN_CFW_PB_EVEN_AI_SEND(
            1U, 7U, OPEN_CFW_PB_EVEN_AI_ENCODE_BUFFER,
            (uint16_t)output.length);
    }
    return 0U;
}

static __attribute__((always_inline, unused)) inline uint32_t
open_cfw_pb_even_ai_receive(
    uint32_t command, const void *payload, uint32_t length)
{
    if (payload == (const void *)0) {
        return 2U;
    }
    return OPEN_CFW_PB_EVEN_AI_RX_DISPATCH(command, payload, length) == 0
        ? 0U : 1U;
}

#if defined(OPEN_CFW_PB_EVEN_AI_INCLUDE_BUFFER_WRITE)
__attribute__((used, noinline))
uint32_t open_cfw_pb_service_even_ai_buffer_write(
    open_cfw_pb_even_ai_output *output, const void *raw_data, uint32_t length)
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

#if defined(OPEN_CFW_PB_EVEN_AI_INCLUDE_ZERO)
__attribute__((used, noinline))
void open_cfw_pb_service_even_ai_zero(void *raw_data, uint32_t length)
{
    uint8_t *data = (uint8_t *)raw_data;
    uint32_t index;
    for (index = 0U; index < length; ++index) {
        data[index] = 0U;
    }
}
#endif

#define OPEN_CFW_PB_EVEN_AI_RX_FUNCTION(name, command, length) \
    __attribute__((used, noinline)) \
    uint32_t name(uint32_t magic, const void *payload) \
    { \
        (void)magic; \
        return open_cfw_pb_even_ai_receive((command), (payload), (length)); \
    }

#if defined(OPEN_CFW_PB_EVEN_AI_INCLUDE_RX_CTRL)
OPEN_CFW_PB_EVEN_AI_RX_FUNCTION(PB_RxEvenAICtrl, 1U, 2U)
#endif
#if defined(OPEN_CFW_PB_EVEN_AI_INCLUDE_RX_VAD)
OPEN_CFW_PB_EVEN_AI_RX_FUNCTION(PB_RxEvenAIVADInfo, 2U, 2U)
#endif
#if defined(OPEN_CFW_PB_EVEN_AI_INCLUDE_RX_ASK)
OPEN_CFW_PB_EVEN_AI_RX_FUNCTION(PB_RxEvenAIAskInfo, 3U, 0x208U)
#endif
#if defined(OPEN_CFW_PB_EVEN_AI_INCLUDE_RX_ANALYSE)
OPEN_CFW_PB_EVEN_AI_RX_FUNCTION(PB_RxEvenAIAnalyseInfo, 4U, 1U)
#endif
#if defined(OPEN_CFW_PB_EVEN_AI_INCLUDE_RX_REPLY)
OPEN_CFW_PB_EVEN_AI_RX_FUNCTION(PB_RxEvenAIReplyInfo, 5U, 0x208U)
#endif
#if defined(OPEN_CFW_PB_EVEN_AI_INCLUDE_RX_SKILL)
OPEN_CFW_PB_EVEN_AI_RX_FUNCTION(PB_RxEvenAISkillInfo, 6U, 0x10CU)
#endif
#if defined(OPEN_CFW_PB_EVEN_AI_INCLUDE_RX_PROMPT)
OPEN_CFW_PB_EVEN_AI_RX_FUNCTION(PB_RxEvenAIPromptInfo, 7U, 2U)
#endif
#if defined(OPEN_CFW_PB_EVEN_AI_INCLUDE_RX_EVENT)
OPEN_CFW_PB_EVEN_AI_RX_FUNCTION(PB_RxEvenAIEvent, 8U, 2U)
#endif
#if defined(OPEN_CFW_PB_EVEN_AI_INCLUDE_RX_HEARTBEAT)
OPEN_CFW_PB_EVEN_AI_RX_FUNCTION(PB_RxEvenAIHeartbeat, 9U, 2U)
#endif
#if defined(OPEN_CFW_PB_EVEN_AI_INCLUDE_RX_CONFIG)
OPEN_CFW_PB_EVEN_AI_RX_FUNCTION(PB_RxEvenAIConfig, 10U, 4U)
#endif

static __attribute__((always_inline, unused)) inline uint32_t
open_cfw_pb_even_ai_prepare(
    uint32_t command, uint32_t magic, uint32_t tag, const void *payload)
{
    if (payload == (const void *)0) {
        return 2U;
    }
    open_cfw_pb_service_even_ai_zero(OPEN_CFW_PB_EVEN_AI_MESSAGE, 0x20CU);
    OPEN_CFW_PB_EVEN_AI_MESSAGE[0] = (uint8_t)command;
    OPEN_CFW_PB_EVEN_AI_MESSAGE[1] = (uint8_t)magic;
    open_cfw_pb_even_ai_store_tag(OPEN_CFW_PB_EVEN_AI_MESSAGE, (uint16_t)tag);
    return 0U;
}

#if defined(OPEN_CFW_PB_EVEN_AI_INCLUDE_TX_CTRL)
__attribute__((used, noinline))
uint32_t APP_PbTxEncodeEvenAICtrl(uint32_t magic, const void *raw_payload)
{
    const uint8_t *payload = (const uint8_t *)raw_payload;
    uint32_t status = open_cfw_pb_even_ai_prepare(1U, magic, 3U, payload);
    if (status != 0U) return status;
    OPEN_CFW_PB_EVEN_AI_MESSAGE[4] = payload[0];
    return open_cfw_pb_even_ai_finish(0U);
}
#endif

#if defined(OPEN_CFW_PB_EVEN_AI_INCLUDE_NOTIFY_CTRL)
__attribute__((used, noinline))
uint32_t APP_PbNotifyEncodeEvenAICtrl(
    uint32_t unused, const void *raw_payload)
{
    const uint8_t *payload = (const uint8_t *)raw_payload;
    uint8_t magic = *OPEN_CFW_PB_EVEN_AI_NOTIFY_MAGIC;
    uint32_t status;
    (void)unused;
    status = open_cfw_pb_even_ai_prepare(1U, magic, 3U, payload);
    if (status != 0U) return status;
    *OPEN_CFW_PB_EVEN_AI_NOTIFY_MAGIC = (uint8_t)(magic + 1U);
    OPEN_CFW_PB_EVEN_AI_MESSAGE[4] = payload[0];
    return open_cfw_pb_even_ai_finish(1U);
}
#endif

#if defined(OPEN_CFW_PB_EVEN_AI_INCLUDE_TX_VAD)
__attribute__((used, noinline))
uint32_t APP_PbTxEncodeEvenAIVADInfo(uint32_t magic, const void *raw_payload)
{
    const uint8_t *payload = (const uint8_t *)raw_payload;
    uint32_t status = open_cfw_pb_even_ai_prepare(2U, magic, 4U, payload);
    if (status != 0U) return status;
    OPEN_CFW_PB_EVEN_AI_MESSAGE[4] = payload[0];
    return open_cfw_pb_even_ai_finish(0U);
}
#endif

#if defined(OPEN_CFW_PB_EVEN_AI_INCLUDE_NOTIFY_VAD)
__attribute__((used, noinline))
uint32_t APP_PbNotifyEncodeEvenAIVADInfo(
    uint32_t unused, const void *raw_payload)
{
    const uint8_t *payload = (const uint8_t *)raw_payload;
    uint8_t magic = *OPEN_CFW_PB_EVEN_AI_NOTIFY_MAGIC;
    uint32_t status;
    (void)unused;
    status = open_cfw_pb_even_ai_prepare(2U, magic, 4U, payload);
    if (status != 0U) return status;
    *OPEN_CFW_PB_EVEN_AI_NOTIFY_MAGIC = (uint8_t)(magic + 1U);
    OPEN_CFW_PB_EVEN_AI_MESSAGE[4] = payload[0];
    return open_cfw_pb_even_ai_finish(1U);
}
#endif

#if defined(OPEN_CFW_PB_EVEN_AI_INCLUDE_TX_ASK)
__attribute__((used, noinline))
uint32_t APP_PbTxEncodeEvenAIAskInfo(uint32_t magic, const void *raw_payload)
{
    const uint8_t *payload = (const uint8_t *)raw_payload;
    uint32_t status = open_cfw_pb_even_ai_prepare(3U, magic, 5U, payload);
    if (status != 0U) return status;
    OPEN_CFW_PB_EVEN_AI_MESSAGE[4] = payload[0];
    return open_cfw_pb_even_ai_finish(0U);
}
#endif

#if defined(OPEN_CFW_PB_EVEN_AI_INCLUDE_TX_ANALYSE)
__attribute__((used, noinline))
uint32_t APP_PbTxEncodeEvenAIAnalyseInfo(uint32_t magic, const void *payload)
{
    uint32_t status = open_cfw_pb_even_ai_prepare(4U, magic, 6U, payload);
    if (status != 0U) return status;
    return open_cfw_pb_even_ai_finish(0U);
}
#endif

#if defined(OPEN_CFW_PB_EVEN_AI_INCLUDE_TX_REPLY)
__attribute__((used, noinline))
uint32_t APP_PbTxEncodeEvenAIReplyInfo(uint32_t magic, const void *raw_payload)
{
    const uint8_t *payload = (const uint8_t *)raw_payload;
    uint32_t status = open_cfw_pb_even_ai_prepare(5U, magic, 7U, payload);
    if (status != 0U) return status;
    OPEN_CFW_PB_EVEN_AI_MESSAGE[4] = payload[0];
    return open_cfw_pb_even_ai_finish(0U);
}
#endif

#if defined(OPEN_CFW_PB_EVEN_AI_INCLUDE_TX_SKILL)
__attribute__((used, noinline))
uint32_t APP_PbTxEncodeEvenAISkillInfo(uint32_t magic, const void *raw_payload)
{
    const uint8_t *payload = (const uint8_t *)raw_payload;
    uint32_t status = open_cfw_pb_even_ai_prepare(6U, magic, 8U, payload);
    if (status != 0U) return status;
    OPEN_CFW_PB_EVEN_AI_MESSAGE[5] = payload[1];
    return open_cfw_pb_even_ai_finish(0U);
}
#endif

#if defined(OPEN_CFW_PB_EVEN_AI_INCLUDE_TX_PROMPT)
__attribute__((used, noinline))
uint32_t APP_PbTxEncodeEvenAIPromptInfo(uint32_t magic, const void *raw_payload)
{
    const uint8_t *payload = (const uint8_t *)raw_payload;
    uint32_t status = open_cfw_pb_even_ai_prepare(7U, magic, 9U, payload);
    if (status != 0U) return status;
    OPEN_CFW_PB_EVEN_AI_MESSAGE[4] = payload[0];
    return open_cfw_pb_even_ai_finish(0U);
}
#endif

#if defined(OPEN_CFW_PB_EVEN_AI_INCLUDE_TX_EVENT)
__attribute__((used, noinline))
uint32_t APP_PbTxEncodeEvenAIEvent(uint32_t magic, const void *raw_payload)
{
    const uint8_t *payload = (const uint8_t *)raw_payload;
    uint32_t status = open_cfw_pb_even_ai_prepare(8U, magic, 10U, payload);
    if (status != 0U) return status;
    OPEN_CFW_PB_EVEN_AI_MESSAGE[4] = payload[0];
    return open_cfw_pb_even_ai_finish(0U);
}
#endif

#if defined(OPEN_CFW_PB_EVEN_AI_INCLUDE_NOTIFY_EVENT)
__attribute__((used, noinline))
uint32_t APP_PbNotifyEncodeEvenAIEvent(
    uint32_t unused, const void *raw_payload)
{
    const uint8_t *payload = (const uint8_t *)raw_payload;
    uint8_t magic = *OPEN_CFW_PB_EVEN_AI_NOTIFY_MAGIC;
    uint32_t status;
    (void)unused;
    status = open_cfw_pb_even_ai_prepare(8U, magic, 10U, payload);
    if (status != 0U) return status;
    *OPEN_CFW_PB_EVEN_AI_NOTIFY_MAGIC = (uint8_t)(magic + 1U);
    OPEN_CFW_PB_EVEN_AI_MESSAGE[4] = payload[0];
    return open_cfw_pb_even_ai_finish(1U);
}
#endif

#if defined(OPEN_CFW_PB_EVEN_AI_INCLUDE_TX_HEARTBEAT)
__attribute__((used, noinline))
uint32_t APP_PbTxEncodeEvenAIHeartbeat(
    uint32_t magic, const void *raw_payload)
{
    const uint8_t *payload = (const uint8_t *)raw_payload;
    uint32_t status = open_cfw_pb_even_ai_prepare(9U, magic, 11U, payload);
    if (status != 0U) return status;
    OPEN_CFW_PB_EVEN_AI_MESSAGE[4] = payload[0];
    OPEN_CFW_PB_EVEN_AI_MESSAGE[5] =
        OPEN_CFW_PB_EVEN_AI_ROLE_GET() == 1U &&
        OPEN_CFW_PB_EVEN_AI_DISPLAY_READY(7U) == 1U ? 0U : 8U;
    return open_cfw_pb_even_ai_finish(0U);
}
#endif

#if defined(OPEN_CFW_PB_EVEN_AI_INCLUDE_TX_CONFIG)
__attribute__((used, noinline))
uint32_t APP_PbTxEncodeEvenAIConfig(uint32_t magic, const void *raw_payload)
{
    const uint8_t *payload = (const uint8_t *)raw_payload;
    uint32_t status = open_cfw_pb_even_ai_prepare(10U, magic, 13U, payload);
    if (status != 0U) return status;
    OPEN_CFW_PB_EVEN_AI_MESSAGE[4] = payload[0];
    OPEN_CFW_PB_EVEN_AI_MESSAGE[5] = payload[1];
    OPEN_CFW_PB_EVEN_AI_MESSAGE[7] = payload[3];
    return open_cfw_pb_even_ai_finish(0U);
}
#endif

#if defined(OPEN_CFW_PB_EVEN_AI_INCLUDE_COMM_RESP)
__attribute__((used, noinline))
uint32_t APP_PbTxEncodeEvenAICommResp(
    uint32_t magic, const void *raw_payload)
{
    const uint8_t *payload = (const uint8_t *)raw_payload;
    open_cfw_pb_service_even_ai_zero(OPEN_CFW_PB_EVEN_AI_MESSAGE, 0x20CU);
    OPEN_CFW_PB_EVEN_AI_MESSAGE[0] = 0xA1U;
    OPEN_CFW_PB_EVEN_AI_MESSAGE[1] = (uint8_t)magic;
    open_cfw_pb_even_ai_store_tag(OPEN_CFW_PB_EVEN_AI_MESSAGE, 12U);
    OPEN_CFW_PB_EVEN_AI_MESSAGE[4] = payload[0];
    return open_cfw_pb_even_ai_finish(0U);
}
#endif

#if defined(OPEN_CFW_PB_EVEN_AI_INCLUDE_RX_FRAME)
__attribute__((used, noinline))
uint32_t APP_PbRxEvenAIFrameDataProcess(const void *data, uint32_t length)
{
    open_cfw_pb_even_ai_input input;
    uint8_t message[0x20CU];
    uint8_t response;
    uint32_t status;
    uint32_t magic;
    if (data == (const void *)0) {
        return 2U;
    }
    open_cfw_pb_service_even_ai_zero(message, sizeof(message));
    input = OPEN_CFW_PB_EVEN_AI_INPUT_FROM_BUFFER(data, (uint16_t)length);
    if (OPEN_CFW_PB_EVEN_AI_DECODE(
            &input, OPEN_CFW_PB_EVEN_AI_DESCRIPTOR, message) == 0U) {
        return 0x2BU;
    }
    magic = message[1];
    if (OPEN_CFW_PB_EVEN_AI_DUPLICATE_STATE[0] == 1U &&
        OPEN_CFW_PB_EVEN_AI_DUPLICATE_STATE[1] == (uint8_t)magic) {
        response = OPEN_CFW_PB_EVEN_AI_DUPLICATE_RESPONSE;
        (void)APP_PbTxEncodeEvenAICommResp(magic, &response);
        return 1U;
    }
    OPEN_CFW_PB_EVEN_AI_DUPLICATE_STATE[0] = 1U;
    OPEN_CFW_PB_EVEN_AI_DUPLICATE_STATE[1] = (uint8_t)magic;
    switch (message[0]) {
    case 1U:
        status = PB_RxEvenAICtrl(magic, message + 4U);
        if (status != 0U) return 1U;
        return APP_PbTxEncodeEvenAICtrl(magic, message + 4U);
    case 2U:
        status = PB_RxEvenAIVADInfo(magic, message + 4U);
        if (status != 0U) return 1U;
        return APP_PbTxEncodeEvenAIVADInfo(magic, message + 4U);
    case 3U:
        status = PB_RxEvenAIAskInfo(magic, message + 4U);
        if (status != 0U) return 1U;
        return APP_PbTxEncodeEvenAIAskInfo(magic, message + 4U);
    case 4U:
        status = PB_RxEvenAIAnalyseInfo(magic, message + 4U);
        if (status != 0U) return 1U;
        return APP_PbTxEncodeEvenAIAnalyseInfo(magic, message + 4U);
    case 5U:
        status = PB_RxEvenAIReplyInfo(magic, message + 4U);
        if (status != 0U) return 1U;
        return APP_PbTxEncodeEvenAIReplyInfo(magic, message + 4U);
    case 6U:
        status = PB_RxEvenAISkillInfo(magic, message + 4U);
        if (status != 0U) return 1U;
        return APP_PbTxEncodeEvenAISkillInfo(magic, message + 4U);
    case 7U:
        status = PB_RxEvenAIPromptInfo(magic, message + 4U);
        if (status != 0U) return 1U;
        return APP_PbTxEncodeEvenAIPromptInfo(magic, message + 4U);
    case 8U:
        status = PB_RxEvenAIEvent(magic, message + 4U);
        if (status != 0U) return 1U;
        return APP_PbTxEncodeEvenAIEvent(magic, message + 4U);
    case 9U:
        status = PB_RxEvenAIHeartbeat(magic, message + 4U);
        if (status != 0U) return 1U;
        return APP_PbTxEncodeEvenAIHeartbeat(magic, message + 4U);
    case 10U:
        status = PB_RxEvenAIConfig(magic, message + 4U);
        if (status != 0U) return 1U;
        return APP_PbTxEncodeEvenAIConfig(magic, message + 4U);
    default:
        response = OPEN_CFW_PB_EVEN_AI_UNKNOWN_RESPONSE;
        return APP_PbTxEncodeEvenAICommResp(magic, &response);
    }
}
#endif
