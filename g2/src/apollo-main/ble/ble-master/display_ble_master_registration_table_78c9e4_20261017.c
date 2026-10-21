/* Authenticated Main ROM record at 0x78c9e4, ending before "ble.mgr". */
#include <stdint.h>

__attribute__((used, section(".g2_flash_0078c9e4")))
const uint8_t audio_ble_master_registration_table[8] = {
    0xa0, 0x00, 0x80, 0x00, 0x10, 0x27, 0x00, 0x01
};

_Static_assert(sizeof(audio_ble_master_registration_table) == 8,
               "stock BLE master registration extent");
