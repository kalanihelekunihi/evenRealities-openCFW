/* Pinned Cordio app_slave_leg.c state transitions, native Main
 * 0x4b2a04, 0x4b2a92 and 0x4b2aaa. */
#include <stdint.h>
extern uint8_t audio_ble_subsystem_link_state_200719c8[];
extern const uint8_t *audio_ble_slave_registration_slot;
extern uint8_t audio_ble_adv_transition_pending_20074f94;
extern uint8_t audio_ble_adv_timer_20073df4[];
extern uint8_t audio_ble_adv_handler_id_20074f92;
extern uint8_t audio_ble_dm_adv_state(uint8_t handle);
extern void WsfTimerStartMs(void *timer,uint32_t milliseconds);
extern void appAdvStart(uint8_t count,const uint8_t *handles,
                        const uint16_t *interval,const uint16_t *duration,
                        const uint8_t *maximum_events,uint8_t configure);
static uint16_t get16(const uint8_t *p) { return (uint16_t)p[0]|((uint16_t)p[1]<<8u); }
static void schedule_transition(void) {
    audio_ble_adv_transition_pending_20074f94=1u;
    audio_ble_adv_timer_20073df4[10u]=0x22u;
    audio_ble_adv_timer_20073df4[8u]=0u;
    audio_ble_adv_timer_20073df4[9u]=0u;
    audio_ble_adv_timer_20073df4[12u]=audio_ble_adv_handler_id_20074f92;
    WsfTimerStartMs(audio_ble_adv_timer_20073df4,200u);
}

void appSlaveLegAdvStart(void)
{
    uint8_t *const state=audio_ble_subsystem_link_state_200719c8;
    uint8_t current=state[0x57u];
    uint16_t interval=get16(audio_ble_slave_registration_slot+6u+(uint32_t)current*2u);
    if (!interval) { state[0x57u]=3u;return; }
    if (!audio_ble_dm_adv_state(0u)) {
        uint8_t handle=0u,maximum_events=0u;
        const uint16_t *duration=(const uint16_t *)(const void *)
            (audio_ble_slave_registration_slot+(uint32_t)current*2u);
        appAdvStart(1u,&handle,&interval,duration,&maximum_events,1u);
    } else if (!audio_ble_adv_transition_pending_20074f94) {
        schedule_transition();
    }
}

void appSlaveLegAdvTypeChanged(void *event)
{
    (void)event;
    audio_ble_subsystem_link_state_200719c8[0x5bu]=0u;
    audio_ble_subsystem_link_state_200719c8[0x57u]=0u;
    appSlaveLegAdvStart();
}

void appSlaveNextLegAdvState(void *event)
{
    (void)event;
    uint8_t *const state=audio_ble_subsystem_link_state_200719c8;
    state[0x57u]=(uint8_t)(state[0x57u]+1u);
    if (state[0x57u]<3u) {
        if (!audio_ble_dm_adv_state(0u)) appSlaveLegAdvStart();
        else if (!audio_ble_adv_transition_pending_20074f94)
            schedule_transition();
    }
}
