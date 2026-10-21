/* Apollo Main BLE bond erase staging, stock base 0x200636a0.
 * The source-owned size word initializes to 0x0a00 bytes.
 */
#include <stdint.h>

uint8_t audio_ble_flash_staging_200636a0[0x0a00]
    __attribute__((section(".bss.opencfw.ble.flash.staging"), aligned(4), used));

_Static_assert(sizeof(audio_ble_flash_staging_200636a0) == 0x0a00u,
               "nominal stock bond flash byte count");
