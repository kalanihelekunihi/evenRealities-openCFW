/* Stock 0x824a0: disconnect cleanup of the existing shared ACK registry. */
#include "native_ack_registry.h"
#include "../board/native_battery_memory.h"
extern uint32_t r1_ack_table_lock(void),r1_ack_table_unlock(void);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_5(uint32_t,const char *,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern void vPortFree(void *);
static const char ring[]="[RING]ack clear: module=%d cmd=%d sub=%d seq=%d, free param=%p";
static const char sdk[]="ack clear: module=%d cmd=%d sub=%d seq=%d, free param=%p";
uint32_t r1_ack_table_clear(void)
{
 (void)r1_ack_table_lock();
 for(uint32_t i=0;i<32;i++){
  volatile uint8_t *record=r1_protocol_reset_workspace+20*i;
  if(!record[0])continue;
  if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
   (void)r1_structured_log_format(0x0d400000,ring,ring,record[1],record[2],record[3],read16(record+4),read32(record+12));
  if(r1_structured_log_mode_get()&2u)
   nrf_log_frontend_std_5(0x001c0003,sdk,record[1],record[2],record[3],read16(record+4),read32(record+12));
  uint32_t argument=read32(record+12);
  if(argument)vPortFree((void *)(uintptr_t)argument);
  record[0]=0;write32(record+8,0);write32(record+12,0);
 }
 return r1_ack_table_unlock();
}
