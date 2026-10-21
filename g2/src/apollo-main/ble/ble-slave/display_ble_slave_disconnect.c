/* Native BLE slave disconnect dispatch 0x4bb04a and Cordio DmConnClose
 * 0x4b6c82, with the already selected live dmCb handler state. */
#include <stdint.h>

extern uint8_t audio_ble_dm_handler_state[]; /* native 0x20073b78 */
extern void *WsfMsgAlloc(uint16_t);
extern void WsfMsgSend(uint8_t,void *);

void audio_ble_dm_conn_close(uint8_t mode,uint16_t connection,uint8_t reason)
{
    uint8_t *packet=WsfMsgAlloc(0x24u);
    if (packet==0) return;
    packet[0]=(uint8_t)connection;
    packet[1]=0u;
    packet[2]=0x19u;
    packet[4]=reason;
    packet[3]=packet[4];
    packet[5]=mode;
    WsfMsgSend(audio_ble_dm_handler_state[0x0cu],packet);
}

void audio_ble_slave_disconnect_body(uint8_t connection)
{
    audio_ble_dm_conn_close(3u,connection,0x13u);
}

/* Native push {r7,lr} / pop {r0,pc}: inherited R7 becomes result R0. */
__attribute__((naked)) uint32_t audio_ble_slave_disconnect_event(
    uint8_t connection __attribute__((unused)))
{
    __asm__ volatile(
        "push {r7, lr}\n"
        "bl audio_ble_slave_disconnect_body\n"
        "pop {r0, pc}\n");
}
