#include "service_codec_porting_host.h"

uint8_t host_codec_init_flag;
uint8_t host_codec_active_flag;
uint8_t host_codec_ring[32];
uint8_t host_codec_rx_buffer[64];
uint32_t host_codec_ring_init_calls;
uint32_t host_codec_callback_calls;
uint32_t host_codec_resume_calls;
uint32_t host_codec_suspend_calls;
uint32_t host_codec_last_port;
size_t host_codec_last_ring_size;
void *host_codec_last_ring;
uint8_t *host_codec_last_buffer;
void (*host_codec_last_callback)(void);
int32_t host_codec_resume_result;
int32_t host_codec_suspend_result;

void host_codec_rx_callback(void) {}
void host_codec_ring_init(void *ring, uint8_t *buffer, size_t size)
{
    ++host_codec_ring_init_calls;
    host_codec_last_ring = ring;
    host_codec_last_buffer = buffer;
    host_codec_last_ring_size = size;
}
void host_codec_uart_set_rx_callback(uint32_t port, void (*callback)(void))
{
    ++host_codec_callback_calls;
    host_codec_last_port = port;
    host_codec_last_callback = callback;
}
int32_t host_codec_uart_resume(uint32_t port)
{
    ++host_codec_resume_calls;
    host_codec_last_port = port;
    return host_codec_resume_result;
}
int32_t host_codec_uart_suspend(uint32_t port)
{
    ++host_codec_suspend_calls;
    host_codec_last_port = port;
    return host_codec_suspend_result;
}
