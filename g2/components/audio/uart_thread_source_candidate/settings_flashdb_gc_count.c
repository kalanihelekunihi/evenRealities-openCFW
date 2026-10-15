/* Native FlashDB GC sector-count callback 0x544b84. */
#include <stdint.h>
static uint32_t word(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
static void put_word(uint8_t *p,uint32_t value) {
    p[0]=(uint8_t)value;p[1]=(uint8_t)(value>>8);
    p[2]=(uint8_t)(value>>16);p[3]=(uint8_t)(value>>24);
}
uint32_t audio_flashdb_gc_count_callback(void *record,void *count_arg,void *address_arg) {
    const uint8_t *sector=(const uint8_t *)record;
    if(sector[0u]!=0u) {
        uint8_t *count=(uint8_t *)count_arg;
        put_word(count,word(count)+1u);
        put_word((uint8_t *)address_arg,word(sector+4u));
    }
    return 0u;
}
