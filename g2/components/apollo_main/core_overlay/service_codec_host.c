/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of platform/audio/service_codec_host.c. */
#include <stddef.h>
#include <stdint.h>

#ifndef OPEN_CFW_SELECTOR
#define OPEN_CFW_SELECTOR 0
#endif

enum {
    OPEN_CFW_CODEC_OK = 0,
    OPEN_CFW_CODEC_ERROR = -1,
    OPEN_CFW_CODEC_TOO_LARGE = -2,
    OPEN_CFW_CODEC_TRUNCATED = -3,
    OPEN_CFW_CODEC_HEADER_CRC = -4,
    OPEN_CFW_CODEC_BODY_TOO_LARGE = -5,
    OPEN_CFW_CODEC_NO_MEMORY = -6,
    OPEN_CFW_CODEC_BODY_CRC = -7,
    OPEN_CFW_CODEC_HEADER_BYTES = 14,
    OPEN_CFW_CODEC_BODY_MAX = 16,
    OPEN_CFW_CODEC_WIRE_MAX = 30,
    OPEN_CFW_CODEC_RETRIES = 3
};

typedef struct __attribute__((packed)) {
    uint32_t magic;
    uint16_t command;
    uint8_t sequence;
    uint8_t flags;
    uint16_t encoded_body_length;
    uint32_t header_crc;
    uint8_t *body;
    uint16_t body_length;
    uint32_t body_crc;
    uint16_t wire_length;
} open_cfw_codec_message_t;

#ifndef OPEN_CFW_CODEC_SEQUENCE
#define OPEN_CFW_CODEC_SEQUENCE \
    (*(volatile uint8_t *)(uintptr_t)0x20075013u)
#endif
#ifndef OPEN_CFW_CODEC_TX_BUFFER
#define OPEN_CFW_CODEC_TX_BUFFER ((uint8_t *)(uintptr_t)0x2007399cu)
#endif
#ifndef OPEN_CFW_CODEC_RX_BUFFER
#define OPEN_CFW_CODEC_RX_BUFFER ((uint8_t *)(uintptr_t)0x2007397cu)
#endif
#ifndef OPEN_CFW_CODEC_VERSION_CACHE
#define OPEN_CFW_CODEC_VERSION_CACHE ((uint8_t *)(uintptr_t)0x20074948u)
#endif

#ifndef OPEN_CFW_CODEC_UART_PORT_INIT
int32_t open_cfw_codec_uart_init(void);
#define OPEN_CFW_CODEC_UART_PORT_INIT() open_cfw_codec_uart_init()
#endif
#ifndef OPEN_CFW_CODEC_UART_PORT_CLOSE
int32_t open_cfw_codec_uart_close(void);
#define OPEN_CFW_CODEC_UART_PORT_CLOSE() open_cfw_codec_uart_close()
#endif
#ifndef OPEN_CFW_CODEC_UART_SET_BAUD
void open_cfw_codec_uart_set_baud(uint32_t baud);
#define OPEN_CFW_CODEC_UART_SET_BAUD(baud) open_cfw_codec_uart_set_baud((baud))
#endif
#ifndef OPEN_CFW_CODEC_UART_WRITE
int32_t open_cfw_codec_uart_write(const uint8_t *data, uint16_t length);
#define OPEN_CFW_CODEC_UART_WRITE(data, length) \
    open_cfw_codec_uart_write((data), (length))
#endif
#ifndef OPEN_CFW_CODEC_UART_READ
int32_t open_cfw_codec_uart_read(uint8_t *data, uint16_t length);
#define OPEN_CFW_CODEC_UART_READ(data, length) \
    open_cfw_codec_uart_read((data), (length))
#endif
#ifndef OPEN_CFW_CODEC_TIME_MS
uint64_t open_cfw_codec_time_ms(void);
#define OPEN_CFW_CODEC_TIME_MS() open_cfw_codec_time_ms()
#endif
#ifndef OPEN_CFW_CODEC_DELAY
void open_cfw_codec_delay(uint32_t ticks);
#define OPEN_CFW_CODEC_DELAY(ticks) open_cfw_codec_delay((ticks))
#endif
#ifndef OPEN_CFW_CODEC_CRC32
uint32_t open_cfw_codec_crc32(const void *data, uint16_t length);
#define OPEN_CFW_CODEC_CRC32(data, length) \
    open_cfw_codec_crc32((data), (length))
#endif
#ifndef OPEN_CFW_CODEC_ALLOCATE
void *open_cfw_codec_allocate(uint32_t length);
#define OPEN_CFW_CODEC_ALLOCATE(length) open_cfw_codec_allocate((length))
#endif
#ifndef OPEN_CFW_CODEC_FREE
void open_cfw_codec_free(void *pointer);
#define OPEN_CFW_CODEC_FREE(pointer) open_cfw_codec_free((pointer))
#endif

#ifndef OPEN_CFW_CODEC_HOST_INIT
int32_t open_cfw_codec_host_init(void);
#define OPEN_CFW_CODEC_HOST_INIT() open_cfw_codec_host_init()
#endif
#ifndef OPEN_CFW_CODEC_HOST_CLEANUP
int32_t open_cfw_codec_host_cleanup(void);
#define OPEN_CFW_CODEC_HOST_CLEANUP() open_cfw_codec_host_cleanup()
#endif
#ifndef OPEN_CFW_CODEC_HOST_PACK
int32_t open_cfw_codec_host_pack_message(uint16_t command_low,
    uint16_t command_high, const uint8_t *body, uint16_t body_length,
    uint8_t with_body_crc, uint8_t *wire, uint16_t *wire_length);
#define OPEN_CFW_CODEC_HOST_PACK(command_low, command_high, body, body_length, \
        with_body_crc, wire, wire_length) \
    open_cfw_codec_host_pack_message((command_low), (command_high), (body), \
        (body_length), (with_body_crc), (wire), (wire_length))
#endif
#ifndef OPEN_CFW_CODEC_HOST_UNPACK
int32_t open_cfw_codec_host_unpack_message(const uint8_t *wire,
    uint16_t wire_length, open_cfw_codec_message_t *message, const void *context);
#define OPEN_CFW_CODEC_HOST_UNPACK(wire, wire_length, message, context) \
    open_cfw_codec_host_unpack_message((wire), (wire_length), (message), (context))
#endif
#ifndef OPEN_CFW_CODEC_HOST_SEND
int32_t open_cfw_codec_host_send_message(uint16_t command_low,
    uint16_t command_high, const uint8_t *body, uint16_t body_length,
    uint8_t with_body_crc);
#define OPEN_CFW_CODEC_HOST_SEND(command_low, command_high, body, body_length, \
        with_body_crc) \
    open_cfw_codec_host_send_message((command_low), (command_high), (body), \
        (body_length), (with_body_crc))
#endif
#ifndef OPEN_CFW_CODEC_HOST_READ_BLOCKING
int32_t open_cfw_codec_host_uart_read_blocking(uint8_t *wire,
    uint16_t capacity, uint32_t timeout_ms, const void *context);
#define OPEN_CFW_CODEC_HOST_READ_BLOCKING(wire, capacity, timeout_ms, context) \
    open_cfw_codec_host_uart_read_blocking((wire), (capacity), (timeout_ms), \
        (context))
#endif
#ifndef OPEN_CFW_CODEC_HOST_READ
int32_t open_cfw_codec_host_read_uart_data(uint8_t *wire, uint16_t capacity,
    uint16_t *wire_length, uint32_t timeout_ms);
#define OPEN_CFW_CODEC_HOST_READ(wire, capacity, wire_length, timeout_ms) \
    open_cfw_codec_host_read_uart_data((wire), (capacity), (wire_length), \
        (timeout_ms))
#endif
#ifndef OPEN_CFW_CODEC_HOST_SEND_WAIT
int32_t open_cfw_codec_host_send_and_wait_response(uint16_t command_low,
    uint16_t command_high, const uint8_t *body, uint16_t body_length,
    uint8_t with_body_crc, open_cfw_codec_message_t *response,
    uint32_t timeout_ms);
#define OPEN_CFW_CODEC_HOST_SEND_WAIT(command_low, command_high, body, \
        body_length, with_body_crc, response, timeout_ms) \
    open_cfw_codec_host_send_and_wait_response((command_low), (command_high), \
        (body), (body_length), (with_body_crc), (response), (timeout_ms))
#endif
#ifndef OPEN_CFW_CODEC_HOST_RELEASE
void open_cfw_codec_host_free_message(open_cfw_codec_message_t *message);
#define OPEN_CFW_CODEC_HOST_RELEASE(message) \
    open_cfw_codec_host_free_message((message))
#endif

#ifndef OPEN_CFW_CODEC_READ_VERSION
int32_t open_cfw_codec_read_version(uint8_t *version, uint32_t timeout_ms);
#define OPEN_CFW_CODEC_READ_VERSION(version, timeout_ms) \
    open_cfw_codec_read_version((version), (timeout_ms))
#endif
#ifndef OPEN_CFW_CODEC_SWITCH_BF
int32_t open_cfw_codec_switch_bf_mode(uint8_t *status, uint32_t timeout_ms);
#define OPEN_CFW_CODEC_SWITCH_BF(status, timeout_ms) \
    open_cfw_codec_switch_bf_mode((status), (timeout_ms))
#endif
#ifndef OPEN_CFW_CODEC_SWITCH_WAKEUP
int32_t open_cfw_codec_switch_wakeup_mode(uint8_t *status, uint32_t timeout_ms);
#define OPEN_CFW_CODEC_SWITCH_WAKEUP(status, timeout_ms) \
    open_cfw_codec_switch_wakeup_mode((status), (timeout_ms))
#endif
#ifndef OPEN_CFW_CODEC_SET_MIC_GAIN
int32_t open_cfw_codec_set_mic_gain(uint8_t gain, uint16_t *status,
    uint32_t timeout_ms);
#define OPEN_CFW_CODEC_SET_MIC_GAIN(gain, status, timeout_ms) \
    open_cfw_codec_set_mic_gain((gain), (status), (timeout_ms))
#endif
#ifndef OPEN_CFW_CODEC_DMIC_CONTROL
int32_t open_cfw_codec_dmic_control(uint8_t enable, uint16_t *status,
    uint32_t timeout_ms);
#define OPEN_CFW_CODEC_DMIC_CONTROL(enable, status, timeout_ms) \
    open_cfw_codec_dmic_control((enable), (status), (timeout_ms))
#endif
#ifndef OPEN_CFW_CODEC_I2S_CONTROL
int32_t open_cfw_codec_i2s_output_control(uint8_t enable, uint8_t *status,
    uint32_t timeout_ms);
#define OPEN_CFW_CODEC_I2S_CONTROL(enable, status, timeout_ms) \
    open_cfw_codec_i2s_output_control((enable), (status), (timeout_ms))
#endif
#ifndef OPEN_CFW_CODEC_MIC_DELAY
int32_t open_cfw_codec_mic_delay_1bit(uint8_t *status, uint32_t timeout_ms);
#define OPEN_CFW_CODEC_MIC_DELAY(status, timeout_ms) \
    open_cfw_codec_mic_delay_1bit((status), (timeout_ms))
#endif

static __attribute__((always_inline, unused)) inline uint16_t open_cfw_get_u16(
    const uint8_t *data)
{
    return (uint16_t)((uint16_t)data[0] | ((uint16_t)data[1] << 8));
}

static __attribute__((always_inline, unused)) inline void open_cfw_put_u16(
    uint8_t *data, uint16_t value)
{
    data[0] = (uint8_t)value;
    data[1] = (uint8_t)(value >> 8);
}

static __attribute__((always_inline, unused)) inline uint32_t open_cfw_get_u32(
    const uint8_t *data)
{
    return (uint32_t)data[0] | ((uint32_t)data[1] << 8) |
        ((uint32_t)data[2] << 16) | ((uint32_t)data[3] << 24);
}

static __attribute__((always_inline, unused)) inline void open_cfw_put_u32(
    uint8_t *data, uint32_t value)
{
    data[0] = (uint8_t)value;
    data[1] = (uint8_t)(value >> 8);
    data[2] = (uint8_t)(value >> 16);
    data[3] = (uint8_t)(value >> 24);
}

static __attribute__((always_inline, unused)) inline void open_cfw_copy(
    uint8_t *destination, const uint8_t *source, uint16_t length)
{
    uint16_t index;
    for (index = 0u; index < length; ++index) {
        destination[index] = source[index];
    }
}

static __attribute__((always_inline, unused)) inline void open_cfw_clear(
    void *destination, uint16_t length)
{
    uint8_t *bytes = (uint8_t *)destination;
    uint16_t index;
    for (index = 0u; index < length; ++index) {
        bytes[index] = 0u;
    }
}

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 1
__attribute__((used, noinline))
int32_t open_cfw_codec_host_init(void)
{
    int32_t status = OPEN_CFW_CODEC_UART_PORT_INIT();
    if (status == 0) {
        OPEN_CFW_CODEC_UART_SET_BAUD(115200u);
    }
    return status;
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 2
__attribute__((used, noinline))
int32_t open_cfw_codec_host_cleanup(void)
{
    return OPEN_CFW_CODEC_UART_PORT_CLOSE();
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 3
__attribute__((used, noinline))
int32_t open_cfw_codec_host_magic_matches(const uint8_t *wire)
{
    if (wire == NULL) {
        return OPEN_CFW_CODEC_ERROR;
    }
    return (wire[0] == (uint8_t)'B' && wire[1] == (uint8_t)'U' &&
        wire[2] == (uint8_t)'X' && wire[3] == (uint8_t)'X') ? 0 : 1;
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 4
__attribute__((used, noinline))
int32_t open_cfw_codec_host_pack_message(uint16_t command_low,
    uint16_t command_high, const uint8_t *body, uint16_t body_length,
    uint8_t with_body_crc, uint8_t *wire, uint16_t *wire_length)
{
    uint16_t encoded_length = body_length;
    uint32_t crc;

    if (wire == NULL || wire_length == NULL ||
        (body_length != 0u && body == NULL)) {
        return OPEN_CFW_CODEC_ERROR;
    }
    if (with_body_crc != 0u) {
        encoded_length = (uint16_t)(encoded_length + 4u);
    }
    if (encoded_length > OPEN_CFW_CODEC_BODY_MAX) {
        return OPEN_CFW_CODEC_TOO_LARGE;
    }

    wire[0] = (uint8_t)'B';
    wire[1] = (uint8_t)'U';
    wire[2] = (uint8_t)'X';
    wire[3] = (uint8_t)'X';
    open_cfw_put_u16(wire + 4,
        (uint16_t)((command_low & 0x00ffu) | (command_high & 0xff00u)));
    wire[6] = OPEN_CFW_CODEC_SEQUENCE;
    OPEN_CFW_CODEC_SEQUENCE = (uint8_t)(OPEN_CFW_CODEC_SEQUENCE + 1u);
    wire[7] = (with_body_crc != 0u) ? 1u : 0u;
    open_cfw_put_u16(wire + 8, encoded_length);
    if (body_length != 0u) {
        open_cfw_copy(wire + OPEN_CFW_CODEC_HEADER_BYTES, body, body_length);
    }
    if (with_body_crc != 0u) {
        crc = OPEN_CFW_CODEC_CRC32(body, body_length);
        open_cfw_put_u32(wire + OPEN_CFW_CODEC_HEADER_BYTES + body_length, crc);
    }
    crc = OPEN_CFW_CODEC_CRC32(wire, 10u);
    open_cfw_put_u32(wire + 10, crc);
    *wire_length = (uint16_t)(OPEN_CFW_CODEC_HEADER_BYTES + encoded_length);
    return OPEN_CFW_CODEC_OK;
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 5
__attribute__((used, noinline))
int32_t open_cfw_codec_host_unpack_message(const uint8_t *wire,
    uint16_t wire_length, open_cfw_codec_message_t *message, const void *context)
{
    uint16_t encoded_length;
    uint16_t body_length;
    uint16_t total_length;
    uint32_t expected_crc;
    uint32_t actual_crc;
    uint8_t *body;
    (void)context;

    if (wire == NULL || message == NULL ||
        wire_length < OPEN_CFW_CODEC_HEADER_BYTES) {
        return OPEN_CFW_CODEC_ERROR;
    }
    open_cfw_clear(message, (uint16_t)sizeof(*message));
    if (!(wire[0] == (uint8_t)'B' && wire[1] == (uint8_t)'U' &&
          wire[2] == (uint8_t)'X' && wire[3] == (uint8_t)'X')) {
        return OPEN_CFW_CODEC_TOO_LARGE;
    }
    encoded_length = open_cfw_get_u16(wire + 8);
    total_length = (uint16_t)(OPEN_CFW_CODEC_HEADER_BYTES + encoded_length);
    if (wire_length < total_length) {
        return OPEN_CFW_CODEC_TRUNCATED;
    }
    expected_crc = open_cfw_get_u32(wire + 10);
    actual_crc = OPEN_CFW_CODEC_CRC32(wire, 10u);
    if (expected_crc != actual_crc) {
        return OPEN_CFW_CODEC_HEADER_CRC;
    }
    if (encoded_length > OPEN_CFW_CODEC_BODY_MAX ||
        ((wire[7] & 1u) != 0u && encoded_length < 4u)) {
        return OPEN_CFW_CODEC_BODY_TOO_LARGE;
    }
    body_length = encoded_length;
    if ((wire[7] & 1u) != 0u) {
        body_length = (uint16_t)(body_length - 4u);
    }

    message->magic = open_cfw_get_u32(wire);
    message->command = open_cfw_get_u16(wire + 4);
    message->sequence = wire[6];
    message->flags = wire[7];
    message->encoded_body_length = encoded_length;
    message->header_crc = expected_crc;
    message->wire_length = total_length;
    if (body_length == 0u) {
        return OPEN_CFW_CODEC_OK;
    }
    body = (uint8_t *)OPEN_CFW_CODEC_ALLOCATE(body_length);
    if (body == NULL) {
        return OPEN_CFW_CODEC_NO_MEMORY;
    }
    open_cfw_copy(body, wire + OPEN_CFW_CODEC_HEADER_BYTES, body_length);
    message->body = body;
    message->body_length = body_length;
    if ((wire[7] & 1u) != 0u) {
        expected_crc = open_cfw_get_u32(
            wire + OPEN_CFW_CODEC_HEADER_BYTES + body_length);
        actual_crc = OPEN_CFW_CODEC_CRC32(body, body_length);
        message->body_crc = expected_crc;
        if (expected_crc != actual_crc) {
            OPEN_CFW_CODEC_FREE(body);
            message->body = NULL;
            message->body_length = 0u;
            return OPEN_CFW_CODEC_BODY_CRC;
        }
    }
    return OPEN_CFW_CODEC_OK;
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 6
__attribute__((used, noinline))
int32_t open_cfw_codec_host_send_message(uint16_t command_low,
    uint16_t command_high, const uint8_t *body, uint16_t body_length,
    uint8_t with_body_crc)
{
    uint16_t wire_length = 0u;
    int32_t status = OPEN_CFW_CODEC_HOST_PACK(command_low, command_high,
        body, body_length, with_body_crc, OPEN_CFW_CODEC_TX_BUFFER,
        &wire_length);
    if (status != 0) {
        return status;
    }
    return OPEN_CFW_CODEC_UART_WRITE(OPEN_CFW_CODEC_TX_BUFFER, wire_length);
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 7
__attribute__((used, noinline))
int32_t open_cfw_codec_host_uart_read_blocking(uint8_t *wire,
    uint16_t capacity, uint32_t timeout_ms, const void *context)
{
    uint64_t start;
    uint16_t received = 0u;
    uint16_t total = OPEN_CFW_CODEC_HEADER_BYTES;
    int32_t count;
    (void)context;

    if (wire == NULL || capacity == 0u) {
        return OPEN_CFW_CODEC_ERROR;
    }
    start = OPEN_CFW_CODEC_TIME_MS();
    while (received < OPEN_CFW_CODEC_HEADER_BYTES) {
        if ((OPEN_CFW_CODEC_TIME_MS() - start) >= timeout_ms) {
            return OPEN_CFW_CODEC_ERROR;
        }
        count = OPEN_CFW_CODEC_UART_READ(wire + received,
            (uint16_t)(OPEN_CFW_CODEC_HEADER_BYTES - received));
        if (count <= 0) {
            OPEN_CFW_CODEC_DELAY(1u);
        } else {
            received = (uint16_t)(received + (uint16_t)count);
        }
    }
    total = (uint16_t)(OPEN_CFW_CODEC_HEADER_BYTES +
        open_cfw_get_u16(wire + 8));
    if (total > capacity || total > OPEN_CFW_CODEC_WIRE_MAX) {
        return OPEN_CFW_CODEC_ERROR;
    }
    while (received < total) {
        if ((OPEN_CFW_CODEC_TIME_MS() - start) >= timeout_ms) {
            return OPEN_CFW_CODEC_ERROR;
        }
        count = OPEN_CFW_CODEC_UART_READ(wire + received,
            (uint16_t)(total - received));
        if (count <= 0) {
            OPEN_CFW_CODEC_DELAY(1u);
        } else {
            received = (uint16_t)(received + (uint16_t)count);
        }
    }
    return (int32_t)received;
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 8
__attribute__((used, noinline))
int32_t open_cfw_codec_host_read_uart_data(uint8_t *wire, uint16_t capacity,
    uint16_t *wire_length, uint32_t timeout_ms)
{
    int32_t count;
    if (wire == NULL || wire_length == NULL || capacity == 0u) {
        return OPEN_CFW_CODEC_ERROR;
    }
    count = OPEN_CFW_CODEC_HOST_READ_BLOCKING(wire, capacity, timeout_ms, NULL);
    if (count < 0) {
        return count;
    }
    *wire_length = (uint16_t)count;
    return OPEN_CFW_CODEC_OK;
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 9
__attribute__((used, noinline))
int32_t open_cfw_codec_host_send_and_wait_response(uint16_t command_low,
    uint16_t command_high, const uint8_t *body, uint16_t body_length,
    uint8_t with_body_crc, open_cfw_codec_message_t *response,
    uint32_t timeout_ms)
{
    uint16_t wire_length = 0u;
    int32_t status;
    int32_t close_status;

    if (response == NULL) {
        return OPEN_CFW_CODEC_ERROR;
    }
    status = OPEN_CFW_CODEC_HOST_INIT();
    if (status != 0) {
        return status;
    }
    status = OPEN_CFW_CODEC_HOST_SEND(command_low, command_high, body,
        body_length, with_body_crc);
    if (status == 0) {
        status = OPEN_CFW_CODEC_HOST_READ(OPEN_CFW_CODEC_RX_BUFFER,
            OPEN_CFW_CODEC_WIRE_MAX, &wire_length, timeout_ms);
    }
    close_status = OPEN_CFW_CODEC_HOST_CLEANUP();
    if (status == 0 && close_status != 0) {
        status = close_status;
    }
    if (status != 0) {
        return status;
    }
    return OPEN_CFW_CODEC_HOST_UNPACK(OPEN_CFW_CODEC_RX_BUFFER, wire_length,
        response, NULL);
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 10
__attribute__((used, noinline))
void open_cfw_codec_host_free_message(open_cfw_codec_message_t *message)
{
    if (message != NULL && message->body != NULL) {
        OPEN_CFW_CODEC_FREE(message->body);
        message->body = NULL;
        message->body_length = 0u;
    }
}
#endif

#if (OPEN_CFW_SELECTOR >= 11 && OPEN_CFW_SELECTOR <= 17) || \
    OPEN_CFW_SELECTOR == 0
static __attribute__((always_inline)) inline int32_t open_cfw_codec_request(
    uint16_t command, const uint8_t *body, uint16_t body_length,
    open_cfw_codec_message_t *response, uint32_t timeout_ms)
{
    int32_t status = OPEN_CFW_CODEC_ERROR;
    uint8_t attempt;
    for (attempt = 0u; attempt < OPEN_CFW_CODEC_RETRIES; ++attempt) {
        open_cfw_clear(response, (uint16_t)sizeof(*response));
        status = OPEN_CFW_CODEC_HOST_SEND_WAIT(command, 0x0100u, body,
            body_length, 0u, response, timeout_ms);
        if (status == 0) {
            break;
        }
        OPEN_CFW_CODEC_HOST_RELEASE(response);
    }
    return status;
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 11
__attribute__((used, noinline))
int32_t open_cfw_codec_read_version(uint8_t *version, uint32_t timeout_ms)
{
    open_cfw_codec_message_t response;
    int32_t status;
    if (version == NULL) {
        return OPEN_CFW_CODEC_ERROR;
    }
    status = open_cfw_codec_request(0x02u, NULL, 0u, &response, timeout_ms);
    if (status != 0) {
        return status;
    }
    if (response.body == NULL || response.body_length < 4u) {
        OPEN_CFW_CODEC_HOST_RELEASE(&response);
        return OPEN_CFW_CODEC_ERROR;
    }
    open_cfw_copy(version, response.body, 4u);
    open_cfw_copy(OPEN_CFW_CODEC_VERSION_CACHE, version, 4u);
    OPEN_CFW_CODEC_HOST_RELEASE(&response);
    return OPEN_CFW_CODEC_OK;
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 12
__attribute__((used, noinline))
int32_t open_cfw_codec_switch_bf_mode(uint8_t *status, uint32_t timeout_ms)
{
    open_cfw_codec_message_t response;
    int32_t result;
    if (status == NULL) return OPEN_CFW_CODEC_ERROR;
    result = open_cfw_codec_request(0x07u, NULL, 0u, &response, timeout_ms);
    if (result == 0 && response.body != NULL && response.body_length >= 1u) {
        *status = response.body[0];
    } else if (result == 0) {
        result = OPEN_CFW_CODEC_ERROR;
    }
    OPEN_CFW_CODEC_HOST_RELEASE(&response);
    return result;
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 13
__attribute__((used, noinline))
int32_t open_cfw_codec_switch_wakeup_mode(uint8_t *status, uint32_t timeout_ms)
{
    open_cfw_codec_message_t response;
    int32_t result;
    if (status == NULL) return OPEN_CFW_CODEC_ERROR;
    result = open_cfw_codec_request(0x08u, NULL, 0u, &response, timeout_ms);
    if (result == 0 && response.body != NULL && response.body_length >= 1u) {
        *status = response.body[0];
    } else if (result == 0) {
        result = OPEN_CFW_CODEC_ERROR;
    }
    OPEN_CFW_CODEC_HOST_RELEASE(&response);
    return result;
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 14
__attribute__((used, noinline))
int32_t open_cfw_codec_query_mic_state(uint16_t *state, uint32_t timeout_ms)
{
    open_cfw_codec_message_t response;
    int32_t result;
    if (state == NULL) return OPEN_CFW_CODEC_ERROR;
    result = open_cfw_codec_request(0x70u, NULL, 0u, &response, timeout_ms);
    if (result == 0 && response.body != NULL && response.body_length >= 2u) {
        *state = open_cfw_get_u16(response.body);
    } else if (result == 0) {
        result = OPEN_CFW_CODEC_ERROR;
    }
    OPEN_CFW_CODEC_HOST_RELEASE(&response);
    return result;
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 15
__attribute__((used, noinline))
int32_t open_cfw_codec_set_mic_gain(uint8_t gain, uint16_t *status,
    uint32_t timeout_ms)
{
    open_cfw_codec_message_t response;
    int32_t result;
    if (status == NULL) return OPEN_CFW_CODEC_ERROR;
    result = open_cfw_codec_request(0x0bu, &gain, 1u, &response, timeout_ms);
    if (result == 0 && response.body != NULL && response.body_length >= 2u) {
        *status = open_cfw_get_u16(response.body);
    } else if (result == 0) {
        result = OPEN_CFW_CODEC_ERROR;
    }
    OPEN_CFW_CODEC_HOST_RELEASE(&response);
    return result;
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 16
__attribute__((used, noinline))
int32_t open_cfw_codec_dmic_control(uint8_t enable, uint16_t *status,
    uint32_t timeout_ms)
{
    open_cfw_codec_message_t response;
    int32_t result;
    uint16_t command = (enable != 0u) ? 0x0cu : 0x0du;
    if (status == NULL) return OPEN_CFW_CODEC_ERROR;
    result = open_cfw_codec_request(command, NULL, 0u, &response, timeout_ms);
    if (result == 0 && response.body != NULL && response.body_length >= 2u) {
        *status = open_cfw_get_u16(response.body);
    } else if (result == 0) {
        result = OPEN_CFW_CODEC_ERROR;
    }
    OPEN_CFW_CODEC_HOST_RELEASE(&response);
    return result;
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 17
__attribute__((used, noinline))
int32_t open_cfw_codec_i2s_output_control(uint8_t enable, uint8_t *status,
    uint32_t timeout_ms)
{
    open_cfw_codec_message_t response;
    uint8_t value = (enable != 0u) ? 1u : 0u;
    int32_t result;
    if (status == NULL) return OPEN_CFW_CODEC_ERROR;
    result = open_cfw_codec_request(0x0fu, &value, 1u, &response, timeout_ms);
    if (result == 0 && response.body != NULL && response.body_length >= 1u) {
        *status = response.body[0];
    } else if (result == 0) {
        result = OPEN_CFW_CODEC_ERROR;
    }
    OPEN_CFW_CODEC_HOST_RELEASE(&response);
    return result;
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 18
__attribute__((used, noinline))
int32_t open_cfw_codec_mic_delay_1bit(uint8_t *status, uint32_t timeout_ms)
{
    uint8_t request[OPEN_CFW_CODEC_HEADER_BYTES];
    open_cfw_codec_message_t response;
    uint16_t wire_length;
    int32_t result = OPEN_CFW_CODEC_ERROR;
    uint8_t attempt;
    if (status == NULL) return OPEN_CFW_CODEC_ERROR;
    request[0] = 0x42u; request[1] = 0x55u;
    request[2] = 0x58u; request[3] = 0x58u;
    request[4] = 0x0eu; request[5] = 0x01u;
    request[6] = 0x01u; request[7] = 0x00u;
    request[8] = 0x00u; request[9] = 0x00u;
    request[10] = 0xd4u; request[11] = 0xdbu;
    request[12] = 0x2fu; request[13] = 0x68u;
    for (attempt = 0u; attempt < OPEN_CFW_CODEC_RETRIES; ++attempt) {
        open_cfw_clear(&response, (uint16_t)sizeof(response));
        result = OPEN_CFW_CODEC_HOST_INIT();
        if (result == 0) {
            result = OPEN_CFW_CODEC_UART_WRITE(request,
                OPEN_CFW_CODEC_HEADER_BYTES);
        }
        if (result == 0) {
            wire_length = 0u;
            result = OPEN_CFW_CODEC_HOST_READ(OPEN_CFW_CODEC_RX_BUFFER,
                OPEN_CFW_CODEC_WIRE_MAX, &wire_length, timeout_ms);
            if (result == 0) {
                result = OPEN_CFW_CODEC_HOST_UNPACK(OPEN_CFW_CODEC_RX_BUFFER,
                    wire_length, &response, NULL);
            }
        }
        (void)OPEN_CFW_CODEC_HOST_CLEANUP();
        if (result == 0) break;
        OPEN_CFW_CODEC_HOST_RELEASE(&response);
    }
    if (result == 0 && response.body != NULL && response.body_length >= 1u) {
        *status = response.body[0];
    } else if (result == 0) {
        result = OPEN_CFW_CODEC_ERROR;
    }
    OPEN_CFW_CODEC_HOST_RELEASE(&response);
    return result;
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 19
__attribute__((used, noinline))
int32_t open_cfw_svc_switch_bf_mode(void)
{
    uint8_t status = 0u;
    int32_t result = OPEN_CFW_CODEC_SWITCH_BF(&status, 200u);
    return (result == 0 && status == 1u) ? 0 :
        ((result != 0) ? result : OPEN_CFW_CODEC_ERROR);
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 20
__attribute__((used, noinline))
int32_t open_cfw_svc_switch_wakeup_mode(void)
{
    uint8_t status = 0u;
    int32_t result = OPEN_CFW_CODEC_SWITCH_WAKEUP(&status, 200u);
    return (result == 0 && status == 0u) ? 0 :
        ((result != 0) ? result : OPEN_CFW_CODEC_ERROR);
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 21
__attribute__((used, noinline))
int32_t open_cfw_svc_set_mic_gain(uint8_t gain)
{
    uint16_t status = 0u;
    int32_t result = OPEN_CFW_CODEC_SET_MIC_GAIN(gain, &status, 200u);
    return (result == 0 && status == 1u) ? 0 :
        ((result != 0) ? result : OPEN_CFW_CODEC_ERROR);
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 22
__attribute__((used, noinline))
int32_t open_cfw_svc_codec_dmic_open(void)
{
    uint16_t status = 0u;
    int32_t result = OPEN_CFW_CODEC_DMIC_CONTROL(1u, &status, 200u);
    return (result == 0 && status == 1u) ? 0 :
        ((result != 0) ? result : OPEN_CFW_CODEC_ERROR);
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 23
__attribute__((used, noinline))
int32_t open_cfw_svc_codec_dmic_close(void)
{
    uint16_t status = 0u;
    int32_t result = OPEN_CFW_CODEC_DMIC_CONTROL(0u, &status, 200u);
    return (result == 0 && status == 1u) ? 0 :
        ((result != 0) ? result : OPEN_CFW_CODEC_ERROR);
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 24
__attribute__((used, noinline))
int32_t open_cfw_svc_codec_mic_delay_1bit(void)
{
    uint8_t status = 0u;
    int32_t result = OPEN_CFW_CODEC_MIC_DELAY(&status, 200u);
    return (result == 0 && status == 1u) ? 0 :
        ((result != 0) ? result : OPEN_CFW_CODEC_ERROR);
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 25
__attribute__((used, noinline))
int32_t open_cfw_svc_i2s_output_control(uint8_t enable)
{
    uint8_t status = 0u;
    int32_t result = OPEN_CFW_CODEC_I2S_CONTROL(enable, &status, 200u);
    return (result == 0 && status == 1u) ? 0 :
        ((result != 0) ? result : OPEN_CFW_CODEC_ERROR);
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 26
__attribute__((used, noinline))
int32_t open_cfw_codec_get_voice_event(void *event_output)
{
    open_cfw_codec_message_t response;
    uint8_t *output = (uint8_t *)event_output;
    uint16_t wire_length;
    int32_t result = OPEN_CFW_CODEC_ERROR;
    uint8_t attempt;
    if (output == NULL) return OPEN_CFW_CODEC_ERROR;
    for (attempt = 0u; attempt < OPEN_CFW_CODEC_RETRIES; ++attempt) {
        open_cfw_clear(&response, (uint16_t)sizeof(response));
        wire_length = 0u;
        result = OPEN_CFW_CODEC_HOST_READ(OPEN_CFW_CODEC_RX_BUFFER,
            OPEN_CFW_CODEC_WIRE_MAX, &wire_length, 200u);
        if (result == 0) {
            result = OPEN_CFW_CODEC_HOST_UNPACK(OPEN_CFW_CODEC_RX_BUFFER,
                wire_length, &response, NULL);
        }
        if (result == 0) break;
        OPEN_CFW_CODEC_HOST_RELEASE(&response);
    }
    if (result != 0) return result;
    if (response.body == NULL || response.body_length < 3u) {
        OPEN_CFW_CODEC_HOST_RELEASE(&response);
        return OPEN_CFW_CODEC_ERROR;
    }
    output[0] = response.body[0];
    open_cfw_put_u16(output + 2, open_cfw_get_u16(response.body + 1));
    OPEN_CFW_CODEC_HOST_RELEASE(&response);
    return OPEN_CFW_CODEC_OK;
}
#endif
