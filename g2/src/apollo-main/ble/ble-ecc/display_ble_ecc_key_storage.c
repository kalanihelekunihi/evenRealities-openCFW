/* Native 0x200726d0 mutable 96-byte ECC key object. DmSecSetEccKey
 * writes all 0x60 bytes; DmSecGetEccKey returns its base. The selected
 * source owns the storage, while native RAM placement remains a linker gate. */
#include <stdint.h>
uint8_t audio_ble_ecc_key_storage[0x60u];
