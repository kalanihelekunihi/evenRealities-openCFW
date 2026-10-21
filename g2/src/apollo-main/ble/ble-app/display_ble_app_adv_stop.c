/* Pinned Cordio app_slave.c appAdvStop, native Main 0x4b43fc.
 * Its child 0x4b46a8 is already selected as audio_ble_app_adv_state. */
#include <stdint.h>
extern uint8_t audio_ble_subsystem_link_state_200719c8[];
extern uint8_t audio_ble_app_adv_state(void);
extern void DmAdvStop(uint8_t number_of_sets,const uint8_t *handles);

void appAdvStop(uint8_t number_of_sets,const uint8_t *handles)
{
    if (number_of_sets==0u) {
        for (uint8_t i=0u;i<2u;i++)
            audio_ble_subsystem_link_state_200719c8[0x57u+i]=3u;
    } else {
        for (uint8_t i=0u;i<number_of_sets;i++)
            audio_ble_subsystem_link_state_200719c8[0x57u+handles[i]]=3u;
    }
    if (!audio_ble_app_adv_state())
        audio_ble_subsystem_link_state_200719c8[0x5du]=0xffu;
    DmAdvStop(number_of_sets,handles);
}
