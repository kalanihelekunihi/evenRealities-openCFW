/* APP_MasterCleanupRingUnpair, native 0x4a2c9c. Live cells retain product ownership. */
#include <stdint.h>
extern volatile uint8_t audio_ble_master_connect_state; /* 0x20074f87 */
extern volatile uint8_t audio_ble_master_publish_flag; /* 0x20074f88 */
extern volatile uint8_t audio_ble_master_link_ready; /* 0x20074f89 */
extern volatile uint8_t audio_ble_ring_link_state; /* 0x20074f85 */
extern volatile uint8_t audio_ble_master_open_connection; /* 0x20074f86 */
extern uint8_t *audio_ble_master_context; /* 0x200742fc */
extern uint8_t audio_uart_hand_record[0x30u]; /* 0x466010 -> RAM 0x200736d4 */
extern uint32_t audio_ble_master_auth_mode_set(uint8_t);
extern uint32_t audio_event_loop_remove_delayed(void (*)(void));
extern void audio_ble_master_connect_event(void);
extern void audio_ble_master_start_try_connect_ring(void); /* native 0x4a23ac */
extern void audio_ble_master_disconnect_delayed(uint32_t);
extern uint32_t audio_ble_master_success_delayed(uint32_t);
extern void audio_ble_master_followup_delayed(void);
extern void audio_ble_master_reset_retry_count(void);
extern void audio_ble_master_clear_failure_notify(void);
extern void audio_ble_ring_connect_policy_reset(void);
extern void audio_ble_master_set_target(const uint8_t *,const char *,uint8_t);
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
extern void audio_uart_ring_unpair_publish_hand_4661a6(void); /* native 0x4661a6 */
extern void audio_uart_ring_unpair_commit_hand_466016(void); /* native 0x466016 */
extern uint8_t audio_uart_device_role_get(void); /* native 0x45a568 */
extern void audio_ble_status_reply(uint8_t);
extern uint8_t audio_ble_remove_pair(uint8_t,const uint8_t *); /* 0x47b59c */
extern void audio_ble_master_security_clear_address(void); /* AppMasterSecClearAddr */
extern void audio_ble_set_ring_link_state(uint8_t,const char *);
extern void audio_ble_ota_connection_changed(uint8_t); /* native 0x4bb04a */
extern const char *audio_ble_ring_link_state_name(uint8_t);
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="ble.master";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_ble_central.c";
static const char function[]="APP_MasterCleanupRingUnpair";
static const char empty_name[]="";
static const uint8_t no_address[8]={0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff};
#define LOG(level,line,mask,plain,compact,...) do { \
 if(audio_log_level()&2u)audio_log_extended(level,module,path,function,line,plain,##__VA_ARGS__); \
 if((audio_log_level()&1u)||(audio_log_level()&4u)) \
  (void)compressed_log_output(mask,compact,compact,##__VA_ARGS__); \
} while(0)
void audio_ble_master_cleanup_ring_unpair_4a2c9c(const uint8_t *remove_record) {
    LOG(2u,0x5b8u,0x08400000u,
        "[RingUnpair] cleanup: clear ring kv, stop all connect/retry state=%s",
        "[ble.master][RingUnpair] cleanup: clear ring kv, stop all connect/retry state=%s",
        audio_ble_ring_link_state_name(audio_ble_ring_link_state));
    (void)audio_ble_master_auth_mode_set(0u);
    audio_ble_master_connect_state=0u;
    audio_ble_master_publish_flag=0u;
    audio_ble_master_link_ready=0u;
    (void)audio_event_loop_remove_delayed(audio_ble_master_connect_event);
    (void)audio_event_loop_remove_delayed(audio_ble_master_start_try_connect_ring);
    (void)audio_event_loop_remove_delayed((void (*)(void))audio_ble_master_disconnect_delayed);
    (void)audio_event_loop_remove_delayed((void (*)(void))audio_ble_master_success_delayed);
    (void)audio_event_loop_remove_delayed(audio_ble_master_followup_delayed);
    audio_ble_master_reset_retry_count();
    audio_ble_master_clear_failure_notify();
    audio_ble_ring_connect_policy_reset();
    audio_ble_master_set_target(no_address,empty_name,0u);
    audio_uart_buffer_zero(audio_uart_hand_record+12u,6u,0xffu);
    audio_uart_ring_unpair_publish_hand_4661a6();
    audio_uart_ring_unpair_commit_hand_466016();
    if(audio_uart_device_role_get()==1u)audio_ble_status_reply(0u);
    if(remove_record!=0)(void)audio_ble_remove_pair(1u,remove_record);
    audio_ble_master_security_clear_address();
    if(audio_ble_ring_link_state==1u && audio_ble_master_open_connection!=0u) {
        uint8_t connection=audio_ble_master_open_connection;
        LOG(3u,0x5d3u,0x0c400000u,
            "[RingUnpair] cleanup: cancel opening connId=%d",
            "[ble.master][RingUnpair] cleanup: cancel opening connId=%d",connection);
        audio_ble_master_disconnect_delayed(connection); /* _masterConnectCancel 0x4a01fc */
        return;
    }
    if(audio_ble_master_context==0 || audio_ble_master_context[0x55u]==0u) {
        audio_ble_set_ring_link_state(0u,"ring unpair cleanup idle");
    } else {
        uint8_t connection=audio_ble_master_context[0x55u];
        LOG(3u,0x5d9u,0x0c400000u,
            "[RingUnpair] cleanup: silent disconnect connId=%d",
            "[ble.master][RingUnpair] cleanup: silent disconnect connId=%d",connection);
        audio_ble_set_ring_link_state(4u,"ring unpair cleanup disconnect");
        audio_ble_ota_connection_changed(connection);
    }
}
