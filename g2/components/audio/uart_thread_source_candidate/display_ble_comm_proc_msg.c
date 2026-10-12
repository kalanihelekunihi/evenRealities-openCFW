/* Native bleProcMsg / _bleCommProcMsg 0x4b75ce, called by _bleCommHandler. */
#include <stdint.h>
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern uint8_t DmConnRole(uint8_t);
extern void audio_ble_tx_complete_notify(void); /* thread_ble_wsf_tx_complete_notify */
extern void attsCsfSetHashUpdateStatus(uint8_t);
extern const uint8_t audio_ble_comm_profile_table[]; /* ROM 0x78c9a4 */
extern void DmSecGenerateEccKeyReq(void);
extern void AttsCalculateDbHash(void);
extern void pairMgrSecAuthFlagSet(uint8_t);
extern uint8_t pairMgrSecAuthFlagGet(void);
extern void PB_LastTxEncodeRingConnectInfoTimeSet(uint32_t);
extern uint8_t *audio_ble_pair_record(uint8_t); /* 0x4bb07c */
extern void audio_ble_pair_record_clear_a(uint8_t *,uint8_t); /* 0x47b488 */
extern void audio_ble_pair_record_clear_b(uint8_t *,uint8_t); /* 0x47b3cc */
extern void audio_event_loop_remove_delayed(void (*)(void));
extern void audio_event_loop_push_delayed(void (*)(void),uint32_t,uint32_t);
extern void audio_ble_comm_disconnect_delayed(uint8_t); /* 0x5354c2 */
extern void audio_ble_comm_link_delayed(void); /* 0x4b81b8 */
extern uint32_t audio_ble_comm_recovery_delayed(uint16_t); /* 0x4bb92c */
extern uint32_t audio_ble_comm_notify_ring_delayed(uint32_t); /* 0x4bc418 */
extern uint32_t audio_ble_comm_notify_followup(void); /* 0x4722cc */
extern const char *audio_ble_disconnect_reason(uint8_t); /* 0x4b848c */
extern const char *audio_ble_pair_failure_reason(uint8_t); /* 0x4b8390 */
extern void audio_ble_pair_complete_prepare(uint8_t *); /* 0x47c084 */
extern void audio_ble_pair_complete_commit(void); /* 0x47bc30 */
extern void audio_ble_pair_failure(uint8_t,uint8_t); /* 0x47c568 */
extern uint32_t g2_flashdb_candidate_tick(void); /* selected 0x4490cc */
extern uint32_t audio_ble_encrypt_tick_200742f4; /* live RAM */
extern void Thread_SendEvtToRingTask(uint32_t);
extern void audio_ble_pair_key_process(void *); /* 0x4bafda */
extern void DmSecSetEccKey(const void *);
extern uint8_t attsCsfGetHashUpdateStatus(void);
extern void audio_ble_pair_key_ready(void *); /* 0x4bb030 */
extern void audio_ble_service_discovery_start(uint8_t); /* 0x531d60 */
extern void HciDrvRadioBoot(uint8_t);
extern void DmDevReset(void);
extern uint8_t audio_ble_comm_state[]; /* 0x200727f0 */
extern void audio_uart_display_connected(void); /* same native0x46f32c */
extern uint32_t PB_TxEncodeNotifyRingConnectInfo(uint32_t);
extern void audio_ble_slave_event_state(uint8_t); /* 0x4bd054 */
extern void audio_ble_slave_security_state(uint8_t); /* 0x4b82e8 */
static const char module[]="ble.comm";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_ble.c";
static const char function[]="_bleCommProcMsg";
#define LOG(level,line,mask,plain,short_text,...) do { \
 if(audio_log_flags()&2u)audio_log_extended(level,module,path,function,line,plain,##__VA_ARGS__); \
 if((audio_log_flags()&1u)||(audio_log_flags()&4u)) \
  (void)compressed_log_output(mask,short_text,short_text,##__VA_ARGS__); \
} while(0)
void audio_ble_comm_message_release(void *raw) {
 uint8_t *m=(uint8_t *)raw;
 uint8_t event=m[2u],conn=m[0u],emit=0u;
 uint8_t *record;
 switch(event) {
 case 0x12u:
  audio_ble_tx_complete_notify();
  if(m[3u]==0x72u)
   LOG(2u,0x187u,0x08400000u,"ATTS_HANDLE_VALUE_CNF status overflow connId %d",
    "[ble.comm]ATTS_HANDLE_VALUE_CNF status overflow connId %d",conn);
  else if(m[3u])
   LOG(1u,0x18bu,0x04800000u,"!!!!ERROR: ATTS_HANDLE_VALUE_CNF status %d connId %d",
    "[ble.comm]!!!!ERROR: ATTS_HANDLE_VALUE_CNF status %d connId %d",m[3u],conn);
  break;
 case 0x15u:break;
 case 0x20u:
  attsCsfSetHashUpdateStatus(1u);
  if(audio_ble_comm_profile_table[0]&8u)DmSecGenerateEccKeyReq();
  else AttsCalculateDbHash();
  emit=1u;
  break;
 case 0x27u:
  if(DmConnRole(conn)==1u) {
   pairMgrSecAuthFlagSet(0u);
   PB_LastTxEncodeRingConnectInfoTimeSet(0u);
  }
  audio_ble_tx_complete_notify();
  record=audio_ble_pair_record(conn);
  if(record) {
   audio_ble_pair_record_clear_a(record,0u);
   audio_ble_pair_record_clear_b(record,0u);
   LOG(4u,0x1b2u,0x10000000u,
    "[Service Discovery] Reset discovery status to force re-discovery on connection",
    "[ble.comm][Service Discovery] Reset discovery status to force re-discovery on connection");
  }
  emit=8u;
  break;
 case 0x28u:
  audio_ble_encrypt_tick_200742f4=0u;
  audio_ble_tx_complete_notify();
  audio_event_loop_remove_delayed((void (*)(void))audio_ble_comm_disconnect_delayed);
  audio_event_loop_remove_delayed(audio_ble_comm_link_delayed);
  if(DmConnRole(conn)==1u)pairMgrSecAuthFlagSet(0u);
  LOG(1u,0x1dbu,0x04c00000u,
   "DM_CONN_CLOSE_IND disconnect connId = %d, Connection closed reason 0x%02x - %s",
   "[ble.comm]DM_CONN_CLOSE_IND disconnect connId = %d, Connection closed reason 0x%02x - %s",
   conn,m[8u],audio_ble_disconnect_reason(m[8u]));
  if(m[8u]==0x3du)
   LOG(1u,0x1dfu,0x04400000u,
    "DM_CONN_CLOSE_IND connId = %d conn close reason HCI_ERR_MIC_FAILURE",
    "[ble.comm]DM_CONN_CLOSE_IND connId = %d conn close reason HCI_ERR_MIC_FAILURE",conn);
  emit=9u;
  break;
 case 0x2au:
  DmSecGenerateEccKeyReq();
  LOG(4u,0x1f1u,0x10400000u,"DM_SEC_PAIR_CMPL_IND connId = %d",
   "[ble.comm]DM_SEC_PAIR_CMPL_IND connId = %d",conn);
  record=audio_ble_pair_record(conn);
  if(record) {
   audio_ble_pair_complete_prepare(record);
   LOG(3u,0x1f7u,0x0c000000u,
    "Pairing completed - updated record timestamp for LRU management",
    "[ble.comm]Pairing completed - updated record timestamp for LRU management");
   audio_ble_pair_complete_commit();
  }
  emit=10u;
  break;
 case 0x2bu:
  audio_event_loop_remove_delayed((void (*)(void))audio_ble_comm_recovery_delayed);
  audio_event_loop_push_delayed((void (*)(void))audio_ble_comm_recovery_delayed,0u,10u);
  DmSecGenerateEccKeyReq();
  LOG(1u,0x212u,0x04800000u,
   "DM_SEC_PAIR_FAIL_IND: status = 0x%02x - %s",
   "[ble.comm]DM_SEC_PAIR_FAIL_IND: status = 0x%02x - %s",
   m[3u],audio_ble_pair_failure_reason(m[3u]));
  audio_ble_pair_failure(conn,m[3u]);
  emit=11u;
  break;
 case 0x2cu:
  record=audio_ble_pair_record(conn);
  if(record) {
   audio_ble_pair_record_clear_a(record,0u);
   audio_ble_pair_record_clear_b(record,0u);
   LOG(4u,0x222u,0x10000000u,
    "[Service Discovery] Reset discovery status after encryption to force re-discovery",
    "[ble.comm][Service Discovery] Reset discovery status after encryption to force re-discovery");
  }
  if(conn && DmConnRole(conn)==1u) {
   audio_event_loop_remove_delayed((void (*)(void))audio_ble_comm_disconnect_delayed);
   audio_event_loop_push_delayed((void (*)(void))audio_ble_comm_disconnect_delayed,conn,1000u);
  }
  audio_ble_slave_security_state(1u);
  if(pairMgrSecAuthFlagGet()==0u) {
   pairMgrSecAuthFlagSet(1u);
   LOG(4u,0x232u,0x10400000u,
    "DM_SEC_ENCRYPT_IND connId = %d encrypted PB_TxEncodeNotifySecAuth not get sec auth flag wait",
    "[ble.comm]DM_SEC_ENCRYPT_IND connId = %d encrypted PB_TxEncodeNotifySecAuth not get sec auth flag wait",conn);
  } else {
   audio_event_loop_remove_delayed((void (*)(void))audio_ble_comm_recovery_delayed);
   audio_event_loop_push_delayed((void (*)(void))audio_ble_comm_recovery_delayed,1u,200u);
   audio_event_loop_push_delayed((void (*)(void))audio_ble_comm_recovery_delayed,1u,1000u);
   audio_event_loop_push_delayed((void (*)(void))audio_ble_comm_recovery_delayed,1u,2000u);
   LOG(4u,0x22fu,0x10400000u,
    "DM_SEC_ENCRYPT_IND connId = %d encrypted PB_TxEncodeNotifySecAuth get sec auth flag will notify",
    "[ble.comm]DM_SEC_ENCRYPT_IND connId = %d encrypted PB_TxEncodeNotifySecAuth get sec auth flag will notify",conn);
  }
  audio_ble_encrypt_tick_200742f4=g2_flashdb_candidate_tick();
  if(DmConnRole(conn)==0u)Thread_SendEvtToRingTask(0x10u);
  emit=12u;
  break;
 case 0x2du:emit=13u;break;
 case 0x2eu:audio_ble_pair_key_process(raw);break;
 case 0x34u:
  DmSecSetEccKey(m+4u);
  if(attsCsfGetHashUpdateStatus())AttsCalculateDbHash();
  break;
 case 0x35u:audio_ble_pair_key_ready(raw);break;
 case 0x3cu:
  LOG(4u,0x251u,0x10400000u,"Clear resolving list status 0x%02x",
   "[ble.comm]Clear resolving list status 0x%02x",m[3u]);
  break;
 case 0x46u:
  LOG(3u,0x1ecu,0x0cc00000u,"DM_PHY_UPDATE_IND status: %d, RX: %d, TX: %d",
   "[ble.comm]DM_PHY_UPDATE_IND status: %d, RX: %d, TX: %d",m[4u],m[9u],m[8u]);
  break;
 case 0x79u:emit=30u;break;
 case 0xa5u:
  LOG(4u,0x201u,0x10400000u,"EVEN_START_SERVICE_DISCOVERY_EVT connId = %d",
   "[ble.comm]EVEN_START_SERVICE_DISCOVERY_EVT connId = %d",conn);
  if(conn)audio_ble_service_discovery_start(conn);
  break;
 case 0xa6u:HciDrvRadioBoot(0u);DmDevReset();break;
 case 0xbcu:
  LOG(4u,0x259u,0x10800000u,"BLE WSF is Running, SConnId = %d, MConnId = %d",
   "[ble.comm]BLE WSF is Running, SConnId = %d, MConnId = %d",
   audio_ble_comm_state[0x54u],audio_ble_comm_state[0x55u]);
  audio_uart_display_connected();
  if(audio_ble_comm_state[0x55u]) {
   audio_event_loop_remove_delayed((void (*)(void))audio_ble_comm_notify_ring_delayed);
   PB_TxEncodeNotifyRingConnectInfo(0u);
   audio_event_loop_remove_delayed((void (*)(void))audio_ble_comm_notify_followup);
   audio_event_loop_push_delayed((void (*)(void))audio_ble_comm_notify_followup,0u,10000u);
  }
  break;
 default:break;
 }
 if(emit)audio_ble_slave_event_state(emit);
}
