#include <stdint.h>

extern uint8_t audio_ble_atts_ccc_runtime_20073b00[];

/* Native 0x52bb64. The event's byte 3 retains the high byte of the
 * incoming connection register after its low half is rewritten. */
void audio_ble_atts_ccc_update_52bb64(uint32_t connection, uint32_t route,
                                       uint32_t operation, uint32_t value)
{
    uint8_t event[9];
    event[0] = (uint8_t)connection;
    event[1] = 0u;
    event[2] = 0x14u;
    event[3] = (uint8_t)(connection >> 24u);
    event[4] = (uint8_t)operation;
    event[5] = (uint8_t)(operation >> 8u);
    event[6] = (uint8_t)value;
    event[7] = (uint8_t)(value >> 8u);
    event[8] = (uint8_t)route;
    uint32_t callback = *(const uint32_t *)(const void *)
        (audio_ble_atts_ccc_runtime_20073b00 + 0x10u);
    ((void (*)(void *))(uintptr_t)callback)(event);
}
