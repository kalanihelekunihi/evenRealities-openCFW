#include <stdint.h>

/* Native RAM state used by selected timers, handlers, and codec clock routing. */
uint32_t audio_ble_profile_runtime_rows[6] __attribute__((section(".g2_ram_20074310")));
uint32_t audio_ble_fast_mode_last_reject_tick __attribute__((section(".g2_ram_20074340")));
uint32_t audio_event_loop_base_tick __attribute__((section(".g2_ram_200745fc")));
volatile uint32_t audio_uart_logger_ble_timeout __attribute__((section(".g2_ram_200746b0")));
volatile uint32_t audio_uart_ring_touch_tick __attribute__((section(".g2_ram_20074900")));
volatile uint32_t audio_uart_ring_wear_tick __attribute__((section(".g2_ram_20074904")));
uint32_t g2_audio_notify_assert_enabled __attribute__((section(".g2_ram_20074a34")));
