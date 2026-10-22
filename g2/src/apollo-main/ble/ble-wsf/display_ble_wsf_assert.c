/* Native WsfAssert 0x569a44, including its reset/idle behavior. */
#include <stdint.h>

extern uint32_t audio_log_flags(void); /* selected 0x43d0ce */
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern void g2_log_fatal_idle(void) __attribute__((noreturn)); /* selected 0x44ab24 */
extern uintptr_t audio_ble_wsf_assert_hook; /* live 0x2007456c */

static const char module[]="wsf.assert";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\wsf\\sources\\port\\freertos\\wsf_assert.c";
static const char name[]="WsfAssert";
static const char message[]="%s, line = %d";
static const char compact[]="[wsf.assert]%s, line = %d";
static const char elog_module[]="elog";
static const char null_format[]="(%s) has assert failed at %s:%ld.";
static const char file_word[]="pFile";

void audio_ble_wsf_assert(const char *file,uint32_t line) __attribute__((noreturn));
/* Stock 0x569A44 (WsfAssert) */
void audio_ble_wsf_assert(const char *file,uint32_t line) {
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(1u,module,path,name,0x2bu,message,file,line);
    uint32_t flags=audio_log_flags();
    if((flags&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x4800000u,compact,compact,file,line);
    if(file==0) {
        uintptr_t hook=audio_ble_wsf_assert_hook;
        if(hook==0u) {
            audio_log_extended(0u,elog_module,path,name,0x2cu,
                               null_format,file_word,name,0x2cu);
            g2_log_fatal_idle();
        }
        ((void (*)(const char *,const char *,uint32_t))hook)(file_word,name,0x2cu);
    }
    for(;;) __asm__ volatile("nop" ::: "memory");
}
