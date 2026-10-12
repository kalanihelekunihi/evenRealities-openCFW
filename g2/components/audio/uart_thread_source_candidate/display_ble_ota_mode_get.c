/* Native 0x46efec: raw byte from shared live cell 0x20074f8b. */
#include <stdint.h>
extern volatile uint8_t audio_ble_slave_unpair_flag_20074f8b;
uint32_t ble_ota_mode_get(void)
{
    return audio_ble_slave_unpair_flag_20074f8b;
}
