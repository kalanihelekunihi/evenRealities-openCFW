#include <stdint.h>
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern uint32_t r1_reset_trace_program_counter_read(uint32_t *);
extern uint32_t r1_reset_trace_return_address_read(uint32_t *);
extern uint32_t r1_reset_trace_byte_read(uint32_t,uint8_t *);
#define DATA(name) __attribute__((section(".r1.reset.decode." #name),used))
DATA(bounds) const uint32_t r1_reset_decode_bounds[2]={0xc44fcu,0xc441cu};
DATA(zero_ring) const char r1_reset_decode_zero_ring[48]="[RING]Reset reason: Power-on or brown-out reset";
DATA(zero_sdk) const char r1_reset_decode_zero_sdk[44]="Reset reason: Power-on or brown-out reset";
DATA(pin_ring) const char r1_reset_decode_pin_ring[44]="[RING]Reset reason: Pin reset (RESETPIN)";
DATA(pin_sdk) const char r1_reset_decode_pin_sdk[36]="Reset reason: Pin reset (RESETPIN)";
DATA(dog_ring) const char r1_reset_decode_dog_ring[44]="[RING]Reset reason: Watchdog reset (DOG)";
DATA(dog_sdk) const char r1_reset_decode_dog_sdk[36]="Reset reason: Watchdog reset (DOG)";
DATA(sreq_ring) const char r1_reset_decode_sreq_ring[60]="[RING]Reset reason: Software system reset request (SREQ)";
DATA(sreq_sdk) const char r1_reset_decode_sreq_sdk[52]="Reset reason: Software system reset request (SREQ)";
DATA(pc_ring) const char r1_reset_decode_pc_ring[60]="[RING]SREQ NVIC_SystemReset hook PC (before AIRCR): 0x%08x";
DATA(pc_sdk) const char r1_reset_decode_pc_sdk[56]="SREQ NVIC_SystemReset hook PC (before AIRCR): 0x%08x";
DATA(lr_ring) const char r1_reset_decode_lr_ring[68]="[RING]SREQ NVIC_SystemReset return addr (LR, map/addr2line): 0x%08x";
DATA(lr_sdk) const char r1_reset_decode_lr_sdk[64]="SREQ NVIC_SystemReset return addr (LR, map/addr2line): 0x%08x";
DATA(tag_ring) const char r1_reset_decode_tag_ring[60]="[RING]SREQ persist tag: %u (see persist_reset_log_code_e)";
DATA(tag_sdk) const char r1_reset_decode_tag_sdk[52]="SREQ persist tag: %u (see persist_reset_log_code_e)";
DATA(caller_ring) const char r1_reset_decode_caller_ring[60]="[RING]SREQ reboot caller: %u (see persist_reboot_caller_e)";
DATA(caller_sdk) const char r1_reset_decode_caller_sdk[56]="SREQ reboot caller: %u (see persist_reboot_caller_e)";
DATA(unread_ring) const char r1_reset_decode_unread_ring[44]="[RING]SREQ persist tag: unreadable or stale";
DATA(unread_sdk) const char r1_reset_decode_unread_sdk[40]="SREQ persist tag: unreadable or stale";
DATA(lock_ring) const char r1_reset_decode_lock_ring[48]="[RING]Reset reason: CPU lock-up reset (LOCKUP)";
DATA(lock_sdk) const char r1_reset_decode_lock_sdk[44]="Reset reason: CPU lock-up reset (LOCKUP)";
DATA(off_ring) const char r1_reset_decode_off_ring[64]="[RING]Reset reason: Wake from System OFF by GPIO DETECT (OFF)";
DATA(off_sdk) const char r1_reset_decode_off_sdk[56]="Reset reason: Wake from System OFF by GPIO DETECT (OFF)";
DATA(lpcomp_ring) const char r1_reset_decode_lpcomp_ring[60]="[RING]Reset reason: Wake from System OFF by LPCOMP (LPCOMP)";
DATA(lpcomp_sdk) const char r1_reset_decode_lpcomp_sdk[56]="Reset reason: Wake from System OFF by LPCOMP (LPCOMP)";
DATA(dif_ring) const char r1_reset_decode_dif_ring[68]="[RING]Reset reason: Wake from System OFF by debug interface (DIF)";
DATA(dif_sdk) const char r1_reset_decode_dif_sdk[60]="Reset reason: Wake from System OFF by debug interface (DIF)";
DATA(lr_pointer) const char * const r1_reset_decode_lr_pointer=r1_reset_decode_lr_ring;
DATA(dif_pointer) const char * const r1_reset_decode_dif_pointer=r1_reset_decode_dif_ring;
static __attribute__((always_inline)) inline uint32_t header(void)
{return (((r1_reset_decode_bounds[0]-r1_reset_decode_bounds[1])>>3)<<16)+3;}
static __attribute__((always_inline)) inline void log0(const char *ring,const char *sdk)
{
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))r1_structured_log_format(0x0c000000u,ring,ring);
 if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0(header(),sdk);
}
static __attribute__((always_inline)) inline void log1(const char *ring,const char *sdk,const uint32_t *value,uint32_t mask)
{
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))r1_structured_log_format(0x0c400000u,ring,ring,*value&mask);
 if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_1(header(),sdk,*value&mask);
}
uint32_t r1_reset_reason_decode_kernel(uint32_t raw,uint32_t incoming_r1,uint32_t incoming_r2,uint32_t incoming_r3)
{
 (void)incoming_r1;(void)incoming_r2;
 uint32_t pc=0,lr=0,tag_word=raw&0xffffff00u,caller_word=incoming_r3&0xffffff00u;
 if(!raw){log0(r1_reset_decode_zero_ring,r1_reset_decode_zero_sdk);return 0;}
 if(raw&1u)log0(r1_reset_decode_pin_ring,r1_reset_decode_pin_sdk);
 if(raw&2u)log0(r1_reset_decode_dog_ring,r1_reset_decode_dog_sdk);
 if(raw&4u){
  log0(r1_reset_decode_sreq_ring,r1_reset_decode_sreq_sdk);
  if(r1_reset_trace_program_counter_read(&pc))log1(r1_reset_decode_pc_ring,r1_reset_decode_pc_sdk,&pc,0xffffffffu);
  if(r1_reset_trace_return_address_read(&lr))log1(r1_reset_decode_lr_pointer,r1_reset_decode_lr_sdk,&lr,0xffffffffu);
  if(r1_reset_trace_byte_read(0,(uint8_t *)&tag_word)){
   log1(r1_reset_decode_tag_ring,r1_reset_decode_tag_sdk,&tag_word,0xff);
   if((uint8_t)tag_word==2 && r1_reset_trace_byte_read(1,(uint8_t *)&caller_word))log1(r1_reset_decode_caller_ring,r1_reset_decode_caller_sdk,&caller_word,0xff);
  }else log0(r1_reset_decode_unread_ring,r1_reset_decode_unread_sdk);
 }
 if(raw&8u)log0(r1_reset_decode_lock_ring,r1_reset_decode_lock_sdk);
 if(raw&0x10000u)log0(r1_reset_decode_off_ring,r1_reset_decode_off_sdk);
 if(raw&0x20000u)log0(r1_reset_decode_lpcomp_ring,r1_reset_decode_lpcomp_sdk);
 if(raw&0x40000u)log0(r1_reset_decode_dif_pointer,r1_reset_decode_dif_sdk);
 return raw&0x7000fu;
}
/* Preserve incoming scratch-register seed bytes via an explicit raw ABI bridge. */
__attribute__((naked,noinline)) uint32_t r1_reset_reason_decode_and_report(uint32_t raw __attribute__((unused)))
{__asm__ volatile("b r1_reset_reason_decode_kernel");}

