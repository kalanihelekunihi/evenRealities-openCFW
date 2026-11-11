/* Stock 0x42d40: seven-event IRQ suppression window. The live cursor must
 * be in [0,6], as established by cold zero state and maintained modulo seven. */
#include <stdint.h>
extern uint32_t osKernelGetTickCount(void),r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
extern uint32_t r1_battery_task_flags_set(uint32_t);
volatile uint8_t r1_nfc_irq_cursor __attribute__((section(".r1.nfc.irq.cursor")))=0;
volatile uint8_t r1_nfc_irq_suppressed __attribute__((section(".r1.nfc.irq.suppressed")))=0;
volatile uint32_t r1_nfc_irq_timestamps[7]
 __attribute__((section(".r1.nfc.irq.timestamps"),aligned(4)))={0};
const char r1_nfc_irq_suppress_ring[]="[RING][IRQ] suppressed! count:%d >= %d";
const char r1_nfc_irq_suppress_sdk[]="[IRQ] suppressed! count:%d >= %d";
const char r1_nfc_irq_resume_ring[]="[RING][IRQ] suppress cleared, count:%d";
const char r1_nfc_irq_resume_sdk[]="[IRQ] suppress cleared, count:%d";
void r1_nfc_charge_monitor_callback_00042d40(uint32_t argument)
{
 (void)argument;
 uint32_t now=osKernelGetTickCount();
 uint32_t cursor=r1_nfc_irq_cursor;
 r1_nfc_irq_timestamps[cursor]=now;
 r1_nfc_irq_cursor=(uint8_t)((cursor+1u)%7u);
 uint32_t count=0;
 for(uint32_t i=0;i<7;++i){
  uint32_t tick=r1_nfc_irq_timestamps[i];
  if(tick && (uint32_t)(now-tick)<=0x2800)++count;
 }
 if(count>=7){
  if(!r1_nfc_irq_suppressed){
   r1_nfc_irq_suppressed=1;
   if((r1_structured_log_mode_get()&1u) || (r1_structured_log_mode_get()&4u))
    (void)r1_structured_log_format(0x0c800000,r1_nfc_irq_suppress_ring,
                                 r1_nfc_irq_suppress_ring,count,7u);
   if(r1_structured_log_mode_get()&2u)
    nrf_log_frontend_std_2(0x001c0003,r1_nfc_irq_suppress_sdk,count,7);
  }
 }else{
  if(r1_nfc_irq_suppressed){
   r1_nfc_irq_suppressed=0;
   if((r1_structured_log_mode_get()&1u) || (r1_structured_log_mode_get()&4u))
    (void)r1_structured_log_format(0x0c400000,r1_nfc_irq_resume_ring,
                                 r1_nfc_irq_resume_ring,count);
   if(r1_structured_log_mode_get()&2u)
    nrf_log_frontend_std_1(0x001c0003,r1_nfc_irq_resume_sdk,count);
  }
  (void)r1_battery_task_flags_set(2);
 }
}
