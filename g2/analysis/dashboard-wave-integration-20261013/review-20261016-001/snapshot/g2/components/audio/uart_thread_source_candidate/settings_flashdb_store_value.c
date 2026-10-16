/* Native FlashDB KV store 0x544d60. The selected FlashDB C lower providers
 * own CRC, flash writes, status encoding, GC retry and cache operations. */
#include <stdint.h>

extern uint32_t g2_log_candidate_module_length(const uint8_t *);
extern int32_t g2_flashdb_print(const char *,...);
extern uint32_t g2_flashdb_db_path(uint32_t);
extern int32_t audio_flashdb_prepare_space(void *,void *,uint32_t);
extern uint32_t g2_flashdb_write_status(uint32_t,uint32_t,uint8_t *,uint32_t,uint32_t,uint32_t);
extern uint32_t g2_flashdb_flash_write(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t g2_flashdb_crc32(uint32_t,const void *,uint32_t);
extern void g2_flashdb_cache_update(void *,const char *,uint32_t,uint32_t);
extern void *g2_flashdb_sector_cache_lookup(uint32_t,uint32_t);

static const char module[]="[FlashDB][kv]";
static const char names[]="[%s][%s] ";
static const char name_error[]="Error: The KV name length is more than %d\n";
static const char size_error[]="Error: The KV size is too big\n";

static uint32_t get_word(const void *p,uint32_t off) {
    return *(const uint32_t *)((const uint8_t *)p+off);
}
static void put_word(void *p,uint32_t off,uint32_t value) {
    *(uint32_t *)((uint8_t *)p+off)=value;
}
static void print_error(uint8_t *db,const char *message,uint32_t arg) {
    (void)g2_flashdb_print(module);
    uint32_t path=g2_flashdb_db_path((uint32_t)(uintptr_t)db);
    (void)g2_flashdb_print(names,(const char *)(uintptr_t)get_word(db,0),
                           (const char *)(uintptr_t)path);
    if(message==name_error) (void)g2_flashdb_print(message,arg);
    else (void)g2_flashdb_print(message);
}
static void update_sector(void *database,void *sector,uint32_t needed,uint8_t *full) {
    uint8_t *s=(uint8_t *)sector;
    uint8_t status[4];
    uint32_t addr=get_word(s,4u);
    *full=0u;
    if(s[1u]==1u) {
        (void)g2_flashdb_write_status((uint32_t)(uintptr_t)database,addr,
                                      status,4u,2u,1u);
        uint8_t *cache=g2_flashdb_sector_cache_lookup((uint32_t)(uintptr_t)database,addr);
        if(cache) cache[1u]=2u;
    } else if(s[1u]==2u &&
              (get_word(s,0x10u)<0x58u || get_word(s,0x10u)-needed<0x58u)) {
        (void)g2_flashdb_write_status((uint32_t)(uintptr_t)database,addr,
                                      status,4u,3u,1u);
        uint8_t *cache=g2_flashdb_sector_cache_lookup((uint32_t)(uintptr_t)database,addr);
        if(cache) cache[1u]=3u;
        *full=1u;
    }
}
static void update_sector_free(void *database,uint32_t sector,uint32_t free_at) {
    uint8_t *cache=g2_flashdb_sector_cache_lookup((uint32_t)(uintptr_t)database,sector);
    if(cache) {
        put_word(cache,0x14u,free_at);
        put_word(cache,0x10u,get_word(cache,4u)+
                 (get_word(database,0xcu)-free_at));
    }
}

uint32_t audio_flashdb_store_value(void *database,void *sector,const char *key,
                                   const void *value,uint32_t value_length) {
    uint8_t *db=(uint8_t *)database;
    uint8_t *s=(uint8_t *)sector;
    uint32_t key_length=g2_log_candidate_module_length((const uint8_t *)key);
    if(key_length>0x40u) {
        print_error(db,name_error,0x40u);
        return 5u;
    }
    uint8_t header[24];
    for(uint32_t i=0;i<24u;i++) header[i]=0xffu;
    put_word(header,4u,0x3030564bu);
    key_length=g2_log_candidate_module_length((const uint8_t *)key);
    put_word(header,8u,value_length+key_length+0x18u);
    header[16u]=(uint8_t)key_length;
    put_word(header,20u,value_length);
    uint32_t total=get_word(header,8u);
    if(get_word(db,0xcu)-0x10u<total) {
        print_error(db,size_error,0u);
        return 7u;
    }
    int32_t address=(int32_t)get_word(s,0x14u);
    if(address==-1) {
        address=audio_flashdb_prepare_space(db,s,total);
        if(address==-1) return 7u;
    }
    uint8_t full=0u;
    update_sector(db,s,total,&full);
    uint32_t crc=g2_flashdb_crc32(0,header+16u,4u);
    crc=g2_flashdb_crc32(crc,header+20u,4u);
    crc=g2_flashdb_crc32(crc,key,key_length);
    crc=g2_flashdb_crc32(crc,value,value_length);
    put_word(header,12u,crc);
    uint32_t result=g2_flashdb_write_status((uint32_t)(uintptr_t)db,(uint32_t)address,
                                            header,6u,1u,0u);
    if(result==0u)
        result=g2_flashdb_flash_write((uint32_t)(uintptr_t)db,(uint32_t)address+4u,
                                      (uint32_t)(uintptr_t)(header+4u),20u,0u);
    if(result==0u) {
        result=g2_flashdb_flash_write((uint32_t)(uintptr_t)db,(uint32_t)address+0x18u,
                                      (uint32_t)(uintptr_t)key,key_length,0u);
        if(full==0u)
            update_sector_free(db,get_word(s,4u),
                               value_length+(uint32_t)address+key_length+0x18u);
        g2_flashdb_cache_update(db,key,key_length,(uint32_t)address);
    }
    if(result==0u)
        result=g2_flashdb_flash_write((uint32_t)(uintptr_t)db,
                                      (uint32_t)address+key_length+0x18u,
                                      (uint32_t)(uintptr_t)value,value_length,0u);
    if(result==0u)
        result=g2_flashdb_write_status((uint32_t)(uintptr_t)db,(uint32_t)address,
                                       header,6u,2u,1u);
    if(result==0u && full!=0u) db[0x30u]=1u;
    return (uint8_t)result;
}
