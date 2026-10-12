/* Native DmSecGetEccKey 0x53490c returns ECC key storage 0x200726d0. */
#include <stdint.h>
extern uint8_t audio_ble_ecc_key_storage[];
uint8_t *DmSecGetEccKey(void)
{
    return audio_ble_ecc_key_storage;
}
