/* Stock Main 0x48ed00 and its little-endian/CRC helpers: TPF1 file header. */
#include <stdint.h>

extern uint32_t audio_tracepoint_version_47dd08(void);

void audio_tracepoint_put_le16_48ece2(uint8_t *out,uint16_t value) {
    out[0]=(uint8_t)value;
    out[1]=(uint8_t)(value>>8);
}

void audio_tracepoint_put_le32_48ecec(uint8_t *out,uint32_t value) {
    out[0]=(uint8_t)value;
    out[1]=(uint8_t)(value>>8);
    out[2]=(uint8_t)(value>>16);
    out[3]=(uint8_t)(value>>24);
}

uint32_t audio_tracepoint_crc32_48ecae(const uint8_t *data,uint32_t length) {
    uint32_t crc=0xffffffffu;
    for(uint32_t i=0;i<length;i++) {
        crc^=data[i];
        for(uint32_t bit=0;bit<8u;bit++)
            crc=(crc>>1) ^ ((crc&1u)!=0u ? 0xedb88320u : 0u);
    }
    return ~crc;
}

void audio_tracepoint_build_header_48ed00(uint8_t *out,uint32_t sequence,
                                           uint32_t generation) {
    out[0]='T';out[1]='P';out[2]='F';out[3]='1';
    audio_tracepoint_put_le16_48ece2(out+4u,3u);
    audio_tracepoint_put_le16_48ece2(out+6u,32u);
    audio_tracepoint_put_le32_48ecec(out+8u,audio_tracepoint_version_47dd08());
    audio_tracepoint_put_le32_48ecec(out+12u,512u);
    audio_tracepoint_put_le32_48ecec(out+16u,sequence);
    audio_tracepoint_put_le32_48ecec(out+20u,generation);
    audio_tracepoint_put_le32_48ecec(out+24u,1000000u);
    audio_tracepoint_put_le32_48ecec(out+28u,audio_tracepoint_crc32_48ecae(out,28u));
}
