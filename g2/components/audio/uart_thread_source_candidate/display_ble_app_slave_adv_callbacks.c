/* Product Cordio legacy callbacks, native 0x4b2afe and 0x4b2b90.
 * The timeout flag/timer/handler are live product RAM with separate owners. */
#include <stdint.h>
extern uint8_t audio_ble_subsystem_link_state_200719c8[];
extern uint8_t audio_ble_adv_transition_pending_20074f94;
extern uint8_t audio_ble_adv_timer_20073df4[];
extern uint8_t audio_ble_adv_handler_id_20074f92;
extern uint8_t audio_ble_dm_adv_state(uint8_t handle); /* selected native 0x4bac4e */
extern void WsfTimerStartMs(void *timer,uint32_t milliseconds);
extern void WsfTimerStop(void *timer);
extern void appSlaveLegAdvTypeChanged(void *event);
extern void appSlaveNextLegAdvState(void *event);
extern void appSlaveLegAdvStart(void);

void appSlaveLegAdvStop(void *message)
{
    uint8_t *const event=(uint8_t *)message;
    if (event[2u]==0x48u && event[4u]==0u) return;
    if (event[2u]==0x22u) {
        uint8_t advertising=audio_ble_dm_adv_state(0u);
        if (!audio_ble_adv_transition_pending_20074f94) {
            if (advertising) audio_ble_adv_transition_pending_20074f94=1u;
        } else if (!advertising) {
            audio_ble_adv_transition_pending_20074f94=0u;
            WsfTimerStop(audio_ble_adv_timer_20073df4);
        }
        if (advertising) {
            audio_ble_adv_timer_20073df4[10u]=0x22u;
            audio_ble_adv_timer_20073df4[8u]=0u;
            audio_ble_adv_timer_20073df4[9u]=0u;
            audio_ble_adv_timer_20073df4[12u]=audio_ble_adv_handler_id_20074f92;
            WsfTimerStartMs(audio_ble_adv_timer_20073df4,100u);
            return;
        }
    }
    if (audio_ble_subsystem_link_state_200719c8[0x5bu])
        appSlaveLegAdvTypeChanged(message);
    else
        appSlaveNextLegAdvState(message);
}

void appSlaveLegAdvRestart(void *message)
{
    uint8_t *const event=(uint8_t *)message;
    uint8_t *const state=audio_ble_subsystem_link_state_200719c8;
    if (event[2u]==0x28u) {
        if (state[0x75u]) { state[0x75u]=0u;return; }
    } else if (event[2u]==0x27u) {
        if (state[0x75u]) { state[0x75u]=0u;return; }
        state[0x57u]=3u;
    }
    if (state[0x57u]==3u) {
        state[0x57u]=0u;
        appSlaveLegAdvStart();
    }
}
