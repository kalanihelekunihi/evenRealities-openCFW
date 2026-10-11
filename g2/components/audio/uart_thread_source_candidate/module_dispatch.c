/* Experimental TinyFrame received-frame dispatch, native0x4919e8.
 * The 24-byte message record is native memset0x4916b8 plus five fields. */
#include <stdint.h>

extern void audio_uart_module_timer_expire(void *,uint32_t,void *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                                uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern const char g2_tf_log_module[],g2_tf_log_file[];
extern const char g2_tf_dispatch_function[],g2_tf_unhandled_message[],
                  g2_tf_unhandled_short[];

void audio_uart_parser_frame_done(void *module) {
    uint8_t *base=(uint8_t *)module;
    uint32_t record[6]={0};
    *(uint16_t *)((uint8_t *)record+0u)=*(uint16_t *)(base+0x14u);
    *(uint16_t *)((uint8_t *)record+4u)=*(uint16_t *)(base+0x601eu);
    record[2]=(uint32_t)(uintptr_t)(base+0x18u);
    *(uint16_t *)((uint8_t *)record+12u)=*(uint16_t *)(base+0x16u);

    for(uint32_t slot=0u;slot<base[0x7158u];++slot) {
        uint8_t *timer=base+0x6430u+slot*0x18u;
        uint8_t (*listener)(void *,void *)=
            *(uint8_t (**)(void *,void *))(timer+4u);
        if(listener!=0 && *(uint16_t *)timer==*(uint16_t *)record) {
            record[4]=*(uint32_t *)(timer+16u);
            record[5]=*(uint32_t *)(timer+20u);
            uint8_t result=listener(module,record);
            *(uint32_t *)(timer+16u)=record[4];
            *(uint32_t *)(timer+20u)=record[5];
            if(result!=0u) {
                if(result==2u)
                    *(uint16_t *)(timer+12u)=*(uint16_t *)(timer+14u);
                else if(result==3u) {
                    *(uint32_t *)(timer+16u)=0u;
                    *(uint32_t *)(timer+20u)=0u;
                    audio_uart_module_timer_expire(module,slot,timer);
                }
                return;
            }
        }
    }

    record[4]=0u;record[5]=0u;
    for(uint32_t slot=0u;slot<base[0x7159u];++slot) {
        uint8_t *entry=base+0x7030u+slot*8u;
        uint8_t (*listener)(void *,void *)=
            *(uint8_t (**)(void *,void *))(entry+4u);
        if(listener!=0 && *(uint16_t *)entry==*(uint16_t *)
                ((uint8_t *)record+4u)) {
            uint8_t result=listener(module,record);
            if(result!=0u) {
                if(result==3u) {
                    *(uint32_t *)(entry+4u)=0u;
                    if(slot==(uint32_t)(uint8_t)(base[0x7159u]-1u))
                        --base[0x7159u];
                }
                return;
            }
        }
    }

    for(uint32_t slot=0u;slot<base[0x715au];++slot) {
        uint32_t *entry=(uint32_t *)(base+0x7130u+slot*4u);
        uint8_t (*listener)(void *,void *)=
            (uint8_t (*)(void *,void *))(uintptr_t)*entry;
        if(listener!=0) {
            uint8_t result=listener(module,record);
            if(result!=0u) {
                if(result==3u) {
                    *entry=0u;
                    if(slot==(uint32_t)(uint8_t)(base[0x715au]-1u))
                        --base[0x715au];
                }
                return;
            }
        }
    }
    if(audio_log_flags()&2u)
        audio_log_extended(1u,g2_tf_log_module,g2_tf_log_file,
                           g2_tf_dispatch_function,0x211u,
                           g2_tf_unhandled_message,record[1]&0xffffu);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0x04400000u,g2_tf_unhandled_short,
                                    g2_tf_unhandled_short,record[1]&0xffffu);
}
