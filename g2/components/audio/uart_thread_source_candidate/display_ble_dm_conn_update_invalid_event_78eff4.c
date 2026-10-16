/* Apollo Main 0x78eff0 action-table adjacency, pinned s200_v2.2.6.10.
 * Cordio defines four valid action bytes. Stock indexes the table with the
 * low three event bits, so indices 4..7 read the adjacent Thumb function
 * pointer 0x004b2df9 at 0x78eff4. This bounded provider captures those
 * observed bytes for the current image; final relocation remains gated. */
#include <stdint.h>

uint8_t audio_ble_dm_conn_update_invalid_event_action(const void *message)
{
    uint8_t index = ((const uint8_t *)message)[2u] & 7u;
    static const uint8_t valid_actions[4u] = {0x10u, 0x20u, 0x11u, 0x21u};
    const uint32_t adjacent_thumb_pointer = 0x004b2df9u;
    if (index < 4u) {
        return valid_actions[index];
    }
    return (uint8_t)(adjacent_thumb_pointer >> ((uint32_t)(index - 4u) * 8u));
}
