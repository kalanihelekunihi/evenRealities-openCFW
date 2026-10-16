/* Cordio dmConnSmActHciUpdated 0x4b6508.
 * Native writes event 0x29 then calls dmConnCb callback at +0x9c. */
#include <stdint.h>

extern uint8_t audio_dm_connection_records[]; /* RAM 0x200712a4 */

void audio_ble_dm_conn_sm_act_hci_updated_4b6508(void *ccb, void *message)
{
    (void)ccb;
    uint8_t *m = (uint8_t *)message;
    m[2u] = 0x29u;
    void (*callback)(void *) =
        *(void (**)(void *))(void *)(audio_dm_connection_records + 0x9cu);
    callback(message);
}
