/* Distinct native input queues, direct ring descriptor, and failure text. */
#include <stdint.h>

void *audio_uart_input_mutex __attribute__((section(".g2_ram_200744e8")));
void *audio_uart_input_queue __attribute__((section(".g2_ram_200744e4")));
void *audio_uart_sync_schedule_queue __attribute__((section(".g2_ram_200749cc")));
void *audio_uart_input_event_flags __attribute__((section(".g2_ram_20074b10")));
uint32_t g2_display_ring[5] __attribute__((section(".g2_ram_20073b60")));
const char audio_uart_input_queue_failure_context[] =
    "input: message queue send failed";
