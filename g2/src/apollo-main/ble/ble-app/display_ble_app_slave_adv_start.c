/* Pinned Cordio app_slave.c appSlaveAdvStart and force-data sync;
 * native Main 0x4b446a, 0x4b33d2 and 0x4b467c. */
#include <stdint.h>
extern uint8_t audio_ble_subsystem_link_state_200719c8[];
extern uint8_t AppDbCheckBonded(void);
extern void appAdvStart(uint8_t count,const uint8_t *handles,
                        const uint16_t *interval,const uint16_t *duration,
                        const uint8_t *maximum_events,uint8_t configure);
static void set16(uint8_t *p,uint16_t v) { p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8u); }

void AppSetBondable(uint8_t bondable)
{
    audio_ble_subsystem_link_state_200719c8[0x54u]=bondable;
}

/* Existing product caller names the same native 0x4b467c entry by role. */
__attribute__((naked)) void audio_ble_app_adv_set_state(uint8_t bondable __attribute__((unused)))
{
    __asm volatile("b AppSetBondable");
}

void appSlaveForceAdvDataSync(uint8_t handle,uint8_t mode)
{
    uint8_t *const state=audio_ble_subsystem_link_state_200719c8;
    uint32_t offset=0x40u+(uint32_t)handle*8u+(uint32_t)mode*4u;
    set16(state+offset,0u);
    set16(state+offset+2u,0u);
    state[0x55u+handle]=0u;
}

void appSlaveAdvStart(uint8_t count,const uint8_t *handles,
                      const uint16_t *interval,const uint16_t *duration,
                      const uint8_t *maximum_events,uint8_t configure,uint8_t mode)
{
    uint8_t *const state=audio_ble_subsystem_link_state_200719c8;
    uint8_t previous=state[0x5du];
    if (mode==2u) {
        if (!AppDbCheckBonded()) {
            AppSetBondable(1u);
            state[0x5du]=1u;
        } else {
            AppSetBondable(0u);
            state[0x5du]=0u;
        }
    } else {
        AppSetBondable(1u); /* product native non-auto branch */
        state[0x5du]=mode;
    }
    if (previous!=state[0x5du]) {
        for (uint8_t i=0u;i<count;i++)
            appSlaveForceAdvDataSync(handles[i],state[0x5du]);
    }
    (void)configure; /* Native always configures on this entry. */
    appAdvStart(count,handles,interval,duration,maximum_events,1u);
}
