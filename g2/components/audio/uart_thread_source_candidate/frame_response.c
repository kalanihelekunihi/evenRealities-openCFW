/* TinyFrame TF_Respond/TF_SendSimple/TF_Send layers at
 * 0x49225a/0x49223c/0x492200. The setup, data feed and finish
 * descendants are explicit native code contracts. */
#include <stdint.h>
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern uint32_t audio_uart_sync_write(const void *,uint32_t); /* 0x584c98 */

void audio_uart_frame_output(void *tf,const void *bytes,uint32_t length) {
    (void)tf;
    (void)audio_uart_sync_write(bytes,length); /* native 0x4d9522 -> 0x541790 -> 0x584c98; timeout 100 is ignored */
}

uint16_t audio_uart_frame_checksum_byte(uint16_t crc,uint8_t value) {
    uint16_t entry=(uint16_t)((crc^value)&0xffu);
    for(uint32_t i=0u;i<8u;++i)
        entry=(uint16_t)((entry>>1u)^((entry&1u)?0xa001u:0u));
    return (uint16_t)(entry^(crc>>8u));
}
uint16_t audio_uart_frame_checksum_finalize(uint16_t crc) {return crc;}
uint32_t audio_uart_frame_header(void *tf,void *destination,const void *frame) {
    uint8_t *state=(uint8_t *)tf;
    uint8_t *out=(uint8_t *)destination;
    uint8_t *desc=(uint8_t *)frame;
    uint16_t id=*(uint16_t *)(void *)desc;
    if(desc[2u]==0u) {
        id=*(uint16_t *)(void *)(state+0xeu);
        *(uint16_t *)(void *)(state+0xeu)=(uint16_t)(id+1u);
        id&=0x7fffu;
        if(state[0xcu]!=0u) id|=0x8000u;
    }
    *(uint16_t *)(void *)desc=id;
    uint16_t crc=audio_uart_frame_checksum_byte(0u,1u);
    out[0]=1u;
    uint16_t fields[3]={id,
        *(const uint16_t *)(const void *)(desc+12u),
        *(const uint16_t *)(const void *)(desc+4u)};
    uint32_t cursor=1u;
    for(uint32_t j=0u;j<3u;++j) {
        uint8_t hi=(uint8_t)(fields[j]>>8u),lo=(uint8_t)fields[j];
        out[cursor++]=hi;crc=audio_uart_frame_checksum_byte(crc,hi);
        out[cursor++]=lo;crc=audio_uart_frame_checksum_byte(crc,lo);
    }
    crc=audio_uart_frame_checksum_finalize(crc);
    out[cursor++]=(uint8_t)(crc>>8u);
    out[cursor++]=(uint8_t)crc;
    return cursor;
}

uint32_t audio_uart_frame_sequence(void) {return 0u;}
void audio_uart_frame_reset(void *tf) {((uint8_t *)tf)[0x642eu]=0u;}
uint32_t audio_uart_frame_check(void *tf) {
    uint8_t *state=(uint8_t *)tf;
    if(state[0x642eu]==0u) {state[0x642eu]=1u;return 1u;}
    static const char module[]="TinyFrame";
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\TinyFrame\\TinyFrame.c";
    static const char fn[]="TF_ClaimTx";
    static const char e_busy[]="[TF] :error TF already locked for tx!\n";
    static const char c_busy[]="[TinyFrame][TF] :error TF already locked for tx!\n";
    if(audio_log_flags()&2u)
        audio_log_extended(1u,module,source,fn,0x23u,e_busy);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0x4000000u,c_busy,c_busy);
    return 0u;
}
uint32_t audio_uart_frame_payload_code(void *destination,const void *source,
                                        uint16_t count,void *checksum) {
    uint8_t *out=(uint8_t *)destination;
    const uint8_t *in=(const uint8_t *)source;
    uint16_t *crc=(uint16_t *)checksum;
    for(uint32_t i=0u;i<count;++i) {
        out[i]=in[i];
        *crc=audio_uart_frame_checksum_byte(*crc,in[i]);
    }
    return count;
}
uint32_t audio_uart_frame_checksum_code(void *destination,void *checksum) {
    uint16_t *crc=(uint16_t *)checksum;
    *crc=audio_uart_frame_checksum_finalize(*crc);
    uint8_t *out=(uint8_t *)destination;
    out[0]=(uint8_t)(*crc>>8u);
    out[1]=(uint8_t)*crc;
    return 2u;
}

uint32_t audio_uart_frame_setup(void *tf,void *frame,uint32_t extra,
                                 uint32_t flags,uint16_t sequence) {
    uint8_t *state=(uint8_t *)tf;
    if(audio_uart_frame_check(tf)==0u) return 0u;
    *(uint32_t *)(void *)(state+0x6424u)=
        audio_uart_frame_header(tf,state+0x6021u,frame);
    *(uint32_t *)(void *)(state+0x6428u)=
        *(const uint16_t *)(const void *)((const uint8_t *)frame+12u);
    if(extra!=0u) {
        extern uint32_t audio_uart_frame_extra(void *,void *,uint32_t,uint32_t,uint16_t); /* 0x4918c2 */
        if(audio_uart_frame_extra(tf,frame,extra,flags,sequence)==0u) {
            audio_uart_frame_reset(tf);
            return 0u;
        }
    }
    *(uint16_t *)(void *)(state+0x642cu)=(uint16_t)audio_uart_frame_sequence();
    return 1u;
}
void audio_uart_frame_feed(void *tf,const void *payload,uint16_t length) {
    uint8_t *state=(uint8_t *)tf;
    uint32_t offset=0u;
    uint32_t pending=length;
    while(pending!=0u) {
        uint32_t used=*(uint32_t *)(void *)(state+0x6424u);
        uint32_t n=0x400u-used;
        if(n>pending) n=pending;
        used+=audio_uart_frame_payload_code(state+0x6021u+used,
                                             (const uint8_t *)payload+offset,
                                             (uint16_t)n,state+0x642cu);
        *(uint32_t *)(void *)(state+0x6424u)=used;
        pending-=n;
        offset+=n;
        if(used==0x400u) {
            audio_uart_frame_output(tf,state+0x6021u,used);
            *(uint32_t *)(void *)(state+0x6424u)=0u;
        }
    }
}
void audio_uart_frame_finish(void *tf) {
    uint8_t *state=(uint8_t *)tf;
    uint32_t used=*(uint32_t *)(void *)(state+0x6424u);
    if(*(uint32_t *)(void *)(state+0x6428u)!=0u) {
        if(0x400u-used<2u) {
            audio_uart_frame_output(tf,state+0x6021u,used);
            used=0u;
            *(uint32_t *)(void *)(state+0x6424u)=0u;
        }
        used+=audio_uart_frame_checksum_code(state+0x6021u+used,
                                               state+0x642cu);
        *(uint32_t *)(void *)(state+0x6424u)=used;
    }
    audio_uart_frame_output(tf,state+0x6021u,used);
    audio_uart_frame_reset(tf);
}

uint32_t audio_uart_frame_send(void *tf,void *frame) {
    uint8_t *descriptor=(uint8_t *)frame;
    if(audio_uart_frame_setup(tf,frame,0u,0u,0u)==0u) return 0u;
    const void *payload=*(const void *const *)(const void *)(descriptor+8u);
    uint16_t length=*(const uint16_t *)(const void *)(descriptor+12u);
    if(length==0u||payload!=0)
        audio_uart_frame_feed(tf,payload,length);
    audio_uart_frame_finish(tf);
    return 1u;
}
void audio_uart_frame_respond(void *tf,void *frame) {
    ((uint8_t *)frame)[2u]=1u;
    (void)audio_uart_frame_send(tf,frame);
}
