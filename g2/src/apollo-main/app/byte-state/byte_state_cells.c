#include <stdint.h>

/* Each native RAM address has its own section for the final link. */
volatile uint8_t audio_ble_ring_link_state __attribute__((section(".g2_ram_20074f85")));
uint8_t audio_ble_slave_unpair_flag_20074f8b __attribute__((section(".g2_ram_20074f8b")));
uint8_t audio_ble_slave_link_flags_20074f8c __attribute__((section(".g2_ram_20074f8c")));
uint8_t audio_ble_slave_adv_stop_flag_20074f8d __attribute__((section(".g2_ram_20074f8d")));
uint8_t audio_uart_display_state[2] __attribute__((section(".g2_ram_20074f2c")));
extern volatile uint8_t g2_audio_log_wake_enabled
    __attribute__((alias("audio_uart_display_state")));
uint8_t g2_codec_i2s_initialized __attribute__((section(".g2_ram_20074fb7")));
