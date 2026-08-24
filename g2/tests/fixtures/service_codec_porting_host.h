#include <stddef.h>
#include <stdint.h>

extern uint8_t host_codec_init_flag;
extern uint8_t host_codec_active_flag;
extern uint8_t host_codec_ring[32];
extern uint8_t host_codec_rx_buffer[64];
void host_codec_rx_callback(void);
void host_codec_ring_init(void *ring, uint8_t *buffer, size_t size);
void host_codec_uart_set_rx_callback(uint32_t port, void (*callback)(void));
int32_t host_codec_uart_resume(uint32_t port);
int32_t host_codec_uart_suspend(uint32_t port);

#define OPEN_CFW_CODEC_INIT_FLAG host_codec_init_flag
#define OPEN_CFW_CODEC_ACTIVE_FLAG host_codec_active_flag
#define OPEN_CFW_CODEC_RING ((void *)host_codec_ring)
#define OPEN_CFW_CODEC_RX_BUFFER host_codec_rx_buffer
#define OPEN_CFW_CODEC_RX_CALLBACK host_codec_rx_callback
#define OPEN_CFW_CODEC_RING_INIT(ring, buffer, size) \
    host_codec_ring_init((ring), (buffer), (size))
#define OPEN_CFW_CODEC_UART_SET_RX_CALLBACK(port, callback) \
    host_codec_uart_set_rx_callback((port), (callback))
#define OPEN_CFW_CODEC_UART_RESUME(port) host_codec_uart_resume((port))
#define OPEN_CFW_CODEC_UART_SUSPEND(port) host_codec_uart_suspend((port))
