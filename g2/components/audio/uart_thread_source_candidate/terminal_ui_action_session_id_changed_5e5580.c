/* Terminal FSM session-id-change action, stock 0x5e5580..0x5e5767. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0];
extern uint8_t audio_ux_get_system_ble_status(void);
extern uint32_t audio_terminal_runtime_event_from_ble(uint32_t);
extern void audio_terminal_ui_stop_service_a_5eceb2(void);
extern void audio_terminal_ui_stop_service_b_5ec268(void);
extern void audio_terminal_ui_stop_service_c_5ebbc6(void);
extern void audio_terminal_ui_stop_service_d_5ec770(void);
extern void audio_terminal_ui_stop_service_e_5ec9c0(void);
extern void audio_terminal_reset_mode_5eae2c(uint32_t);
extern void audio_terminal_reset_ancillary_5e65f8(void);
extern void audio_terminal_ui_event_5e5484(uint32_t,uint32_t,uint32_t);
extern int32_t audio_terminal_ui_action_5e583c(uint32_t,uint32_t);
extern int32_t audio_terminal_ui_action_5e522e(uint32_t,uint32_t);
extern int32_t audio_terminal_ui_action_5e5290(uint32_t,uint32_t);
extern int32_t audio_terminal_ui_action_5e52c2(uint32_t,uint32_t);
extern int32_t audio_terminal_ui_action_5e6548(uint32_t,uint32_t);
extern int32_t audio_terminal_ui_action_5e641c(uint32_t,uint32_t);
extern int32_t audio_terminal_ui_action_5e57c6(uint32_t,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="terminal.ui";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_ui.c";
static const char function[]="terminal_ui_action_session_id_changed";
static const char blocked[]="session id changed while blocked, keep blocked UI";
static const char blocked_short[]="[terminal.ui]session id changed while blocked, keep blocked UI";
static const char activated[]="session id changed from notification activate: session=%lu";
static const char activated_short[]="[terminal.ui]session id changed from notification activate: session=%lu";
static const char restored[]="session id changed, visible content reset: restore=%d";
static const char restored_short[]="[terminal.ui]session id changed, visible content reset: restore=%d";

static uint32_t session_word(void) {
    const uint8_t *p=audio_terminal_ui_state_base+0x288u;
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}

int32_t audio_terminal_ui_action_5e5580(uint32_t old_state,uint32_t event_payload) {
    uint32_t old_byte=(uint8_t)old_state;
    uint32_t event=(uint8_t)audio_terminal_runtime_event_from_ble(
        audio_ux_get_system_ble_status());
    if (old_byte==3u && (event==2u || event==3u || event==4u)) {
        if ((audio_log_flags()&2u)!=0u)
            audio_log_extended(3u,module,path,function,0x3abu,blocked);
        if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x0c000000u,blocked_short,blocked_short);
        return 4;
    }
    audio_terminal_ui_stop_service_a_5eceb2();
    audio_terminal_ui_stop_service_b_5ec268();
    audio_terminal_ui_stop_service_c_5ebbc6();
    audio_terminal_ui_stop_service_d_5ec770();
    audio_terminal_ui_stop_service_e_5ec9c0();
    audio_terminal_reset_mode_5eae2c(4u);
    audio_terminal_ui_state_base[0x27eu]=0u;
    if (old_byte==10u && audio_terminal_ui_state_base[0x27fu]!=0u &&
        session_word()==event_payload) {
        (void)audio_terminal_ui_action_5e583c(old_byte,0u);
        audio_terminal_ui_event_5e5484(4u,event_payload,0u);
        audio_terminal_reset_ancillary_5e65f8();
        if ((audio_log_flags()&2u)!=0u)
            audio_log_extended(3u,module,path,function,0x3bbu,activated,event_payload);
        if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x0c400000u,activated_short,
                                        activated_short,event_payload);
        return 8;
    }
    if ((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,function,0x3bfu,restored,event);
    if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0c400000u,restored_short,restored_short,event);
    switch (event) {
    case 2u:(void)audio_terminal_ui_action_5e522e(old_byte,0u);return 4;
    case 3u:(void)audio_terminal_ui_action_5e5290(old_byte,0u);return 4;
    case 4u:(void)audio_terminal_ui_action_5e52c2(old_byte,0u);return 4;
    case 22u:(void)audio_terminal_ui_action_5e6548(old_byte,session_word());return 11;
    case 6u:(void)audio_terminal_ui_action_5e583c(old_byte,0u);return 8;
    case 7u:(void)audio_terminal_ui_action_5e641c(old_byte,1u);return 10;
    default:(void)audio_terminal_ui_action_5e57c6(old_byte,0u);return 3;
    }
}
