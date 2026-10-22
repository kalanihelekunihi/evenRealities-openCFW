/* Native _bleSlaveProcMsg, 0x46e098. Product RAM and descendants are explicit. */
#include <stdint.h>

extern uint8_t *audio_ble_profile_connection_context; /* 0x2007432c */
extern uint8_t *audio_ble_slave_mode_context; /* 0x20074330 */
extern uint8_t *audio_ble_dm_conn_cell; /* 0x20074328 */
extern uint8_t audio_ble_subsystem_link_state_200719c8[];
extern uint8_t audio_ble_slave_unpair_flag_20074f8b;
extern uint8_t audio_ble_slave_adv_stop_flag_20074f8d;
extern uint8_t audio_ble_slave_link_flags_20074f8c;
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern uint8_t DmConnRole(uint8_t);
extern void dmSlaveAdvStopOnDisconnect(void *);
extern void audio_ble_adv_init(void *); /* _bleAdvInit */
extern void appSlaveConnOpen(void *);
extern void audio_ble_slave_request_mtu(void *); /* _bleSlaveRequestMtuExchange */
extern void audio_ble_slave_open_followup(void); /* 0x46f098 */
extern void audio_ble_slave_open_watchdog(uint32_t); /* 0x46f350 */
extern void audio_ble_slave_disconnect_followup(uint32_t); /* 0x46effc */
extern void audio_ble_phone_advertising_restart(void); /* 0x46ee70 */
extern void audio_event_loop_remove_delayed(void (*)(void));
extern void audio_event_loop_push_delayed(void (*)(void),uint32_t,uint32_t);
extern uint32_t audio_uart_command_pending(void); /* productModeGet */
extern uint8_t audio_ble_pair_count(uint8_t); /* 0x47a676 */
extern void audio_ble_slave_security_state(uint8_t); /* 0x4b82e8 */
extern void tpl_reset_receive_contexts_004b9984(void);
extern int32_t Thread_BleMsgtxQueueClear(void);
extern int32_t Thread_BleMsgrxQueueClear(void);
extern const uint8_t *audio_ble_dm_conn_peer_address(const uint8_t *); /* 0x47aec0 */
extern uint8_t audio_ble_dm_conn_address_type(const uint8_t *); /* 0x47aec8 */
extern void audio_ble_remove_pair(uint8_t,const uint8_t *); /* 0x47b59c */
extern void audio_ble_slave_event_state(uint8_t); /* 0x4bd054 */
extern void audio_ble_slave_disconnect_event(uint8_t); /* 0x4bb04a */
extern void audio_ble_slave_security_request(uint8_t); /* _bleSlaveSecReq */
extern uint8_t audio_ble_app_adv_state(void); /* 0x4b46a8 */
extern uint8_t audio_ble_dm_adv_state(uint8_t); /* 0x4bac4e */
extern void audio_ble_app_adv_set_state(uint8_t); /* 0x4b467c */
extern void AppSetAdvType(uint8_t);
extern void AppAdvStart(uint8_t);
extern void AppAdvStop(void);
extern void TPL_RxPacketTimeoutHandler(void *);
extern void PB_TxEncodeNotifySecAuthImpl(uint8_t);
extern void PB_TxEncodeNotifyRingConnectInfoImpl(uint8_t);

static const char module[]="ble.Slave";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_ble_peripheral.c";
static const char function[]="_bleSlaveProcMsg";
#define LOG(level,line,mask,plain,short_text,...) do { \
 if (audio_log_flags()&2u) audio_log_extended(level,module,path,function,line,plain,##__VA_ARGS__); \
 if ((audio_log_flags()&1u)||(audio_log_flags()&4u)) \
  (void)compressed_log_output(mask,short_text,short_text,##__VA_ARGS__); \
} while (0)
static uint16_t half(const uint8_t *p) {return (uint16_t)(p[0]|((uint16_t)p[1]<<8));}
static uint32_t word(const uint8_t *p) {return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static void put_half(uint8_t *p,uint16_t n) {p[0]=(uint8_t)n;p[1]=(uint8_t)(n>>8);}
static void put_word(uint8_t *p,uint32_t n) {p[0]=(uint8_t)n;p[1]=(uint8_t)(n>>8);p[2]=(uint8_t)(n>>16);p[3]=(uint8_t)(n>>24);}
static uint8_t conn_id(void) {return audio_ble_profile_connection_context[0x54u];}
static void retry_adv(uint32_t ms) {
 audio_event_loop_remove_delayed(audio_ble_phone_advertising_restart);
 audio_event_loop_push_delayed(audio_ble_phone_advertising_restart,0u,ms);
}
/* Stock 0x0046E098 (_bleSlaveProcMsg) */
void audio_ble_adv_message_preprocess(void *raw) {
 uint8_t *m=(uint8_t *)raw;
 uint8_t event=m[2u],emit=0u,dm,app,id;
 const uint8_t *peer;
 uint8_t type;
 switch(event) {
 case 5u:case 13u:case 14u:
  if(DmConnRole(m[0])==1u)dmSlaveAdvStopOnDisconnect(raw);
  break;
 case 9u:case 10u:
  if(DmConnRole(m[0])==1u)LOG(4u,0x170u,0x10000000u,
   "DM_ROLE_SLAVE ATTC_WRITE_RSP","[ble.Slave]DM_ROLE_SLAVE ATTC_WRITE_RSP");
  break;
 case 0x15u:audio_ble_adv_init(raw);break;
 case 0x16u:
  if(DmConnRole(m[0])==1u) {
   put_half(audio_ble_slave_mode_context+0x22u,half(m+14u));
   LOG(3u,0x193u,0x0c400000u,"slave Negotiated MTU = %d",
       "[ble.Slave]slave Negotiated MTU = %d",half(audio_ble_slave_mode_context+0x22u));
  }
  break;
 case 0x21u:
  emit=3u;
  LOG(3u,0x183u,0x0c000000u,"DM_ADV_START_IND","[ble.Slave]DM_ADV_START_IND");
  break;
 case 0x22u:
  emit=4u;
  LOG(3u,0x188u,0x0c000000u,"DM_ADV_STOP_IND","[ble.Slave]DM_ADV_STOP_IND");
  if(audio_ble_slave_adv_stop_flag_20074f8d) {
   LOG(3u,0x18bu,0x0c000000u,
    "[Ring Connection] DM_ADV_STOP_IND received, flag was set, will restart after delay",
    "[ble.Slave][Ring Connection] DM_ADV_STOP_IND received, flag was set, will restart after delay");
   audio_ble_slave_adv_stop_flag_20074f8d=0u;
  }
  break;
 case 0x27u:
  if(DmConnRole(m[0])==1u) {
   audio_ble_slave_unpair_flag_20074f8b=0u;
   audio_ble_slave_mode_context[0x20u]=0u;
   appSlaveConnOpen(raw);
   audio_ble_slave_request_mtu(raw);
   audio_event_loop_remove_delayed(audio_ble_slave_open_followup);
   if(audio_uart_command_pending()==0u)
    audio_event_loop_push_delayed(audio_ble_slave_open_followup,0u,30000u);
   audio_event_loop_remove_delayed((void (*)(void))audio_ble_slave_open_watchdog);
   audio_event_loop_push_delayed((void (*)(void))audio_ble_slave_open_watchdog,1u,3000u);
   LOG(3u,0x1a2u,0x0c400000u,"DM_CONN_OPEN_IND connect connId = %d",
    "[ble.Slave]DM_CONN_OPEN_IND connect connId = %d",half(m));
   id=audio_ble_pair_count(0u);
   LOG(3u,0x1abu,0x0c400000u,"Current paired devices: Slaves=%d",
    "[ble.Slave]Current paired devices: Slaves=%d",id);
  }
  break;
 case 0x28u:
  if(DmConnRole(m[0])==1u) {
   audio_event_loop_remove_delayed(audio_ble_slave_open_followup);
   audio_event_loop_remove_delayed((void (*)(void))audio_ble_slave_open_watchdog);
   audio_ble_slave_mode_context[0x20u]=0u;
   audio_ble_slave_link_flags_20074f8c&=0x80u;
   LOG(3u,0x1c0u,0x0c800000u,
    ">>> DM_ROLE_SLAVE disconnect connId = %d, Connection closed reason 0x%x <<<",
    "[ble.Slave]>>> DM_ROLE_SLAVE disconnect connId = %d, Connection closed reason 0x%x <<<",
    conn_id(),m[8u]);
   audio_event_loop_remove_delayed((void (*)(void))audio_ble_slave_disconnect_followup);
   audio_ble_slave_security_state(0u);
   audio_ble_profile_connection_context[0x54u]=0u;
   tpl_reset_receive_contexts_004b9984();
   Thread_BleMsgtxQueueClear();
   Thread_BleMsgrxQueueClear();
   if(audio_ble_slave_unpair_flag_20074f8b==0u) {
    audio_ble_slave_unpair_flag_20074f8b=0u;
    retry_adv(1000u);
    LOG(3u,0x1d7u,0x0c400000u,
     "DM_ROLE_SLAVE disconnect start adv after 1s _g_unpairGlassesFlag = %d",
     "[ble.Slave]DM_ROLE_SLAVE disconnect start adv after 1s _g_unpairGlassesFlag = %d",
     audio_ble_slave_unpair_flag_20074f8b);
   } else {
    peer=audio_ble_dm_conn_peer_address((const uint8_t *)(uintptr_t)word(audio_ble_dm_conn_cell));
    type=audio_ble_dm_conn_address_type((const uint8_t *)(uintptr_t)word(audio_ble_dm_conn_cell));
    audio_ble_remove_pair(type,peer);
    audio_ble_slave_unpair_flag_20074f8b=0u;
    LOG(3u,0x1cdu,0x0dc00000u,
     "slave unpair, addrType = %d,  peerAddr = %02X:%02X:%02X:%02X:%02X:%02X",
     "[ble.Slave]slave unpair, addrType = %d,  peerAddr = %02X:%02X:%02X:%02X:%02X:%02X",
     type,peer[5],peer[4],peer[3],peer[2],peer[1],peer[0]);
    retry_adv(5000u);
   }
  }
  break;
 case 0x37u:
  LOG(4u,0x1b0u,0x10000000u,"DM_PRIV_RESOLVED_ADDR_IND",
   "[ble.Slave]DM_PRIV_RESOLVED_ADDR_IND");
  put_word(audio_ble_slave_mode_context+4u,word(audio_ble_dm_conn_cell));
  LOG(3u,0x1b3u,0x0c400000u,"Current paired devices dbHdl = %p",
   "[ble.Slave]Current paired devices dbHdl = %p",(void *)(uintptr_t)word(audio_ble_slave_mode_context+4u));
  break;
 case 0x47u:emit=0x15u;break;
 case 0x48u:
  emit=0x16u;
  LOG(3u,0x17eu,0x0c000000u,"DM_ADV_SET_STOP_IND","[ble.Slave]DM_ADV_SET_STOP_IND");
  break;
 case 0xadu:
  LOG(4u,0x218u,0x10000000u,"EVEN_SLAVE_DISCONNECT_EVT",
   "[ble.Slave]EVEN_SLAVE_DISCONNECT_EVT");
  if(!audio_ble_profile_connection_context || !conn_id())
   LOG(2u,0x21au,0x08000000u,"EVEN_SLAVE_DISCONNECT_EVT: connId is 0, return",
    "[ble.Slave]EVEN_SLAVE_DISCONNECT_EVT: connId is 0, return");
  else audio_ble_slave_disconnect_event(conn_id());
  break;
 case 0xb5u:
  if(!audio_ble_profile_connection_context || !conn_id())
   LOG(2u,0x20au,0x08000000u,"EVEN_SLAVE_SECURITY_REQUEST_EVT: connId is 0, return",
    "[ble.Slave]EVEN_SLAVE_SECURITY_REQUEST_EVT: connId is 0, return");
  else {
   id=m[8u];
   LOG(4u,0x20eu,0x10400000u,"EVEN_SLAVE_SECURITY_REQUEST_EVT state = %d",
    "[ble.Slave]EVEN_SLAVE_SECURITY_REQUEST_EVT state = %d",id);
   if(id) {audio_ble_slave_security_request(conn_id());audio_ble_slave_security_state(1u);}
  }
  break;
 case 0xb6u:
  app=audio_ble_app_adv_state();dm=audio_ble_dm_adv_state(0u);
  audio_ble_slave_unpair_flag_20074f8b=0u;
  LOG(3u,0x1dfu,0x0c800000u,"EVEN_SLAVE_ADV_AGAIN_EVT, AppState=%d, DmState=%d",
   "[ble.Slave]EVEN_SLAVE_ADV_AGAIN_EVT, AppState=%d, DmState=%d",app,dm);
  audio_ble_slave_adv_stop_flag_20074f8d=0u;
  if(dm==0u) {
   if(audio_ble_subsystem_link_state_200719c8[0x57u]==0u ||
      audio_ble_subsystem_link_state_200719c8[0x57u]>2u) {
    audio_ble_subsystem_link_state_200719c8[0x57u]=0u;
    LOG(3u,0x1e9u,0x0c000000u,"[Auto Restart] Reset advState to APP_ADV_STATE1",
     "[ble.Slave][Auto Restart] Reset advState to APP_ADV_STATE1");
   }
   audio_ble_app_adv_set_state(1u);AppSetAdvType(0u);AppAdvStart(1u);
   LOG(3u,0x1eeu,0x0c000000u,"[Auto Restart] Stack did not auto restart, manually starting advertising",
    "[ble.Slave][Auto Restart] Stack did not auto restart, manually starting advertising");
  } else if(dm==5u) {
   LOG(2u,0x1f0u,0x08400000u,"[Auto Restart] DM state is STOPPING (%d), will restart after stop complete",
    "[ble.Slave][Auto Restart] DM state is STOPPING (%d), will restart after stop complete",5u);
   retry_adv(200u);
  } else if(dm==1u || dm==3u) {
   LOG(3u,500u,0x0c400000u,"[Auto Restart] Stack already restarted advertising (dmState=%d), skip manual start",
    "[ble.Slave][Auto Restart] Stack already restarted advertising (dmState=%d), skip manual start",dm);
  } else {
   LOG(2u,0x1f7u,0x08400000u,"[Auto Restart] Unknown DM state (%d), delay retry",
    "[ble.Slave][Auto Restart] Unknown DM state (%d), delay retry",dm);
   retry_adv(200u);
  }
  break;
 case 0xb7u:
  app=audio_ble_app_adv_state();
  LOG(3u,0x200u,0x0c400000u,"EVEN_SLAVE_ADV_STOP_EVT, IsAdvertising %d",
   "[ble.Slave]EVEN_SLAVE_ADV_STOP_EVT, IsAdvertising %d",app);
  if(app) {
   LOG(4u,0x202u,0x10000000u,"AppAdvStop","[ble.Slave]AppAdvStop");
   AppAdvStop();
  }
  break;
 case 0xb8u:
  if(word(m+4u)==0u || half(m+8u)!=3u)
   LOG(1u,0x22au,0x04800000u,
    "EVEN_SLAVE_TPL_RX_TIMEOUT: invalid message format, pValue=%p, valueLen=%d",
    "[ble.Slave]EVEN_SLAVE_TPL_RX_TIMEOUT: invalid message format, pValue=%p, valueLen=%d",
    (void *)(uintptr_t)word(m+4u),half(m+8u));
  else TPL_RxPacketTimeoutHandler((void *)(uintptr_t)word(m+4u));
  break;
 case 0xbau:case 0xbbu:
  if(!audio_ble_profile_connection_context || !conn_id()) {
   if(event==0xbau)
    LOG(2u,0x231u,0x08000000u,"EVEN_SLAVE_NOTIFY_SEC_AUTH: connId is 0, return",
     "[ble.Slave]EVEN_SLAVE_NOTIFY_SEC_AUTH: connId is 0, return");
   else
    LOG(2u,0x23du,0x08000000u,"EVEN_SLAVE_NOTIFY_RING_CONNECT_INFO: connId is 0, return",
     "[ble.Slave]EVEN_SLAVE_NOTIFY_RING_CONNECT_INFO: connId is 0, return");
  } else {
   id=m[8u];
   if(event==0xbau) {
    LOG(4u,0x235u,0x10400000u,"EVEN_SLAVE_NOTIFY_SEC_AUTH pairRet = %d",
     "[ble.Slave]EVEN_SLAVE_NOTIFY_SEC_AUTH pairRet = %d",id);
    audio_ble_slave_security_state(1u);PB_TxEncodeNotifySecAuthImpl(id);
   } else {
    LOG(4u,0x241u,0x10400000u,"EVEN_SLAVE_NOTIFY_RING_CONNECT_INFO connRet = %d",
     "[ble.Slave]EVEN_SLAVE_NOTIFY_RING_CONNECT_INFO connRet = %d",id);
    PB_TxEncodeNotifyRingConnectInfoImpl(id);
   }
  }
  break;
 default:break;
 }
 if(emit)audio_ble_slave_event_state(emit);
}
