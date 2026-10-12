/* Native attExecCallback 0x4b5074: callback event has defined bytes
 * 0..3, 8..12 and 14..15; bytes 4..7 and 13 remain ambient stack. */
#include <stdint.h>
extern uint8_t audio_ble_att_common_state[]; /* selected RAM 0x200610ac */
void audio_ble_att_exec_callback_4b5074(uint8_t connection,uint8_t operation,
                                         uint16_t handle,uint8_t status,uint16_t extra) {
    uintptr_t callback=*(volatile const uintptr_t *)(const void *)(audio_ble_att_common_state+0x58u);
    if(callback==0u)return;
    uint8_t event[16];
    *(uint16_t *)(void *)(event+0u)=connection;
    event[2u]=operation;
    event[3u]=status;
    *(uint16_t *)(void *)(event+8u)=0u;
    *(uint16_t *)(void *)(event+10u)=handle;
    event[12u]=0u;
    *(uint16_t *)(void *)(event+14u)=extra;
    ((void (*)(const void *))callback)(event);
}
