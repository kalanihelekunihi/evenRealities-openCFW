/* Native DmSmpCbackExec 0x4d24a8 and pinned Cordio dm_sec.c. */
#include <stdint.h>
extern uint8_t audio_dm_connection_records[]; /* native dmConnCb RAM 0x200712a4 */
extern uint8_t audio_ble_dm_handler_state[];  /* native dmCb RAM 0x20073b78 */
typedef void (*dm_callback_t)(void *event);
void DmSmpCbackExec(void *event) {
    uint8_t code=((const uint8_t *)event)[2];
    if (code==0x2au || code==0x2cu) {
        dm_callback_t att=*(dm_callback_t *)(void *)(audio_dm_connection_records+0x90u);
        if (att) att(event);
    }
    dm_callback_t client=*(dm_callback_t *)(void *)(audio_ble_dm_handler_state+8u);
    client(event);
}
