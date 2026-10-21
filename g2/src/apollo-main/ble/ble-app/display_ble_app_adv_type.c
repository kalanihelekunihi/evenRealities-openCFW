/* Pinned Cordio app_slave.c appSetAdvType and native Main 0x4b4510.
 * Live appSlaveCb bytes remain an explicit product RAM contract. */
#include <stdint.h>
extern uint8_t audio_ble_subsystem_link_state_200719c8[];
extern void appSlaveResetAdvDataOffset(uint8_t handle);
extern void appAdvStart(uint8_t number_of_sets,const uint8_t *handles,
                        const uint16_t *intervals,const uint16_t *durations,
                        const uint8_t *maximum_events,uint8_t configure);
extern void DmAdvStop(uint8_t number_of_sets,const uint8_t *handles);

void appSetAdvType(uint8_t handle,uint8_t type,uint16_t interval,
                   uint16_t duration,uint8_t maximum_events,uint8_t configure)
{
    if (type==1u || type==4u) return;
    uint8_t *const state=audio_ble_subsystem_link_state_200719c8;
    if (state[0x59u+handle]==type) return;
    state[0x59u+handle]=type;
    if (state[0x5du]==0xffu) return;
    appSlaveResetAdvDataOffset(handle);
    if (state[0x57u+handle]==3u) {
        state[0x57u+handle]=0u;
        appAdvStart(1u,&handle,&interval,&duration,&maximum_events,configure);
    } else {
        state[0x5bu+handle]=1u;
        state[0x57u+handle]=3u;
        DmAdvStop(1u,&handle);
    }
}
