#include <stdint.h>
#include "../uart-rx/uart-rx-consumer/ring.h"

uart3_ring_t g2_audio_uart_ring_state
    __attribute__((section(".g2_ram_20073ed4"), used));
uint8_t g2_audio_uart_storage[64]
    __attribute__((section(".g2_ram_200731b0"), used));
volatile uint8_t g2_audio_uart_initialized
    __attribute__((section(".g2_ram_20075014"), used));
volatile uint8_t g2_audio_uart_resumed
    __attribute__((section(".g2_ram_20075015"), used));
volatile uint8_t g2_uart_service_nonce[4]
    __attribute__((section(".g2_ram_20074928"), used));
uint8_t g2_uart_driver_state[4u * 0x11cu]
    __attribute__((section(".g2_ram_2006a02c"), used));
