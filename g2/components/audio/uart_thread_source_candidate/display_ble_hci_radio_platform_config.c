/* Apollo Main compressed SRAM record 0x75d3f4 initializes these adjacent
 * native cells at 0x200001b0 and 0x200001b4. The source graph owns their
 * exact values; absolute RAM placement and the full scatter remain open. */
#include <stdint.h>

volatile uint32_t audio_ble_hci_radio_platform_pin_200001b0 = 1u;
const uint8_t audio_ble_hci_radio_resource_config_200001b4[20u] = {
    0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x24u, 0xf4u, 0x00u,
    0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u,
    0x00u, 0x00u, 0x00u, 0x00u,
};
