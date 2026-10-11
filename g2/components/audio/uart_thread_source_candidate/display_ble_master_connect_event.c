/* APP_MasterConnectEvent, native 0x4a1b60. Product state remains typed imports. */
#include <stdint.h>
extern volatile uint8_t audio_ble_master_connect_state; /* 0x20074f87 */
extern volatile uint8_t audio_ble_master_connection_flag; /* 0x20074f84 */
extern volatile uint8_t audio_ble_ring_link_state; /* 0x20074f85 */
extern uint8_t *audio_ble_master_context; /* pointer cell 0x200742fc */
extern uint8_t audio_ble_master_target_address[6]; /* 0x200003c0 */
extern uint32_t audio_uart_ring_active(void); /* 0x4a2914 */
extern void audio_ble_master_reset_retry_count(void); /* 0x4a2300 */
extern void audio_ble_master_clear_failure_notify(void); /* 0x4a15c0 */
extern uint32_t audio_ble_master_link_matches_target(const uint8_t *); /* 0x4a2864 */
extern uint8_t audio_dm_conn_role(uint8_t); /* DmConnRole */
extern const uint8_t *audio_dm_conn_peer_address(uint8_t); /* DmConnPeerAddr */
extern uint32_t audio_ble_privacy_compare_address(const uint8_t *,const uint8_t *); /* 0x4d294a */
extern void *audio_wsf_msg_alloc(uint16_t);
extern void audio_wsf_msg_send(uint8_t,void *);
extern uint32_t audio_event_loop_remove_delayed(void (*)(void));
extern void audio_event_loop_push_delayed(void (*)(void),uint32_t,uint32_t);
extern uint32_t audio_ble_master_success_delayed(uint32_t); /* 0x4bc418 */
extern void audio_ble_master_followup_delayed(void); /* 0x4c4ee4 */
extern void audio_ble_master_disconnect_delayed(uint32_t); /* 0x4a01fc */
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="ble.master";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_ble_central.c";
static const char function[]="APP_MasterConnectEvent";
#define LOG(level,line,mask,plain,compact,...) do { \
 if(audio_log_level()&2u) audio_log_extended(level,module,source,function,line,plain,##__VA_ARGS__); \
 if((audio_log_level()&1u)||(audio_log_level()&4u)) \
  (void)compressed_log_output(mask,compact,compact,##__VA_ARGS__); \
} while(0)
void audio_ble_master_connect_event(uint32_t event,uint32_t unused1,uint32_t unused2,uint32_t caller_context) {
    (void)unused1;(void)unused2;
    (void)audio_event_loop_remove_delayed((void (*)(void))audio_ble_master_connect_event);
    audio_ble_master_connect_state=0u;
    uint8_t from_retry=(uint8_t)((uint8_t)event>>7);
    uint8_t disconnect_local=(uint8_t)((event>>8)&1u);
    LOG(4u,0x404u,0x11000000u,
      "APP_MasterConnectEvent: event=0x%02X, fromRetry=%d, disconnectByLocal=%d, MConnId=%d",
      "[ble.master]APP_MasterConnectEvent: event=0x%02X, fromRetry=%d, disconnectByLocal=%d, MConnId=%d",
      event&0xfe7fu,from_retry,disconnect_local,audio_ble_master_context[0x55u]);
    (void)caller_context;
    if(event&1u) {
      uint8_t connection=audio_ble_master_context[0x55u];
      audio_ble_master_connection_flag=from_retry;
      if(audio_uart_ring_active()==0u) {
        LOG(2u,0x40du,0x08000000u,
          "APP_MasterConnectEvent: not ring owner role, skip master connect",
          "[ble.master]APP_MasterConnectEvent: not ring owner role, skip master connect");
        audio_ble_master_reset_retry_count();
        audio_ble_master_clear_failure_notify();
        audio_ble_master_connection_flag=0u;
      } else if(audio_ble_ring_link_state==6u) {
        LOG(3u,0x416u,0x0c000000u,
          "APP_MasterConnectEvent: unpair in progress, skip connect",
          "[ble.master]APP_MasterConnectEvent: unpair in progress, skip connect");
        audio_ble_master_clear_failure_notify();
        audio_ble_master_connection_flag=0u;
      } else if(from_retry==0u && audio_ble_master_link_matches_target(audio_ble_master_target_address)!=0u) {
        LOG(3u,0x421u,0x0c000000u,
          "APP_MasterConnectEvent: stable connected to target, notify success",
          "[ble.master]APP_MasterConnectEvent: stable connected to target, notify success");
        audio_ble_master_clear_failure_notify();
        audio_ble_master_connection_flag=0u;
        (void)audio_event_loop_remove_delayed((void (*)(void))audio_ble_master_success_delayed);
        audio_event_loop_push_delayed((void (*)(void))audio_ble_master_success_delayed,0u,100u);
        audio_event_loop_push_delayed((void (*)(void))audio_ble_master_success_delayed,0u,2000u);
        (void)audio_event_loop_remove_delayed(audio_ble_master_followup_delayed);
        audio_event_loop_push_delayed(audio_ble_master_followup_delayed,0u,200u);
      } else {
        if(connection!=0u && from_retry==0u && audio_dm_conn_role(connection)==0u) {
          const uint8_t *peer=audio_dm_conn_peer_address(connection);
          if(peer!=0 && audio_ble_privacy_compare_address(peer,audio_ble_master_target_address)!=0u) {
            LOG(3u,0x432u,0x0c000000u,
              "APP_MasterConnectEvent: BLE open to target but GATT not ready, wait",
              "[ble.master]APP_MasterConnectEvent: BLE open to target but GATT not ready, wait");
            return;
          }
          LOG(3u,0x436u,0x0c400000u,
            "APP_MasterConnectEvent: connected but Not connected to target, connId=%d, disconnect first then connect to target",
            "[ble.master]APP_MasterConnectEvent: connected but Not connected to target, connId=%d, disconnect first then connect to target",connection);
          (void)audio_event_loop_remove_delayed((void (*)(void))audio_ble_master_disconnect_delayed);
          audio_event_loop_push_delayed((void (*)(void))audio_ble_master_disconnect_delayed,connection,0u);
        }
        uint8_t *message=(uint8_t *)audio_wsf_msg_alloc(12u);
        if(message!=0) {
          LOG(4u,0x43eu,0x10000000u,
            "APP_MasterConnectEvent: Sending EVEN_MASTER_CONNECT_EVT to protocol stack thread",
            "[ble.master]APP_MasterConnectEvent: Sending EVEN_MASTER_CONNECT_EVT to protocol stack thread");
          message[2]=0xaeu;
          *(uint16_t *)(void *)message=(uint16_t)audio_ble_master_context[0x55u];
          *(uint16_t *)(void *)(message+8u)=1u;
          audio_wsf_msg_send(audio_ble_master_context[0x56u],message);
        }
      }
    } else if((event&2u)!=0u && audio_ble_master_context[0x55u]!=0u) {
      audio_ble_master_connection_flag=0u;
      uint8_t *message=(uint8_t *)audio_wsf_msg_alloc(12u);
      if(message!=0) {
        LOG(4u,0x449u,0x10000000u,
          "pMsg->hdr.event = EVEN_MASTER_DISCONNECT_EVT",
          "[ble.master]pMsg->hdr.event = EVEN_MASTER_DISCONNECT_EVT");
        message[2]=0xafu;
        *(uint16_t *)(void *)message=(uint16_t)audio_ble_master_context[0x55u];
        *(uint16_t *)(void *)(message+8u)=(uint16_t)(event&0xff7fu);
        audio_wsf_msg_send(audio_ble_master_context[0x56u],message);
      }
    }
}
