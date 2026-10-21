#include "instance.h"
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern void uart_thread_handler(void *argument);
extern void *osThreadNew(void (*function)(void *),void *argument,const void *attributes);
extern uint32_t platform_log_flags(void);
extern void platform_log_error(uint32_t level,const void *module,const void *file,
                               const void *format,uint32_t line,const void *function);
extern void compressed_log_output(uint32_t mask,const void *message,const void *message_copy);
int32_t uart_instance_init(void){
 void *thread=osThreadNew(uart_thread_handler,0,(const void *)(uintptr_t)0x75c1ecu);
 W(0x20074b0c)=(uint32_t)(uintptr_t)thread;
 if(thread)return 0;
 if(platform_log_flags()&2u)
  platform_log_error(1,(const void *)(uintptr_t)0x7846d0u,
    (const void *)(uintptr_t)0x710b64u,(const void *)(uintptr_t)0x7846e4u,
    197,(const void *)(uintptr_t)0x75c1c8u);
 if((platform_log_flags()&1u)||(platform_log_flags()&4u))
  compressed_log_output(0x04000000u,(const void *)(uintptr_t)0x72fa80u,
    (const void *)(uintptr_t)0x72fa80u);
 return -1;
}
