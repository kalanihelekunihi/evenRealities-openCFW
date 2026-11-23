/* Apollo Main compressed SRAM record 0x75d3f4 initializes these adjacent
 * native cells at 0x200001b0 and 0x200001b4. The source graph owns their
 * exact values; absolute RAM placement and the full scatter remain open. */
#include <stdint.h>

volatile uint32_t audio_ble_hci_radio_platform_pin_200001b0 = 1u;
/* Not const: stock keeps this 20-byte template in SRAM at 0x200001b4
 * (init +4 = 0x00f42400 = 16 MHz). Acquire 0x52dd94 copies it; nothing
 * writes the cell first. A const object landed in .rodata (0x63a9cc) and
 * left the RAM cell zero. */
uint8_t audio_ble_hci_radio_resource_config_200001b4[20u] = {
    0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x24u, 0xf4u, 0x00u,
    0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u,
    0x00u, 0x00u, 0x00u, 0x00u,
};
