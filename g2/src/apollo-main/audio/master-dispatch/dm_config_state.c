#include <stdint.h>

/* Native compressed SRAM 0x20000694. DmPrivInit writes the last observed
 * four-byte slot at +0x3c. The full native allocation span is still open. */
uint8_t audio_ble_dm_config[0x40];
extern volatile uint8_t audio_ble_mode_runtime_20000694[0x40]
    __attribute__((alias("audio_ble_dm_config")));
