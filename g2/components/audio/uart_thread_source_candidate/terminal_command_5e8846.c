/* Apollo terminal_action_mode_sync, native 0x5e8846. */
#include <stdint.h>
extern uint32_t audio_settings_terminal_mode(void);
extern void audio_settings_terminal_mode_set(uint32_t);
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
extern uint32_t audio_terminal_send_status_reply(const void *);
extern void audio_input_message_send_id4(uint32_t);
extern uint32_t audio_get_running_app_ids(uint32_t *,uint32_t *);
extern uint8_t audio_uart_device_role_get(void);
extern void audio_uart_master_display_stop(uint32_t,const void *,uint16_t,uint32_t);
extern void audio_td_state_reset(void);
extern void audio_terminal_reset_output_tracking(void);
extern void audio_terminal_runtime_event_callback_1(uint32_t,const void *);
extern void audio_ble_status_register_callback(void (*)(uint32_t,const void *));
extern void audio_ble_status_unregister_callback(void (*)(uint32_t,const void *));
extern void audio_os_delay(uint32_t);
extern void audio_uart_ring_wear_persist_48eb32(uint32_t,uint32_t,const void *);
extern uint32_t audio_system_alert_command_45a8ee(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t g2_flashdb_candidate_tick(void);
extern uint64_t audio_uart_ring_u64_div_47cc60(uint32_t,uint32_t,uint32_t,uint32_t);
extern void audio_ble_param_reset_delayed_event(uint32_t);
extern uint8_t audio_terminal_ui_mode;
uint8_t audio_terminal_mode_sync_pending; /* native RAM 0x2006e344 */
uint32_t audio_terminal_mode_start_tick; /* native RAM 0x20074a8c */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="terminal.pb";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_pb_msg_handler.c";
static const char function[]="terminal_action_mode_sync";
static const char null_message[]="terminal mode sync is null";
static const char null_short[]="[terminal.pb]terminal mode sync is null";
static const char received[]="mode_sync recv: current_mode_enable=%d -> target_mode_enable=%d ";
static const char received_short[]="[terminal.pb]mode_sync recv: current_mode_enable=%d -> target_mode_enable=%d ";
static const char unchanged[]="mode_sync no state change, send status reply";
static const char unchanged_short[]="[terminal.pb]mode_sync no state change, send status reply";
static const char running[]="terminal enter running apps: foreground=%d background=%d";
static const char running_short[]="[terminal.pb]terminal enter running apps: foreground=%d background=%d";
static const char running_failed[]="terminal mode enter, getRunningAppID failed";
static const char running_failed_short[]="[terminal.pb]terminal mode enter, getRunningAppID failed";
static const char startup[]="terminal mode enter, startup requested: use_time=%d";
static const char startup_short[]="[terminal.pb]terminal mode enter, startup requested: use_time=%d";
static const char already_closed[]="terminal mode exit, ui already closed, send status reply";
static const char already_closed_short[]="[terminal.pb]terminal mode exit, ui already closed, send status reply";

uint32_t audio_terminal_command_5e8846(const void *payload,uint32_t length) {
    (void)length;
    uint8_t reply[8];
    audio_uart_buffer_zero(reply,2u,0u);
    if(payload==0) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(1u,module,path,function,263u,null_message);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x04000000u,null_short,null_short);
        return UINT32_MAX;
    }
    uint8_t incoming=*(const uint8_t *)payload;
    uint32_t target=incoming==2u?1u:0u;
    uint32_t current=audio_settings_terminal_mode();
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,function,269u,received,current,target);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0c800000u,received_short,received_short,current,target);
    reply[0]=incoming;reply[1]=0u;
    if(target==current) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(3u,module,path,function,275u,unchanged);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x0c000000u,unchanged_short,unchanged_short);
        (void)audio_terminal_send_status_reply(reply);
        return 0u;
    }
    audio_input_message_send_id4(target);
    if(target==1u) {
        uint32_t background=0u,foreground=0u,delay=0u;
        if(audio_get_running_app_ids(&background,&foreground)==0u) {
            if((audio_log_flags()&2u)!=0u)
                audio_log_extended(3u,module,path,function,287u,running,foreground,background);
            if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
                (void)compressed_log_output(0x0c800000u,running_short,running_short,
                                            foreground,background);
            if(foreground!=0u) {
                if(audio_uart_device_role_get()==1u)
                    audio_uart_master_display_stop(foreground&0xffffu,0,0u,0u);
                delay=500u;
            }
            if(background!=0u) {
                if(audio_uart_device_role_get()==1u)
                    audio_uart_master_display_stop(background&0xffffu,0,0u,0u);
                delay+=500u;
            }
        } else {
            if((audio_log_flags()&2u)!=0u)
                audio_log_extended(2u,module,path,function,301u,running_failed);
            if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
                (void)compressed_log_output(0x08000000u,running_failed_short,running_failed_short);
        }
        audio_td_state_reset();
        audio_terminal_reset_output_tracking();
        audio_ble_status_register_callback(audio_terminal_runtime_event_callback_1);
        audio_terminal_mode_sync_pending=1u;
        if(delay==0u) delay=300u;
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(3u,module,path,function,309u,startup,delay);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x0c400000u,startup_short,startup_short,delay);
        audio_os_delay(delay);
        audio_settings_terminal_mode_set(1u);
        if(audio_uart_device_role_get()==1u) {
            const uint32_t descriptor[2]={5u,2u};
            audio_uart_ring_wear_persist_48eb32(0x40101u,2u,descriptor);
        }
        if(audio_uart_device_role_get()==1u) {
            (void)audio_system_alert_command_45a8ee(48u,0u,0u,0u);
            audio_terminal_mode_start_tick=g2_flashdb_candidate_tick();
        }
    } else {
        uint32_t elapsed=g2_flashdb_candidate_tick()-audio_terminal_mode_start_tick;
        uint64_t scaled=(uint64_t)elapsed*1000u;
        uint32_t duration=(uint32_t)audio_uart_ring_u64_div_47cc60((uint32_t)scaled,(uint32_t)(scaled>>32),1000u,0u);
        if(audio_uart_device_role_get()==1u) {
            const uint32_t descriptor[2]={5u,duration};
            audio_uart_ring_wear_persist_48eb32(0x40103u,2u,descriptor);
        }
        if(audio_uart_device_role_get()==1u) {
            const uint32_t descriptor[2]={5u,2u};
            audio_uart_ring_wear_persist_48eb32(0x40102u,2u,descriptor);
        }
        audio_settings_terminal_mode_set(0u);
        audio_td_state_reset();
        audio_terminal_reset_output_tracking();
        audio_ble_param_reset_delayed_event(10000u);
        audio_ble_status_unregister_callback(audio_terminal_runtime_event_callback_1);
        if(audio_terminal_ui_mode==0u) {
            if((audio_log_flags()&2u)!=0u)
                audio_log_extended(3u,module,path,function,335u,already_closed);
            if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
                (void)compressed_log_output(0x0c000000u,already_closed_short,already_closed_short);
            (void)audio_terminal_send_status_reply(reply);
        } else {
            audio_terminal_mode_sync_pending=1u;
            if(audio_uart_device_role_get()==1u)
                audio_uart_master_display_stop(48u,0,0u,0u);
        }
    }
    return 0u;
}
