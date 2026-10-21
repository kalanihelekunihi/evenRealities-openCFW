/* Apollo Main ROM 0x776a84: Cordio dmConnActSetMain[6].
 * Order follows third-party/upstream/cordio/ble-host/sources/stack/dm/dm_conn.c
 * and the six pinned Thumb pointers at the stock address. */
#include <stdint.h>

typedef void (*audio_ble_dm_action)(void *, void *);
extern void audio_ble_dm_conn_sm_act_none_4b63ca(void *, void *);
extern void audio_ble_dm_conn_sm_act_close_4b63cc(void *, void *);
extern void audio_ble_dm_conn_sm_act_opened_4b63d8(void *, void *);
extern void audio_ble_dm_conn_sm_act_failed_4b6488(void *, void *);
extern void audio_ble_dm_conn_sm_act_closed_4b64ce(void *, void *);
extern void audio_ble_dm_conn_sm_act_hci_updated_4b6508(void *, void *);

const audio_ble_dm_action audio_ble_dm_conn_state_table_a[6] = {
    audio_ble_dm_conn_sm_act_none_4b63ca,
    audio_ble_dm_conn_sm_act_close_4b63cc,
    audio_ble_dm_conn_sm_act_opened_4b63d8,
    audio_ble_dm_conn_sm_act_failed_4b6488,
    audio_ble_dm_conn_sm_act_closed_4b64ce,
    audio_ble_dm_conn_sm_act_hci_updated_4b6508,
};

_Static_assert(sizeof(audio_ble_dm_conn_state_table_a) == 24u,
               "Cordio main connection action-set size");
