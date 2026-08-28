/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room implementation of the four linked G2
 * pb_service_glasses_case.c entries. Diagnostic-only logging and assertion
 * dispatch are intentionally omitted; the recovered message, nanopb, state,
 * sequence, and BLE transport contracts are preserved.
 */

#include <stdint.h>

typedef struct {
    void *callback;
    void *state;
    uint32_t bytes_left;
    const char *error;
} open_cfw_pb_case_input;

struct open_cfw_pb_case_output;
typedef uint32_t (*open_cfw_pb_case_write_fn)(
    struct open_cfw_pb_case_output *, const void *, uint32_t);
typedef struct open_cfw_pb_case_output {
    open_cfw_pb_case_write_fn write;
    void *context;
    uint32_t capacity;
    uint32_t length;
    const char *error;
} open_cfw_pb_case_output;

typedef struct {
    uint8_t battery;
    uint8_t charging;
    uint8_t lid;
    uint8_t glasses_present;
} open_cfw_pb_case_info;

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(open_cfw_pb_case_input) == 16U,
    "G2 nanopb input stream ABI changed");
_Static_assert(sizeof(open_cfw_pb_case_output) == 20U,
    "G2 nanopb output stream ABI changed");
#endif
_Static_assert(sizeof(open_cfw_pb_case_info) == 4U,
    "G2 glasses-case info ABI changed");

#ifndef OPEN_CFW_PB_CASE_MESSAGE_RX
#define OPEN_CFW_PB_CASE_MESSAGE_RX ((uint8_t *)(uintptr_t)0x200F5A90U)
#endif
#ifndef OPEN_CFW_PB_CASE_MESSAGE_TX
#define OPEN_CFW_PB_CASE_MESSAGE_TX ((uint8_t *)(uintptr_t)0x200F5A9CU)
#endif
#ifndef OPEN_CFW_PB_CASE_ENCODE_BUFFER
#define OPEN_CFW_PB_CASE_ENCODE_BUFFER ((uint8_t *)(uintptr_t)0x2037C5A0U)
#endif
#ifndef OPEN_CFW_PB_CASE_DESCRIPTOR
#define OPEN_CFW_PB_CASE_DESCRIPTOR ((const void *)(uintptr_t)0x0077793CU)
#endif
#ifndef OPEN_CFW_PB_CASE_NOTIFY_SEQUENCE
#define OPEN_CFW_PB_CASE_NOTIFY_SEQUENCE ((uint8_t *)(uintptr_t)0x20074FFAU)
#endif

#ifndef OPEN_CFW_PB_CASE_INPUT_FROM_BUFFER
open_cfw_pb_case_input open_cfw_nanopb_istream_from_buffer(
    const void *data, uint32_t length);
#define OPEN_CFW_PB_CASE_INPUT_FROM_BUFFER(data, length) \
    open_cfw_nanopb_istream_from_buffer((data), (length))
#endif
#ifndef OPEN_CFW_PB_CASE_DECODE
uint32_t open_cfw_nanopb_decode(
    open_cfw_pb_case_input *input, const void *descriptor, void *message);
#define OPEN_CFW_PB_CASE_DECODE(input, descriptor, message) \
    open_cfw_nanopb_decode((input), (descriptor), (message))
#endif
#ifndef OPEN_CFW_PB_CASE_ENCODE
uint32_t open_cfw_format_message_encode(
    void *output, const void *descriptor, const void *message);
#define OPEN_CFW_PB_CASE_ENCODE(output, descriptor, message) \
    open_cfw_format_message_encode((output), (descriptor), (message))
#endif
#ifndef OPEN_CFW_PB_CASE_SEND
int open_cfw_ble_msgtx_pb_send(
    uint32_t route, uint32_t service, const void *data, uint32_t length);
#define OPEN_CFW_PB_CASE_SEND(route, service, data, length) \
    open_cfw_ble_msgtx_pb_send((route), (service), (data), (length))
#endif
#ifndef OPEN_CFW_PB_CASE_NOTIFY
int open_cfw_ble_msgtx_pb_notify(
    uint32_t route, uint32_t service, const void *data, uint32_t length);
#define OPEN_CFW_PB_CASE_NOTIFY(route, service, data, length) \
    open_cfw_ble_msgtx_pb_notify((route), (service), (data), (length))
#endif
#ifndef OPEN_CFW_PB_CASE_BATTERY_GET
uint32_t open_cfw_glasses_case_battery_get(void);
#define OPEN_CFW_PB_CASE_BATTERY_GET() open_cfw_glasses_case_battery_get()
#endif
#ifndef OPEN_CFW_PB_CASE_CHARGING_GET
uint32_t open_cfw_glasses_case_charging_get(void);
#define OPEN_CFW_PB_CASE_CHARGING_GET() open_cfw_glasses_case_charging_get()
#endif
#ifndef OPEN_CFW_PB_CASE_LID_GET
uint32_t open_cfw_glasses_case_lid_get(void);
#define OPEN_CFW_PB_CASE_LID_GET() open_cfw_glasses_case_lid_get()
#endif
#ifndef OPEN_CFW_PB_CASE_PRESENT_GET
uint32_t open_cfw_glasses_case_present_get(void);
#define OPEN_CFW_PB_CASE_PRESENT_GET() open_cfw_glasses_case_present_get()
#endif

#if defined(OPEN_CFW_PB_CASE_RX_FRAME_ONLY)
#define OPEN_CFW_PB_CASE_INCLUDE_RX_FRAME 1
#elif defined(OPEN_CFW_PB_CASE_RX_INFO_ONLY)
#define OPEN_CFW_PB_CASE_INCLUDE_RX_INFO 1
#elif defined(OPEN_CFW_PB_CASE_TX_INFO_ONLY)
#define OPEN_CFW_PB_CASE_INCLUDE_TX_INFO 1
#elif defined(OPEN_CFW_PB_CASE_NOTIFY_INFO_ONLY)
#define OPEN_CFW_PB_CASE_INCLUDE_NOTIFY_INFO 1
#elif defined(OPEN_CFW_PB_CASE_BUFFER_WRITE_ONLY)
#define OPEN_CFW_PB_CASE_INCLUDE_BUFFER_WRITE 1
#else
#define OPEN_CFW_PB_CASE_INCLUDE_RX_FRAME 1
#define OPEN_CFW_PB_CASE_INCLUDE_RX_INFO 1
#define OPEN_CFW_PB_CASE_INCLUDE_TX_INFO 1
#define OPEN_CFW_PB_CASE_INCLUDE_NOTIFY_INFO 1
#define OPEN_CFW_PB_CASE_INCLUDE_BUFFER_WRITE 1
#endif

uint32_t open_cfw_pb_service_glasses_case_buffer_write(
    open_cfw_pb_case_output *output, const void *data, uint32_t length);
#if !defined(OPEN_CFW_PB_CASE_INCLUDE_RX_INFO)
uint32_t PB_RxGlassesCaseInfo(uint32_t sequence, const void *info);
#endif
#if !defined(OPEN_CFW_PB_CASE_INCLUDE_TX_INFO)
uint32_t APP_PbTxEncodeGlassesCaseInfo(uint32_t sequence, const void *info);
#endif

static __attribute__((always_inline, unused)) inline void open_cfw_pb_case_zero(
    uint8_t *data, uint32_t length)
{
    uint32_t index;
    for (index = 0U; index < length; ++index) {
        data[index] = 0U;
    }
}

static __attribute__((always_inline, unused)) inline void
open_cfw_pb_case_output_init(open_cfw_pb_case_output *output)
{
    output->write = open_cfw_pb_service_glasses_case_buffer_write;
    output->context = OPEN_CFW_PB_CASE_ENCODE_BUFFER;
    output->capacity = 0x100U;
    output->length = 0U;
    output->error = (const char *)0;
}

#if defined(OPEN_CFW_PB_CASE_INCLUDE_BUFFER_WRITE)
__attribute__((used, noinline))
uint32_t open_cfw_pb_service_glasses_case_buffer_write(
    open_cfw_pb_case_output *output, const void *raw_data, uint32_t length)
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

#if defined(OPEN_CFW_PB_CASE_INCLUDE_RX_INFO)
__attribute__((used, noinline))
uint32_t PB_RxGlassesCaseInfo(uint32_t sequence, const void *info)
{
    (void)sequence;
    return info == (const void *)0 ? 2U : 0U;
}
#endif

#if defined(OPEN_CFW_PB_CASE_INCLUDE_TX_INFO)
__attribute__((used, noinline))
uint32_t APP_PbTxEncodeGlassesCaseInfo(uint32_t sequence, const void *raw_info)
{
    uint8_t *message = OPEN_CFW_PB_CASE_MESSAGE_TX;
    open_cfw_pb_case_output output;
    if (raw_info == (const void *)0) {
        return 2U;
    }
    open_cfw_pb_case_output_init(&output);
    open_cfw_pb_case_zero(message, 10U);
    message[0] = 1U;
    message[1] = (uint8_t)sequence;
    message[2] = 3U;
    message[4] = (uint8_t)OPEN_CFW_PB_CASE_BATTERY_GET();
    message[5] = (uint8_t)OPEN_CFW_PB_CASE_CHARGING_GET();
    message[6] = (uint8_t)OPEN_CFW_PB_CASE_LID_GET();
    message[7] = OPEN_CFW_PB_CASE_PRESENT_GET() == 1U ? 1U : 0U;
    message[8] = 0U;
    if (OPEN_CFW_PB_CASE_ENCODE(
            &output, OPEN_CFW_PB_CASE_DESCRIPTOR, message) == 0U) {
        return 0x2BU;
    }
    (void)OPEN_CFW_PB_CASE_SEND(
        1U, 0x81U, OPEN_CFW_PB_CASE_ENCODE_BUFFER,
        (uint16_t)output.length);
    return 0U;
}
#endif

#if defined(OPEN_CFW_PB_CASE_INCLUDE_NOTIFY_INFO)
__attribute__((used, noinline))
uint32_t APP_PbNotifyEncodeGlassesCaseInfo(
    uint32_t event, const void *raw_info)
{
    const open_cfw_pb_case_info *info =
        (const open_cfw_pb_case_info *)raw_info;
    uint8_t *message = OPEN_CFW_PB_CASE_MESSAGE_TX;
    open_cfw_pb_case_output output;
    (void)event;
    if (info == (const open_cfw_pb_case_info *)0) {
        return 2U;
    }
    open_cfw_pb_case_output_init(&output);
    open_cfw_pb_case_zero(message, 10U);
    message[0] = 1U;
    message[1] = *OPEN_CFW_PB_CASE_NOTIFY_SEQUENCE;
    *OPEN_CFW_PB_CASE_NOTIFY_SEQUENCE =
        (uint8_t)(*OPEN_CFW_PB_CASE_NOTIFY_SEQUENCE + 1U);
    message[2] = 3U;
    message[4] = info->battery;
    message[5] = info->charging;
    message[6] = info->lid;
    message[7] = info->glasses_present;
    message[8] = 0U;
    if (OPEN_CFW_PB_CASE_ENCODE(
            &output, OPEN_CFW_PB_CASE_DESCRIPTOR, message) == 0U) {
        return 0x2BU;
    }
    (void)OPEN_CFW_PB_CASE_NOTIFY(
        1U, 0x81U, OPEN_CFW_PB_CASE_ENCODE_BUFFER,
        (uint16_t)output.length);
    return 0U;
}
#endif

#if defined(OPEN_CFW_PB_CASE_INCLUDE_RX_FRAME)
__attribute__((used, noinline))
uint32_t APP_PbRxGlassesCaseFrameDataProcess(
    const void *data, uint32_t length)
{
    uint8_t *message = OPEN_CFW_PB_CASE_MESSAGE_RX;
    open_cfw_pb_case_input input;
    uint32_t status;
    if (data == (const void *)0) {
        return 2U;
    }
    open_cfw_pb_case_zero(message, 10U);
    input = OPEN_CFW_PB_CASE_INPUT_FROM_BUFFER(data, (uint16_t)length);
    if (OPEN_CFW_PB_CASE_DECODE(
            &input, OPEN_CFW_PB_CASE_DESCRIPTOR, message) == 0U) {
        return 0x2BU;
    }
    if (message[0] != 1U) {
        return 1U;
    }
    status = PB_RxGlassesCaseInfo(message[1], message + 4U);
    if (status != 0U) {
        return 1U;
    }
    return APP_PbTxEncodeGlassesCaseInfo(message[1], message + 4U);
}
#endif
