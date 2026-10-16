#include <stdint.h>
#include <stddef.h>
/* Native 7f030. Share the reset reader's canonical context. The crash
 * initializer remains an explicit provider, never a fabricated empty body. */
extern volatile uint32_t r1_reset_trace_context[6];
extern void __aeabi_memclr(void *,size_t);
extern void r1_health_crash_record_initializer(void);
extern int r1_native_vsnprintf(char *,size_t,const char *,volatile uint32_t *);
extern uint32_t r1_stdout_write(uint32_t,volatile void *,uint32_t);
__attribute__((used,noinline)) uint32_t r1_retained_log_body(volatile uint32_t *frame)
{
 volatile uint8_t *flag=(volatile uint8_t *)r1_reset_trace_context;
 volatile uint16_t *cursor=(volatile uint16_t *)(flag+2);
 if(!frame[4])return 0;
 if(!flag[0]){
  flag[0]=1;*cursor=0;
  __aeabi_memclr((void *)(uintptr_t)r1_reset_trace_context[3],3008);
  __aeabi_memclr((void *)(uintptr_t)r1_reset_trace_context[2],1008);
  uint32_t marker=r1_reset_trace_context[1];
  r1_reset_trace_context[4]=marker;
  *(volatile uint32_t *)(uintptr_t)marker=UINT32_C(0x5a5a5a5a);
  r1_health_crash_record_initializer();
 }
 uint32_t old=*cursor;
 int32_t available=3007-(int32_t)old;
 if(available<=0)return old;
 int32_t result=r1_native_vsnprintf((char *)(uintptr_t)(r1_reset_trace_context[3]+old),(size_t)available,(const char *)(uintptr_t)frame[4],frame+5);
 if(result>0){
  uint16_t next=(uint16_t)(*cursor+(uint32_t)result);*cursor=next;
  if(next>=3007)*cursor=3007;
  uint32_t at=*cursor;
  *(volatile uint8_t *)(uintptr_t)(r1_reset_trace_context[3]+at)=10;
  *cursor=(uint16_t)(at+1);
  uint32_t start=r1_reset_trace_context[3]+*cursor-(uint32_t)result-1;
  return r1_stdout_write(0,(volatile void *)(uintptr_t)start,(uint32_t)result+1);
 }
 return (uint32_t)result;
}
__attribute__((naked)) uint32_t r1_retained_log_printf_sink(const char *format __attribute__((unused)),...)
{
 __asm__ volatile("push {r0,r1,r2,r3}\n"
                  "push {r4,r5,r6,lr}\n"
                  "mov r0,sp\n"
                  "bl r1_retained_log_body\n"
                  "pop {r4,r5,r6}\n"
                  "ldr pc,[sp],#20\n");
}
