/* CommonMalloc native 0x4646f0: ten mutex-owned heap attempts with
 * exponential CMSIS delay and exact diagnostic arguments. */
#include <stdint.h>
extern void *codec_allocate(uint32_t); /* selected 0x474cd2 */
extern uint32_t audio_delay(uint32_t); /* selected 0x449376 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="sync.module.api";
static const char source_file[]=
 "D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\sync_interface_api.c";
static const char function_name[]="CommonMalloc";
static const char message[]="malloc failed, retry %d/%d after %dms";
static const char short_message[]=
 "[sync.module.api]malloc failed, retry %d/%d after %dms";
/* Stock 0x4646F0 (CommonMalloc) */
void *audio_uart_alloc_retry(uint32_t bytes) {
    void *p=0;
    uint32_t delay=1u;
    for(uint32_t attempt=0u;attempt<10u;++attempt) {
        p=codec_allocate(bytes);
        if(p!=0) break;
        if(audio_log_flags()&2u)
            audio_log_extended(2u,module,source_file,function_name,0x1eu,
                               message,attempt+1u,10u,delay);
        if((audio_log_flags()&1u)||(audio_log_flags()&4u))
            (void)compressed_log_output(0x08c00000u,short_message,
                                        short_message,attempt+1u,10u,delay);
        (void)audio_delay(delay);
        delay<<=1;
    }
    return p;
}
