/* Native FlashDB space-search callbacks 0x5447b6 and 0x5447e0. */
#include <stdint.h>

static uint32_t word(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
static void put_word(uint8_t *p,uint32_t value) {
    p[0]=(uint8_t)value;p[1]=(uint8_t)(value>>8);
    p[2]=(uint8_t)(value>>16);p[3]=(uint8_t)(value>>24);
}

uint32_t audio_flashdb_space_count_callback(void *record,void *live_arg,void *deleted_arg) {
    const uint8_t *kv=(const uint8_t *)record;
    uint8_t *live_count=(uint8_t *)live_arg;
    uint8_t *deleted_count=(uint8_t *)deleted_arg;
    if(kv[0]!=0u&&kv[1]==1u)
        put_word(live_count,word(live_count)+1u);
    else if(kv[0]!=0u&&kv[1]==2u)
        put_word(deleted_count,word(deleted_count)+1u);
    return 0u;
}

uint32_t audio_flashdb_space_match_callback(void *record,void *context_arg,void *unused) {
    (void)unused;
    const uint8_t *kv=(const uint8_t *)record;
    const uint8_t *context=(const uint8_t *)context_arg;
    if(kv[0]==0u) return 0u;
    if(word(context+4u)+0x58u>=word(kv+16u)) return 0u;
    uint8_t type=kv[2];
    if(type!=1u) {
        if(type!=2u||*((const uint8_t *)(uintptr_t)word(context)+0x30u)!=0u)
            return 0u;
    }
    put_word((uint8_t *)(uintptr_t)word(context+8u),word(kv+20u));
    return 1u;
}
