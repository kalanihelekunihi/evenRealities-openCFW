/* Native Cordio dmAdvInit 0x4b30e4 and dmAdvCbInit 0x4b3098. */
#include <stdint.h>

extern uint8_t audio_ble_dm_adv_control[]; /* live RAM 0x20073394 */
extern uint8_t audio_ble_dm_handler_state[]; /* selected live RAM 0x20073b78 */

static void half(uint8_t *p,uint16_t v) {
    p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);
}
void audio_ble_dm_adv_callback_init(uint8_t index) {
    audio_ble_dm_adv_control[0x18u+index]=0xffu;
    half(audio_ble_dm_adv_control+0x10u+(uint32_t)index*2u,0x640u);
    half(audio_ble_dm_adv_control+0x14u+(uint32_t)index*2u,0x780u);
    audio_ble_dm_adv_control[0x1au+index]=7u;
    audio_ble_dm_handler_state[0x11u+index]=0u;
    audio_ble_dm_adv_control[0x1du+index]=0u;
}
void audio_ble_dm_adv_lower(void) {
    for(uint8_t index=0;index<2u;index++)
        audio_ble_dm_adv_callback_init(index);
    audio_ble_dm_adv_control[0xcu]=audio_ble_dm_handler_state[0xcu];
    audio_ble_dm_handler_state[0xeu]=0u;
}
