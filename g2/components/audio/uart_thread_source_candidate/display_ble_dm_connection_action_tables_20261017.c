/* Cordio DM connection action tables at stock ROM 0x78d41c/0x78d424,
 * 0x785be0/0x78d42c. Rows follow the pinned dm_conn_{master,slave}
 * legacy action sets and update action sets; bodies remain independent. */
#include <stdint.h>

extern void audio_ble_dm_action_536a86(void);
extern void audio_ble_dm_action_55bc5c(void);
extern void audio_ble_dm_action_55bc70(void);
extern void audio_ble_dm_action_55bc7c(void);
extern void audio_ble_dm_action_536ac8(void);
extern void audio_ble_dm_action_536adc(void);
extern void audio_ble_dm_action_536af0(void);
extern void audio_ble_dm_action_536b04(void);
extern void audio_ble_dm_action_56e526(void);
extern void audio_ble_dm_action_56e564(void);

const uintptr_t audio_ble_dm_master_table_a[2] = {
    (uintptr_t)&audio_ble_dm_action_536a86,
    (uintptr_t)&audio_ble_dm_action_55bc5c,
};
const uintptr_t audio_ble_dm_master_table_b[2] = {
    (uintptr_t)&audio_ble_dm_action_55bc70,
    (uintptr_t)&audio_ble_dm_action_55bc7c,
};
const uintptr_t audio_ble_dm_slave_table_a[4] = {
    (uintptr_t)&audio_ble_dm_action_536ac8,
    (uintptr_t)&audio_ble_dm_action_536adc,
    (uintptr_t)&audio_ble_dm_action_536af0,
    (uintptr_t)&audio_ble_dm_action_536b04,
};
const uintptr_t audio_ble_dm_slave_table_b[2] = {
    (uintptr_t)&audio_ble_dm_action_56e526,
    (uintptr_t)&audio_ble_dm_action_56e564,
};

_Static_assert(sizeof(audio_ble_dm_master_table_a) == 8u, "DM master ABI");
_Static_assert(sizeof(audio_ble_dm_master_table_b) == 8u, "DM master update ABI");
_Static_assert(sizeof(audio_ble_dm_slave_table_a) == 16u, "DM slave ABI");
_Static_assert(sizeof(audio_ble_dm_slave_table_b) == 8u, "DM slave update ABI");
