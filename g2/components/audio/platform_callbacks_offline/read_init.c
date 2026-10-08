#include "callbacks.h"
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t platform_copy_words(uint32_t source,uint32_t *destination,uint32_t words);
extern void platform_finish_init(void);
uint32_t audio_platform_read_words(uint32_t kind,uint32_t offset,uint32_t count,uint32_t *dst) {
    kind=(uint8_t)kind;
    uint32_t cfg=W(0x400201bc),power=W(0x40021008),limit;
    if(!dst) return 6;
    switch(kind) {
    case 0: limit=(cfg&(1u<<4))?0x40:0x200; break;
    case 1: limit=(cfg&(1u<<3))?0x2c0:0x600; break;
    case 2: limit=0x40; break;
    case 3: limit=0x2c0; break;
    case 4: limit=0x200; break;
    case 5: limit=0x600; break;
    default: return 6;
    }
    /* Exact uint32 addition: does not repair stock overflow behavior. */
    if(offset+count>limit) return 5;
    uint32_t base,word_offset=offset;
    if(kind==0) {
        if(cfg&(1u<<4)) { if(!(power&(1u<<27))) return 9; base=0x42004000; }
        else base=0x42000000;
    } else if(kind==1) {
        base=0x42002000;
        if(cfg&(1u<<3)) { if(!(power&(1u<<27))) return 9; base=0x42006000; }
        else if(offset>=0x200) word_offset+=0x280;
    } else if(kind==2 || kind==3) {
        if(!(power&(1u<<27))) return 9;
        base=kind==2?0x42004000:0x42006000;
    } else base=kind==4?0x42000000:0x42002000;
    (void)platform_copy_words(base+word_offset*4u,dst,count);
    return 0;
}
uint32_t audio_platform_read_words_restricted(uint32_t kind,uint32_t offset,uint32_t count,uint32_t *dst) {
    uint8_t k=kind;
    return (k==1||k==3||k==5) ? audio_platform_read_words(k,offset,count,dst) : 6;
}
uint32_t audio_platform_newer_initialize(void) {
    if((W(0x400201bc)&8u) && !(W(0x40021008)&(1u<<27))) return 7;
    uint32_t *data=(uint32_t *)(uintptr_t)0x2005665c;
    uint32_t result=audio_platform_read_words_restricted(1,0x25c,20,data+1);
    if(result) return result;
    uint32_t temporary[5];
    result=audio_platform_read_words_restricted(1,0x270,5,temporary);
    if(result) return result;
    for(unsigned i=0;i<5;i++) data[21+i]=temporary[i];
    result=audio_platform_read_words_restricted(1,0x278,1,temporary);
    if(result) return result;
    data[26]=temporary[0];data[0]=0x1f01600d;
    platform_finish_init();return 0;
}

uint32_t audio_platform_get_revision(uint32_t *destination) {
    uint32_t *cached=(uint32_t *)(uintptr_t)0x200001e8;
    if(*cached==0xffffffffu) {
        uint32_t result=audio_platform_read_words_restricted(1,0x244,1,cached);
        if(*cached==0 || result!=0) *cached=0;
    }
    if(!destination) return 6;
    *destination=*cached;return 0;
}
