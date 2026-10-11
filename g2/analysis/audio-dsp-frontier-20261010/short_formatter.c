#include <stdint.h>

extern uint32_t audio_log_flags(void);
extern uint32_t audio_log_level(void);
extern uint32_t audio_log_tick(void);
extern uint32_t audio_log_context(void);
extern uint32_t audio_string_length(const char *);
extern void audio_log_emit(const void *packet, uint32_t length);
extern volatile uint8_t audio_log_sequence;

static uint32_t word(const void *p) {
    const uint8_t *b=(const uint8_t *)p;
    return (uint32_t)b[0]|((uint32_t)b[1]<<8)|((uint32_t)b[2]<<16)|((uint32_t)b[3]<<24);
}
static void put_word(void *p,uint32_t v) {
    uint8_t *b=(uint8_t *)p;
    b[0]=(uint8_t)v;b[1]=(uint8_t)(v>>8);b[2]=(uint8_t)(v>>16);b[3]=(uint8_t)(v>>24);
}

/* Stock short formatter 0x43cb84. Encodes argument values in a 44-byte
 * event packet, rather than formatting them as printable text. */
void audio_log_short_format(uint32_t token, const char *format, const void *raw_args) {
    uint8_t packet[44];
    for (uint32_t i=0;i<44;i++) packet[i]=0;
    uint32_t category=(token>>26)&7u, limit=(token>>22)&15u;
    if (audio_log_flags()&4u) {
        if (category>=6u) return;
    } else if (audio_log_flags()&1u) {
        if (audio_log_level()<category) return;
    }
    uint32_t header=0x7bu;
    uint8_t seq=audio_log_sequence;
    audio_log_sequence=(uint8_t)(seq+1u);
    header|=(uint32_t)seq<<8;
    header|=(audio_log_tick()%1000u)<<16;
    header|=55u<<26;
    put_word(packet,header);
    put_word(packet+4,audio_log_context());
    put_word(packet+8,token);
    uint32_t used=0,length=12,count=0;
    uintptr_t cursor=(uintptr_t)raw_args;
    for (const char *p=format;*p && (uint16_t)used<32u && (uint8_t)count<(uint8_t)limit;++p) {
        if (*p!='%') continue;
        ++p;
        if (*p=='0'||*p=='-'||*p=='+'||*p==' '||*p=='#') ++p;
        while (*p>='0'&&*p<='9') ++p;
        if (*p=='.') {
            ++p;
            if (*p=='*') {cursor+=4;++p;}
            else while (*p>='0'&&*p<='9') ++p;
        }
        int longlong=0;
        if (*p=='l') {++p;if (*p=='l'){++p;longlong=1;}}
        else if (*p=='h') {++p;if (*p=='h') ++p;}
        if (!*p) continue;
        if (*p=='%') continue;
        if (*p=='s') {
            if ((uint16_t)(used+16u)<33u) {
                uintptr_t str=(uintptr_t)word((const void *)cursor);cursor+=4;
                uint32_t n=str?audio_string_length((const char *)str):0u;
                uint32_t copy=n<16u?n:16u;
                uint32_t start=n>=16u?n-16u:0u;
                for(uint32_t i=0;i<copy;i++) packet[12+used+i]=((const uint8_t *)str)[start+i];
                used+=16;length+=16;count++;
            } else {cursor+=4;count++;}
            continue;
        }
        if (*p=='f'||*p=='F') {
            cursor=(cursor+7u)&~(uintptr_t)7u;
            uint32_t lo=word((const void *)cursor),hi=word((const void *)(cursor+4));cursor+=8;
            if ((uint16_t)(used+4u)<33u) {
                union{uint64_t u;double d;} d={.u=((uint64_t)hi<<32)|lo};
                union{uint32_t u;float f;} f={.f=(float)d.d};
                put_word(packet+12+used,f.u);used+=4;length+=4;count++;
            } else count++;
            continue;
        }
        int numeric=(*p=='X'||*p=='c'||*p=='d'||*p=='i'||*p=='o'||*p=='p'||*p=='u'||*p=='x');
        if (numeric && longlong) cursor=(cursor+7u)&~(uintptr_t)7u;
        uint32_t v=word((const void *)cursor);cursor+=(numeric && longlong)?8u:4u;
        if ((uint16_t)(used+4u)<33u) {put_word(packet+12+used,v);used+=4;length+=4;}
        count++;
    }
    token=(token&~0x03c00000u)|((uint8_t)count<<22);
    put_word(packet+8,token);
    audio_log_emit(packet,(uint16_t)length);
}
