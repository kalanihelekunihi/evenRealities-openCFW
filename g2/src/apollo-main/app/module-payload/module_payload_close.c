/* TinyFrame multipart payload 0x492114 and close 0x492198, including
 * byte-copy CRC 0x492032, footer 0x49207a, and flush wrapper 0x4d9522.
 * The actual sync UART send 0x541790 remains a typed code child. */
#include <stdint.h>
extern uint32_t audio_uart_sync_send(const void *,uint32_t,uint32_t); /* 0x541790 */
static uint16_t crc_update(uint16_t crc,uint8_t value) {
    crc^=value;
    for(uint32_t i=0u;i<8u;++i)
        crc=(uint16_t)((crc>>1)^((crc&1u)?0xa001u:0u));
    return crc;
}
static void flush(uint8_t *tf) {
    uint32_t count=*(uint32_t *)(tf+0x6424u);
    (void)audio_uart_sync_send(tf+0x6021u,count,100u);
}
void audio_uart_module_payload_core(void *module,const void *payload,
                                     uint32_t length) {
    uint8_t *tf=(uint8_t *)module;
    const uint8_t *src=(const uint8_t *)payload;
    uint32_t consumed=0u;
    while(length!=0u) {
        uint32_t used=*(uint32_t *)(tf+0x6424u);
        uint32_t take=length;
        if(0x400u-used<take) take=0x400u-used;
        uint16_t crc=*(uint16_t *)(tf+0x642cu);
        for(uint32_t i=0u;i<take;++i) {
            uint8_t value=src[consumed+i];
            tf[0x6021u+used+i]=value;
            crc=crc_update(crc,value);
        }
        *(uint16_t *)(tf+0x642cu)=crc;
        used+=take;
        *(uint32_t *)(tf+0x6424u)=used;
        length-=take;
        consumed+=take;
        if(used==0x400u) {
            flush(tf);
            *(uint32_t *)(tf+0x6424u)=0u;
        }
    }
}
void audio_uart_module_close_core(void *module) {
    uint8_t *tf=(uint8_t *)module;
    if(*(uint32_t *)(tf+0x6428u)!=0u) {
        uint32_t used=*(uint32_t *)(tf+0x6424u);
        if(0x400u-used<2u) {
            flush(tf);
            used=0u;
            *(uint32_t *)(tf+0x6424u)=0u;
        }
        uint16_t crc=*(uint16_t *)(tf+0x642cu);
        tf[0x6021u+used]=(uint8_t)(crc>>8);
        tf[0x6021u+used+1u]=(uint8_t)crc;
        *(uint32_t *)(tf+0x6424u)=used+2u;
    }
    flush(tf);
    tf[0x642eu]=0u;
}
