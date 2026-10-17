/* Copyright (c) 2020, Armink, <armink.ztl@gmail.com>
 * SPDX-License-Identifier: Apache-2.0
 * Extracted from pinned FlashDB 2.0.0; only function visibility/names adapt. */
#include <stdint.h>
#include <stddef.h>
#include <flashdb.h>
#include <fdb_low_lvl.h>
#define FAILED_ADDR 0xFFFFFFFF /* upstream fdb_tsdb.c:50 */
#define TSL_STATUS_TABLE_SIZE FDB_STATUS_TABLE_SIZE(FDB_TSL_STATUS_NUM)
#define SECTOR_HDR_DATA_SIZE FDB_WG_ALIGN(sizeof(struct sector_hdr_data))
#define LOG_IDX_DATA_SIZE FDB_WG_ALIGN(sizeof(struct log_idx_data))
#define db_sec_size(db) (((fdb_db_t)db)->sec_size)
#define db_max_size(db) (((fdb_db_t)db)->max_size)
struct sector_hdr_data {
    uint8_t status[FDB_STORE_STATUS_TABLE_SIZE]; /**< sector store status @see fdb_sector_store_status_t */
    uint32_t magic;                              /**< magic word(`T`, `S`, `L`, `0`) */
    fdb_time_t start_time;                       /**< the first start node's timestamp */
    struct {
        fdb_time_t time;                         /**< the last end node's timestamp */
        uint32_t index;                          /**< the last end node's index */
        uint8_t status[TSL_STATUS_TABLE_SIZE];   /**< end node status, @see fdb_tsl_status_t */
    } end_info[2];
    uint32_t reserved;
};
struct log_idx_data {
    uint8_t status_table[TSL_STATUS_TABLE_SIZE]; /**< node status, @see fdb_tsl_status_t */
    fdb_time_t time;                             /**< node timestamp */
    uint32_t log_len;                            /**< node total length (header + name + value), must align by FDB_WRITE_GRAN */
    uint32_t log_addr;                           /**< node address */
};
struct query_count_args {
    fdb_tsl_status_t status;
    size_t count;
};
uint32_t r1_fdb_get_next_sector_addr(fdb_tsdb_t db, tsdb_sec_info_t pre_sec, uint32_t traversed_len)
{
    if (traversed_len + db_sec_size(db) <= db_max_size(db)) {
        if (pre_sec->addr + db_sec_size(db) < db_max_size(db)) {
            return pre_sec->addr + db_sec_size(db);
        } else {
            /* the next sector is on the top of the database */
            return 0;
        }
    } else {
        /* finished */
        return FAILED_ADDR;
    }
}
uint32_t r1_fdb_get_last_sector_addr(fdb_tsdb_t db, tsdb_sec_info_t pre_sec, uint32_t traversed_len)
{
    if (traversed_len + db_sec_size(db) <= db_max_size(db)) {
        if (pre_sec->addr >= db_sec_size(db)) {
            /* the next sector is previous sector */
            return pre_sec->addr - db_sec_size(db);
        } else {
            /* the next sector is the last sector */
            return db_max_size(db) - db_sec_size(db);
        }
    } else {
        return FAILED_ADDR;
    }
}
uint32_t r1_fdb_get_next_tsl_addr(tsdb_sec_info_t sector, fdb_tsl_t pre_tsl)
{
    uint32_t addr = FAILED_ADDR;

    if (sector->status == FDB_SECTOR_STORE_EMPTY) {
        return FAILED_ADDR;
    }

    if (pre_tsl->addr.index + LOG_IDX_DATA_SIZE <= sector->end_idx) {
        addr = pre_tsl->addr.index + LOG_IDX_DATA_SIZE;
    } else {
        /* no TSL */
        return FAILED_ADDR;
    }

    return addr;
}
uint32_t r1_fdb_get_last_tsl_addr(tsdb_sec_info_t sector, fdb_tsl_t pre_tsl)
{
    uint32_t addr = FAILED_ADDR;

    if (sector->status == FDB_SECTOR_STORE_EMPTY) {
        return FAILED_ADDR;
    }

    if (pre_tsl->addr.index >= (sector->addr + SECTOR_HDR_DATA_SIZE + LOG_IDX_DATA_SIZE)) {
        addr = pre_tsl->addr.index - LOG_IDX_DATA_SIZE;
    } else {
        return FAILED_ADDR;
    }

    return addr;
}
bool r1_fdb_query_count_cb(fdb_tsl_t tsl, void *arg)
{
    struct query_count_args *args = arg;

    if (tsl->status == args->status) {
        args->count++;
    }

    return false;
}

_Static_assert(sizeof(struct fdb_db)==40 && sizeof(struct fdb_tsdb)==100,"native DB extents");
_Static_assert(offsetof(struct fdb_db,sec_size)==12 && offsetof(struct fdb_db,max_size)==16 && offsetof(struct fdb_db,oldest_addr)==20 && offsetof(struct fdb_db,init_ok)==24 && offsetof(struct fdb_db,lock)==28 && offsetof(struct fdb_db,unlock)==32,"native parent offsets");
_Static_assert(offsetof(struct fdb_tsdb,cur_sec)==40 && offsetof(struct fdb_tsdb,last_time)==80 && offsetof(struct fdb_tsdb,rollover)==92,"native TSDB offsets");
_Static_assert(sizeof(struct tsdb_sec_info)==40 && offsetof(struct tsdb_sec_info,status)==1 && offsetof(struct tsdb_sec_info,addr)==4 && offsetof(struct tsdb_sec_info,start_time)==12 && offsetof(struct tsdb_sec_info,end_time)==16 && offsetof(struct tsdb_sec_info,end_idx)==20,"native sector layout");
_Static_assert(sizeof(struct fdb_tsl)==20 && offsetof(struct fdb_tsl,status)==0 && offsetof(struct fdb_tsl,time)==4 && offsetof(struct fdb_tsl,addr.index)==12,"native TSL layout");
_Static_assert(sizeof(struct query_count_args)==8 && offsetof(struct query_count_args,count)==4 && SECTOR_HDR_DATA_SIZE==80 && LOG_IDX_DATA_SIZE==32,"native short enum/32-bit write geometry");
