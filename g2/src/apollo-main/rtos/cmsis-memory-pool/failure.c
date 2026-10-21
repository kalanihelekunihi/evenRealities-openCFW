/* Recovered main-image failure/logger wrapper, not full formatter attribution. */
#include <stdint.h>
#include <stdarg.h>
extern uint32_t audio_heap_formatter(char *,const char *,va_list);
uint32_t audio_heap_log(const char *format,...){
 if(!*(volatile uint32_t *)0x200742f0u)return 0;
 va_list args;va_start(args,format);
 uint32_t result=audio_heap_formatter((char*)0x2006b930u,format,args);
 va_end(args);
 ((void(*)(char*))(uintptr_t)*(volatile uint32_t*)0x200742f0u)((char*)0x2006b930u);
 return result;
}
__attribute__((noreturn)) void audio_heap_malloc_failed(void){
 audio_heap_log((const char*)0x758f70u);
 for(;;){}
}
