/* Native WsfBufAlloc 0x530446: size class scan and free-list pop. */
#include <stdint.h>
struct wsf_pool_desc_init;
extern struct wsf_pool_desc_init *audio_wsf_pool_list; /* selected WsfBufInit product BSS */
extern volatile uint8_t audio_wsf_pool_count; /* selected WsfBufInit product BSS */
extern void WsfCsEnter(void);
extern void WsfCsExit(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
void *WsfBufAlloc(uint16_t length) {
    const uint8_t *const classes=(const uint8_t *)audio_wsf_pool_list;
    for(uint32_t i=0u;i<audio_wsf_pool_count;i++) {
        const uint8_t *row=classes+i*12u;
        uint16_t capacity=(uint16_t)row[0]|(uint16_t)((uint16_t)row[1]<<8u);
        if(length>capacity)continue;
        WsfCsEnter();
        uint8_t *block=*(uint8_t *const *)(const void *)(row+8u);
        if(block) {
            *(uint8_t **)(void *)(row+8u)=*(uint8_t **)(void *)block;
            *(uint32_t *)(void *)(block+4u)=0u;
            WsfCsExit();
            return block;
        }
        WsfCsExit();
    }
    if(audio_log_flags()&2u)
        audio_log_extended(1u,"wsf.buf",
            "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\wsf\\sources\\port\\freertos\\wsf_buf.c",
            "WsfBufAlloc",0x141u,"WsfBufAlloc failed len:%u",length);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0x04400000u,
            "[wsf.buf]WsfBufAlloc failed len:%u",
            "[wsf.buf]WsfBufAlloc failed len:%u",length);
    return 0;
}
