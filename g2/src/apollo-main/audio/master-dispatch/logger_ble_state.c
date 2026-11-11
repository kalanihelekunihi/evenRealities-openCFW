/* Native logger BLE enable flag and observed descriptor prefix. */
#include <stdint.h>

volatile uint8_t audio_uart_logger_ble_enabled
    __attribute__((section(".g2_ram_20074fe2")));

/* Setter writes byte 8 and a 32-bit callback at byte 12. */
uint8_t audio_uart_ble_logger_descriptor[16]
    __attribute__((section(".g2_ram_20073b90")));
/* Stock 0x20073b90 is a single 16-byte sink table: one literal-pool word 0x448fcc is
 * loaded by the UART sink setter 0x448c74 (+0x00/+0x04), the BLE sink setter 0x448cb8
 * (+0x08/+0x0c) and the transport 0x448dd2. g2_elog_sink is entry 0 (Fix 33). */
extern uint8_t g2_elog_sink[8] __attribute__((alias("audio_uart_ble_logger_descriptor")));
