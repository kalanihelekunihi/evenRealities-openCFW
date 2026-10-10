#include <stdint.h>
#include <stddef.h>
#define FDB_KV_CACHE_TABLE_SIZE 64
#define FDB_DATA_UNUSED 0xffffffffu
struct node{uint16_t name_crc,active;uint32_t addr;};
typedef struct{struct node kv_cache_table[64];}*fdb_kvdb_t;
static uint32_t fdb_calc_crc32(uint32_t seed,const void*name,size_t len){return 0x77770000u;}
static void update_kv_cache(fdb_kvdb_t db, const char *name, size_t name_len, uint32_t addr)
{
    size_t i, empty_index = FDB_KV_CACHE_TABLE_SIZE, min_activity_index = FDB_KV_CACHE_TABLE_SIZE;
    uint16_t name_crc = (uint16_t) (fdb_calc_crc32(0, name, name_len) >> 16), min_activity = 0xFFFF;

    for (i = 0; i < FDB_KV_CACHE_TABLE_SIZE; i++) {
        if (addr != FDB_DATA_UNUSED) {
            /* update the KV address in cache */
            if (db->kv_cache_table[i].name_crc == name_crc) {
                db->kv_cache_table[i].addr = addr;
                return;
            } else if ((db->kv_cache_table[i].addr == FDB_DATA_UNUSED) && (empty_index == FDB_KV_CACHE_TABLE_SIZE)) {
                empty_index = i;
            } else if (db->kv_cache_table[i].addr != FDB_DATA_UNUSED) {
                if (db->kv_cache_table[i].active > 0) {
                    db->kv_cache_table[i].active--;
                }
                if (db->kv_cache_table[i].active < min_activity) {
                    min_activity_index = i;
                    min_activity = db->kv_cache_table[i].active;
                }
            }
        } else if (db->kv_cache_table[i].name_crc == name_crc) {
            /* delete the KV */
            db->kv_cache_table[i].addr = FDB_DATA_UNUSED;
            db->kv_cache_table[i].active = 0;
            return;
        }
    }
    /* add the KV to cache, using LRU (Least Recently Used) like algorithm */
    if (empty_index < FDB_KV_CACHE_TABLE_SIZE) {
        db->kv_cache_table[empty_index].addr = addr;
        db->kv_cache_table[empty_index].name_crc = name_crc;
        db->kv_cache_table[empty_index].active = FDB_KV_CACHE_TABLE_SIZE;
    } else if (min_activity_index < FDB_KV_CACHE_TABLE_SIZE) {
        db->kv_cache_table[min_activity_index].addr = addr;
        db->kv_cache_table[min_activity_index].name_crc = name_crc;
        db->kv_cache_table[min_activity_index].active = FDB_KV_CACHE_TABLE_SIZE;
    }
}
static struct{struct node kv_cache_table[64];}db;
void test(int mode){for(int i=0;i<64;i++){db.kv_cache_table[i].name_crc=i;db.kv_cache_table[i].active=5;db.kv_cache_table[i].addr=0x10000+i;}if(mode==1)db.kv_cache_table[63].name_crc=0x7777;update_kv_cache((fdb_kvdb_t)&db,"name",4,0x12345678);}
const void*output(void){return &db;}
