/* Apollo dmDevPassEvtToConnCte 0x4b3008.
 * Four-byte event record: connection ID, zero, 0x6f, event type. */
#include <stdint.h>

extern uint8_t audio_ble_dm_config[]; /* RAM 0x20000694 */

void audio_ble_dm_dev_pass_conn_cte_4b3008(uint8_t event, uint8_t connection_id)
{
    uint8_t record[4] = {connection_id, 0u, 0x6fu, event};
    const uint8_t *slot = audio_ble_dm_config + 0x34u;
    uint32_t owner = (uint32_t)slot[0u] | ((uint32_t)slot[1u] << 8u) |
                     ((uint32_t)slot[2u] << 16u) |
                     ((uint32_t)slot[3u] << 24u);
    void (*callback)(const void *) =
        *(void (**)(const void *))(void *)(uintptr_t)(owner + 8u);
    callback(record);
}
