#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdio.h>
#include <time.h>
#include "fdb_low_lvl.h"
#define KV_STATUS_TABLE_SIZE FDB_STATUS_TABLE_SIZE(FDB_KV_STATUS_NUM)
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

const unsigned evidence[]={FDB_WRITE_GRAN,KV_STATUS_TABLE_SIZE,offsetof(struct kv_hdr_data,magic),sizeof(struct kv_hdr_data),sizeof(struct kv_hdr_data)-offsetof(struct kv_hdr_data,magic),sizeof(struct fdb_kv),offsetof(struct fdb_kv,value_len),offsetof(struct fdb_kv,addr.value),sizeof(struct fdb_kvdb),offsetof(struct fdb_db,init_ok),offsetof(struct fdb_db,lock),offsetof(struct fdb_db,unlock)};
