/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room production implementation of the eight linked G2
 * pb_service_health.c entries. Diagnostic-only logging and assertions are
 * deliberately omitted; the message, nanopb descriptor, and transport ABIs
 * are retained and fail-closed host contracts cover the observable policy.
 */

typedef unsigned char open_cfw_pb_health_u8;
typedef unsigned short open_cfw_pb_health_u16;
typedef unsigned int open_cfw_pb_health_u32;

struct open_cfw_pb_health_output;
typedef unsigned int (*open_cfw_pb_health_write_fn)(
    struct open_cfw_pb_health_output *, const void *, unsigned int);

struct open_cfw_pb_health_output {
    open_cfw_pb_health_write_fn write;
    void *context;
    unsigned int capacity;
    unsigned int length;
    const char *error;
};

unsigned int open_cfw_format_message_encode(
    void *output, const void *descriptor, const void *source);
int open_cfw_ble_msgtx_pb_send(
    unsigned int route, unsigned int service,
    const void *payload, unsigned int length);
int open_cfw_health_data_save_single(const void *input);
int open_cfw_health_data_save_multiple(const void *input);
int open_cfw_health_data_save_single_highlight(const void *input);
int open_cfw_health_data_save_multiple_highlights(const void *input);

#ifndef OPEN_CFW_PB_HEALTH_MESSAGE
#define OPEN_CFW_PB_HEALTH_MESSAGE \
    ((open_cfw_pb_health_u8 *)0x200F5DC4U)
#endif
#ifndef OPEN_CFW_PB_HEALTH_BUFFER
#define OPEN_CFW_PB_HEALTH_BUFFER \
    ((open_cfw_pb_health_u8 *)0x2037C6A0U)
#endif
#ifndef OPEN_CFW_PB_HEALTH_DESCRIPTOR
#define OPEN_CFW_PB_HEALTH_DESCRIPTOR ((const void *)0x00777A14U)
#endif
#ifndef OPEN_CFW_PB_HEALTH_ENCODE
#define OPEN_CFW_PB_HEALTH_ENCODE(output, descriptor, source) \
    open_cfw_format_message_encode((output), (descriptor), (source))
#endif
#ifndef OPEN_CFW_PB_HEALTH_SEND
#define OPEN_CFW_PB_HEALTH_SEND(route, service, payload, length) \
    open_cfw_ble_msgtx_pb_send((route), (service), (payload), (length))
#endif
#ifndef OPEN_CFW_PB_HEALTH_SAVE_SINGLE
#define OPEN_CFW_PB_HEALTH_SAVE_SINGLE(input) \
    open_cfw_health_data_save_single((input))
#endif
#ifndef OPEN_CFW_PB_HEALTH_SAVE_MULTIPLE
#define OPEN_CFW_PB_HEALTH_SAVE_MULTIPLE(input) \
    open_cfw_health_data_save_multiple((input))
#endif
#ifndef OPEN_CFW_PB_HEALTH_SAVE_SINGLE_HIGHLIGHT
#define OPEN_CFW_PB_HEALTH_SAVE_SINGLE_HIGHLIGHT(input) \
    open_cfw_health_data_save_single_highlight((input))
#endif
#ifndef OPEN_CFW_PB_HEALTH_SAVE_MULTIPLE_HIGHLIGHTS
#define OPEN_CFW_PB_HEALTH_SAVE_MULTIPLE_HIGHLIGHTS(input) \
    open_cfw_health_data_save_multiple_highlights((input))
#endif

#if !defined(OPEN_CFW_PB_HEALTH_RX_SINGLE_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_TX_SINGLE_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_RX_MULTIPLE_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_TX_MULTIPLE_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_RX_SINGLE_HIGHLIGHT_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_TX_SINGLE_HIGHLIGHT_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_RX_MULTIPLE_HIGHLIGHTS_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_TX_MULTIPLE_HIGHLIGHTS_ONLY)
#define OPEN_CFW_PB_HEALTH_INCLUDE_BUFFER_WRITE 1
#endif
#if defined(OPEN_CFW_PB_HEALTH_BUFFER_WRITE_ONLY)
#define OPEN_CFW_PB_HEALTH_INCLUDE_BUFFER_WRITE 1
#endif

#if defined(OPEN_CFW_PB_HEALTH_INCLUDE_BUFFER_WRITE)
__attribute__((used, noinline))
unsigned int open_cfw_pb_service_health_buffer_write(
    struct open_cfw_pb_health_output *output,
    const void *raw_data,
    unsigned int length)
{
    const open_cfw_pb_health_u8 *data =
        (const open_cfw_pb_health_u8 *)raw_data;
    open_cfw_pb_health_u8 *destination =
        (open_cfw_pb_health_u8 *)output->context;
    unsigned int index;

    if (output->length > output->capacity ||
        length > output->capacity - output->length) {
        return 0U;
    }
    for (index = 0U; index < length; ++index) {
        destination[output->length + index] = data[index];
    }
    return 1U;
}
#else
unsigned int open_cfw_pb_service_health_buffer_write(
    struct open_cfw_pb_health_output *output,
    const void *raw_data,
    unsigned int length);
#endif

static __attribute__((always_inline)) inline void
open_cfw_pb_health_zero(open_cfw_pb_health_u8 *data, unsigned int length)
{
    unsigned int index;
    for (index = 0U; index < length; ++index) {
        data[index] = 0U;
    }
}

static __attribute__((always_inline)) inline void
open_cfw_pb_health_put_u16(open_cfw_pb_health_u8 *data, unsigned int value)
{
    data[0] = (open_cfw_pb_health_u8)value;
    data[1] = (open_cfw_pb_health_u8)(value >> 8);
}

static __attribute__((always_inline)) inline void
open_cfw_pb_health_put_u32(
    open_cfw_pb_health_u8 *data,
    const open_cfw_pb_health_u8 *source)
{
    data[0] = source[0];
    data[1] = source[1];
    data[2] = source[2];
    data[3] = source[3];
}

static __attribute__((always_inline, unused)) inline unsigned int
open_cfw_pb_health_tx(
    unsigned int sequence,
    const void *raw_input,
    unsigned int command,
    unsigned int tag,
    unsigned int kind)
{
    const open_cfw_pb_health_u8 *input =
        (const open_cfw_pb_health_u8 *)raw_input;
    open_cfw_pb_health_u8 *message = OPEN_CFW_PB_HEALTH_MESSAGE;
    open_cfw_pb_health_u8 *buffer = OPEN_CFW_PB_HEALTH_BUFFER;
    struct open_cfw_pb_health_output output;
    unsigned int index;

    if (input == (const open_cfw_pb_health_u8 *)0) {
        return 2U;
    }
    output.write = open_cfw_pb_service_health_buffer_write;
    output.context = buffer;
    output.capacity = 0x100U;
    output.length = 0U;
    output.error = (const char *)0;
    open_cfw_pb_health_zero(message, 0x31CU);
    message[0] = (open_cfw_pb_health_u8)command;
    message[1] = (open_cfw_pb_health_u8)sequence;
    open_cfw_pb_health_put_u16(message + 2U, tag);

    if (kind == 1U) {
        message[4] = input[0];
        open_cfw_pb_health_put_u32(message + 8U, input + 4U);
        open_cfw_pb_health_put_u32(message + 12U, input + 8U);
        open_cfw_pb_health_put_u32(message + 16U, input + 12U);
        open_cfw_pb_health_put_u32(message + 20U, input + 16U);
        message[24] = 0U;
        message[25] = input[21];
    } else if (kind == 2U) {
        message[4] = input[0];
        message[0xC8U] = 0U;
    } else if (kind == 3U) {
        message[4] = input[0];
        message[0x108U] = 0U;
    } else {
        const unsigned int count =
            (unsigned int)input[0] | ((unsigned int)input[1] << 8);
        if (count > 3U) {
            return 0x2BU;
        }
        open_cfw_pb_health_put_u16(message + 4U, count);
        for (index = 0U; index < count; ++index) {
            const unsigned int offset = 0x106U * index;
            message[6U + offset] = input[2U + offset];
            message[0x10AU + offset] = input[0x106U + offset];
        }
        message[0x318U] = 0U;
    }

    if (OPEN_CFW_PB_HEALTH_ENCODE(
            &output,
            OPEN_CFW_PB_HEALTH_DESCRIPTOR,
            message
        ) == 0U) {
        return 0x2BU;
    }
    (void)OPEN_CFW_PB_HEALTH_SEND(
        1U, 0x0EU, buffer, (open_cfw_pb_health_u16)output.length);
    return 0U;
}

#if !defined(OPEN_CFW_PB_HEALTH_BUFFER_WRITE_ONLY)

#if !defined(OPEN_CFW_PB_HEALTH_TX_SINGLE_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_RX_MULTIPLE_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_TX_MULTIPLE_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_RX_SINGLE_HIGHLIGHT_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_TX_SINGLE_HIGHLIGHT_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_RX_MULTIPLE_HIGHLIGHTS_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_TX_MULTIPLE_HIGHLIGHTS_ONLY)
__attribute__((used, noinline))
unsigned int PB_RxHealthSingleData(unsigned int route, const void *input)
{
    (void)route;
    if (input == (const void *)0) {
        return 2U;
    }
    return OPEN_CFW_PB_HEALTH_SAVE_SINGLE(input) == 0 ? 0U : 1U;
}
#endif

#if !defined(OPEN_CFW_PB_HEALTH_RX_SINGLE_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_RX_MULTIPLE_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_TX_MULTIPLE_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_RX_SINGLE_HIGHLIGHT_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_TX_SINGLE_HIGHLIGHT_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_RX_MULTIPLE_HIGHLIGHTS_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_TX_MULTIPLE_HIGHLIGHTS_ONLY)
__attribute__((used, noinline))
unsigned int APP_PbTxEncodeHealthSingleData(
    unsigned int sequence, const void *input)
{
    return open_cfw_pb_health_tx(sequence, input, 1U, 3U, 1U);
}
#endif

#if !defined(OPEN_CFW_PB_HEALTH_RX_SINGLE_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_TX_SINGLE_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_TX_MULTIPLE_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_RX_SINGLE_HIGHLIGHT_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_TX_SINGLE_HIGHLIGHT_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_RX_MULTIPLE_HIGHLIGHTS_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_TX_MULTIPLE_HIGHLIGHTS_ONLY)
__attribute__((used, noinline))
unsigned int PB_RxHealthMultData(unsigned int route, const void *input)
{
    (void)route;
    if (input == (const void *)0) {
        return 2U;
    }
    return OPEN_CFW_PB_HEALTH_SAVE_MULTIPLE(input) == 0 ? 0U : 1U;
}
#endif

#if !defined(OPEN_CFW_PB_HEALTH_RX_SINGLE_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_TX_SINGLE_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_RX_MULTIPLE_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_RX_SINGLE_HIGHLIGHT_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_TX_SINGLE_HIGHLIGHT_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_RX_MULTIPLE_HIGHLIGHTS_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_TX_MULTIPLE_HIGHLIGHTS_ONLY)
__attribute__((used, noinline))
unsigned int APP_PbTxEncodeHealthMultData(
    unsigned int sequence, const void *input)
{
    return open_cfw_pb_health_tx(sequence, input, 2U, 4U, 2U);
}
#endif

#if !defined(OPEN_CFW_PB_HEALTH_RX_SINGLE_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_TX_SINGLE_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_RX_MULTIPLE_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_TX_MULTIPLE_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_TX_SINGLE_HIGHLIGHT_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_RX_MULTIPLE_HIGHLIGHTS_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_TX_MULTIPLE_HIGHLIGHTS_ONLY)
__attribute__((used, noinline))
unsigned int PB_RxHealthSingleHighlight(
    unsigned int route, const void *input)
{
    (void)route;
    if (input == (const void *)0) {
        return 2U;
    }
    return OPEN_CFW_PB_HEALTH_SAVE_SINGLE_HIGHLIGHT(input) == 0 ? 0U : 1U;
}
#endif

#if !defined(OPEN_CFW_PB_HEALTH_RX_SINGLE_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_TX_SINGLE_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_RX_MULTIPLE_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_TX_MULTIPLE_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_RX_SINGLE_HIGHLIGHT_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_RX_MULTIPLE_HIGHLIGHTS_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_TX_MULTIPLE_HIGHLIGHTS_ONLY)
__attribute__((used, noinline))
unsigned int APP_PbTxEncodeHealthSingleHighlight(
    unsigned int sequence, const void *input)
{
    return open_cfw_pb_health_tx(sequence, input, 3U, 5U, 3U);
}
#endif

#if !defined(OPEN_CFW_PB_HEALTH_RX_SINGLE_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_TX_SINGLE_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_RX_MULTIPLE_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_TX_MULTIPLE_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_RX_SINGLE_HIGHLIGHT_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_TX_SINGLE_HIGHLIGHT_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_TX_MULTIPLE_HIGHLIGHTS_ONLY)
__attribute__((used, noinline))
unsigned int PB_RxHealthMultHighlight(
    unsigned int route, const void *input)
{
    (void)route;
    if (input == (const void *)0) {
        return 2U;
    }
    return OPEN_CFW_PB_HEALTH_SAVE_MULTIPLE_HIGHLIGHTS(input) == 0 ? 0U : 1U;
}
#endif

#if !defined(OPEN_CFW_PB_HEALTH_RX_SINGLE_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_TX_SINGLE_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_RX_MULTIPLE_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_TX_MULTIPLE_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_RX_SINGLE_HIGHLIGHT_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_TX_SINGLE_HIGHLIGHT_ONLY) && \
    !defined(OPEN_CFW_PB_HEALTH_RX_MULTIPLE_HIGHLIGHTS_ONLY)
__attribute__((used, noinline))
unsigned int APP_PbTxEncodeHealthMultHighlight(
    unsigned int sequence, const void *input)
{
    return open_cfw_pb_health_tx(sequence, input, 4U, 6U, 4U);
}
#endif

#endif
