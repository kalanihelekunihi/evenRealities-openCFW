/* Native Apollo Main BLE secondary callback 0x503936: return event[2]. */
#include <stdint.h>

uint32_t audio_ble_subsystem_handler_503936(const uint8_t *event)
{
    return event[2];
}
