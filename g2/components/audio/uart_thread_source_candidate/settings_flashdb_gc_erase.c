/* Native FlashDB GC sector erase 0x5445f2. */
#include <stdint.h>
extern uint32_t audio_flashdb_partition_erase(uint32_t,uint32_t,uint32_t); /* 0x585a32 */
extern uint32_t g2_flashdb_set_status(uint8_t *,uint32_t,uint32_t); /* 0x585870 */
extern uint32_t g2_flashdb_flash_write(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t); /* 0x585a52 */
extern void g2_flashdb_update_sector_cache(uint32_t,const void *); /* 0x543c48 */
extern uint32_t g2_flashdb_db_path(uint32_t); /* 0x585c94 */
extern int32_t g2_flashdb_print(const char *,...); /* 0x4733ee */
static const char prefix[]="[FlashDB][kv]";
static const char names[]="[%s][%s] ";
static const char assertion[]="(%s) has assert failed at %s.\n";
static const char condition[]="addr % db_sec_size(db) == 0";
static const char source_path[]="format_sector";
static uint32_t word(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
static void put_word(uint8_t *p,uint32_t value) {
    p[0]=(uint8_t)value;p[1]=(uint8_t)(value>>8);
    p[2]=(uint8_t)(value>>16);p[3]=(uint8_t)(value>>24);
}
uint32_t audio_flashdb_gc_erase(uint32_t database,uint32_t address,uint32_t marker) {
    uint8_t *db=(uint8_t *)(uintptr_t)database;
    uint32_t sector_size=word(db+12u);
    uint8_t header[16]={0};
    if(address%sector_size!=0u) {
        (void)g2_flashdb_print(prefix);
        uint32_t path=g2_flashdb_db_path(database);
        (void)g2_flashdb_print(names,(const char *)(uintptr_t)word(db),(const char *)(uintptr_t)path);
        (void)g2_flashdb_print(assertion,condition,source_path);
        for(;;) {}
    }
    uint32_t result=(uint8_t)audio_flashdb_partition_erase(database,address,sector_size);
    if(result==0u) {
        for(uint32_t i=0u;i<16u;i++) header[i]=0xffu;
        (void)g2_flashdb_set_status(header,4u,1u);
        (void)g2_flashdb_set_status(header+1u,4u,1u);
        put_word(header+4u,0x30424446u);
        put_word(header+8u,marker);
        put_word(header+12u,UINT32_MAX);
        result=(uint8_t)g2_flashdb_flash_write(database,address,(uint32_t)(uintptr_t)header,16u,1u);
        uint8_t sector[24]={0};
        put_word(sector+4u,address);
        put_word(sector+20u,UINT32_MAX);
        g2_flashdb_update_sector_cache(database,sector);
    }
    return (uint8_t)result;
}
