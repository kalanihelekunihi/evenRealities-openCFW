/* Terminal FSM session-list update, stock 0x5ed318..0x5ed490. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0];
extern int32_t audio_td_current_session_index_signed(void);
extern void audio_terminal_ui_stop_service_b_5ec268(void);
extern void audio_terminal_ui_stop_service_c_5ebbc6(void);
extern void audio_terminal_ui_stop_service_d_5ec770(void);
extern void audio_terminal_ui_stop_service_e_5ec9c0(void);
extern void audio_terminal_reset_mode_5eae2c(uint32_t);
extern int32_t audio_terminal_ui_action_5e57c6(uint32_t,uint32_t);
extern void audio_terminal_session_list_rebuild_5ecef6(int32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="terminal.ui";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_session_list_ui.c";
static const char function[]="terminal_ui_action_session_list_update";
static const char deferred[]="session list update deferred while loading: selected=%d clear=%d keep=%d";
static const char deferred_short[]="[terminal.ui]session list update deferred while loading: selected=%d clear=%d keep=%d";
static const char updated[]="session list update: state=%d selected=%d clear=%d keep=%d";
static const char updated_short[]="[terminal.ui]session list update: state=%d selected=%d clear=%d keep=%d";

uint32_t audio_terminal_ui_action_5ed318(uint32_t old_state,uint32_t payload) {
    uint32_t clear=(payload>>31)&1u;
    uint32_t keep=(payload>>30)&1u;
    int32_t selected=keep!=0u?
        *(const int16_t *)(const void *)(audio_terminal_ui_state_base+0x27au):
        audio_td_current_session_index_signed();
    if (clear!=0u) {
        audio_terminal_ui_stop_service_b_5ec268();
        audio_terminal_ui_stop_service_c_5ebbc6();
        audio_terminal_ui_stop_service_d_5ec770();
        audio_terminal_ui_stop_service_e_5ec9c0();
        audio_terminal_ui_state_base[0x280u]=0u;
        *(uint32_t *)(void *)(audio_terminal_ui_state_base+0x284u)=0u;
        audio_terminal_reset_mode_5eae2c(4u);
        if ((uint8_t)old_state==2u || (uint8_t)old_state==12u)
            (void)audio_terminal_ui_action_5e57c6((uint8_t)old_state,0u);
    }
    if ((uint8_t)old_state==11u && audio_terminal_ui_state_base[0x27du]!=0u) {
        *(int16_t *)(void *)(audio_terminal_ui_state_base+0x27au)=(int16_t)selected;
        if ((audio_log_flags()&2u)!=0u)
            audio_log_extended(3u,module,path,function,0x1eau,deferred,
                               (uint32_t)(int16_t)selected,clear,keep);
        if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x0cc00000u,deferred_short,deferred_short,
                                        (uint32_t)(int16_t)selected,clear,keep);
        return 0u;
    }
    if ((uint8_t)old_state==11u)
        audio_terminal_session_list_rebuild_5ecef6((int16_t)selected);
    else
        *(int16_t *)(void *)(audio_terminal_ui_state_base+0x27au)=(int16_t)selected;
    if ((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,function,0x1f3u,updated,
                           (uint32_t)(uint8_t)old_state,
                           (uint32_t)(int16_t)selected,clear,keep);
    if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0d000000u,updated_short,updated_short,
                                    (uint32_t)(uint8_t)old_state,
                                    (uint32_t)(int16_t)selected,clear,keep);
    return 0u;
}
