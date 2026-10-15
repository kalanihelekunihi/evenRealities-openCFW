/* Native Apollo Main callback 0x4b3bec. The selected caller passes a
 * three-byte event and ignores the returned event class. The stock body
 * reads the 16-bit event ID and returns event[2], without writing state. */
#include <stdint.h>

uint32_t audio_ble_subsystem_primary_handler_4b3bec(const uint8_t *event)
{
    volatile const uint16_t *event_id = (volatile const uint16_t *)(const void *)event;
    (void)*event_id;
    return ((volatile const uint8_t *)event)[2];
}
