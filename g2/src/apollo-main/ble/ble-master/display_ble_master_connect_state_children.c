/* Native 0x4a2300, 0x4a15c0, 0x4a2864; product cells remain imports. */
#include <stdint.h>
extern volatile uint16_t audio_ble_master_connect_wait; /* 0x20074f18 */
extern volatile uint8_t audio_ble_master_failure_notify; /* 0x20074f82 */
extern volatile uint8_t audio_ble_master_failure_count; /* 0x20074f83 */
extern volatile uint8_t audio_ble_ring_link_state; /* 0x20074f85 */
extern volatile uint8_t audio_ble_master_link_ready; /* 0x20074f89 */
extern uint8_t *audio_ble_master_context; /* 0x200742fc */
extern const uint8_t *audio_dm_conn_peer_address(uint8_t);
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="ble.master";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_ble_central.c";
/* Stock 0x004A2300 (APP_MasterResetRetryConnectCnt) */
void audio_ble_master_reset_retry_count(void) {
    uint32_t previous=audio_ble_master_connect_wait;
    if(audio_log_level()&2u) audio_log_extended(3u,module,source,"APP_MasterResetRetryConnectCnt",0x4d0u,
        "APP_MasterResetRetryConnectCnt: reset retry count from %d to 0",previous);
    if((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(0x0c400000u,
          "[ble.master]APP_MasterResetRetryConnectCnt: reset retry count from %d to 0",
          "[ble.master]APP_MasterResetRetryConnectCnt: reset retry count from %d to 0",previous);
    audio_ble_master_connect_wait=0u;
}
/* Stock 0x004A15C0 (APP_MasterClearRingConnectFailureNotifyAfterRetry) */
void audio_ble_master_clear_failure_notify(void) {
    if(audio_ble_master_failure_notify!=0u || audio_ble_master_failure_count!=0u) {
      uint32_t count=audio_ble_master_failure_count;
      if(audio_log_level()&2u) audio_log_extended(3u,module,source,
        "APP_MasterClearRingConnectFailureNotifyAfterRetry",0x37au,
        "Ring connect failure notify cleared, failedCount=%d",count);
      if((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(0x0c400000u,
          "[ble.master]Ring connect failure notify cleared, failedCount=%d",
          "[ble.master]Ring connect failure notify cleared, failedCount=%d",count);
    }
    audio_ble_master_failure_notify=0u;
    audio_ble_master_failure_count=0u;
}
/* Stock 0x004A2864 (central_master_link_matches_target_004a2864) */
uint32_t audio_ble_master_link_matches_target(const uint8_t *target) {
    if(audio_ble_ring_link_state!=2u || audio_ble_master_link_ready==0u ||
       audio_ble_master_context==0 || audio_ble_master_context[0x55u]==0u) return 0u;
    if(target==0) return 1u;
    const uint8_t *peer=audio_dm_conn_peer_address(audio_ble_master_context[0x55u]);
    if(peer==0) return 0u;
    for(uint32_t i=0;i<6u;i++) if(peer[i]!=target[i]) return 0u;
    return 1u;
}
