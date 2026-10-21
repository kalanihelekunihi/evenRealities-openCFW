/* Apollo Main compressed SRAM record 0x75d3f4 initializes this live
 * bond-flash byte count to 0x0a00 at native 0x20004524. It covers ten
 * 256-byte NVM rows in the selected erase path. Absolute RAM placement
 * and full startup scatter remain open. */
#include <stdint.h>

volatile uint16_t audio_ble_bond_flash_bytes_20004524 = 0x0a00u;
