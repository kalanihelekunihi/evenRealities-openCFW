/* Native APP_MasterPublishRingLinkReady 0x4a271e and its one-call event
 * bridge central_emit_ring_link_event 0x4a153c. Product RAM is externally
 * placed; no startup value is assigned here. */
#include <stdint.h>
extern volatile uint8_t audio_ble_ring_link_state; /* 0x20074f85 */
extern volatile uint8_t audio_ble_master_link_ready; /* 0x20074f89 */
extern volatile uint8_t audio_ble_master_connection_flag; /* 0x20074f84 */
extern volatile uint8_t audio_ble_master_publish_flag; /* 0x20074f88 */
extern uint8_t *audio_ble_master_context; /* pointer cell 0x200742fc */
extern void audio_ble_slave_security_state(uint8_t); /* selected 0x4b82e8 */
extern uint32_t audio_uart_ring_active(void); /* selected 0x4a2914 */
extern void audio_ble_ring_policy_notify_success_49f646(void);
extern void audio_ble_master_emit_ring_event(uint8_t); /* selected 0x4ac16c */
extern const char *audio_ble_ring_link_state_name(uint8_t); /* selected 0x49f828 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,...);
static const char module[]="ble.master";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_ble_central.c";
static const char function[]="APP_MasterPublishRingLinkReady";
static const char state_skipped[]="PublishRingLinkReady skipped: state=%s";
static const char state_skipped_short[]="[ble.master]PublishRingLinkReady skipped: state=%s";
static const char no_connection[]="PublishRingLinkReady skipped: no active master conn";
static const char no_connection_short[]="[ble.master]PublishRingLinkReady skipped: no active master conn";
static const char published[]="Ring link published to UX/App after touch enabled";
static const char published_short[]="[ble.master]Ring link published to UX/App after touch enabled";
void audio_ble_central_emit_ring_link_event_4a153c(uint8_t event) {
    audio_ble_master_emit_ring_event(event);
}
void audio_uart_ring_publish_link_ready_4a271e(void) {
    if(audio_ble_master_link_ready!=0u)return;
    if(audio_ble_ring_link_state!=2u) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(2u,module,path,function,0x521u,state_skipped,
                               audio_ble_ring_link_state_name(audio_ble_ring_link_state));
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x08400000u,state_skipped_short,state_skipped_short,
                                        audio_ble_ring_link_state_name(audio_ble_ring_link_state));
        return;
    }
    if(audio_ble_master_context==0 || audio_ble_master_context[0x55u]==0u) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(2u,module,path,function,0x525u,no_connection);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x08000000u,no_connection_short);
        return;
    }
    audio_ble_master_link_ready=1u;
    audio_ble_master_connection_flag=0u;
    audio_ble_master_publish_flag=1u;
    audio_ble_slave_security_state(3u);
    if(audio_uart_ring_active()!=0u)
        audio_ble_ring_policy_notify_success_49f646();
    audio_ble_central_emit_ring_link_event_4a153c(3u);
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,function,0x531u,published);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0c000000u,published_short,published_short);
}
