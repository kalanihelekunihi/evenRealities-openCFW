/* Stock 0x41a40: rate-limited channel audit used by ATI recovery. */
#include <stdint.h>
#include "cmsis_os2.h"
#include "../board/native_iqs_state.h"
#include "../board/native_touch_transport.h"
extern uint32_t r1_model_dependent_limit_get(void),r1_product_sn_letter_decode(void);
extern int r1_native_snprintf(char *,uint32_t,const char *,...);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_4(uint32_t,const char *,uint32_t,uint32_t,uint32_t,uint32_t);
volatile uint32_t r1_iqs_ati_error_sequence __attribute__((section(".r1.iqs.audit_sequence"),aligned(4)))=0;
volatile uint32_t r1_iqs_ati_last_report_tick __attribute__((section(".r1.iqs.audit_tick"),aligned(4)))=0;
static int ring_enabled(void)
{return (r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u);}
void r1_iqs7211e_ati_error_audit_policy(void)
{
 r1_iqs_ati_error_sequence=r1_iqs_ati_error_sequence+1u;
 uint32_t ticks=osKernelGetTickCount();
 if(r1_iqs_ati_error_sequence!=1u && (uint32_t)(ticks-r1_iqs_ati_last_report_tick)<10000u)return;
 r1_iqs_ati_last_report_tick=ticks;
 uint32_t channels=r1_model_dependent_limit_get();
 uint16_t samples[24]={0};
 const volatile uint8_t *configuration=r1_iqs_model_configuration;
 (void)r1_iqs7211e_register_read_port(0x56,0xe3,samples,(uint8_t)(channels*2u),1);
 uint32_t minimum=65535,maximum=0;
 uint8_t active=0;
 /* Stock leaves this private buffer unwritten if every channel is masked.
  * C defines that case as an empty list, including partial/failing reads. */
 char list[160]={0};int length=0;
 for(uint8_t i=0;i<channels;i++) {
  uint32_t value=samples[i];
  if(configuration && configuration[5u+i]==255u)continue;
  if(value<minimum)minimum=value;
  if(value>maximum)maximum=value;
  active=(uint8_t)(active+1u);
  if(length<152)length+=r1_native_snprintf(list+length,160u-(uint32_t)length,"%u ",value);
 }
 if(!active)minimum=0;
 const char *geometry=channels==24?"8x3":"7x3";
 const char *header="[RING]ATI_ERR|seq=%u|R%u|%s|div=%u";
 if(ring_enabled()) {
  uint32_t decoded=r1_product_sn_letter_decode();
  uint32_t divider=configuration?*(const volatile uint16_t *)configuration:0;
  (void)r1_structured_log_format(0x05000000,header,header,r1_iqs_ati_error_sequence,decoded,geometry,divider);
 }
 if(r1_structured_log_mode_get()&2u) {
  uint32_t decoded=r1_product_sn_letter_decode();
  uint32_t divider=configuration?*(const volatile uint16_t *)configuration:0;
  nrf_log_frontend_std_4(0x001c0001,"ATI_ERR|seq=%u|R%u|%s|div=%u",r1_iqs_ati_error_sequence,decoded,(uint32_t)(uintptr_t)geometry,divider);
 }
 const char *values="[RING]ATI_ERR|act=%u|min=%u|max=%u|[%s]";
 if(ring_enabled())(void)r1_structured_log_format(0x05000000,values,values,(uint32_t)active,minimum,maximum,list);
 if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_4(0x001c0001,"ATI_ERR|act=%u|min=%u|max=%u|[%s]",active,minimum,maximum,(uint32_t)(uintptr_t)list);
}
