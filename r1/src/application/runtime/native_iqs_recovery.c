/* Stock IQS recovery policy 0x6f9e4 and reset/reconfigure wrapper 0x6fce8. */
#include <stdint.h>
#include "../board/native_iqs_state.h"
#include "../board/native_touch_transport.h"
extern void r1_iqs7211e_ati_error_audit_policy(void),r1_iqs7211e_configure(void);
extern uint32_t r1_touch_task_event_post(uint32_t);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
static int ring_enabled(void)
{return (r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u);}
static void log_plain(uint32_t ring_id,uint32_t sdk_id,const char *ring,const char *sdk)
{
 if(ring_enabled())(void)r1_structured_log_format(ring_id,ring,ring);
 if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0(sdk_id,sdk);
}
void r1_iqs7211e_ati_recovery_policy(void)
{
 log_plain(0x04000000,0x001c0001,"[RING]\n IQS7211E_ATI_Error","\n IQS7211E_ATI_Error");
 r1_iqs7211e_ati_error_audit_policy();
 (void)r1_touch_task_event_post(0x20);
 uint32_t consecutive=r1_iqs_recovery_consecutive;
 if(consecutive<255u)r1_iqs_recovery_consecutive=(uint8_t)++consecutive;
 uint32_t used=r1_iqs_recovery_used;
 if(consecutive>=5u && used<3u) {
  r1_iqs_recovery_used=(uint8_t)(used+1u);
  r1_iqs_recovery_consecutive=0;
  r1_touch_slider_flag=1;
  const char *ring="[RING]ATI_ERR_RECOVERY|trigger close+reinit, retry=%u/%u";
  if(ring_enabled())(void)r1_structured_log_format(0x04800000,ring,ring,(uint32_t)r1_iqs_recovery_used,3u);
  if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_2(0x001c0001,"ATI_ERR_RECOVERY|trigger close+reinit, retry=%u/%u",r1_iqs_recovery_used,3u);
  (void)r1_touch_task_event_post(4);
 }else if(used>=3u) {
  const char *ring="[RING]ATI_ERR_RECOVERY|gave up after %u retries";
  if(ring_enabled())(void)r1_structured_log_format(0x04400000,ring,ring,(uint32_t)r1_iqs_recovery_used);
  if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_1(0x001c0001,"ATI_ERR_RECOVERY|gave up after %u retries",r1_iqs_recovery_used);
 }else {
  uint8_t word[2]={0x20,0};
  (void)r1_iqs7211e_register_write_port(0x56,0x33,word,2,1);
  log_plain(0x04000000,0x001c0001,"[RING]\n IQS7211E_Triggered_Re-ATI_for_recovery","\n IQS7211E_Triggered_Re-ATI_for_recovery");
 }
}
void r1_iqs7211e_reset_reconfigure(void)
{
 log_plain(0x0c000000,0x001c0003,"[RING]\n IQS7211E_Reset_occurred","\n IQS7211E_Reset_occurred");
 r1_iqs7211e_configure();
 log_plain(0x0c000000,0x001c0003,"[RING]\n IQS7211E_Init_finished","\n IQS7211E_Init_finished");
}
