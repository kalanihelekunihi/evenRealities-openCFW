/* TinyFrame TX claim 0x4916c8, ID listener 0x4918c2, header 0x491f54,
 * and begin engine 0x4920aa. CRC16/ARC recurrence matches the authenticated
 * native 0xa001 table and the receive parser's bounded comparison. */
#include <stdint.h>
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="TinyFrame";
static const char source_file[]=
 "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\TinyFrame\\TinyFrame.c";
static const char claim_function[]="TF_ClaimTx";
static const char claim_message[]="[TF] :error TF already locked for tx!\n";
static const char claim_short[]="[TinyFrame][TF] :error TF already locked for tx!\n";
static const char listener_function[]="TF_AddIdListener";
static const char listener_message[]="[TF] :error Failed to add ID listener\n";
static const char listener_short[]="[TinyFrame][TF] :error Failed to add ID listener\n";
static void log_failure(const char *function,uint32_t line,const char *message,
                        const char *short_message) {
    if(audio_log_flags()&2u)
        audio_log_extended(1u,module,source_file,function,line,message);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0x04000000u,short_message,
                                    short_message);
}
static uint16_t crc_update(uint16_t crc,uint8_t value) {
    crc^=value;
    for(uint32_t i=0u;i<8u;++i)
        crc=(uint16_t)((crc>>1)^((crc&1u)?0xa001u:0u));
    return crc;
}
static uint32_t add_id_listener(uint8_t *tf,uint8_t *frame,void *on_begin,
                                void *on_end,uint16_t timeout) {
    for(uint32_t i=0u;i<128u;++i) {
        uint8_t *entry=tf+0x6430u+i*0x18u;
        if(*(uint32_t *)(entry+4u)==0u) {
            *(uint32_t *)(entry+4u)=(uint32_t)(uintptr_t)on_begin;
            *(uint32_t *)(entry+8u)=(uint32_t)(uintptr_t)on_end;
            *(uint16_t *)entry=*(uint16_t *)frame;
            *(uint32_t *)(entry+0x10u)=*(uint32_t *)(frame+0x10u);
            *(uint32_t *)(entry+0x14u)=*(uint32_t *)(frame+0x14u);
            *(uint16_t *)(entry+0xcu)=timeout;
            *(uint16_t *)(entry+0xeu)=timeout;
            if(tf[0x7158u]<=i) tf[0x7158u]=(uint8_t)(i+1u);
            return 1u;
        }
    }
    log_failure(listener_function,0x14cu,listener_message,listener_short);
    return 0u;
}
static uint32_t write_header(uint8_t *tf,uint8_t *frame) {
    uint16_t id;
    if(frame[2u]==0u) {
        id=*(uint16_t *)(tf+0xeu);
        *(uint16_t *)(tf+0xeu)=(uint16_t)(id+1u);
        id&=0x7fffu;
        if(tf[0xcu]!=0u) id|=0x8000u;
    } else id=*(uint16_t *)frame;
    *(uint16_t *)frame=id;
    uint16_t size=*(uint16_t *)(frame+0xcu);
    uint16_t type=*(uint16_t *)(frame+4u);
    uint8_t *dst=tf+0x6021u;
    uint16_t crc=crc_update(0u,1u);
    dst[0]=1u;
    uint16_t words[3]={id,size,type};
    uint32_t at=1u;
    for(uint32_t j=0u;j<3u;++j) {
        uint8_t hi=(uint8_t)(words[j]>>8),lo=(uint8_t)words[j];
        dst[at++]=hi;crc=crc_update(crc,hi);
        dst[at++]=lo;crc=crc_update(crc,lo);
    }
    dst[at++]=(uint8_t)(crc>>8);
    dst[at++]=(uint8_t)crc;
    return at;
}
uint32_t audio_uart_module_begin_core(void *module_ptr,void *frame_ptr,
                                      void *on_begin,void *on_end,
                                      uint16_t timeout) {
    uint8_t *tf=(uint8_t *)module_ptr,*frame=(uint8_t *)frame_ptr;
    if(tf[0x642eu]!=0u) {
        log_failure(claim_function,0x23u,claim_message,claim_short);
        return 0u;
    }
    tf[0x642eu]=1u;
    *(uint32_t *)(tf+0x6424u)=write_header(tf,frame);
    *(uint32_t *)(tf+0x6428u)=*(uint16_t *)(frame+0xcu);
    if(on_begin!=0 && add_id_listener(tf,frame,on_begin,on_end,timeout)==0u) {
        tf[0x642eu]=0u;
        return 0u;
    }
    *(uint16_t *)(tf+0x642cu)=0u; /* native CRC_Init returns zero */
    return 1u;
}
