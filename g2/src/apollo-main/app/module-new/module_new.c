/* TinyFrame TF_InitStatic 0x491752, TF_Init 0x4917d2, and
 * TF_AddTypeListener 0x491962 from authenticated native source. */
#include <stdint.h>
extern void *codec_allocate(uint32_t); /* selected 0x474cd2 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="TinyFrame";
static const char source_file[]=
 "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\TinyFrame\\TinyFrame.c";
static const char static_function[]="TF_InitStatic";
static const char init_function[]="TF_Init";
static const char add_function[]="TF_AddTypeListener";
static const char static_error[]="[TF] :error TF_InitStatic() failed, tf is null.\n";
static const char static_error_short[]=
 "[TinyFrame][TF] :error TF_InitStatic() failed, tf is null.\n";
static const char alloc_error[]="[TF] :error TF_Init() failed, out of memory.\n";
static const char alloc_error_short[]=
 "[TinyFrame][TF] :error TF_Init() failed, out of memory.\n";
static const char add_error[]="[TF] :error Failed to add type listener\n";
static const char add_error_short[]=
 "[TinyFrame][TF] :error Failed to add type listener\n";
static void error_log(const char *function,uint32_t line,const char *message,
                      const char *short_message) {
    if(audio_log_flags()&2u)
        audio_log_extended(1u,module,source_file,function,line,message);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0x04000000u,short_message,
                                    short_message);
}
uint32_t audio_uart_module_init_static(void *memory,uint32_t master) {
    if(memory==0) {
        error_log(static_function,0xdcu,static_error,static_error_short);
        return 0u;
    }
    uint8_t *tf=(uint8_t *)memory;
    uint32_t preserved4=*(uint32_t *)(tf+4u);
    uint32_t preserved8=*(uint32_t *)(tf+8u);
    for(uint32_t i=0u;i<0x7160u;++i) tf[i]=0u;
    *(uint32_t *)(tf+8u)=preserved8;
    *(uint32_t *)(tf+4u)=preserved4;
    tf[12]=(uint8_t)master;
    *(uint32_t *)tf=0xa5a5a5a5u;
    *(uint32_t *)(tf+0x715cu)=0x5a5a5a5au;
    return 1u;
}
void *audio_uart_module_new(uint32_t master) {
    void *tf=codec_allocate(0x7160u);
    if(tf==0) {
        error_log(init_function,0xf4u,alloc_error,alloc_error_short);
        return 0;
    }
    (void)audio_uart_module_init_static(tf,master);
    return tf;
}
uint32_t audio_uart_module_listener(void *memory,uint32_t type,void *callback) {
    uint8_t *tf=(uint8_t *)memory;
    for(uint32_t i=0u;i<32u;++i) {
        uint8_t *record=tf+0x7030u+i*8u;
        if(*(uint32_t *)(record+4u)==0u) {
            *(uint32_t *)(record+4u)=(uint32_t)(uintptr_t)callback;
            *(uint16_t *)record=(uint16_t)type;
            if(tf[0x7159u]<=i) tf[0x7159u]=(uint8_t)(i+1u);
            return 1u;
        }
    }
    error_log(add_function,0x162u,add_error,add_error_short);
    return 0u;
}
