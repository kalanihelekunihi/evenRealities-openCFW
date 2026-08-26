#include "service_codec_host_host.h"
#include <stdlib.h>
#include <string.h>

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
} host_message_t;

uint8_t host_codec_sequence;
uint8_t host_codec_tx_buffer[30];
uint8_t host_codec_rx_buffer[30];
uint8_t host_codec_version_cache[4];
uint8_t host_uart_input[64];
uint16_t host_uart_input_length;
uint16_t host_uart_input_position;
uint8_t host_uart_output[64];
uint16_t host_uart_output_length;
uint8_t host_response_body[16];
uint16_t host_response_body_length;
uint64_t host_now_ms;
uint32_t host_delay_calls;
uint32_t host_init_calls;
uint32_t host_close_calls;
uint32_t host_baud;
uint32_t host_alloc_calls;
uint32_t host_free_calls;
uint32_t host_send_wait_calls;
uint32_t host_release_calls;
uint16_t host_last_command_low;
uint16_t host_last_command_high;
uint16_t host_last_body_length;
uint8_t host_last_body[16];
uint8_t host_last_flag;
uint32_t host_last_timeout;
uint8_t host_last_enable;
uint8_t host_last_gain;
int32_t host_init_result;
int32_t host_close_result;
int32_t host_write_result;
int32_t host_pack_result;
int32_t host_send_result;
int32_t host_read_result;
int32_t host_unpack_result;
int32_t host_send_wait_result;
uint32_t host_send_wait_failures;
int32_t host_low_level_result;
uint16_t host_low_level_status16;
uint8_t host_low_level_status8;
uint8_t host_version_result[4];

int32_t host_codec_uart_port_init(void) { ++host_init_calls; return host_init_result; }
int32_t host_codec_uart_port_close(void) { ++host_close_calls; return host_close_result; }
void host_codec_uart_set_baud(uint32_t baud) { host_baud = baud; }
int32_t host_codec_uart_write(const uint8_t *data, uint16_t length)
{
    if (length > sizeof(host_uart_output)) return -1;
    memcpy(host_uart_output, data, length);
    host_uart_output_length = length;
    return host_write_result;
}
int32_t host_codec_uart_read(uint8_t *data, uint16_t length)
{
    uint16_t available;
    if (host_uart_input_position >= host_uart_input_length) return 0;
    available = (uint16_t)(host_uart_input_length - host_uart_input_position);
    if (length > available) length = available;
    memcpy(data, host_uart_input + host_uart_input_position, length);
    host_uart_input_position = (uint16_t)(host_uart_input_position + length);
    return (int32_t)length;
}
uint64_t host_codec_time_ms(void) { return host_now_ms; }
void host_codec_delay(uint32_t ticks) { ++host_delay_calls; host_now_ms += ticks; }
uint32_t host_codec_crc32(const void *data, uint16_t length)
{
    const uint8_t *bytes = (const uint8_t *)data;
    uint32_t crc = 0xffffffffu;
    uint16_t index;
    uint8_t bit;
    for (index = 0u; index < length; ++index) {
        crc ^= bytes[index];
        for (bit = 0u; bit < 8u; ++bit) {
            crc = (crc >> 1) ^ ((crc & 1u) ? 0xedb88320u : 0u);
        }
    }
    return crc ^ 0xffffffffu;
}
void *host_codec_allocate(uint32_t length) { ++host_alloc_calls; return malloc(length); }
void host_codec_free(void *pointer) { ++host_free_calls; free(pointer); }

int32_t host_codec_host_init(void) { ++host_init_calls; return host_init_result; }
int32_t host_codec_host_cleanup(void) { ++host_close_calls; return host_close_result; }
int32_t host_codec_host_pack(uint16_t command_low, uint16_t command_high,
    const uint8_t *body, uint16_t body_length, uint8_t with_body_crc,
    uint8_t *wire, uint16_t *wire_length)
{
    host_last_command_low = command_low;
    host_last_command_high = command_high;
    host_last_body_length = body_length;
    host_last_flag = with_body_crc;
    if (body != NULL && body_length <= sizeof(host_last_body))
        memcpy(host_last_body, body, body_length);
    if (host_pack_result == 0) { wire[0] = 0xaau; *wire_length = 1u; }
    return host_pack_result;
}
int32_t host_codec_host_unpack(const uint8_t *wire, uint16_t wire_length,
    void *message, const void *context)
{
    host_message_t *response = (host_message_t *)message;
    (void)wire; (void)wire_length; (void)context;
    if (host_unpack_result == 0) {
        response->body = host_response_body;
        response->body_length = host_response_body_length;
    }
    return host_unpack_result;
}
int32_t host_codec_host_send(uint16_t command_low, uint16_t command_high,
    const uint8_t *body, uint16_t body_length, uint8_t with_body_crc)
{
    host_last_command_low = command_low; host_last_command_high = command_high;
    host_last_body_length = body_length; host_last_flag = with_body_crc;
    if (body != NULL && body_length <= sizeof(host_last_body))
        memcpy(host_last_body, body, body_length);
    return host_send_result;
}
int32_t host_codec_host_read_blocking(uint8_t *wire, uint16_t capacity,
    uint32_t timeout_ms, const void *context)
{
    (void)wire; (void)capacity; (void)context; host_last_timeout = timeout_ms;
    return host_read_result;
}
int32_t host_codec_host_read(uint8_t *wire, uint16_t capacity,
    uint16_t *wire_length, uint32_t timeout_ms)
{
    (void)wire; (void)capacity; host_last_timeout = timeout_ms;
    if (host_read_result == 0) *wire_length = host_uart_input_length;
    return host_read_result;
}
int32_t host_codec_host_send_wait(uint16_t command_low, uint16_t command_high,
    const uint8_t *body, uint16_t body_length, uint8_t with_body_crc,
    void *response_pointer, uint32_t timeout_ms)
{
    host_message_t *response = (host_message_t *)response_pointer;
    ++host_send_wait_calls;
    host_last_command_low = command_low; host_last_command_high = command_high;
    host_last_body_length = body_length; host_last_flag = with_body_crc;
    host_last_timeout = timeout_ms;
    if (body != NULL && body_length <= sizeof(host_last_body))
        memcpy(host_last_body, body, body_length);
    if (host_send_wait_calls <= host_send_wait_failures) return -9;
    if (host_send_wait_result != 0) return host_send_wait_result;
    response->body = host_response_body;
    response->body_length = host_response_body_length;
    return 0;
}
void host_codec_host_release(void *message_pointer)
{
    host_message_t *message = (host_message_t *)message_pointer;
    ++host_release_calls;
    message->body = NULL;
    message->body_length = 0u;
}

int32_t host_codec_read_version(uint8_t *version, uint32_t timeout_ms)
{ memcpy(version, host_version_result, 4u); host_last_timeout = timeout_ms; return host_low_level_result; }
int32_t host_codec_switch_bf(uint8_t *status, uint32_t timeout_ms)
{ *status = host_low_level_status8; host_last_timeout = timeout_ms; return host_low_level_result; }
int32_t host_codec_switch_wakeup(uint8_t *status, uint32_t timeout_ms)
{ *status = host_low_level_status8; host_last_timeout = timeout_ms; return host_low_level_result; }
int32_t host_codec_set_mic_gain(uint8_t gain, uint16_t *status, uint32_t timeout_ms)
{ host_last_gain = gain; *status = host_low_level_status16; host_last_timeout = timeout_ms; return host_low_level_result; }
int32_t host_codec_dmic_control(uint8_t enable, uint16_t *status, uint32_t timeout_ms)
{ host_last_enable = enable; *status = host_low_level_status16; host_last_timeout = timeout_ms; return host_low_level_result; }
int32_t host_codec_i2s_control(uint8_t enable, uint8_t *status, uint32_t timeout_ms)
{ host_last_enable = enable; *status = host_low_level_status8; host_last_timeout = timeout_ms; return host_low_level_result; }
int32_t host_codec_mic_delay(uint8_t *status, uint32_t timeout_ms)
{ *status = host_low_level_status8; host_last_timeout = timeout_ms; return host_low_level_result; }
