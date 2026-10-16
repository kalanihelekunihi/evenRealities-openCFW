/* Cordio dmDevPassEvtToDevPriv 0x4b2ea6: bounded event-forwarding path.
 * Native logging branches are retained as an unresolved product gate. */
#include <stdint.h>

extern uint8_t audio_ble_dm_config[]; /* native dmFcnIfTbl 0x20000694 */
typedef void (*audio_ble_dm_msg_handler)(void *);

void dmDevPassEvtToDevPriv(uint8_t event, uint8_t param,
                           uint8_t adv_handle, uint8_t connectable)
{
    uint8_t indication[6];
    indication[0u] = param;
    indication[1u] = 0u;
    indication[2u] = event;
    indication[4u] = adv_handle;
    indication[5u] = connectable;
    uint8_t *const interface = *(uint8_t **)(void *)(audio_ble_dm_config + 4u);
    (*(audio_ble_dm_msg_handler *)(void *)(interface + 8u))(indication);
}
