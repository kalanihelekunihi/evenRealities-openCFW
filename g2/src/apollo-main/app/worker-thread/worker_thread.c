/* Native thread-pool worker 0x49110c. Queue item size is 0x14, established
 * by selected pool constructor 0x491184; all callback argument words are
 * written by osMessageQueueGet into the stack item, not invented locals. */
#include <stdint.h>
#include <stddef.h>
extern void *audio_uart_pool_queue; /* live RAM 0x20074aa0 */
extern int32_t audio_uart_queue_receive(void *,void *,uint32_t,uint32_t); /* selected 0x449b3c */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char*,const char*,const char*,uint32_t,const char*,...);
extern uint32_t compressed_log_output(uint32_t,const char*,const char*,...);
static const char module[]="thread_pool";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\thread_pool.c";
static const char fn[]="worker_thread";
static const char extended[]="worker_thread app ID: %d running.";
static const char compact[]="[thread_pool]worker_thread app ID: %d running.";
static uint32_t rd32(const uint8_t *p) {return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
void audio_uart_worker_thread(void *unused) {
    (void)unused;
    for(;;) {
        uint8_t item[20];
        for(;;) {
            if(audio_uart_queue_receive(audio_uart_pool_queue,item,0u,UINT32_MAX)==0 &&
               rd32(item)!=0u) break;
        }
        uint32_t app_id=rd32(item+4u);
        if(audio_log_flags()&2u)
            audio_log_extended(4u,module,source,fn,0x3au,extended,app_id);
        if((audio_log_flags()&1u)||(audio_log_flags()&4u))
            (void)compressed_log_output(0x10400000u,compact,compact,app_id);
        void (*callback)(uint32_t,uint32_t,uint32_t,uint32_t)=
            (void (*)(uint32_t,uint32_t,uint32_t,uint32_t))(uintptr_t)rd32(item);
        callback(app_id,rd32(item+12u),rd32(item+16u),
                 (uint32_t)((uint16_t)item[8]|((uint16_t)item[9]<<8)));
    }
}
