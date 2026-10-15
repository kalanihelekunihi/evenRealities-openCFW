#include <stdint.h>

/* Native ROM 0x78efec: one Thumb entry 0x004b6531 for dmConnUpdExecute. */
extern void audio_ble_dm_conn_upd_execute_4b6532(void *, const void *);
typedef void (*audio_ble_dm_conn_update_entry_t)(void *, const void *);
const audio_ble_dm_conn_update_entry_t audio_ble_dm_conn_state_table_b[1] = {
    audio_ble_dm_conn_upd_execute_4b6532,
};
