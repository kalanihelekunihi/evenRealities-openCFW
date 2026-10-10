#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdio.h>
#include <time.h>
#include "fdb_low_lvl.h"
#define KV_STATUS_TABLE_SIZE FDB_STATUS_TABLE_SIZE(FDB_KV_STATUS_NUM)
#define KV_MAGIC_OFFSET offsetof(struct kv_hdr_data,magic)
#define db_init_ok(db) (((fdb_db_t)db)->init_ok)
#define db_name(db) (((fdb_db_t)db)->name)
#define db_lock(db) do{if(((fdb_db_t)db)->lock)((fdb_db_t)db)->lock((fdb_db_t)db);}while(0)
#define db_unlock(db) do{if(((fdb_db_t)db)->unlock)((fdb_db_t)db)->unlock((fdb_db_t)db);}while(0)
#undef FDB_INFO
#define FDB_INFO(...) diagnostic()
void diagnostic(void);
bool find_kv(fdb_kvdb_t,const char*,fdb_kv_t);
struct kv_hdr_data {
    uint8_t status_table[KV_STATUS_TABLE_SIZE];  /**< KV node status, @see fdb_kv_status_t */
    uint32_t magic;                              /**< magic word(`K`, `V`, `0`, `0`) */
    uint32_t len;                                /**< KV node total length (header + name + value), must align by FDB_WRITE_GRAN */
    uint32_t crc32;                              /**< KV node crc32(name_len + data_len + name + value) */
    uint8_t name_len;                            /**< name length */
    uint32_t value_len;                          /**< value length */
#if (FDB_WRITE_GRAN == 64)
    uint8_t padding[4];                          /**< align padding for 64bit write granularity */
#endif
#if (FDB_WRITE_GRAN == 128)
    uint8_t padding[12];                         /**< align padding for 128bit write granularity */
#endif
};
typedef struct kv_hdr_data *kv_hdr_data_t;
static size_t get_kv(fdb_kvdb_t db, const char *key, void *value_buf, size_t buf_len, size_t *value_len)
{
    struct fdb_kv kv;
    size_t read_len = 0;

    if (find_kv(db, key, &kv)) {
        if (value_len) {
            *value_len = kv.value_len;
        }
        if (buf_len > kv.value_len) {
            read_len = kv.value_len;
        } else {
            read_len = buf_len;
        }
        if (value_buf){
            _fdb_flash_read((fdb_db_t)db, kv.addr.value, (uint32_t *) value_buf, read_len);
        }
    } else if (value_len) {
        *value_len = 0;
    }

    return read_len;
}
size_t fdb_kv_get_blob(fdb_kvdb_t db, const char *key, fdb_blob_t blob)
{
    size_t read_len = 0;

    if (!db_init_ok(db)) {
        FDB_INFO("Error: KV (%s) isn't initialize OK.\n", db_name(db));
        return 0;
    }

    /* lock the KV cache */
    db_lock(db);

    read_len = get_kv(db, key, blob->buf, blob->size, &blob->saved.len);

    /* unlock the KV cache */
    db_unlock(db);

    return read_len;
}
static fdb_err_t write_kv_hdr(fdb_kvdb_t db, uint32_t addr, kv_hdr_data_t kv_hdr)
{
    fdb_err_t result = FDB_NO_ERR;
    /* write the status will by write granularity */
    result = _fdb_write_status((fdb_db_t)db, addr, kv_hdr->status_table, FDB_KV_STATUS_NUM, FDB_KV_PRE_WRITE, false);
    if (result != FDB_NO_ERR) {
        return result;
    }
    /* write other header data */
    result = _fdb_flash_write((fdb_db_t)db, addr + KV_MAGIC_OFFSET, &kv_hdr->magic, sizeof(struct kv_hdr_data) - KV_MAGIC_OFFSET, false);

    return result;
}
size_t test_get(fdb_kvdb_t d,const char*k,void*b,size_t n,size_t*l){return get_kv(d,k,b,n,l);}
fdb_err_t test_write(fdb_kvdb_t d,uint32_t a,kv_hdr_data_t h){return write_kv_hdr(d,a,h);}

volatile uint32_t read_address, read_count;
bool find_kv(fdb_kvdb_t d,const char*k,fdb_kv_t v){for(unsigned i=0;i<sizeof(*v);i++)((volatile unsigned char*)v)[i]=0xa7;v->value_len=8;v->addr.value=0xabc400;return true;}
fdb_err_t _fdb_flash_read(fdb_db_t d,uint32_t a,void*b,size_t n){read_address=a;read_count=n;return FDB_READ_ERR;}
fdb_err_t _fdb_flash_write(fdb_db_t d,uint32_t a,const void*b,size_t n,bool sync){return FDB_NO_ERR;}
fdb_err_t _fdb_write_status(fdb_db_t d,uint32_t a,uint8_t*t,size_t n,size_t i,bool sync){return FDB_NO_ERR;}
void diagnostic(void){__asm volatile("bkpt #0");}
