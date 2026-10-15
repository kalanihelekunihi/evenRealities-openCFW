/* Native logger BLE enable flag and observed descriptor prefix. */
#include <stdint.h>

volatile uint8_t audio_uart_logger_ble_enabled
    __attribute__((section(".g2_ram_20074fe2")));

/* Setter writes byte 8 and a 32-bit callback at byte 12. */
uint8_t audio_uart_ble_logger_descriptor[16]
    __attribute__((section(".g2_ram_20073b90")));
