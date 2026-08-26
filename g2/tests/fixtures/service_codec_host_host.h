#include <stddef.h>
#include <stdint.h>

extern uint8_t host_codec_sequence;
extern uint8_t host_codec_tx_buffer[30];
extern uint8_t host_codec_rx_buffer[30];
extern uint8_t host_codec_version_cache[4];

int32_t host_codec_uart_port_init(void);
int32_t host_codec_uart_port_close(void);
void host_codec_uart_set_baud(uint32_t baud);
int32_t host_codec_uart_write(const uint8_t *data, uint16_t length);
int32_t host_codec_uart_read(uint8_t *data, uint16_t length);
uint64_t host_codec_time_ms(void);
void host_codec_delay(uint32_t ticks);
uint32_t host_codec_crc32(const void *data, uint16_t length);
void *host_codec_allocate(uint32_t length);
void host_codec_free(void *pointer);

int32_t host_codec_host_init(void);
int32_t host_codec_host_cleanup(void);
int32_t host_codec_host_pack(uint16_t command_low, uint16_t command_high,
    const uint8_t *body, uint16_t body_length, uint8_t with_body_crc,
    uint8_t *wire, uint16_t *wire_length);
int32_t host_codec_host_unpack(const uint8_t *wire, uint16_t wire_length,
    void *message, const void *context);
int32_t host_codec_host_send(uint16_t command_low, uint16_t command_high,
    const uint8_t *body, uint16_t body_length, uint8_t with_body_crc);
int32_t host_codec_host_read_blocking(uint8_t *wire, uint16_t capacity,
    uint32_t timeout_ms, const void *context);
int32_t host_codec_host_read(uint8_t *wire, uint16_t capacity,
    uint16_t *wire_length, uint32_t timeout_ms);
int32_t host_codec_host_send_wait(uint16_t command_low, uint16_t command_high,
    const uint8_t *body, uint16_t body_length, uint8_t with_body_crc,
    void *response, uint32_t timeout_ms);
void host_codec_host_release(void *message);

int32_t host_codec_read_version(uint8_t *version, uint32_t timeout_ms);
int32_t host_codec_switch_bf(uint8_t *status, uint32_t timeout_ms);
int32_t host_codec_switch_wakeup(uint8_t *status, uint32_t timeout_ms);
int32_t host_codec_set_mic_gain(uint8_t gain, uint16_t *status,
    uint32_t timeout_ms);
int32_t host_codec_dmic_control(uint8_t enable, uint16_t *status,
    uint32_t timeout_ms);
int32_t host_codec_i2s_control(uint8_t enable, uint8_t *status,
    uint32_t timeout_ms);
int32_t host_codec_mic_delay(uint8_t *status, uint32_t timeout_ms);

#define OPEN_CFW_CODEC_SEQUENCE host_codec_sequence
#define OPEN_CFW_CODEC_TX_BUFFER host_codec_tx_buffer
#define OPEN_CFW_CODEC_RX_BUFFER host_codec_rx_buffer
#define OPEN_CFW_CODEC_VERSION_CACHE host_codec_version_cache
#define OPEN_CFW_CODEC_UART_PORT_INIT() host_codec_uart_port_init()
#define OPEN_CFW_CODEC_UART_PORT_CLOSE() host_codec_uart_port_close()
#define OPEN_CFW_CODEC_UART_SET_BAUD(baud) host_codec_uart_set_baud((baud))
#define OPEN_CFW_CODEC_UART_WRITE(data, length) \
    host_codec_uart_write((data), (length))
#define OPEN_CFW_CODEC_UART_READ(data, length) \
    host_codec_uart_read((data), (length))
#define OPEN_CFW_CODEC_TIME_MS() host_codec_time_ms()
#define OPEN_CFW_CODEC_DELAY(ticks) host_codec_delay((ticks))
#define OPEN_CFW_CODEC_CRC32(data, length) host_codec_crc32((data), (length))
#define OPEN_CFW_CODEC_ALLOCATE(length) host_codec_allocate((length))
#define OPEN_CFW_CODEC_FREE(pointer) host_codec_free((pointer))
#define OPEN_CFW_CODEC_HOST_INIT() host_codec_host_init()
#define OPEN_CFW_CODEC_HOST_CLEANUP() host_codec_host_cleanup()
#define OPEN_CFW_CODEC_HOST_PACK(command_low, command_high, body, body_length, \
        with_body_crc, wire, wire_length) \
    host_codec_host_pack((command_low), (command_high), (body), (body_length), \
        (with_body_crc), (wire), (wire_length))
#define OPEN_CFW_CODEC_HOST_UNPACK(wire, wire_length, message, context) \
    host_codec_host_unpack((wire), (wire_length), (void *)(message), (context))
#define OPEN_CFW_CODEC_HOST_SEND(command_low, command_high, body, body_length, \
        with_body_crc) \
    host_codec_host_send((command_low), (command_high), (body), (body_length), \
        (with_body_crc))
#define OPEN_CFW_CODEC_HOST_READ_BLOCKING(wire, capacity, timeout_ms, context) \
    host_codec_host_read_blocking((wire), (capacity), (timeout_ms), (context))
#define OPEN_CFW_CODEC_HOST_READ(wire, capacity, wire_length, timeout_ms) \
    host_codec_host_read((wire), (capacity), (wire_length), (timeout_ms))
#define OPEN_CFW_CODEC_HOST_SEND_WAIT(command_low, command_high, body, \
        body_length, with_body_crc, response, timeout_ms) \
    host_codec_host_send_wait((command_low), (command_high), (body), \
        (body_length), (with_body_crc), (void *)(response), (timeout_ms))
#define OPEN_CFW_CODEC_HOST_RELEASE(message) \
    host_codec_host_release((void *)(message))
#define OPEN_CFW_CODEC_READ_VERSION(version, timeout_ms) \
    host_codec_read_version((version), (timeout_ms))
#define OPEN_CFW_CODEC_SWITCH_BF(status, timeout_ms) \
    host_codec_switch_bf((status), (timeout_ms))
#define OPEN_CFW_CODEC_SWITCH_WAKEUP(status, timeout_ms) \
    host_codec_switch_wakeup((status), (timeout_ms))
#define OPEN_CFW_CODEC_SET_MIC_GAIN(gain, status, timeout_ms) \
    host_codec_set_mic_gain((gain), (status), (timeout_ms))
#define OPEN_CFW_CODEC_DMIC_CONTROL(enable, status, timeout_ms) \
    host_codec_dmic_control((enable), (status), (timeout_ms))
#define OPEN_CFW_CODEC_I2S_CONTROL(enable, status, timeout_ms) \
    host_codec_i2s_control((enable), (status), (timeout_ms))
#define OPEN_CFW_CODEC_MIC_DELAY(status, timeout_ms) \
    host_codec_mic_delay((status), (timeout_ms))
