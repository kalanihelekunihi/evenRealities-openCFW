#include <stdint.h>

extern uint32_t audio_ble_link_mask_select_47ae78(uint32_t, uint8_t, uint8_t *);
extern void audio_ble_dm_sec_resolve_52bb20(uint32_t, uint32_t, uint32_t, uint32_t);

/* Native 0x4b36b2. The selected byte and link pointer are passed to
 * the downstream security request as separate arguments. */
void audio_ble_slave_resolve_4b36b2(void *record)
{
    uint8_t *row = (uint8_t *)record;
    uint32_t handle = *(uint32_t *)record;
    uint8_t selected = 0u;
    uint32_t link = handle == 0u ? 0u :
        audio_ble_link_mask_select_47ae78(handle, 1u, &selected);
    if (link == 0u) {
        row[6] = 0u;
        audio_ble_dm_sec_resolve_52bb20(row[4], 0u, 0u, 0u);
    } else {
        row[6] = row[5] == 0u ? 1u : 0u;
        audio_ble_dm_sec_resolve_52bb20(row[4], 1u, selected, link);
    }
}
