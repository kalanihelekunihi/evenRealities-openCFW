/* Native FlashDB GC KV move 0x5449c0. Lower FAL/FlashDB operations retain
 * their separately selected C implementations and product flash contracts. */
#include <stdint.h>

extern uint32_t audio_flashdb_kv_delete(void *,const char *,void *,uint32_t);
extern int32_t audio_flashdb_space_search(void *,void *,uint32_t);
extern void *audio_settings_copy_text(void *,const void *,uint32_t);
extern uint32_t g2_flashdb_find_no_cache(uint32_t,const char *,void *);
extern uint32_t g2_flashdb_write_status(uint32_t,uint32_t,uint8_t *,uint32_t,uint32_t,uint32_t);
extern uint32_t g2_flashdb_flash_read(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t g2_flashdb_flash_write(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern void g2_flashdb_cache_update(void *,const char *,uint32_t,uint32_t);
extern void *g2_flashdb_sector_cache_lookup(uint32_t,uint32_t);

static uint32_t get_word(const void *p,uint32_t off) {
    return *(const uint32_t *)((const uint8_t *)p+off);
}

static void update_sector_status(void *db,void *sector,uint32_t needed) {
    uint8_t *s=(uint8_t *)sector;
    uint8_t status[4];
    uint32_t address=get_word(s,4u);
    if(s[1u]==1u) {
        (void)g2_flashdb_write_status((uint32_t)(uintptr_t)db,address,
                                      status,4u,2u,1u);
        uint8_t *cache=g2_flashdb_sector_cache_lookup((uint32_t)(uintptr_t)db,address);
        if(cache) cache[1u]=2u;
    } else if(s[1u]==2u &&
              (get_word(s,0x10u)<0x58u || get_word(s,0x10u)-needed<0x58u)) {
        (void)g2_flashdb_write_status((uint32_t)(uintptr_t)db,address,
                                      status,4u,3u,1u);
        uint8_t *cache=g2_flashdb_sector_cache_lookup((uint32_t)(uintptr_t)db,address);
        if(cache) cache[1u]=3u;
    }
}

static void update_sector_free_bytes(void *db,uint32_t sector,uint32_t free_at) {
    uint8_t *cache=g2_flashdb_sector_cache_lookup((uint32_t)(uintptr_t)db,sector);
    if(cache) {
        *(uint32_t *)(void *)(cache+0x14u)=free_at;
        *(uint32_t *)(void *)(cache+0x10u)=get_word(cache,4u)+
            (get_word(db,0xcu)-free_at);
    }
}

uint32_t audio_flashdb_gc_move(uint32_t database,void *record) {
    uint8_t *db=(uint8_t *)(uintptr_t)database;
    uint8_t *kv=(uint8_t *)record;
    uint8_t status[4];
    uint32_t sector[6]={0};
    uint8_t found_record[88];
    uint8_t name[65]={0};
    uint8_t chunk[32];
    uint32_t result=0u;
    if(kv[0u]==2u)
        (void)audio_flashdb_kv_delete(db,0,kv,0u);
    uint32_t length=get_word(kv,8u);
    uint32_t destination=(uint32_t)audio_flashdb_space_search(db,sector,length);
    if(destination==UINT32_MAX) return 7u;
    if(db[0x31u]!=0u && kv[0u]==3u) {
        (void)audio_settings_copy_text(name,kv+0x10u,kv[2u]);
        if(g2_flashdb_find_no_cache(database,(const char *)name,found_record)!=0u) {
            (void)audio_flashdb_kv_delete(db,0,kv,1u);
            return 0u;
        }
    }
    update_sector_status(db,sector,length);
    (void)g2_flashdb_write_status(database,destination,status,6u,1u,0u);
    uint32_t payload=length-4u;
    for(uint32_t offset=0u;offset<payload;) {
        uint32_t count=payload-offset>32u?32u:payload-offset;
        (void)g2_flashdb_flash_read(database,get_word(kv,0x50u)+4u+offset,
                                    (uint32_t)(uintptr_t)chunk,count);
        result=g2_flashdb_flash_write(database,destination+4u+offset,
                                      (uint32_t)(uintptr_t)chunk,count,1u);
        offset+=count;
    }
    (void)g2_flashdb_write_status(database,destination,status,6u,2u,1u);
    uint32_t sector_size=get_word(db,0xcu);
    update_sector_free_bytes(db,sector_size*(destination/sector_size),
                             get_word(kv,0xcu)+destination+kv[2u]+0x18u);
    g2_flashdb_cache_update(db,(const char *)kv+0x10u,kv[2u],destination);
    (void)audio_flashdb_kv_delete(db,0,kv,1u);
    return (uint8_t)result;
}
